"""
Quick test script for Information Gatherer MVP

Modify the query and run it!

Usage:
    python test_info_gatherer.py
"""

import asyncio
from agents.information_gatherer_mvp import gather_information


async def main():
    """Test Information Gatherer with your own query."""

    # CHANGE THIS TO YOUR QUERY
    # For MVP, we can ask about a topic and provide a URL to fetch
    my_query = """Please fetch information about Python programming from this URL:
https://en.wikipedia.org/wiki/Python_(programming_language)

Summarize the key points about Python."""

    # Optional: Add classification from Query Classifier
    # This helps the Information Gatherer use the right strategy
    classification = {
        "query_type": "factual",
        "research_strategy": "quick-answer",
        "complexity_score": 3
    }

    print(f"\n{'='*60}")
    print(f"Testing Information Gatherer")
    print(f"Query: {my_query}")
    print(f"{'='*60}\n")

    # Gather information
    result = await gather_information(my_query, classification)

    # Print results
    if "error" not in result:
        print("\n[SUCCESS] Information Gathering Successful!")
        print(f"\nTotal Sources: {result.get('total_sources', 'N/A')}")

        print(f"\nKey Findings:")
        for i, finding in enumerate(result.get('key_findings', []), 1):
            print(f"  {i}. {finding}")

        print(f"\nSources Used:")
        for source in result.get('sources', []):
            print(f"  - {source.get('title', 'N/A')}")
            print(f"    URL: {source.get('url', 'N/A')}")
            print(f"    Relevance: {source.get('relevance', 'N/A')}")

        print(f"\nSynthesized Information:")
        print(f"{result.get('synthesized_info', 'N/A')[:500]}...")

    else:
        print(f"\n[ERROR] Error: {result.get('error', 'Unknown error')}")
        print(f"Message: {result.get('message', '')}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
