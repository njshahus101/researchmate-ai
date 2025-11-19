"""
Quick test of the orchestrator agent
"""

import asyncio
from main import ResearchMateAI

async def test():
    print("\n" + "="*60)
    print("Testing Orchestrator")
    print("="*60)

    # Create app
    app = ResearchMateAI()

    # Test query
    query = "Best wireless headphones under $200"
    print(f"\nQuery: {query}\n")

    # Run pipeline
    result = await app.research(query, user_id="test_user")

    # Show results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Status: {result['status']}")

    if result['status'] == 'success':
        classification = result['stages']['classification']['output']
        print(f"\nClassification:")
        print(f"  Type: {classification.get('query_type')}")
        print(f"  Strategy: {classification.get('research_strategy')}")
        print(f"  Complexity: {classification.get('complexity_score')}/10")

        if 'information_gathering' in result['stages']:
            ig = result['stages']['information_gathering']
            print(f"\nInformation Gathering: {ig['status']}")

        print(f"\nTotal Duration: {result['total_duration_ms']:.2f}ms")
    else:
        print(f"Error: {result.get('error_message')}")

    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test())
