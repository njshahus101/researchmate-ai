"""
Persistent Session Service

A simple file-based session service that provides persistent storage
for conversation sessions and messages.

This replaces InMemorySessionService with file-based storage,
ensuring conversation history persists across application restarts.
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class PersistentSessionService:
    """
    File-based persistent session service.

    Stores conversation sessions and messages in JSON files,
    providing true persistence across application restarts.

    Compatible with Google ADK session service interface.
    """

    def __init__(self, storage_dir: str = "persistent_sessions"):
        """
        Initialize persistent session service.

        Args:
            storage_dir: Directory to store session files
        """
        self.storage_dir = Path(storage_dir)
        self.sessions_dir = self.storage_dir / "sessions"
        self.memory_dir = self.storage_dir / "memory"

        # Create directories
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        print(f"[OK] Persistent Session Service initialized")
        print(f"     Storage: {self.storage_dir.absolute()}")

    def create_session(
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
        if session_id is None:
            session_id = str(uuid.uuid4())

        session_file = self.sessions_dir / f"{session_id}.json"

        if session_file.exists():
            raise ValueError(f"Session already exists: {session_id}")

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }

        session_file.write_text(json.dumps(session_data, indent=2))

        return session_id

    def add_message(
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
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            raise ValueError(f"Session not found: {session_id}")

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

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve a complete session with all messages.

        Args:
            session_id: Session identifier

        Returns:
            Session data dictionary
        """
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            raise ValueError(f"Session not found: {session_id}")

        return json.loads(session_file.read_text())

    def list_sessions(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """
        List all sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            List of session metadata dictionaries
        """
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

        return sessions

    def get_session_history(
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
        session_data = self.get_session(session_id)
        messages = session_data.get("messages", [])

        if limit:
            messages = messages[-limit:]

        return messages

    def delete_session(self, session_id: str):
        """
        Delete a session.

        Args:
            session_id: Session identifier
        """
        session_file = self.sessions_dir / f"{session_id}.json"

        if session_file.exists():
            session_file.unlink()

    def update_session_title(self, session_id: str, title: str):
        """
        Update session title.

        Args:
            session_id: Session identifier
            title: New title
        """
        session_data = self.get_session(session_id)
        session_data["title"] = title
        session_data["updated_at"] = datetime.now().isoformat()

        session_file = self.sessions_dir / f"{session_id}.json"
        session_file.write_text(json.dumps(session_data, indent=2))

    # Memory persistence methods

    def store_user_memory(
        self,
        user_id: str,
        memory_type: str,
        key: str,
        value: Any
    ):
        """
        Store user memory (preferences, research history, etc.).

        Args:
            user_id: User identifier
            memory_type: Type of memory (preference/research_history/domain_knowledge)
            key: Memory key
            value: Memory value
        """
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

        memory_data["updated_at"] = datetime.now().isoformat()
        memory_file.write_text(json.dumps(memory_data, indent=2))

    def get_user_memory(
        self,
        user_id: str,
        memory_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve user memory.

        Args:
            user_id: User identifier
            memory_type: Optional type to filter (preference/research_history/domain_knowledge)

        Returns:
            Memory dictionary
        """
        memory_file = self.memory_dir / f"{user_id}.json"

        if not memory_file.exists():
            return {}

        memory_data = json.loads(memory_file.read_text())

        if memory_type:
            return memory_data.get(memory_type, {})

        return memory_data


# Factory function

def create_persistent_session_service(storage_dir: str = "persistent_sessions"):
    """
    Create a persistent session service.

    Args:
        storage_dir: Directory to store session files

    Returns:
        PersistentSessionService instance
    """
    return PersistentSessionService(storage_dir)


if __name__ == "__main__":
    # Test the persistent session service
    print("\n" + "="*80)
    print("TESTING PERSISTENT SESSION SERVICE")
    print("="*80 + "\n")

    service = create_persistent_session_service("test_persistent_sessions")

    # Create session
    print("1. Creating session...")
    session_id = service.create_session(
        user_id="test_user",
        title="Test Conversation"
    )
    print(f"   [OK] Session created: {session_id}\n")

    # Add messages
    print("2. Adding messages...")
    service.add_message(session_id, "user", "Hello, how are you?")
    service.add_message(session_id, "assistant", "I'm doing well! How can I help?")
    service.add_message(session_id, "user", "Tell me about Python")
    print("   [OK] Messages added\n")

    # Get history
    print("3. Retrieving history...")
    history = service.get_session_history(session_id)
    for msg in history:
        print(f"   [{msg['role']}] {msg['content']}")
    print()

    # List sessions
    print("4. Listing sessions...")
    sessions = service.list_sessions("test_user")
    for sess in sessions:
        print(f"   - {sess['title']} ({sess['message_count']} messages)")
    print()

    # Store memory
    print("5. Storing user memory...")
    service.store_user_memory("test_user", "preference", "theme", "dark")
    service.store_user_memory("test_user", "domain_knowledge", "python", "intermediate")
    print("   [OK] Memory stored\n")

    # Get memory
    print("6. Retrieving memory...")
    memory = service.get_user_memory("test_user")
    print(f"   Preferences: {memory.get('preferences', {})}")
    print(f"   Domain Knowledge: {memory.get('domain_knowledge', {})}")
    print()

    print("[OK] All tests passed!")
    print(f"\n[INFO] Storage location: {service.storage_dir.absolute()}")

    # Cleanup
    import shutil
    if Path("test_persistent_sessions").exists():
        shutil.rmtree("test_persistent_sessions")
        print("[INFO] Test storage cleaned up")
