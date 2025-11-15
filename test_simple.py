"""
Simple Test - Query Classifier MVP

Tests the Query Classifier Agent with a single query.
"""

import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types


async def main():
    """Simple test of Query Classifier."""
    # Load environment
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not found in .env file")
        return

    print("\n" + "="*60)
    print("ResearchMate AI - Query Classifier Test")
    print("="*60 + "\n")

    # Create retry config
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )

    # Create agent
    agent = LlmAgent(
        name="query_classifier",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        description="Query analyzer",
        instruction="""Analyze this query and classify it.

Respond with JSON:
{
    "query_type": "factual|comparative|exploratory|monitoring",
    "complexity_score": 1-10,
    "research_strategy": "quick-answer|multi-source|deep-dive",
    "key_topics": ["topic1", "topic2"],
    "reasoning": "brief explanation"
}
""",
        tools=[],
    )

    # Create runner
    runner = InMemoryRunner(agent=agent)

    # Test queries
    queries = [
        "What is the capital of Japan?",
        "Best wireless headphones under $200",
        "Explain quantum computing for beginners",
    ]

    for query in queries:
        print(f"Query: {query}")
        print("-" * 60)

        try:
            response = await runner.run_debug(query)
            print(f"Classification successful!")
            print(f"-" * 60 + "\n")

            # Small delay
            await asyncio.sleep(1)

        except Exception as e:
            print(f"Error: {e}\n")

    print("="*60)
    print("SUCCESS! Query Classifier is working!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
