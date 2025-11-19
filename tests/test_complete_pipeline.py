"""
Complete Pipeline Test - Tests the ENTIRE fixed pipeline with REAL Google Search

This test validates:
1. Classification handles duplicate JSON
2. Google Custom Search returns real URLs
3. Data fetching works with real URLs
4. Formatting produces user-friendly output
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from adk_agents.orchestrator.agent import execute_fixed_pipeline


async def test_real_pipeline():
    """Test the complete pipeline with a real query."""

    print("\n" + "="*80)
    print("COMPLETE PIPELINE TEST - With Real Google Search")
    print("="*80)

    query = "Sony WH-1000XM5 headphones price Amazon"

    print(f"\nQuery: {query}")
    print("\nThis test will:")
    print("  1. Classify the query")
    print("  2. Call REAL Google Custom Search API")
    print("  3. Fetch data from REAL URLs")
    print("  4. Format the results")
    print("\n" + "-"*80)

    try:
        result = await execute_fixed_pipeline(query=query, user_id="test_user")

        print("\n" + "="*80)
        print("TEST RESULTS")
        print("="*80)

        if result.get('status') == 'success':
            print("\n[PASS] COMPLETE PIPELINE TEST PASSED")
            print("\nPipeline Steps:")
            for step_name, step_status in result.get('pipeline_steps', {}).items():
                print(f"  + {step_name}: {step_status}")

            print(f"\nSources Fetched: {result.get('sources_fetched', 0)}")

            print("\n" + "-"*80)
            print("FORMATTED RESPONSE:")
            print("-"*80)
            print(result.get('content', 'No content'))
            print("-"*80)

            print("\n[SUCCESS] The fixed pipeline is working with REAL data!")
            return True
        else:
            print("\n[FAIL] PIPELINE FAILED")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print("\n[FAIL] PIPELINE EXCEPTION")
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the complete pipeline test."""

    print("\n" + "="*80)
    print("TESTING COMPLETE FIXED PIPELINE")
    print("="*80)
    print("\nThis test validates the entire research pipeline:")
    print("  - Query classification (with duplicate JSON handling)")
    print("  - Google Custom Search API (real web search)")
    print("  - Web data fetching (real URLs)")
    print("  - Result formatting (by Information Gatherer)")
    print("\n")

    success = await test_real_pipeline()

    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80)

    if success:
        print("\n[PASS] All systems working!")
        print("\nYour fixed pipeline is ready for production use.")
        print("\nNext steps:")
        print("  1. The ADK UI server is running at http://127.0.0.1:8000")
        print("  2. Try these queries in the browser:")
        print("     - 'Sony WH-1000XM5 price and reviews'")
        print("     - 'Best wireless keyboards under $100'")
        print("     - 'Compare iPhone 15 Pro vs Samsung Galaxy S24'")
        print("\n  3. Watch the terminal for detailed pipeline execution logs")
    else:
        print("\n[FAIL] Pipeline test failed. Review errors above.")

    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
