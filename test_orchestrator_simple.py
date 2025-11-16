"""
Simple test script for Orchestrator Agent via main.py

Tests the orchestrator integration by running a simple query through the pipeline.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import the ResearchMateAI class from main
from main import ResearchMateAI


async def test_orchestrator():
    """Test the orchestrator with a simple query."""

    print("\n" + "="*70)
    print("TESTING ORCHESTRATOR AGENT - SIMPLE TEST")
    print("="*70 + "\n")

    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("[ERROR] GOOGLE_API_KEY not found!")
        print("Please set it in your .env file")
        return

    print("[OK] API Key found")
    print("\n" + "-"*70)
    print("INITIALIZING RESEARCHMATE AI")
    print("-"*70 + "\n")

    # Create the ResearchMate AI instance
    try:
        app = ResearchMateAI()
        print("\n[OK] ResearchMate AI initialized successfully!")
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test queries
    test_queries = [
        "What is the capital of Japan?",  # Should be quick-answer
        # "Best wireless headphones under $200",  # Multi-source (we can test this later)
    ]

    for i, query in enumerate(test_queries, 1):
        print("\n" + "="*70)
        print(f"TEST {i}/{len(test_queries)}: {query}")
        print("="*70 + "\n")

        try:
            result = await app.research(query, user_id="test_user")

            print("\n" + "-"*70)
            print("RESULTS")
            print("-"*70)
            print(f"Status: {result['status']}")

            if result['status'] == 'success':
                # Show classification
                if 'classification' in result['stages']:
                    classification = result['stages']['classification']['output']
                    print(f"\nQuery Classification:")
                    print(f"  Type: {classification.get('query_type', 'N/A')}")
                    print(f"  Complexity: {classification.get('complexity_score', 'N/A')}/10")
                    print(f"  Strategy: {classification.get('research_strategy', 'N/A')}")
                    print(f"  Topics: {', '.join(classification.get('key_topics', []))}")

                # Show information gathering
                if 'information_gathering' in result['stages']:
                    ig_stage = result['stages']['information_gathering']
                    print(f"\nInformation Gathering:")
                    print(f"  Status: {ig_stage['status']}")
                    if ig_stage['status'] == 'success':
                        print(f"  Duration: {ig_stage['duration_ms']:.2f}ms")
                        print(f"\n  Response Preview:")
                        content = ig_stage['output']
                        preview = content[:200] + "..." if len(content) > 200 else content
                        print(f"  {preview}")
                    elif ig_stage['status'] == 'skipped':
                        print(f"  Reason: {ig_stage['reason']}")

                print(f"\n[OK] Total Duration: {result['total_duration_ms']:.2f}ms")
            else:
                print(f"\n[ERROR] Error: {result.get('error_message', 'Unknown error')}")

        except Exception as e:
            print(f"\n[ERROR] Test failed with error: {e}")
            import traceback
            traceback.print_exc()

    # Show metrics
    print("\n" + "="*70)
    print("PIPELINE METRICS")
    print("="*70)
    app._show_metrics()

    print("\n" + "="*70)
    print("[OK] TESTING COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_orchestrator())
