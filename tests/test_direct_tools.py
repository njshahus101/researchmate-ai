"""
Direct test of the orchestrator's gather_information function
This bypasses the LLM decision-making to test if direct tool calling works
"""

import asyncio
from adk_agents.orchestrator.agent import gather_information

async def test():
    print("Testing direct tool calling...")
    print("=" * 70)

    # Simulate classification result
    classification = {
        "query_type": "comparative",
        "research_strategy": "multi-source",
        "complexity_score": 5
    }

    # Call gather_information directly
    result = await gather_information(
        query="Fetch current price and details of Sony WH-1000XM5",
        classification=classification
    )

    print("\n" + "=" * 70)
    print("RESULT:")
    print("=" * 70)
    print(f"Status: {result.get('status')}")
    print(f"Sources fetched: {result.get('sources_fetched')}")
    print(f"\nContent:\n{result.get('content')[:500]}...")

if __name__ == "__main__":
    asyncio.run(test())
