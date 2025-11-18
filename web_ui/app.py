"""
ResearchMate AI - Custom Web UI
FastAPI backend with direct orchestrator integration
"""

import sys
import uuid
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from pydantic import BaseModel
import asyncio

# Add parent directory to path to import adk_agents
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import orchestrator agent
from adk_agents.orchestrator.agent import agent as orchestrator_agent, execute_fixed_pipeline
from google.adk.runners import InMemoryRunner

# Import database
from database import db

# Initialize FastAPI app
app = FastAPI(title="ResearchMate AI", version="1.0.0")

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


# ============================================================
# Request/Response Models
# ============================================================

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: int


class SessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"


# ============================================================
# API Endpoints
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - sends message to orchestrator agent
    """
    try:
        # Create or get session
        session_id = request.session_id
        if not session_id:
            session_id = str(uuid.uuid4())
            db.create_session(session_id, title="New Conversation")

        # Store user message
        db.add_message(session_id, "user", request.message)

        # Call orchestrator agent directly using the pipeline
        print(f"\n[WEB UI] Processing query: {request.message[:100]}...")
        print(f"[WEB UI] Session ID: {session_id}")

        # Call the fixed pipeline directly (bypass ADK's extra LLM call)
        result = await execute_fixed_pipeline(
            query=request.message,
            user_id="web_user"
        )

        # Extract the content from pipeline result
        if result.get("status") == "success":
            response_text = result.get("content", "")
            print(f"[WEB UI] Pipeline completed successfully")
        else:
            response_text = f"Error: {result.get('error', 'Unknown error')}"
            print(f"[WEB UI] Pipeline failed: {result.get('error')}")

        # Store assistant response
        db.add_message(
            session_id,
            "assistant",
            response_text,
            metadata={
                "pipeline_status": result.get("status"),
                "sources_fetched": result.get("sources_fetched", 0),
                "pipeline_steps": result.get("pipeline_steps", {})
            }
        )

        # Auto-generate session title from first message
        messages = db.get_session_messages(session_id)
        if len(messages) == 2:  # First Q&A pair
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            db.update_session_title(session_id, title)

        return ChatResponse(
            response=response_text,
            session_id=session_id,
            message_id=len(messages)
        )

    except Exception as e:
        print(f"[WEB UI] ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def get_sessions(user_id: str = "default"):
    """Get all conversation sessions"""
    sessions = db.get_all_sessions(user_id)
    return {"sessions": sessions}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific session with all messages"""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.get_session_messages(session_id)
    return {
        "session": session,
        "messages": messages
    }


@app.post("/api/sessions")
async def create_session(request: SessionCreate):
    """Create a new conversation session"""
    session_id = str(uuid.uuid4())
    db.create_session(session_id, title=request.title)
    return {"session_id": session_id}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a conversation session"""
    db.delete_session(session_id)
    return {"status": "deleted"}


@app.put("/api/sessions/{session_id}/title")
async def update_session_title(session_id: str, title: str):
    """Update session title"""
    db.update_session_title(session_id, title)
    return {"status": "updated"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ResearchMate AI Web UI",
        "version": "1.0.0"
    }


# ============================================================
# Main Entry Point
# ============================================================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("ResearchMate AI - Custom Web UI")
    print("="*60)
    print("\nStarting server...")
    print("Access the UI at: http://localhost:8080")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
