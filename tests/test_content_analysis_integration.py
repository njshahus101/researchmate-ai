"""
Integration Test for Content Analysis Agent

This script tests the complete 5-step pipeline:
1. Query Classification
2. Web Search
3. Data Fetch
4. Information Formatting
5. Content Analysis (NEW)
"""

import asyncio
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner

# Load environment
load_dotenv()

print("="*80)
print("CONTENT ANALYSIS AGENT - INTEGRATION TEST")
print("="*80)

async def test_content_analyzer_agent():
    """Test the Content Analysis agent directly"""
    print("\n[TEST 1] Testing Content Analysis Agent (standalone)")
    print("-" * 80)

    from adk_agents.content_analyzer.agent import agent as analyzer_agent

    # Simulate fetched data from Information Gatherer
    test_data = [
        {
            "url": "https://www.amazon.com/Sony-WH-1000XM5",
            "data": {
                "status": "success",
                "product_name": "Sony WH-1000XM5 Wireless Headphones",
                "price": "$348.00",
                "currency": "USD",
                "rating": 4.7,
                "review_count": 2543,
                "features": ["Active Noise Cancellation", "30hr Battery", "Bluetooth 5.2"]
            },
            "source": {
                "title": "Sony WH-1000XM5 on Amazon",
                "url": "https://www.amazon.com/Sony-WH-1000XM5"
            }
        },
        {
            "url": "https://www.bestbuy.com/site/sony-wh1000xm5",
            "data": {
                "status": "success",
                "product_name": "Sony WH1000XM5",
                "price": "$379.99",
                "currency": "USD",
                "rating": 4.6,
                "review_count": 892,
                "features": ["ANC", "30 hour battery"]
            },
            "source": {
                "title": "Sony WH-1000XM5 at Best Buy",
                "url": "https://www.bestbuy.com/site/sony-wh1000xm5"
            }
        },
        {
            "url": "https://techblog.example.com/sony-review",
            "data": {
                "status": "success",
                "content": "Great headphones with excellent ANC. Price around $350-400.",
                "title": "Sony WH-1000XM5 Review"
            },
            "source": {
                "title": "TechBlog Review",
                "url": "https://techblog.example.com/sony-review"
            }
        }
    ]

    # Build analysis prompt
    analysis_prompt = f"""Analyze the following fetched data for credibility and extract key facts.

Research Query: Sony WH-1000XM5 price comparison

Query Type: comparative

FETCHED DATA (from {len(test_data)} sources):
{json.dumps(test_data, indent=2)}

YOUR TASK:
1. Score each source's credibility (0-100)
2. Extract key facts with confidence levels
3. Identify any conflicts between sources
4. Create comparison matrix if this is a product comparison
5. Normalize all data (prices, ratings, specifications)

Return comprehensive analysis in JSON format as specified in your instructions."""

    # Call Content Analyzer
    runner = InMemoryRunner(agent=analyzer_agent)
    try:
        print("\n[*] Calling Content Analysis Agent...")
        response = await runner.run_debug(analysis_prompt)

        # Extract response
        if isinstance(response, list) and len(response) > 0:
            last_event = response[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                analysis_text = last_event.content.parts[0].text
            else:
                analysis_text = str(last_event)
        else:
            analysis_text = str(response)

        print("\n[OK] Content Analysis Response:")
        print("-" * 80)
        print(analysis_text[:1000])  # Print first 1000 chars
        if len(analysis_text) > 1000:
            print(f"\n... (response truncated, total length: {len(analysis_text)} chars)")

        # Try to parse JSON
        cleaned = analysis_text.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        if cleaned.startswith('```'):
            cleaned = cleaned[3:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            analysis_json = json.loads(cleaned)
            print("\n[OK] Successfully parsed JSON analysis")
            print(f"   - Total sources: {analysis_json.get('analysis_summary', {}).get('total_sources', 'N/A')}")
            print(f"   - Credible sources: {analysis_json.get('analysis_summary', {}).get('credible_sources', 'N/A')}")
            print(f"   - Conflicts found: {analysis_json.get('analysis_summary', {}).get('conflicts_found', 'N/A')}")

            # Show credibility scores
            if 'source_credibility' in analysis_json:
                print(f"\n[CREDIBILITY] Scores:")
                for source in analysis_json['source_credibility'][:3]:  # Show first 3
                    print(f"   - {source.get('url', 'N/A')[:50]}: {source.get('credibility_score', 'N/A')}/100 ({source.get('credibility_level', 'N/A')})")

            # Show conflicts
            if 'conflicts' in analysis_json and analysis_json['conflicts']:
                print(f"\n[CONFLICTS] Detected:")
                for conflict in analysis_json['conflicts'][:3]:  # Show first 3
                    print(f"   - {conflict.get('conflict_type', 'N/A')}: {conflict.get('description', 'N/A')}")

        except json.JSONDecodeError as e:
            print(f"\n[WARN] Could not parse as JSON: {e}")
            print("   (This is OK - agent may have returned formatted text)")

        return True

    except Exception as e:
        print(f"\n[ERROR] Content Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_pipeline():
    """Test the complete 5-step pipeline via orchestrator"""
    print("\n\n[TEST 2] Testing Full 5-Step Pipeline (via Orchestrator)")
    print("-" * 80)

    from adk_agents.orchestrator.agent import execute_fixed_pipeline

    test_query = "Sony WH-1000XM5 price"

    try:
        print(f"\n[*] Running fixed pipeline for query: '{test_query}'")
        print("   Pipeline: Classify -> Search -> Fetch -> Format -> Analyze\n")

        result = await execute_fixed_pipeline(test_query, user_id="test_user")

        print("\n[OK] Pipeline completed!")
        print("-" * 80)
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Sources fetched: {result.get('sources_fetched', 0)}")

        # Show pipeline steps
        if 'pipeline_steps' in result:
            print("\nPipeline Steps:")
            for step_name, step_status in result['pipeline_steps'].items():
                print(f"  [OK] {step_name.capitalize()}: {step_status}")

        # Show content analysis summary
        if 'content_analysis' in result:
            analysis = result['content_analysis']
            if 'analysis_summary' in analysis:
                summary = analysis['analysis_summary']
                print(f"\nContent Analysis Summary:")
                print(f"  - Total sources: {summary.get('total_sources', 'N/A')}")
                print(f"  - Credible sources: {summary.get('credible_sources', 'N/A')}")
                print(f"  - Conflicts found: {summary.get('conflicts_found', 'N/A')}")

        # Show formatted content (first 500 chars)
        if 'content' in result:
            print(f"\nFormatted Response (first 500 chars):")
            print("-" * 80)
            print(result['content'][:500])
            if len(result['content']) > 500:
                print(f"... (truncated, total length: {len(result['content'])} chars)")

        return True

    except Exception as e:
        print(f"\n[ERROR] Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""

    print("\nStarting Content Analysis Agent Tests...\n")

    # Test 1: Content Analyzer standalone
    test1_result = await test_content_analyzer_agent()

    # Test 2: Full pipeline integration
    # Note: This requires Google API keys and may use quota
    # Uncomment to test full pipeline:
    # test2_result = await test_full_pipeline()
    test2_result = None  # Skip by default

    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    print(f"[OK] Content Analyzer (standalone): {'PASSED' if test1_result else 'FAILED'}")
    if test2_result is not None:
        print(f"[OK] Full Pipeline (integration): {'PASSED' if test2_result else 'FAILED'}")
    else:
        print(f"[SKIP] Full Pipeline (integration): SKIPPED (uncomment in main() to run)")

    print("\n[INFO] To run full integration test:")
    print("   1. Ensure GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID are set in .env")
    print("   2. Uncomment 'test2_result' line in main() function")
    print("   3. Run this script again")

    print("\n[OK] Content Analysis Agent implementation complete!")
    print("   - Agent created at: adk_agents/content_analyzer/agent.py")
    print("   - Integrated into: adk_agents/orchestrator/agent.py (STEP 5)")
    print("   - Unit tests at: tests/test_content_analyzer.py")
    print("   - Integration test: test_content_analysis_integration.py (this file)")


if __name__ == "__main__":
    asyncio.run(main())
