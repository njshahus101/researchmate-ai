"""
Session Service

Factory functions for creating session services with different storage backends.
"""

from google.adk.sessions import InMemorySessionService, DatabaseSessionService
import os


def create_session_service(use_database: bool = False, db_url: str = None):
    """
    Create a session service based on configuration.

    Args:
        use_database: If True, use DatabaseSessionService (persistent)
                     If False, use InMemorySessionService (temporary)
        db_url: Database URL (only used if use_database=True)
                Default: sqlite:///researchmate_sessions.db

    Returns:
        Session service instance
    """

    if use_database:
        # Use persistent database storage
        if db_url is None:
            db_url = os.getenv("DATABASE_URL", "sqlite:///researchmate_sessions.db")

        print(f"📦 Creating DatabaseSessionService...")
        print(f"   Database: {db_url}")

        return DatabaseSessionService(db_url=db_url)

    else:
        # Use in-memory storage (data lost on restart)
        print(f"📦 Creating InMemorySessionService...")
        print(f"   ⚠️  Sessions will not persist across restarts")

        return InMemorySessionService()


if __name__ == "__main__":
    # Test session service creation
    print("Testing session service creation...\n")

    # Test in-memory
    print("1. In-Memory Session Service:")
    session_service_mem = create_session_service(use_database=False)
    print(f"   Type: {type(session_service_mem).__name__}\n")

    # Test database
    print("2. Database Session Service:")
    session_service_db = create_session_service(
        use_database=True,
        db_url="sqlite:///test_sessions.db"
    )
    print(f"   Type: {type(session_service_db).__name__}\n")

    print("✅ Session services created successfully!")

    # Clean up test database
    if os.path.exists("test_sessions.db"):
        os.remove("test_sessions.db")
