"""
MCP Session Service

A session service implementation that uses the MCP File System Server
for persistent storage of conversation sessions and messages.

This replaces InMemorySessionService with persistent, MCP-backed storage.
"""

import asyncio
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPSessionService:
    """
    Session service backed by MCP File System Server.

    Provides persistent storage for:
    - Conversation sessions
    - Message history
    - User context

    Compatible with Google ADK session service interface.

    Usage:
        async with MCPSessionService() as service:
            session_id = await service.create_session("user_123", "My Session")
            await service.add_message(session_id, "user", "Hello!")
    """

    def __init__(self, mcp_server_path: str = None):
        """
        Initialize MCP Session Service.

        Args:
            mcp_server_path: Path to MCP server script (defaults to mcp_servers/filesystem_server.py)
        """
        if mcp_server_path is None:
            # Default to the filesystem server in mcp_servers/
            project_root = Path(__file__).parent.parent
            mcp_server_path = str(project_root / "mcp_servers" / "filesystem_server.py")

        self.mcp_server_path = mcp_server_path
        self._session: Optional[ClientSession] = None
        self._stdio_context = None
        self._read_stream = None
        self._write_stream = None

    async def __aenter__(self):
        """Enter async context - start MCP server"""
        server_params = StdioServerParameters(
            command="python",
            args=[self.mcp_server_path],
            env=None
        )

        # Start the stdio client
        self._stdio_context = stdio_client(server_params)
        self._read_stream, self._write_stream = await self._stdio_context.__aenter__()

        # Create and initialize session
        self._session = ClientSession(self._read_stream, self._write_stream)
        await self._session.initialize()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context - cleanup MCP server"""
        if self._session:
            await self._session.__aexit__(exc_type, exc_val, exc_tb)

        if self._stdio_context:
            await self._stdio_context.__aexit__(exc_type, exc_val, exc_tb)

        return False

    async def create_session(
        self,
        user_id: str = "default",
        title: str = "New Conversation",
        session_id: Optional[str] = None
    ) -> str:
        """
        Create a new conversation session.

        Args:
            user_id: User identifier
            title: Session title
            session_id: Optional session ID (generated if not provided)

        Returns:
            Session ID
        """
        if not self._session:
            raise RuntimeError("Service not initialized. Use 'async with MCPSessionService() as service:'")

        if session_id is None:
            session_id = str(uuid.uuid4())

        result = await self._session.call_tool(
            "create_session",
            arguments={
                "session_id": session_id,
                "user_id": user_id,
                "title": title
            }
        )

        response = json.loads(result.content[0].text)

        if response["status"] == "error":
            raise Exception(f"Failed to create session: {response['message']}")

        return session_id

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a message to a session.

        Args:
            session_id: Session identifier
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Optional metadata dictionary

        Returns:
            Result dictionary with status
        """
        if not self._session:
            raise RuntimeError("Service not initialized. Use 'async with MCPSessionService() as service:'")

        result = await self._session.call_tool(
            "add_message",
            arguments={
                "session_id": session_id,
                "role": role,
                "content": content,
                "metadata": metadata or {}
            }
        )

        return json.loads(result.content[0].text)

    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve a complete session with all messages.

        Args:
            session_id: Session identifier

        Returns:
            Session data dictionary
        """
        if not self._session:
            raise RuntimeError("Service not initialized. Use 'async with MCPSessionService() as service:'")

        result = await self._session.call_tool(
            "get_session",
            arguments={"session_id": session_id}
        )

        response = json.loads(result.content[0].text)

        if response["status"] == "error":
            raise Exception(f"Failed to get session: {response['message']}")

        return response["session"]

    async def list_sessions(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """
        List all sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            List of session metadata dictionaries
        """
        if not self._session:
            raise RuntimeError("Service not initialized. Use 'async with MCPSessionService() as service:'")

        result = await self._session.call_tool(
            "list_sessions",
            arguments={"user_id": user_id}
        )

        response = json.loads(result.content[0].text)

        if response["status"] == "error":
            raise Exception(f"Failed to list sessions: {response['message']}")

        return response["sessions"]

    async def get_session_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get message history for a session.

        Args:
            session_id: Session identifier
            limit: Optional limit on number of messages to return

        Returns:
            List of message dictionaries
        """
        session_data = await self.get_session(session_id)
        messages = session_data.get("messages", [])

        if limit:
            messages = messages[-limit:]

        return messages

    async def close(self):
        """Close the MCP client session (deprecated - use async context manager instead)"""
        await self.__aexit__(None, None, None)


