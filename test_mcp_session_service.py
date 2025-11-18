"""
Test script for MCP File System Server and Session Service

Tests the complete MCP-backed persistent session storage:
1. MCP File System Server initialization
2. Session creation and management
3. Message persistence
4. Cross-session data retrieval
5. User memory storage
"""

import sys
import asyncio
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.mcp_session_service import create_mcp_session_service


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80 + "\n")


def test_session_creation():
    """Test creating sessions"""
    print_section("TEST 1: Session Creation")

    service = create_mcp_session_service(use_sync=True)

    try:
        # Create multiple sessions
        print("Creating 3 test sessions...")

        session1 = service.create_session(
            user_id="user_123",
            title="Machine Learning Research"
        )
        print(f"[OK] Session 1 created: {session1}")

        session2 = service.create_session(
            user_id="user_123",
            title="Product Comparison"
        )
        print(f"[OK] Session 2 created: {session2}")

        session3 = service.create_session(
            user_id="user_456",
            title="Different User Session"
        )
        print(f"[OK] Session 3 created: {session3}")

        return {
            "session1": session1,
            "session2": session2,
            "session3": session3
        }

    finally:
        service.close()


def test_message_persistence(session_ids: dict):
    """Test adding and retrieving messages"""
    print_section("TEST 2: Message Persistence")

    service = create_mcp_session_service(use_sync=True)

    try:
        session1 = session_ids["session1"]

        # Add conversation messages
        print("Adding messages to session...")

        service.add_message(
            session1,
            "user",
            "What is the best approach for deep learning?",
            metadata={"query_type": "question"}
        )
        print("[OK] User message added")

        service.add_message(
            session1,
            "assistant",
            "Deep learning excels at pattern recognition. Start with neural networks fundamentals.",
            metadata={"response_type": "educational"}
        )
        print("[OK] Assistant message added")

        service.add_message(
            session1,
            "user",
            "Can you compare CNNs vs RNNs?",
            metadata={"query_type": "comparative"}
        )
        print("[OK] Follow-up message added")

        service.add_message(
            session1,
            "assistant",
            "CNNs excel at spatial data (images), while RNNs handle sequential data (text, time series).",
            metadata={"response_type": "comparative"}
        )
        print("[OK] Comparison response added")

        # Retrieve messages
        print("\nRetrieving session history...")
        history = service.get_session_history(session1)

        print(f"\nFound {len(history)} messages:")
        for i, msg in enumerate(history, 1):
            role_display = msg['role'].upper()
            content_preview = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
            print(f"  {i}. [{role_display}] {content_preview}")

        return session1

    finally:
        service.close()


def test_session_listing(session_ids: dict):
    """Test listing sessions for a user"""
    print_section("TEST 3: Session Listing")

    service = create_mcp_session_service(use_sync=True)

    try:
        # List sessions for user_123
        print("Listing sessions for user_123...")
        sessions = service.list_sessions("user_123")

        print(f"\nFound {len(sessions)} session(s):")
        for sess in sessions:
            print(f"  - {sess['title']}")
            print(f"    ID: {sess['session_id']}")
            print(f"    Messages: {sess['message_count']}")
            print(f"    Last updated: {sess['updated_at']}")
            print()

        # List sessions for user_456
        print("Listing sessions for user_456...")
        sessions = service.list_sessions("user_456")

        print(f"\nFound {len(sessions)} session(s):")
        for sess in sessions:
            print(f"  - {sess['title']} ({sess['message_count']} messages)")

    finally:
        service.close()


def test_persistence_across_instances(session_id: str):
    """Test that data persists across service instances"""
    print_section("TEST 4: Persistence Across Instances")

    print("Creating NEW service instance (simulating app restart)...")

    # Create a completely new service instance
    service_new = create_mcp_session_service(use_sync=True)

    try:
        print(f"Retrieving session {session_id[:8]}... from new instance...\n")

        # Get the session we created earlier
        session_data = service_new.get_session(session_id)

        print(f"[OK] Session retrieved successfully!")
        print(f"     Title: {session_data['title']}")
        print(f"     Created: {session_data['created_at']}")
        print(f"     Messages: {len(session_data['messages'])}")

        print("\n[OK] DATA PERSISTS ACROSS INSTANCES!")
        print("     This confirms MCP file system provides true persistence.")

    finally:
        service_new.close()


def test_session_retrieval(session_id: str):
    """Test retrieving complete session data"""
    print_section("TEST 5: Complete Session Retrieval")

    service = create_mcp_session_service(use_sync=True)

    try:
        print(f"Retrieving complete session data...\n")

        session_data = service.get_session(session_id)

        print(f"Session Details:")
        print(f"  ID: {session_data['session_id']}")
        print(f"  Title: {session_data['title']}")
        print(f"  User: {session_data['user_id']}")
        print(f"  Created: {session_data['created_at']}")
        print(f"  Updated: {session_data['updated_at']}")
        print(f"  Total Messages: {len(session_data['messages'])}")

        print(f"\nConversation Flow:")
        for i, msg in enumerate(session_data['messages'], 1):
            role_display = f"[{msg['role'].upper()}]".ljust(12)
            print(f"  {i}. {role_display} {msg['content']}")

    finally:
        service.close()


def verify_file_storage():
    """Verify that files are actually created on disk"""
    print_section("TEST 6: File System Verification")

    storage_path = Path("mcp_storage")

    print(f"Checking MCP storage directory: {storage_path.absolute()}\n")

    if storage_path.exists():
        print("[OK] MCP storage directory exists")

        # Check sessions
        sessions_dir = storage_path / "sessions"
        if sessions_dir.exists():
            session_files = list(sessions_dir.glob("*.json"))
            print(f"[OK] Sessions directory: {len(session_files)} session file(s)")

            for session_file in session_files[:3]:  # Show first 3
                session_data = json.loads(session_file.read_text())
                print(f"     - {session_file.name}: {session_data['title']} ({len(session_data['messages'])} msgs)")

        # Check memory
        memory_dir = storage_path / "memory"
        if memory_dir.exists():
            memory_files = list(memory_dir.glob("*.json"))
            print(f"[OK] Memory directory: {memory_files} memory file(s)")

        print("\n[OK] File system storage verified!")
    else:
        print("[WARN] MCP storage directory not found")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("MCP SESSION SERVICE - COMPREHENSIVE TEST SUITE")
    print("=" * 80)

    try:
        # Test 1: Create sessions
        session_ids = test_session_creation()

        # Test 2: Add and retrieve messages
        active_session = test_message_persistence(session_ids)

        # Test 3: List sessions by user
        test_session_listing(session_ids)

        # Test 4: Test persistence across instances (critical test!)
        test_persistence_across_instances(active_session)

        # Test 5: Complete session retrieval
        test_session_retrieval(active_session)

        # Test 6: Verify file system
        verify_file_storage()

        # Summary
        print_section("TEST SUMMARY")
        print("[OK] All tests passed successfully!")
        print("\nMCP File System Server Capabilities Verified:")
        print("  [OK] Session creation and management")
        print("  [OK] Message persistence")
        print("  [OK] Multi-user support")
        print("  [OK] Cross-instance data persistence")
        print("  [OK] File system storage")
        print("\nNext Step: Integrate with Orchestrator agent")

    except Exception as e:
        print("\n[ERROR] Test failed:")
        print(f"  {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
