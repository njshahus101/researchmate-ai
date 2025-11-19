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

# Import persistent session service
from services.persistent_session_service import create_persistent_session_service

# Initialize persistent session service for web UI
# IMPORTANT: Use same directory as orchestrator so web UI can see session history
# Use parent directory's orchestrator_sessions (since web UI runs from web_ui/ subdirectory)
orchestrator_sessions_path = str(Path(__file__).parent.parent / "orchestrator_sessions")
session_service = create_persistent_session_service(orchestrator_sessions_path)

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
    quality_report: Optional[dict] = None


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
    session_id = None
    actual_session_id = None
    
    try:
        # Get existing session ID or None (orchestrator will create new session)
        session_id = request.session_id

        # Call orchestrator agent directly using the pipeline
        # The orchestrator now handles session creation and message storage
        print(f"\n[WEB UI] ========== NEW REQUEST ==========")
        print(f"[WEB UI] Processing query: {request.message[:100]}...")
        print(f"[WEB UI] Session ID: {session_id or 'new'}")

        # Call the fixed pipeline with session_id (orchestrator handles session persistence)
        print(f"[WEB UI] Calling execute_fixed_pipeline...")
        result = await execute_fixed_pipeline(
            query=request.message,
            user_id="web_user",
            session_id=session_id
        )
        print(f"[WEB UI] Pipeline returned: status={result.get('status')}")

        # Extract the content and session ID from pipeline result
        if result.get("status") == "success":
            response_text = result.get("content", "")
            actual_session_id = result.get("session_id", session_id)

            # Log quality score if available
            quality_report = result.get("quality_report")
            if quality_report:
                print(f"[WEB UI] Quality Score: {quality_report.get('overall_score')}/100")

            print(f"[WEB UI] Pipeline completed successfully")
            print(f"[WEB UI] Response length: {len(response_text)} characters")
        else:
            response_text = f"Error: {result.get('error', 'Unknown error')}"
            actual_session_id = result.get("session_id", session_id or str(uuid.uuid4()))
            print(f"[WEB UI] Pipeline failed: {result.get('error')}")

        # Auto-generate session title from first message if this is a new session
        if not session_id and actual_session_id:
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            print(f"[WEB UI] Updating session title...")
            try:
                session_service.update_session_title(actual_session_id, title)
                print(f"[WEB UI] Session title updated successfully")
            except Exception as title_error:
                print(f"[WEB UI] Warning: Could not update session title: {title_error}")

        # Get message count for response
        try:
            print(f"[WEB UI] Retrieving session data...")
            session_data = session_service.get_session(actual_session_id)
            message_count = len(session_data.get("messages", []))
            print(f"[WEB UI] Session has {message_count} messages")
        except Exception as session_error:
            print(f"[WEB UI] Warning: Could not get session data: {session_error}")
            message_count = 0

        print(f"[WEB UI] Creating response object...")
        print(f"[WEB UI]   - response length: {len(response_text)}")
        print(f"[WEB UI]   - session_id: {actual_session_id}")
        print(f"[WEB UI]   - message_id: {message_count}")
        
        response_obj = ChatResponse(
            response=response_text,
            session_id=actual_session_id,
            message_id=message_count,
            quality_report=result.get("quality_report")
        )
        print(f"[WEB UI] Response object created successfully")
        print(f"[WEB UI] Returning response to client...")
        print(f"[WEB UI] ========== REQUEST COMPLETE ==========\n")
        return response_obj

    except Exception as e:
        print(f"\n[WEB UI] ========== ERROR OCCURRED ==========")
        print(f"[WEB UI] Error Type: {type(e).__name__}")
        print(f"[WEB UI] Error Message: {e}")
        print(f"[WEB UI] Session ID when error occurred: {actual_session_id or session_id or 'None'}")
        print(f"[WEB UI] ========== FULL TRACEBACK ==========")
        import traceback
        traceback.print_exc()
        print(f"[WEB UI] =====================================\n")

        # Return detailed error information to help diagnose
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc()
        }
        
        # Create a user-friendly error message but include details for debugging
        error_message = f"An error occurred: {type(e).__name__} - {str(e)[:200]}"
        raise HTTPException(status_code=500, detail=error_message)


@app.get("/api/sessions")
async def get_sessions(user_id: str = "web_user"):
    """Get all conversation sessions"""
    sessions = session_service.list_sessions(user_id)
    # Map session_id to id for frontend compatibility
    for session in sessions:
        session["id"] = session["session_id"]
    return {"sessions": sessions}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific session with all messages"""
    try:
        session_data = session_service.get_session(session_id)
        return {
            "session": {
                "id": session_data["session_id"],
                "title": session_data["title"],
                "created_at": session_data["created_at"],
                "updated_at": session_data["updated_at"],
                "user_id": session_data["user_id"]
            },
            "messages": session_data["messages"]
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")


@app.post("/api/sessions")
async def create_session(request: SessionCreate):
    """Create a new conversation session"""
    session_id = session_service.create_session(
        user_id="web_user",
        title=request.title
    )
    return {"session_id": session_id}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a conversation session"""
    session_service.delete_session(session_id)
    return {"status": "deleted"}


@app.put("/api/sessions/{session_id}/title")
async def update_session_title(session_id: str, title: str):
    """Update session title"""
    session_service.update_session_title(session_id, title)
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
