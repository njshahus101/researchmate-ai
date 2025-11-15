"""
Memory Service

Implements the Memory Bank for long-term storage of user preferences,
research history, and domain knowledge.
"""

from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime


class MemoryService:
    """
    Memory Bank implementation for ResearchMate AI.

    Stores and retrieves:
    - User preferences (priorities, communication style)
    - Research history (past topics, queries)
    - Domain knowledge (expertise levels, interests)
    - Contextual relationships (topic connections)
    """

    def __init__(self, storage_path: str = "memory_bank.json"):
        """
        Initialize the Memory Service.

        Args:
            storage_path: Path to JSON file for persistent storage
        """
        self.storage_path = storage_path
        self.memory = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from persistent storage."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load memory: {e}")
                return self._create_empty_memory()
        return self._create_empty_memory()

    def _create_empty_memory(self) -> Dict[str, Any]:
        """Create empty memory structure."""
        return {
            "users": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }

    def _save_memory(self):
        """Save memory to persistent storage."""
        try:
            self.memory["metadata"]["last_updated"] = datetime.now().isoformat()
            with open(self.storage_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save memory: {e}")

    def get_user_memory(self, user_id: str) -> Dict[str, Any]:
        """
        Get all memory for a specific user.

        Args:
            user_id: User identifier

        Returns:
            User's memory dictionary
        """
        if user_id not in self.memory["users"]:
            self.memory["users"][user_id] = {
                "preferences": {},
                "research_history": [],
                "domain_knowledge": {},
                "topic_connections": [],
                "created_at": datetime.now().isoformat()
            }
            self._save_memory()

        return self.memory["users"][user_id]

    def store_preference(self, user_id: str, key: str, value: Any):
        """
        Store a user preference.

        Args:
            user_id: User identifier
            key: Preference key (e.g., "priority_battery_life")
            value: Preference value
        """
        user_memory = self.get_user_memory(user_id)
        user_memory["preferences"][key] = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }
        self._save_memory()

    def get_preference(self, user_id: str, key: str) -> Optional[Any]:
        """
        Get a user preference.

        Args:
            user_id: User identifier
            key: Preference key

        Returns:
            Preference value or None
        """
        user_memory = self.get_user_memory(user_id)
        pref = user_memory["preferences"].get(key)
        return pref["value"] if pref else None

    def add_research_entry(self, user_id: str, query: str, query_type: str, topics: List[str]):
        """
        Add an entry to research history.

        Args:
            user_id: User identifier
            query: The research query
            query_type: Type of query (factual, comparative, etc.)
            topics: List of topics researched
        """
        user_memory = self.get_user_memory(user_id)

        entry = {
            "query": query,
            "query_type": query_type,
            "topics": topics,
            "timestamp": datetime.now().isoformat()
        }

        user_memory["research_history"].append(entry)

        # Update topic connections
        self._update_topic_connections(user_id, topics)

        self._save_memory()

    def _update_topic_connections(self, user_id: str, topics: List[str]):
        """
        Update topic connection graph.

        Args:
            user_id: User identifier
            topics: List of related topics
        """
        user_memory = self.get_user_memory(user_id)

        # Create connections between topics researched together
        for i, topic1 in enumerate(topics):
            for topic2 in topics[i+1:]:
                connection = {
                    "topic1": topic1,
                    "topic2": topic2,
                    "last_seen_together": datetime.now().isoformat()
                }

                # Check if connection exists
                existing = next(
                    (c for c in user_memory["topic_connections"]
                     if (c["topic1"] == topic1 and c["topic2"] == topic2) or
                        (c["topic1"] == topic2 and c["topic2"] == topic1)),
                    None
                )

                if existing:
                    existing["last_seen_together"] = datetime.now().isoformat()
                else:
                    user_memory["topic_connections"].append(connection)

    def get_related_topics(self, user_id: str, topic: str) -> List[str]:
        """
        Get topics related to a given topic.

        Args:
            user_id: User identifier
            topic: Topic to find connections for

        Returns:
            List of related topics
        """
        user_memory = self.get_user_memory(user_id)
        related = []

        for connection in user_memory["topic_connections"]:
            if connection["topic1"].lower() == topic.lower():
                related.append(connection["topic2"])
            elif connection["topic2"].lower() == topic.lower():
                related.append(connection["topic1"])

        return list(set(related))  # Remove duplicates

    def get_recent_research(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent research history.

        Args:
            user_id: User identifier
            limit: Maximum number of entries to return

        Returns:
            List of recent research entries
        """
        user_memory = self.get_user_memory(user_id)
        history = user_memory["research_history"]

        # Return most recent entries
        return history[-limit:] if len(history) > limit else history

    def update_domain_knowledge(self, user_id: str, domain: str, expertise_level: str):
        """
        Update user's domain expertise.

        Args:
            user_id: User identifier
            domain: Domain name (e.g., "machine_learning")
            expertise_level: Level (beginner, intermediate, expert)
        """
        user_memory = self.get_user_memory(user_id)
        user_memory["domain_knowledge"][domain] = {
            "expertise_level": expertise_level,
            "updated_at": datetime.now().isoformat()
        }
        self._save_memory()

    def get_domain_expertise(self, user_id: str, domain: str) -> Optional[str]:
        """
        Get user's expertise level in a domain.

        Args:
            user_id: User identifier
            domain: Domain name

        Returns:
            Expertise level or None
        """
        user_memory = self.get_user_memory(user_id)
        knowledge = user_memory["domain_knowledge"].get(domain)
        return knowledge["expertise_level"] if knowledge else None


if __name__ == "__main__":
    # Test the Memory Service
    memory = MemoryService(storage_path="test_memory.json")

    user_id = "test_user_123"

    # Store preferences
    memory.store_preference(user_id, "priority_battery_life", True)
    memory.store_preference(user_id, "preferred_brands", ["Sony", "Apple"])

    # Add research history
    memory.add_research_entry(
        user_id,
        "Best wireless headphones under $200",
        "comparative",
        ["headphones", "audio", "wireless"]
    )

    memory.add_research_entry(
        user_id,
        "Sony WH-1000XM5 battery life",
        "factual",
        ["headphones", "Sony", "battery"]
    )

    # Get related topics
    related = memory.get_related_topics(user_id, "headphones")
    print(f"✅ Topics related to 'headphones': {related}")

    # Get preferences
    pref = memory.get_preference(user_id, "priority_battery_life")
    print(f"✅ Battery life priority: {pref}")

    # Clean up test file
    if os.path.exists("test_memory.json"):
        os.remove("test_memory.json")
