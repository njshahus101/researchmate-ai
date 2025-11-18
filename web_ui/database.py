"""
Database module for ResearchMate AI Web UI
Handles conversation history storage using SQLite
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class Database:
    """SQLite database handler for conversation history"""

    def __init__(self, db_path: str = "conversations.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn

    def init_database(self):
        """Create tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                title TEXT,
                user_id TEXT DEFAULT 'default'
            )
        """)

        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)

        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session
            ON messages(session_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_user
            ON sessions(user_id)
        """)

        conn.commit()
        conn.close()

    def create_session(self, session_id: str, title: str = "New Conversation", user_id: str = "default") -> str:
        """Create a new conversation session"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sessions (id, title, user_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, title, user_id, datetime.now(), datetime.now()))

        conn.commit()
        conn.close()

        return session_id

    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to a session"""
        conn = self.get_connection()
        cursor = conn.cursor()

        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute("""
            INSERT INTO messages (session_id, role, content, metadata, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, role, content, metadata_json, datetime.now()))

        # Update session's updated_at timestamp
        cursor.execute("""
            UPDATE sessions SET updated_at = ? WHERE id = ?
        """, (datetime.now(), session_id))

        conn.commit()
        conn.close()

    def get_session_messages(self, session_id: str) -> List[Dict]:
        """Get all messages for a session"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, session_id, role, content, timestamp, metadata
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """, (session_id,))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                "id": row["id"],
                "session_id": row["session_id"],
                "role": row["role"],
                "content": row["content"],
                "timestamp": row["timestamp"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else None
            })

        conn.close()
        return messages

    def get_all_sessions(self, user_id: str = "default") -> List[Dict]:
        """Get all sessions for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, created_at, updated_at, title, user_id
            FROM sessions
            WHERE user_id = ?
            ORDER BY updated_at DESC
        """, (user_id,))

        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "id": row["id"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "title": row["title"],
                "user_id": row["user_id"]
            })

        conn.close()
        return sessions

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get a specific session"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, created_at, updated_at, title, user_id
            FROM sessions
            WHERE id = ?
        """, (session_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row["id"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "title": row["title"],
                "user_id": row["user_id"]
            }
        return None

    def update_session_title(self, session_id: str, title: str):
        """Update session title"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?
        """, (title, datetime.now(), session_id))

        conn.commit()
        conn.close()

    def delete_session(self, session_id: str):
        """Delete a session and all its messages"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Delete messages first
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))

        # Delete session
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

        conn.commit()
        conn.close()

    def clear_all_sessions(self, user_id: str = "default"):
        """Clear all sessions for a user (for testing/reset)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get all session IDs for user
        cursor.execute("SELECT id FROM sessions WHERE user_id = ?", (user_id,))
        session_ids = [row["id"] for row in cursor.fetchall()]

        # Delete all messages for these sessions
        for session_id in session_ids:
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))

        # Delete all sessions
        cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))

        conn.commit()
        conn.close()


# Singleton instance
db = Database()
