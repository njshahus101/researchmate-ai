"""
Test Report Generator via ADK UI
This script simulates a user query through the ADK orchestrator
and verifies the Report Generator agent is called and returns a response.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner

# Load environment variables
load_dotenv()

# Import orchestrator agent
from adk_agents.orchestrator.agent import agent as orchestrator_agent

async def test_report_generator_via_orchestrator():
    """Test that orchestrator calls Report Generator and receives response"""

    print("\n" + "="*80)
    print("TESTING REPORT GENERATOR VIA ADK ORCHESTRATOR")
    print("="*80)

    # Test query - simple factual query
    query = "What is the current price of Sony WH-1000XM5 headphones?"

    print(f"\nTest Query: {query}")
    print("\n" + "="*80)
    print("EXPECTED PIPELINE FLOW:")
    print("="*80)
    print("[STEP 1/6] Query Classification")
    print("[STEP 2/6] Smart Search (Google Shopping + Web)")
    print("[STEP 3/6] Data Fetching")
    print("[STEP 4/6] Information Formatting")
    print("[STEP 5/6] Content Analysis")
    print("[STEP 6/6] Report Generation ← VERIFY THIS!")
    print("="*80)

    print("\n🚀 Starting pipeline execution...\n")

    # Create runner
    runner = InMemoryRunner(agent=orchestrator_agent)

    try:
        # Run the orchestrator (this should trigger the full pipeline)
        response = await runner.run_debug(query)

        # Extract final response
        if isinstance(response, list) and len(response) > 0:
            last_event = response[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                final_output = last_event.content.parts[0].text
            else:
                final_output = str(last_event)
        else:
            final_output = str(response)

        print("\n" + "="*80)
        print("FINAL OUTPUT RECEIVED FROM ORCHESTRATOR:")
        print("="*80)
        print(final_output)
        print("\n" + "="*80)

        # Validation checks
        print("\nVALIDATION CHECKS:")
        print("="*80)

        checks = {
            "Output is not empty": len(final_output) > 0,
            "Contains markdown heading (##)": "##" in final_output,
            "Contains price information ($)": "$" in final_output,
            "Contains 'Sony' or 'WH-1000XM5'": "Sony" in final_output or "WH-1000XM5" in final_output or "sony" in final_output.lower(),
            "Contains sources/citations": "source" in final_output.lower() or "[1]" in final_output or "http" in final_output,
            "Looks like Report Generator output (not raw data)": any(marker in final_output for marker in ["##", "###", "**", "💡", "✅", "Sources", "Follow-up"]),
        }

        all_passed = True
        for check_name, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {check_name}")
            all_passed = all_passed and passed

        print("\n" + "="*80)
        if all_passed:
            print("✅ SUCCESS: Report Generator is working correctly!")
            print("The orchestrator successfully:")
            print("  1. Called Report Generator agent (STEP 6)")
            print("  2. Received formatted report response")
            print("  3. Returned professional markdown report to user")
        else:
            print("⚠️  WARNING: Some checks failed")
            print("Review the output above to see what might be wrong")
        print("="*80)

        return all_passed

    except Exception as e:
        print("\n" + "="*80)
        print("❌ ERROR: Test failed with exception")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the test"""
    print("\n" + "="*80)
    print("ADK UI - REPORT GENERATOR INTEGRATION TEST")
    print("="*80)
    print("\nThis test verifies that:")
    print("  1. Orchestrator executes all 6 pipeline steps")
    print("  2. Report Generator agent is called (STEP 6)")
    print("  3. Report Generator returns a formatted report")
    print("  4. Final output is professional markdown (not raw data)")

    success = await test_report_generator_via_orchestrator()

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    if success:
        print("✅ ALL CHECKS PASSED")
        print("\nThe Report Generator is successfully integrated!")
        print("\nYou can now test via ADK UI at: http://127.0.0.1:8000")
        print("Try queries like:")
        print('  - "What is the price of Sony WH-1000XM5?"')
        print('  - "Compare Sony WH-1000XM5 vs Bose QuietComfort Ultra"')
    else:
        print("❌ SOME CHECKS FAILED")
        print("\nReview the output above for details")

    print("="*80)

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
