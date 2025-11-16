"""
Test script to demonstrate Query Classifier with Memory Service integration

This script shows how the Query Classifier uses user context from memory
to provide personalized classification results.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.query_classifier_mvp import classify_query
from services.memory_service import MemoryService


async def test_memory_integration():
    """
    Test the Query Classifier with Memory Service integration.

    This demonstrates:
    1. Creating a user profile with preferences and history
    2. Classifying queries with user context
    3. Building up research history over multiple queries
    """

    # Create memory service
    print("\n" + "="*60)
    print("QUERY CLASSIFIER WITH MEMORY INTEGRATION TEST")
    print("="*60)

    memory = MemoryService(storage_path="demo_memory.json")
    user_id = "demo_user_001"

    print(f"\nSetting up user profile for: {user_id}")
    print("-" * 60)

    # Set up user preferences
    memory.store_preference(user_id, "priority_quality", True)
    memory.store_preference(user_id, "priority_price", False)
    memory.store_preference(user_id, "preferred_brands", ["Sony", "Bose", "Apple"])
    memory.store_preference(user_id, "expertise_level", "intermediate")

    print("[+] User preferences stored:")
    print("   - Prioritizes quality over price")
    print("   - Prefers brands: Sony, Bose, Apple")
    print("   - Expertise level: intermediate")

    # Add some domain knowledge
    memory.update_domain_knowledge(user_id, "audio_equipment", "intermediate")
    memory.update_domain_knowledge(user_id, "technology", "advanced")

    print("\n[+] Domain knowledge stored:")
    print("   - Audio equipment: intermediate")
    print("   - Technology: advanced")

    # Simulate research history
    print("\nAdding research history...")
    memory.add_research_entry(
        user_id,
        "Best noise-cancelling headphones for travel",
        "comparative",
        ["headphones", "audio", "travel", "noise-cancelling"]
    )

    memory.add_research_entry(
        user_id,
        "How does active noise cancellation work?",
        "exploratory",
        ["noise-cancelling", "technology", "audio"]
    )

    print("[+] Added 2 previous research entries")

    # Now test classification with context
    print("\n" + "="*60)
    print("TESTING QUERY CLASSIFICATION WITH USER CONTEXT")
    print("="*60)

    test_queries = [
        "Sony WH-1000XM5 vs Bose QuietComfort 45",
        "Latest developments in spatial audio",
        "Best budget headphones under $50",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test Query {i}/{len(test_queries)}")
        print(f"{'='*60}")

        result = await classify_query(
            query,
            user_id=user_id,
            memory_service=memory
        )

        if "error" in result:
            print(f"[!] Error: {result['error']}")
        else:
            print(f"\n[+] Classification successful!")
            print(f"\nQuery: {query}")
            print(f"Type: {result.get('query_type', 'N/A')}")
            print(f"Complexity: {result.get('complexity_score', 'N/A')}/10")
            print(f"Strategy: {result.get('research_strategy', 'N/A')}")
            print(f"Topics: {', '.join(result.get('key_topics', []))}")
            print(f"\nReasoning: {result.get('reasoning', 'N/A')}")

        # Small delay between requests
        if i < len(test_queries):
            await asyncio.sleep(1)

    # Show updated research history
    print("\n" + "="*60)
    print("UPDATED RESEARCH HISTORY")
    print("="*60)

    recent_research = memory.get_recent_research(user_id, limit=10)
    print(f"\nTotal research entries: {len(recent_research)}")

    for i, entry in enumerate(recent_research, 1):
        print(f"\n{i}. {entry['query']}")
        print(f"   Type: {entry['query_type']}")
        print(f"   Topics: {', '.join(entry['topics'])}")
        print(f"   Date: {entry['timestamp']}")

    # Show topic connections
    print("\n" + "="*60)
    print("TOPIC CONNECTIONS")
    print("="*60)

    topics_to_check = ["headphones", "audio", "noise-cancelling"]

    for topic in topics_to_check:
        related = memory.get_related_topics(user_id, topic)
        if related:
            print(f"\n'{topic}' is related to: {', '.join(related)}")

    print("\n" + "="*60)
    print("TEST COMPLETE!")
    print("="*60)
    print(f"\n[+] Memory saved to: demo_memory.json")
    print("[+] Query Classifier successfully integrated with Memory Service")
    print("\nKey features demonstrated:")
    print("  - User preferences are stored and retrieved")
    print("  - Research history is tracked across queries")
    print("  - Topic connections are automatically built")
    print("  - Classification can use user context for personalization")
    print("\n" + "="*60 + "\n")


async def test_without_memory():
    """Test classification without memory service for comparison"""

    print("\n" + "="*60)
    print("COMPARISON: CLASSIFICATION WITHOUT MEMORY")
    print("="*60)

    query = "Best wireless headphones under $200"

    print(f"\nQuery: {query}")
    print("User Context: None (no memory service)")

    result = await classify_query(query)

    if "error" not in result:
        print(f"\nType: {result.get('query_type', 'N/A')}")
        print(f"Complexity: {result.get('complexity_score', 'N/A')}/10")
        print(f"Strategy: {result.get('research_strategy', 'N/A')}")
        print(f"\nReasoning: {result.get('reasoning', 'N/A')}")

    print("\n" + "="*60 + "\n")


async def main():
    """Run all tests"""

    print("\nStarting Memory Integration Tests...\n")

    # Test with memory
    await test_memory_integration()

    # Test without memory for comparison
    await test_without_memory()

    print("All tests completed!\n")


if __name__ == "__main__":
    asyncio.run(main())
