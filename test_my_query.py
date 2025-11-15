"""
Quick test script - modify the query and run it!

Usage:
    python test_my_query.py
"""

import asyncio
from agents.query_classifier_mvp import classify_query


async def main():
    """Test with your own query."""

    # CHANGE THIS TO YOUR QUERY
    my_query = "What are the best programming languages to learn in 2025?"

    print(f"\n{'='*60}")
    print(f"Testing Query: {my_query}")
    print(f"{'='*60}\n")

    # Classify the query
    result = await classify_query(my_query)

    # Print results
    if "error" not in result:
        print("\n[SUCCESS] Classification Successful!")
        print(f"\nQuery Type: {result.get('query_type', 'N/A')}")
        print(f"Complexity: {result.get('complexity_score', 'N/A')}/10")
        print(f"Strategy: {result.get('research_strategy', 'N/A')}")
        print(f"Key Topics: {', '.join(result.get('key_topics', []))}")
        print(f"\nReasoning: {result.get('reasoning', 'N/A')}")
    else:
        print(f"\n[ERROR] Error: {result.get('error', 'Unknown error')}")
        print(f"Message: {result.get('message', '')}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
