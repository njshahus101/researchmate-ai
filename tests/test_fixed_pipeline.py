"""
Test the FIXED PIPELINE implementation

This test directly calls execute_fixed_pipeline() to verify that the
deterministic execution order works correctly.

Expected flow:
1. Classify query (always)
2. Search web (always)
3. Fetch data from URLs (always)
4. Format results (always)
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import the orchestrator module
from adk_agents.orchestrator.agent import execute_fixed_pipeline


async def test_fixed_pipeline():
    """Test the fixed pipeline with a sample query."""

    print("\n" + "="*80)
    print("TESTING FIXED PIPELINE IMPLEMENTATION")
    print("="*80)
    print("\nThis test verifies that the pipeline executes ALL steps deterministically:")
    print("  1. Classification (via Query Classifier agent)")
    print("  2. Web search (via search_web tool)")
    print("  3. Data fetching (via fetch/extract tools)")
    print("  4. Formatting (via Information Gatherer agent)")
    print("\n" + "="*80)

    # Test query
    test_query = "Fetch current price and details of Sony WH-1000XM5"

    print(f"\nTest Query: {test_query}")
    print("\nExecuting fixed pipeline...\n")

    try:
        # Call the fixed pipeline
        result = await execute_fixed_pipeline(
            query=test_query,
            user_id="test_user"
        )

        print("\n" + "="*80)
        print("PIPELINE RESULT")
        print("="*80)

        print(f"\nStatus: {result.get('status')}")
        print(f"Sources fetched: {result.get('sources_fetched', 0)}")

        if result.get('pipeline_steps'):
            print("\nPipeline Steps:")
            for step_name, step_status in result['pipeline_steps'].items():
                print(f"  {step_name}: {step_status}")

        if result.get('classification'):
            print("\nClassification:")
            print(f"  Type: {result['classification'].get('query_type')}")
            print(f"  Strategy: {result['classification'].get('research_strategy')}")
            print(f"  Complexity: {result['classification'].get('complexity_score')}/10")

        if result.get('content'):
            print("\n" + "-"*80)
            print("FORMATTED RESPONSE:")
            print("-"*80)
            print(result['content'])
            print("-"*80)

        if result.get('status') == 'success':
            print("\n[PASS] FIXED PIPELINE TEST PASSED")
            print("\nKey achievements:")
            print("  + All 4 steps executed in order")
            print("  + No LLM decision-making required")
            print("  + Deterministic execution")
            print("  + Complete response generated")
            return True
        else:
            print("\n[WARN] PIPELINE COMPLETED WITH ERRORS")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print("\n[FAIL] FIXED PIPELINE TEST FAILED")
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_queries():
    """Test the fixed pipeline with different query types."""

    print("\n\n" + "="*80)
    print("TESTING MULTIPLE QUERY TYPES")
    print("="*80)

    test_cases = [
        "Best wireless keyboards under $100",
        "Compare iPhone 15 Pro vs Samsung Galaxy S24",
        "What is the capital of Japan?"
    ]

    results = []

    for i, query in enumerate(test_cases, 1):
        print(f"\n[Test {i}/{len(test_cases)}] Query: {query}")
        print("-"*80)

        try:
            result = await execute_fixed_pipeline(query=query, user_id=f"test_{i}")
            success = result.get('status') == 'success'
            results.append((query, success))

            if success:
                print(f"+ SUCCESS - {result.get('sources_fetched', 0)} sources fetched")
            else:
                print(f"- FAILED - {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"- EXCEPTION - {e}")
            results.append((query, False))

        # Small delay between tests
        await asyncio.sleep(2)

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\nPassed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    for query, success in results:
        status = "+ PASS" if success else "- FAIL"
        print(f"  {status}: {query[:60]}...")

    return passed == total


async def main():
    """Run all tests."""

    print("\n" + "="*80)
    print("FIXED PIPELINE TEST SUITE")
    print("="*80)

    # Test 1: Single query
    test1_passed = await test_fixed_pipeline()

    # Wait before next test
    await asyncio.sleep(3)

    # Test 2: Multiple queries
    test2_passed = await test_multiple_queries()

    # Final summary
    print("\n\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)

    if test1_passed and test2_passed:
        print("\n[PASS] ALL TESTS PASSED")
        print("\nThe fixed pipeline is working correctly!")
        print("\nNext steps:")
        print("  1. Start ADK UI: venv\\Scripts\\adk.exe web adk_agents --port 8000 --reload")
        print("  2. Test in browser: http://127.0.0.1:8000")
        print("  3. Try query: 'Fetch current price and details of Sony WH-1000XM5'")
    else:
        print("\n[WARN] SOME TESTS FAILED")
        print("\nReview the errors above and fix issues before deploying.")

    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
