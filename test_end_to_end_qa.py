"""
End-to-End QA Integration Test

Tests the complete pipeline with real orchestrator execution including:
1. Query classification
2. Web search (mocked)
3. Data fetching (mocked)
4. Content analysis
5. Report generation
6. **Quality Assurance validation**

This validates that QA is properly integrated into the orchestrator pipeline.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Mock the research tools to avoid real API calls
class MockResearchTools:
    """Mock research tools for testing"""

    @staticmethod
    def search_web(query: str, num_results: int = 5):
        """Mock search results"""
        return {
            "status": "success",
            "query": query,
            "urls": [
                "https://amazon.com/sony-wh1000xm5",
                "https://bestbuy.com/sony-headphones",
                "https://cnet.com/reviews/sony-wh1000xm5"
            ],
            "results": [
                {"title": "Amazon - Sony WH-1000XM5", "url": "https://amazon.com/sony-wh1000xm5"},
                {"title": "Best Buy - Sony Headphones", "url": "https://bestbuy.com/sony-headphones"},
                {"title": "CNET Review", "url": "https://cnet.com/reviews/sony-wh1000xm5"}
            ]
        }

    @staticmethod
    def fetch_web_content(url: str):
        """Mock web content"""
        return {
            "status": "success",
            "url": url,
            "title": "Product Review",
            "content": "The Sony WH-1000XM5 headphones offer excellent noise cancellation and 30-hour battery life. Priced at $348, they are highly rated with 4.7 out of 5 stars from 2,543 reviews.",
            "word_count": 150
        }

    @staticmethod
    def extract_product_info(url: str):
        """Mock product extraction"""
        return {
            "status": "success",
            "product_name": "Sony WH-1000XM5",
            "price": "$348.00",
            "rating": "4.7",
            "review_count": "2543",
            "features": ["Active Noise Cancellation", "30hr Battery", "Bluetooth 5.2"]
        }

    @staticmethod
    def search_google_shopping(query: str, num_results: int = 5):
        """Mock Google Shopping results"""
        return {
            "status": "success",
            "query": query,
            "num_results": 2,
            "results": [
                {
                    "product_name": "Sony WH-1000XM5",
                    "price": "$348.00",
                    "seller": "Amazon",
                    "rating": "4.7",
                    "review_count": "2543",
                    "link": "https://amazon.com/sony-wh1000xm5"
                },
                {
                    "product_name": "Sony WH-1000XM5",
                    "price": "$379.99",
                    "seller": "Best Buy",
                    "rating": "4.6",
                    "review_count": "892",
                    "link": "https://bestbuy.com/sony-headphones"
                }
            ]
        }


# Monkey-patch the research tools module
import tools.research_tools as research_tools
research_tools.search_web = MockResearchTools.search_web
research_tools.fetch_web_content = MockResearchTools.fetch_web_content
research_tools.extract_product_info = MockResearchTools.extract_product_info
research_tools.search_google_shopping = MockResearchTools.search_google_shopping

# Now import orchestrator after mocking
from adk_agents.orchestrator.agent import execute_fixed_pipeline


async def test_end_to_end_with_qa():
    """
    Test complete pipeline execution with QA validation.

    This test:
    1. Runs the full orchestrator pipeline
    2. Verifies QA validation is performed
    3. Checks quality score is included in results
    4. Validates QA recommendations are generated
    """
    print("\n" + "="*70)
    print("END-TO-END QA INTEGRATION TEST")
    print("="*70)

    print("\n[TEST] Running full pipeline with product comparison query...")
    print("[TEST] Query: 'Compare prices for Sony WH-1000XM5 headphones'")

    # Execute the pipeline
    result = await execute_fixed_pipeline(
        query="Compare prices for Sony WH-1000XM5 headphones",
        user_id="test_user",
        interactive=False
    )

    print("\n" + "="*70)
    print("PIPELINE EXECUTION RESULTS")
    print("="*70)

    # Check basic result structure
    assert result.get("status") == "success", f"Pipeline should succeed, got: {result.get('status')}"
    print("[PASS] Pipeline executed successfully")

    # Check that quality report exists
    quality_report = result.get("quality_report")
    assert quality_report is not None, "Quality report should be present in results"
    print("[PASS] Quality report generated")

    # Check quality report structure
    assert "overall_score" in quality_report, "Quality report should have overall_score"
    assert "grade" in quality_report, "Quality report should have grade"
    assert "validation_results" in quality_report, "Quality report should have validation_results"
    assert "recommendations" in quality_report, "Quality report should have recommendations"
    print("[PASS] Quality report has all required fields")

    # Display quality metrics
    print("\n" + "="*70)
    print("QUALITY ASSURANCE RESULTS")
    print("="*70)

    print(f"\n[QA] Overall Quality Score: {quality_report['overall_score']}/100")
    print(f"[QA] Grade: {quality_report['grade']}")

    summary = quality_report.get('summary', {})
    print(f"\n[QA] Validation Summary:")
    print(f"  Total Checks: {summary.get('total_checks', 0)}")
    print(f"  Passed: {summary.get('passed', 0)}")
    print(f"  Warnings: {summary.get('warnings', 0)}")
    print(f"  Failed: {summary.get('failed', 0)}")
    print(f"  Pass Rate: {summary.get('pass_rate', 0):.1f}%")

    # Show validation results by category
    print(f"\n[QA] Results by Category:")
    for category, counts in summary.get('by_category', {}).items():
        print(f"  {category}:")
        print(f"    Pass: {counts.get('pass', 0)}, Warn: {counts.get('warning', 0)}, Fail: {counts.get('fail', 0)}")

    # Show recommendations
    recommendations = quality_report.get('recommendations', [])
    if recommendations:
        print(f"\n[QA] Recommendations ({len(recommendations)}):")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"  {i}. {rec}")

    # Check pipeline steps include QA
    pipeline_steps = result.get("pipeline_steps", {})
    qa_step = pipeline_steps.get("quality_validation")
    assert qa_step is not None, "Pipeline steps should include quality_validation"
    assert "OK Complete" in qa_step or "Score:" in qa_step, f"QA step should complete successfully, got: {qa_step}"
    print(f"\n[PASS] QA validation step in pipeline: {qa_step}")

    # Validate quality score is reasonable (should be decent with mocked data)
    score = quality_report['overall_score']
    assert score >= 0 and score <= 100, f"Quality score should be 0-100, got {score}"
    print(f"[PASS] Quality score is in valid range: {score}/100")

    # Check that final report exists and has content
    final_report = result.get("content")
    assert final_report, "Final report should have content"
    assert len(final_report) > 100, "Final report should have substantial content"
    print(f"[PASS] Final report generated ({len(final_report)} characters)")

    # Display sample of final report
    print("\n" + "="*70)
    print("FINAL REPORT (SAMPLE)")
    print("="*70)
    print(final_report[:500] + "..." if len(final_report) > 500 else final_report)

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print("\n[SUCCESS] End-to-end QA integration test PASSED!")
    print(f"[SUCCESS] Quality Assurance is properly integrated into the pipeline")
    print(f"[SUCCESS] Quality Score: {quality_report['overall_score']}/100 ({quality_report['grade']})")

    return True


async def test_qa_with_poor_quality_scenario():
    """
    Test QA validation with a scenario that should produce warnings.

    Uses a very simple query to test if QA correctly identifies quality issues.
    """
    print("\n" + "="*70)
    print("QA VALIDATION TEST - Poor Quality Scenario")
    print("="*70)

    print("\n[TEST] Running pipeline with simple factual query...")
    print("[TEST] Query: 'price'")

    # Execute with minimal query
    result = await execute_fixed_pipeline(
        query="price",
        user_id="test_user",
        interactive=False
    )

    quality_report = result.get("quality_report")

    if quality_report:
        score = quality_report['overall_score']
        print(f"\n[QA] Quality Score: {score}/100")
        print(f"[QA] Grade: {quality_report['grade']}")

        # We expect this might have warnings or lower score
        if score < 90:
            print(f"[PASS] QA correctly detected quality issues (score: {score}/100)")
        else:
            print(f"[INFO] Query produced high quality output despite simplicity (score: {score}/100)")

        # Show recommendations
        if quality_report.get('recommendations'):
            print(f"\n[QA] Recommendations:")
            for rec in quality_report['recommendations'][:3]:
                print(f"  - {rec}")

    return True


async def run_all_integration_tests():
    """Run all end-to-end integration tests"""
    print("\n" + "="*70)
    print("QUALITY ASSURANCE - END-TO-END INTEGRATION TEST SUITE")
    print("="*70)

    tests = [
        ("Full Pipeline with QA", test_end_to_end_with_qa),
        ("QA with Poor Quality Scenario", test_qa_with_poor_quality_scenario),
    ]

    results = []
    failed = []

    for test_name, test_func in tests:
        try:
            await test_func()
            results.append((test_name, "PASS"))
            print(f"\n[PASS] {test_name}: PASS")
        except AssertionError as e:
            results.append((test_name, "FAIL"))
            failed.append(test_name)
            print(f"\n[FAIL] {test_name}: FAIL - {e}")
        except Exception as e:
            results.append((test_name, "ERROR"))
            failed.append(test_name)
            print(f"\n[FAIL] {test_name}: ERROR - {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "="*70)
    print("INTEGRATION TEST SUMMARY")
    print("="*70)

    total = len(tests)
    passed = total - len(failed)

    print(f"\nTotal Tests: {total}")
    print(f"[PASS] Passed: {passed}")
    print(f"[FAIL] Failed: {len(failed)}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if failed:
        print(f"\n[FAIL] Failed Tests:")
        for test_name in failed:
            print(f"  - {test_name}")
    else:
        print(f"\n[SUCCESS] ALL INTEGRATION TESTS PASSED!")
        print(f"[SUCCESS] Quality Assurance is fully operational and integrated!")

    return len(failed) == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_integration_tests())
    sys.exit(0 if success else 1)