# Synchronous wrapper for easier integration

class MCPSessionServiceSync:
    """
    Synchronous wrapper for MCPSessionService.

    Provides a simple synchronous API by managing the event loop internally.
    Useful for integrating with non-async code.

    Usage:
        service = MCPSessionServiceSync()
        session_id = service.create_session("user_123", "My Session")
        service.add_message(session_id, "user", "Hello!")
        service.close()  # Important: call close() when done
    """

    def __init__(self, mcp_server_path: str = None):
        """Initialize synchronous MCP session service"""
        self._async_service = MCPSessionService(mcp_server_path)
        self._loop = None
        self._initialized = False

    def _get_loop(self):
        """Get or create event loop"""
        if self._loop is None or self._loop.is_closed():
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop

    def _run_async(self, coro):
        """Run an async coroutine synchronously"""
        loop = self._get_loop()
        return loop.run_until_complete(coro)

    def _ensure_initialized(self):
        """Ensure the async service is initialized"""
        if not self._initialized:
            # Enter the async context
            loop = self._get_loop()
            loop.run_until_complete(self._async_service.__aenter__())
            self._initialized = True

    def create_session(
        self,
        user_id: str = "default",
        title: str = "New Conversation",
        session_id: Optional[str] = None
    ) -> str:
        """Create a new session (synchronous)"""
        self._ensure_initialized()
        return self._run_async(
            self._async_service.create_session(user_id, title, session_id)
        )

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a message to a session (synchronous)"""
        self._ensure_initialized()
        return self._run_async(
            self._async_service.add_message(session_id, role, content, metadata)
        )

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get a session (synchronous)"""
        self._ensure_initialized()
        return self._run_async(self._async_service.get_session(session_id))

    def list_sessions(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """List sessions (synchronous)"""
        self._ensure_initialized()
        return self._run_async(self._async_service.list_sessions(user_id))

    def get_session_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get session history (synchronous)"""
        self._ensure_initialized()
        return self._run_async(
            self._async_service.get_session_history(session_id, limit)
        )

    def close(self):
        """Close the service"""
        if self._initialized:
            self._run_async(self._async_service.__aexit__(None, None, None))
            self._initialized = False
        if self._loop and not self._loop.is_closed():
            self._loop.close()
            self._loop = None


# Factory function for creating session service

def create_mcp_session_service(
    use_sync: bool = True,
    mcp_server_path: Optional[str] = None
) -> Any:
    """
    Factory function to create MCP session service.

    Args:
        use_sync: If True, return synchronous wrapper. If False, return async service.
        mcp_server_path: Optional path to MCP server script

    Returns:
        MCPSessionServiceSync or MCPSessionService instance
    """
    if use_sync:
        print("[OK] Creating MCP Session Service (Synchronous)")
        print("     Storage: MCP File System Server (Persistent)")
        return MCPSessionServiceSync(mcp_server_path)
    else:
        print("[OK] Creating MCP Session Service (Async)")
        print("     Storage: MCP File System Server (Persistent)")
        return MCPSessionService(mcp_server_path)


if __name__ == "__main__":
    # Test the MCP session service
    print("\nTesting MCP Session Service...\n")

    # Create synchronous service
    service = create_mcp_session_service(use_sync=True)

    try:
        # Create a test session
        print("1. Creating session...")
        session_id = service.create_session(
            user_id="test_user",
            title="Test Conversation"
        )
        print(f"   Session created: {session_id}\n")

        # Add messages
        print("2. Adding messages...")
        service.add_message(session_id, "user", "Hello, how are you?")
        service.add_message(session_id, "assistant", "I'm doing well! How can I help you today?")
        service.add_message(session_id, "user", "Tell me about machine learning")
        print("   Messages added\n")

        # Get session history
        print("3. Retrieving session history...")
        history = service.get_session_history(session_id)
        for msg in history:
            print(f"   [{msg['role']}] {msg['content'][:50]}...")
        print()

        # List all sessions
        print("4. Listing all sessions...")
        sessions = service.list_sessions("test_user")
        print(f"   Found {len(sessions)} session(s)")
        for sess in sessions:
            print(f"   - {sess['title']} ({sess['message_count']} messages)")
        print()

        print("[OK] MCP Session Service test complete!")

    finally:
        service.close()
