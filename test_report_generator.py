"""
Test Report Generator Agent Integration

This script tests the complete pipeline with the Report Generator agent.
It verifies that:
1. Report Generator is loaded correctly
2. Final reports are tailored to query type
3. Citations are properly formatted
4. Follow-up questions are generated
5. Markdown formatting is correct
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

async def test_factual_query():
    """Test Report Generator with a factual query"""
    print("\n" + "="*80)
    print("TEST 1: FACTUAL QUERY - Sony WH-1000XM5 price")
    print("="*80)

    query = "What is the current price of Sony WH-1000XM5 headphones on Amazon?"

    runner = InMemoryRunner(agent=orchestrator_agent)
    try:
        response = await runner.run_debug(query)

        # Extract final response
        if isinstance(response, list) and len(response) > 0:
            last_event = response[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                report = last_event.content.parts[0].text
            else:
                report = str(last_event)
        else:
            report = str(response)

        print("\n" + "="*80)
        print("FINAL REPORT:")
        print("="*80)
        print(report)
        print("\n" + "="*80)

        # Validate report structure for factual queries
        print("\nVALIDATION CHECKS:")
        checks = {
            "Contains heading (##)": "##" in report,
            "Contains sources section": "Sources" in report or "source" in report.lower(),
            "Contains follow-up questions": "💡" in report or "Follow-up" in report,
            "Contains pricing information": "$" in report or "price" in report.lower(),
            "Contains credibility indicator": "Credibility" in report or "High" in report or "Medium" in report,
        }

        for check, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {check}")

        return all(checks.values())

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_comparative_query():
    """Test Report Generator with a comparative query"""
    print("\n" + "="*80)
    print("TEST 2: COMPARATIVE QUERY - Headphones comparison")
    print("="*80)

    query = "Compare Sony WH-1000XM5 vs Bose QuietComfort Ultra headphones"

    runner = InMemoryRunner(agent=orchestrator_agent)
    try:
        response = await runner.run_debug(query)

        # Extract final response
        if isinstance(response, list) and len(response) > 0:
            last_event = response[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                report = last_event.content.parts[0].text
            else:
                report = str(last_event)
        else:
            report = str(response)

        print("\n" + "="*80)
        print("FINAL REPORT:")
        print("="*80)
        print(report)
        print("\n" + "="*80)

        # Validate report structure for comparative queries
        print("\nVALIDATION CHECKS:")
        checks = {
            "Contains comparison table (|)": "|" in report,
            "Contains executive summary": "Summary" in report or "Recommendation" in report,
            "Contains sources section": "Sources" in report or "source" in report.lower(),
            "Contains follow-up questions": "💡" in report or "Follow-up" in report,
            "Contains pros/cons or analysis": "Pros" in report or "Cons" in report or "Analysis" in report,
            "Contains ratings or scores": "rating" in report.lower() or "score" in report.lower() or "/5" in report or "/10" in report,
        }

        for check, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {check}")

        return all(checks.values())

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_exploratory_query():
    """Test Report Generator with an exploratory query"""
    print("\n" + "="*80)
    print("TEST 3: EXPLORATORY QUERY - Understanding a topic")
    print("="*80)

    query = "Explain how noise cancellation technology works in headphones"

    runner = InMemoryRunner(agent=orchestrator_agent)
    try:
        response = await runner.run_debug(query)

        # Extract final response
        if isinstance(response, list) and len(response) > 0:
            last_event = response[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                report = last_event.content.parts[0].text
            else:
                report = str(last_event)
        else:
            report = str(response)

        print("\n" + "="*80)
        print("FINAL REPORT:")
        print("="*80)
        print(report)
        print("\n" + "="*80)

        # Validate report structure for exploratory queries
        print("\nVALIDATION CHECKS:")
        checks = {
            "Contains multiple sections (###)": report.count("###") >= 3,
            "Contains overview/introduction": "Overview" in report or "Introduction" in report or "What" in report,
            "Contains sources section": "Sources" in report or "source" in report.lower(),
            "Contains follow-up questions": "💡" in report or "Follow-up" in report,
            "Contains detailed explanation": len(report) > 500,  # Exploratory should be comprehensive
        }

        for check, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {check}")

        return all(checks.values())

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("REPORT GENERATOR AGENT - INTEGRATION TESTS")
    print("="*80)
    print("\nThese tests verify the complete pipeline with Report Generator:")
    print("  1. Query Classifier → classifies query type")
    print("  2. Search → finds relevant URLs")
    print("  3. Data Fetching → extracts content")
    print("  4. Information Gatherer → formats data")
    print("  5. Content Analyzer → assesses credibility")
    print("  6. Report Generator → creates tailored report")
    print("\n" + "="*80)

    # Run tests
    results = []

    # Test 1: Factual query
    result1 = await test_factual_query()
    results.append(("Factual Query Test", result1))

    # Test 2: Comparative query
    result2 = await test_comparative_query()
    results.append(("Comparative Query Test", result2))

    # Test 3: Exploratory query
    result3 = await test_exploratory_query()
    results.append(("Exploratory Query Test", result3))

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    print("="*80)

    return all(passed for _, passed in results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
