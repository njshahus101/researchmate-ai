"""
MCP File System Server for ResearchMate AI

A proper Model Context Protocol server that provides persistent file system storage
for conversation sessions, user memory, and agent state.

Uses the official MCP Python SDK to implement resources and tools for:
- Session management (create, read, update, list sessions)
- Memory persistence (user preferences, research history)
- Conversation history (messages, context)
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)


class FileSystemServer:
    """
    MCP File System Server for ResearchMate AI.

    Provides persistent storage for:
    - Conversation sessions
    - User memory and preferences
    - Research history
    - Agent state
    """

    def __init__(self, storage_root: str = "mcp_storage"):
        """
        Initialize the file system server.

        Args:
            storage_root: Root directory for all MCP storage
        """
        self.storage_root = Path(storage_root)
        self.sessions_dir = self.storage_root / "sessions"
        self.memory_dir = self.storage_root / "memory"
        self.state_dir = self.storage_root / "state"

        # Create directories if they don't exist
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.server = Server("researchmate-filesystem")
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up MCP resource and tool handlers"""

        # Register list_resources handler
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List all available resources (sessions, memory files, etc.)"""
            resources = []

            # List all session files
            for session_file in self.sessions_dir.glob("*.json"):
                resources.append(
                    Resource(
                        uri=f"session://{session_file.stem}",
                        name=f"Session: {session_file.stem}",
                        mimeType="application/json",
                        description=f"Conversation session {session_file.stem}"
                    )
                )

            # List all memory files
            for memory_file in self.memory_dir.glob("*.json"):
                resources.append(
                    Resource(
                        uri=f"memory://{memory_file.stem}",
                        name=f"Memory: {memory_file.stem}",
                        mimeType="application/json",
                        description=f"User memory for {memory_file.stem}"
                    )
                )

            return resources

        # Register read_resource handler
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a resource by URI"""
            if uri.startswith("session://"):
                session_id = uri.replace("session://", "")
                return self._read_session(session_id)
            elif uri.startswith("memory://"):
                user_id = uri.replace("memory://", "")
                return self._read_memory(user_id)
            else:
                raise ValueError(f"Unsupported URI scheme: {uri}")

        # Register list_tools handler
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available tools"""
            return [
                Tool(
                    name="create_session",
                    description="Create a new conversation session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Unique session identifier"},
                            "user_id": {"type": "string", "description": "User identifier"},
                            "title": {"type": "string", "description": "Session title"}
                        },
                        "required": ["session_id", "user_id"]
                    }
                ),
                Tool(
                    name="add_message",
                    description="Add a message to a session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"},
                            "role": {"type": "string", "description": "Message role (user/assistant/system)"},
                            "content": {"type": "string", "description": "Message content"},
                            "metadata": {"type": "object", "description": "Optional metadata"}
                        },
                        "required": ["session_id", "role", "content"]
                    }
                ),
                Tool(
                    name="get_session",
                    description="Retrieve a complete session with all messages",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier"}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="list_sessions",
                    description="List all sessions for a user",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User identifier"}
                        },
                        "required": ["user_id"]
                    }
                ),
                Tool(
                    name="store_memory",
                    description="Store user memory (preferences, research history)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User identifier"},
                            "memory_type": {"type": "string", "description": "Type of memory (preference/research_history/domain_knowledge)"},
                            "key": {"type": "string", "description": "Memory key"},
                            "value": {"type": "object", "description": "Memory value"}
                        },
                        "required": ["user_id", "memory_type", "key", "value"]
                    }
                ),
                Tool(
                    name="get_memory",
                    description="Retrieve user memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User identifier"},
                            "memory_type": {"type": "string", "description": "Type of memory"},
                            "key": {"type": "string", "description": "Memory key (optional)"}
                        },
                        "required": ["user_id"]
                    }
                )
            ]

        # Register call_tool handler
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            if name == "create_session":
                result = self._create_session(
                    arguments["session_id"],
                    arguments["user_id"],
                    arguments.get("title", "New Session")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "add_message":
                result = self._add_message(
                    arguments["session_id"],
                    arguments["role"],
                    arguments["content"],
                    arguments.get("metadata")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "get_session":
                result = self._get_session(arguments["session_id"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "list_sessions":
                result = self._list_sessions(arguments["user_id"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "store_memory":
                result = self._store_memory(
                    arguments["user_id"],
                    arguments["memory_type"],
                    arguments["key"],
                    arguments["value"]
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "get_memory":
                result = self._get_memory(
                    arguments["user_id"],
                    arguments.get("memory_type"),
                    arguments.get("key")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            else:
                raise ValueError(f"Unknown tool: {name}")

    # Session management methods

    def _create_session(self, session_id: str, user_id: str, title: str = "New Session") -> Dict[str, Any]:
        """Create a new session"""
        session_file = self.sessions_dir / f"{session_id}.json"

        if session_file.exists():
            return {"status": "error", "message": "Session already exists"}

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }

        session_file.write_text(json.dumps(session_data, indent=2))

        return {"status": "success", "session_id": session_id}

    def _add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a message to a session"""
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            return {"status": "error", "message": "Session not found"}

        session_data = json.loads(session_file.read_text())

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        session_data["messages"].append(message)
        session_data["updated_at"] = datetime.now().isoformat()

        session_file.write_text(json.dumps(session_data, indent=2))

        return {"status": "success", "message_count": len(session_data["messages"])}

    def _get_session(self, session_id: str) -> Dict[str, Any]:
        """Get a complete session"""
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            return {"status": "error", "message": "Session not found"}

        session_data = json.loads(session_file.read_text())
        return {"status": "success", "session": session_data}

    def _list_sessions(self, user_id: str) -> Dict[str, Any]:
        """List all sessions for a user"""
        sessions = []

        for session_file in self.sessions_dir.glob("*.json"):
            session_data = json.loads(session_file.read_text())
            if session_data.get("user_id") == user_id:
                sessions.append({
                    "session_id": session_data["session_id"],
                    "title": session_data["title"],
                    "created_at": session_data["created_at"],
                    "updated_at": session_data["updated_at"],
                    "message_count": len(session_data["messages"])
                })

        # Sort by updated_at descending
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)

        return {"status": "success", "sessions": sessions, "count": len(sessions)}

    def _read_session(self, session_id: str) -> str:
        """Read a session resource"""
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            return json.dumps({"error": "Session not found"})

        return session_file.read_text()

    # Memory management methods

    def _store_memory(
        self,
        user_id: str,
        memory_type: str,
        key: str,
        value: Any
    ) -> Dict[str, Any]:
        """Store user memory"""
        memory_file = self.memory_dir / f"{user_id}.json"

        if memory_file.exists():
            memory_data = json.loads(memory_file.read_text())
        else:
            memory_data = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "preferences": {},
                "research_history": [],
                "domain_knowledge": {}
            }

        if memory_type == "preference":
            memory_data["preferences"][key] = {
                "value": value,
                "updated_at": datetime.now().isoformat()
            }
        elif memory_type == "research_history":
            memory_data["research_history"].append({
                "key": key,
                "data": value,
                "timestamp": datetime.now().isoformat()
            })
        elif memory_type == "domain_knowledge":
            memory_data["domain_knowledge"][key] = {
                "value": value,
                "updated_at": datetime.now().isoformat()
            }
        else:
            return {"status": "error", "message": f"Unknown memory type: {memory_type}"}

        memory_data["updated_at"] = datetime.now().isoformat()
        memory_file.write_text(json.dumps(memory_data, indent=2))

        return {"status": "success"}

    def _get_memory(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
        key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve user memory"""
        memory_file = self.memory_dir / f"{user_id}.json"

        if not memory_file.exists():
            return {"status": "error", "message": "No memory found for user"}

        memory_data = json.loads(memory_file.read_text())

        if memory_type is None:
            # Return all memory
            return {"status": "success", "memory": memory_data}

        if memory_type not in memory_data:
            return {"status": "error", "message": f"Unknown memory type: {memory_type}"}

        if key is None:
            # Return all memory of this type
            return {"status": "success", memory_type: memory_data[memory_type]}

        # Return specific key
        if memory_type == "research_history":
            # Research history is a list, search by key
            items = [item for item in memory_data["research_history"] if item.get("key") == key]
            return {"status": "success", "items": items}
        else:
            # Preferences and domain_knowledge are dicts
            if key in memory_data[memory_type]:
                return {"status": "success", "value": memory_data[memory_type][key]}
            else:
                return {"status": "error", "message": f"Key not found: {key}"}

    def _read_memory(self, user_id: str) -> str:
        """Read a memory resource"""
        memory_file = self.memory_dir / f"{user_id}.json"

        if not memory_file.exists():
            return json.dumps({"error": "Memory not found"})

        return memory_file.read_text()

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for the MCP file system server"""
    server = FileSystemServer(storage_root="mcp_storage")
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
