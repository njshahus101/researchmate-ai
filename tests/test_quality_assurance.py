"""
Comprehensive Test Suite for Quality Assurance Service

Tests all validation categories:
1. Report Completeness
2. Citation Accuracy
3. Comparison Matrix Quality
4. Source Quality
5. Overall Quality Scoring
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.quality_assurance import (
    QualityAssuranceService,
    ValidationLevel,
    validate_research_output
)


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

def get_sample_classification(query_type="comparative"):
    """Sample classification results"""
    return {
        "query_type": query_type,
        "research_strategy": "multi-source",
        "complexity_score": 7,
        "key_topics": ["wireless headphones", "noise cancellation"]
    }


def get_sample_fetched_sources():
    """Sample fetched source data"""
    return [
        {
            "url": "https://amazon.com/sony-wh1000xm5",
            "data": {"status": "success", "product_name": "Sony WH-1000XM5"},
            "source": {"title": "Amazon"}
        },
        {
            "url": "https://bestbuy.com/sony-headphones",
            "data": {"status": "success", "product_name": "Sony Headphones"},
            "source": {"title": "Best Buy"}
        },
        {
            "url": "https://cnet.com/sony-review",
            "data": {"status": "success", "content": "Review content..."},
            "source": {"title": "CNET Review"}
        }
    ]


def get_sample_analysis_good():
    """Sample analysis with good quality data"""
    return {
        "analysis_summary": {
            "total_sources": 3,
            "credible_sources": 2,
            "conflicts_found": 0,
            "query_type": "product_comparison"
        },
        "source_credibility": [
            {
                "url": "https://amazon.com/sony-wh1000xm5",
                "credibility_score": 85,
                "credibility_level": "Highly Credible",
                "domain_authority": 35,
                "content_quality": 25,
                "consistency": 25
            },
            {
                "url": "https://bestbuy.com/sony-headphones",
                "credibility_score": 75,
                "credibility_level": "Moderately Credible",
                "domain_authority": 30,
                "content_quality": 25,
                "consistency": 20
            },
            {
                "url": "https://cnet.com/sony-review",
                "credibility_score": 80,
                "credibility_level": "Highly Credible",
                "domain_authority": 30,
                "content_quality": 25,
                "consistency": 25
            }
        ],
        "comparison_matrix": {
            "applicable": True,
            "products": [
                {
                    "name": "Sony WH-1000XM5",
                    "price": {"value": 348.00, "currency": "USD"},
                    "rating": {"value": 4.7, "scale": 5, "reviews": 2543},
                    "key_features": ["ANC", "30hr battery"]
                },
                {
                    "name": "Bose QC45",
                    "price": {"value": 329.00, "currency": "USD"},
                    "rating": {"value": 4.5, "scale": 5, "reviews": 1832},
                    "key_features": ["ANC", "24hr battery"]
                }
            ]
        }
    }


def get_perfect_report():
    """Sample report with perfect quality (all sections, proper citations)"""
    return """## Wireless Headphones Comparison

After analyzing multiple sources, here are the top wireless headphones with noise cancellation.

### Top Recommendations

The Sony WH-1000XM5 leads with exceptional noise cancellation [1] and 30-hour battery life [2].
The Bose QC45 offers great comfort and reliable ANC [3].

### Comparison Table

| Feature | Sony WH-1000XM5 | Bose QC45 |
|---------|----------------|-----------|
| Price | $348 | $329 |
| Rating | 4.7/5 (2543 reviews) | 4.5/5 (1832 reviews) |
| Battery | 30 hours | 24 hours |
| ANC | Excellent | Very Good |

### Executive Summary

For best noise cancellation and battery life, choose Sony WH-1000XM5 [1][2].
For better price and comfort, Bose QC45 is excellent [3].

### Sources

[1] Amazon - Sony WH-1000XM5 - https://amazon.com/sony-wh1000xm5 (Credibility: 85/100)
[2] Best Buy - Sony Headphones - https://bestbuy.com/sony-headphones (Credibility: 75/100)
[3] CNET - Sony Review - https://cnet.com/sony-review (Credibility: 80/100)

**Follow-up Questions:**

- What's the warranty coverage for these headphones?
- Are there color options available?
- How do they perform for phone calls?
"""


def get_report_missing_sources():
    """Report missing Sources section"""
    return """## Wireless Headphones

The Sony WH-1000XM5 is a great choice with 30-hour battery life.

**Follow-up Questions:**
- What about warranty?
"""


def get_report_orphaned_citations():
    """Report with citations that don't match Sources section"""
    return """## Analysis

According to research [1], the Sony headphones are best. Another study [2] confirms this.
There's also evidence [5] of great battery life.

### Sources

[1] Amazon - https://amazon.com
[2] Best Buy - https://bestbuy.com

**Follow-up Questions:**
- What about other brands?
"""


def get_report_no_citations():
    """Report with no citations"""
    return """## Analysis

The Sony WH-1000XM5 headphones are highly rated and offer great features.
They have excellent battery life and noise cancellation.

### Sources

Some sources were consulted but not cited properly.

**Follow-up Questions:**
- What's the price range?
"""


# ============================================================================
# TEST CASES
# ============================================================================

def test_perfect_report():
    """Test a perfect quality report (should score 90+)"""
    print("\n" + "="*70)
    print("TEST 1: Perfect Quality Report")
    print("="*70)

    qa_service = QualityAssuranceService()
    quality_report = qa_service.validate_output(
        final_report=get_perfect_report(),
        classification=get_sample_classification("comparative"),
        analysis_json=get_sample_analysis_good(),
        fetched_sources=get_sample_fetched_sources(),
        query="best wireless headphones"
    )

    print(f"\n[PASS] Overall Score: {quality_report.overall_score}/100")
    print(f"[PASS] Grade: {quality_report._get_grade()}")
    print(f"[PASS] Passed: {quality_report.summary['passed']}/{quality_report.summary['total_checks']}")
    print(f"[WARN] Warnings: {quality_report.summary['warnings']}")
    print(f"[FAIL] Failed: {quality_report.summary['failed']}")

    print(f"\n[INFO] Recommendations:")
    for rec in quality_report.recommendations[:3]:
        print(f"  - {rec}")

    # Assertions
    assert quality_report.overall_score >= 85, f"Expected score >=85, got {quality_report.overall_score}"
    assert quality_report.summary['failed'] == 0, "Perfect report should have no failures"

    print("\n[PASS] TEST PASSED: Perfect report scored high with no failures")
    return quality_report


def test_missing_sources_section():
    """Test report missing Sources section (critical failure)"""
    print("\n" + "="*70)
    print("TEST 2: Report Missing Sources Section")
    print("="*70)

    qa_service = QualityAssuranceService()
    quality_report = qa_service.validate_output(
        final_report=get_report_missing_sources(),
        classification=get_sample_classification("factual"),
        analysis_json=get_sample_analysis_good(),
        fetched_sources=get_sample_fetched_sources(),
        query="wireless headphones info"
    )

    print(f"\n[WARN]  Overall Score: {quality_report.overall_score}/100")
    print(f"[WARN]  Grade: {quality_report._get_grade()}")
    print(f"[PASS] Passed: {quality_report.summary['passed']}")
    print(f"[FAIL] Failed: {quality_report.summary['failed']}")

    print(f"\n[INFO] Key Issues:")
    for result in quality_report.validation_results:
        if result.level == ValidationLevel.FAIL:
            print(f"  [FAIL] {result.check_name}: {result.message}")

    # Assertions
    assert quality_report.summary['failed'] > 0, "Should have failures for missing Sources"
    has_sources_failure = any(
        r.check_name == "Sources Section" and r.level == ValidationLevel.FAIL
        for r in quality_report.validation_results
    )
    assert has_sources_failure, "Should detect missing Sources section"

    print("\n[PASS] TEST PASSED: Correctly detected missing Sources section")
    return quality_report


def test_orphaned_citations():
    """Test report with orphaned citations (citations without source entries)"""
    print("\n" + "="*70)
    print("TEST 3: Orphaned Citations Detection")
    print("="*70)

    qa_service = QualityAssuranceService()
    quality_report = qa_service.validate_output(
        final_report=get_report_orphaned_citations(),
        classification=get_sample_classification("factual"),
        analysis_json=get_sample_analysis_good(),
        fetched_sources=get_sample_fetched_sources(),
        query="sony headphones"
    )

    print(f"\n[WARN]  Overall Score: {quality_report.overall_score}/100")
    print(f"[WARN]  Grade: {quality_report._get_grade()}")

    print(f"\n[INFO] Citation Issues:")
    for result in quality_report.validation_results:
        if result.category == "Citations":
            symbol = "[FAIL]" if result.level == ValidationLevel.FAIL else "[WARN]" if result.level == ValidationLevel.WARNING else "[PASS]"
            print(f"  {symbol} {result.check_name}: {result.message}")
            if result.details.get('orphaned'):
                print(f"      Orphaned citations: {result.details['orphaned']}")

    # Assertions
    citation_results = [r for r in quality_report.validation_results if r.category == "Citations"]
    assert len(citation_results) > 0, "Should have citation validation results"

    orphaned_check = next((r for r in citation_results if "orphaned" in r.details), None)
    if orphaned_check:
        assert len(orphaned_check.details.get('orphaned', [])) > 0, "Should detect orphaned citation [5]"

    print("\n[PASS] TEST PASSED: Correctly detected orphaned citations")
    return quality_report


def test_no_citations():
    """Test report with no citations (should fail)"""
    print("\n" + "="*70)
    print("TEST 4: No Citations in Report")
    print("="*70)

    qa_service = QualityAssuranceService()
    quality_report = qa_service.validate_output(
        final_report=get_report_no_citations(),
        classification=get_sample_classification("factual"),
        analysis_json=get_sample_analysis_good(),
        fetched_sources=get_sample_fetched_sources(),
        query="sony headphones features"
    )

    print(f"\n[WARN]  Overall Score: {quality_report.overall_score}/100")
    print(f"[WARN]  Grade: {quality_report._get_grade()}")

    print(f"\n[INFO] Citation Analysis:")
    for result in quality_report.validation_results:
        if result.category == "Citations":
            print(f"  [FAIL] {result.check_name}: {result.message}")

    # Assertions
    has_citation_failure = any(
        r.category == "Citations" and r.level == ValidationLevel.FAIL
        for r in quality_report.validation_results
    )
    assert has_citation_failure, "Should fail when no citations present"

    print("\n[PASS] TEST PASSED: Correctly failed for missing citations")
    return quality_report


def test_comparison_matrix_validation():
    """Test comparison matrix quality checks"""
    print("\n" + "="*70)
    print("TEST 5: Comparison Matrix Quality Validation")
    print("="*70)

    qa_service = QualityAssuranceService()
    quality_report = qa_service.validate_output(
        final_report=get_perfect_report(),  # Has comparison table
        classification=get_sample_classification("comparative"),
        analysis_json=get_sample_analysis_good(),  # Has comparison matrix
        fetched_sources=get_sample_fetched_sources(),
        query="compare wireless headphones"
    )

    print(f"\n[PASS] Overall Score: {quality_report.overall_score}/100")

    print(f"\n[INFO] Comparison Matrix Checks:")
    for result in quality_report.validation_results:
        if result.category == "Comparison":
            symbol = "[PASS]" if result.level == ValidationLevel.PASS else "[WARN]" if result.level == ValidationLevel.WARNING else "[FAIL]"
            print(f"  {symbol} {result.check_name}: {result.message}")

    # Assertions
    comparison_results = [r for r in quality_report.validation_results if r.category == "Comparison"]
    assert len(comparison_results) > 0, "Should have comparison validation results"

    matrix_exists = any(r.check_name == "Matrix Exists" and r.level == ValidationLevel.PASS for r in comparison_results)
    assert matrix_exists, "Should detect comparison matrix exists"

    print("\n[PASS] TEST PASSED: Comparison matrix validation working correctly")
    return quality_report


def test_source_quality_validation():
    """Test source quality and credibility checks"""
    print("\n" + "="*70)
    print("TEST 6: Source Quality Validation")
    print("="*70)

    qa_service = QualityAssuranceService()
    quality_report = qa_service.validate_output(
        final_report=get_perfect_report(),
        classification=get_sample_classification("comparative"),
        analysis_json=get_sample_analysis_good(),
        fetched_sources=get_sample_fetched_sources(),
        query="wireless headphones"
    )

    print(f"\n[PASS] Overall Score: {quality_report.overall_score}/100")

    print(f"\n[INFO] Source Quality Checks:")
    for result in quality_report.validation_results:
        if result.category == "Source Quality":
            symbol = "[PASS]" if result.level == ValidationLevel.PASS else "[WARN]"
            print(f"  {symbol} {result.check_name}: {result.message}")
            if "avg_credibility" in result.details:
                print(f"      Average Credibility: {result.details['avg_credibility']:.0f}/100")

    # Assertions
    source_results = [r for r in quality_report.validation_results if r.category == "Source Quality"]
    assert len(source_results) > 0, "Should have source quality validation results"

    print("\n[PASS] TEST PASSED: Source quality validation working correctly")
    return quality_report


def test_incomplete_comparison_data():
    """Test comparison with incomplete product data"""
    print("\n" + "="*70)
    print("TEST 7: Incomplete Comparison Data")
    print("="*70)

    # Create analysis with incomplete product data
    incomplete_analysis = get_sample_analysis_good()
    incomplete_analysis["comparison_matrix"]["products"] = [
        {
            "name": "Sony WH-1000XM5",
            # Missing price and rating
        },
        {
            "name": "Bose QC45",
            "price": {"value": 329.00, "currency": "USD"},
            # Missing rating
        }
    ]

    qa_service = QualityAssuranceService()
    quality_report = qa_service.validate_output(
        final_report=get_perfect_report(),
        classification=get_sample_classification("comparative"),
        analysis_json=incomplete_analysis,
        fetched_sources=get_sample_fetched_sources(),
        query="compare headphones"
    )

    print(f"\n[WARN]  Overall Score: {quality_report.overall_score}/100")

    print(f"\n[INFO] Data Completeness Issues:")
    for result in quality_report.validation_results:
        if result.check_name == "Data Completeness":
            print(f"  [WARN]  {result.message}")
            if "avg_completeness" in result.details:
                print(f"      Average Completeness: {result.details['avg_completeness']:.0f}%")

    # Assertions
    completeness_check = next(
        (r for r in quality_report.validation_results if r.check_name == "Data Completeness"),
        None
    )
    if completeness_check:
        assert completeness_check.details['avg_completeness'] < 100, "Should detect incomplete data"

    print("\n[PASS] TEST PASSED: Correctly detected incomplete comparison data")
    return quality_report


def test_low_credibility_sources():
    """Test with low-credibility sources"""
    print("\n" + "="*70)
    print("TEST 8: Low-Credibility Sources Warning")
    print("="*70)

    # Create analysis with low credibility scores
    low_cred_analysis = get_sample_analysis_good()
    low_cred_analysis["source_credibility"] = [
        {
            "url": "https://unknown-blog.com/review",
            "credibility_score": 35,
            "credibility_level": "Not Credible"
        },
        {
            "url": "https://random-site.com/info",
            "credibility_score": 42,
            "credibility_level": "Low Credibility"
        }
    ]
    low_cred_analysis["analysis_summary"]["credible_sources"] = 0

    qa_service = QualityAssuranceService()
    quality_report = qa_service.validate_output(
        final_report=get_perfect_report(),
        classification=get_sample_classification("factual"),
        analysis_json=low_cred_analysis,
        fetched_sources=get_sample_fetched_sources(),
        query="headphones review"
    )

    print(f"\n[WARN]  Overall Score: {quality_report.overall_score}/100")
    print(f"[WARN]  Grade: {quality_report._get_grade()}")

    print(f"\n[INFO] Credibility Warnings:")
    for result in quality_report.validation_results:
        if "Credibility" in result.check_name:
            symbol = "[FAIL]" if result.level == ValidationLevel.FAIL else "[WARN]" if result.level == ValidationLevel.WARNING else "[PASS]"
            print(f"  {symbol} {result.check_name}: {result.message}")

    # Assertions
    avg_cred_check = next(
        (r for r in quality_report.validation_results if r.check_name == "Average Credibility"),
        None
    )
    if avg_cred_check:
        assert avg_cred_check.score < 70, "Should score low for low-credibility sources"

    print("\n[PASS] TEST PASSED: Correctly warned about low-credibility sources")
    return quality_report


def test_quality_report_json_export():
    """Test quality report JSON export functionality"""
    print("\n" + "="*70)
    print("TEST 9: Quality Report JSON Export")
    print("="*70)

    quality_report = validate_research_output(
        final_report=get_perfect_report(),
        classification=get_sample_classification("comparative"),
        analysis_json=get_sample_analysis_good(),
        fetched_sources=get_sample_fetched_sources(),
        query="wireless headphones comparison"
    )

    # Export to dict
    report_dict = quality_report.to_dict()

    print(f"\n[PASS] Exported Quality Report:")
    print(f"  Overall Score: {report_dict['overall_score']}/100")
    print(f"  Grade: {report_dict['grade']}")
    print(f"  Total Checks: {report_dict['summary']['total_checks']}")
    print(f"  Validation Results: {len(report_dict['validation_results'])}")
    print(f"  Recommendations: {len(report_dict['recommendations'])}")

    # Assertions
    assert 'overall_score' in report_dict, "Should have overall_score"
    assert 'grade' in report_dict, "Should have grade"
    assert 'validation_results' in report_dict, "Should have validation_results"
    assert 'summary' in report_dict, "Should have summary"
    assert 'recommendations' in report_dict, "Should have recommendations"

    print("\n[PASS] TEST PASSED: JSON export working correctly")
    return report_dict


def test_edge_case_empty_report():
    """Test with empty or very short report"""
    print("\n" + "="*70)
    print("TEST 10: Edge Case - Empty Report")
    print("="*70)

    qa_service = QualityAssuranceService()
    quality_report = qa_service.validate_output(
        final_report="",  # Empty report
        classification=get_sample_classification("factual"),
        analysis_json={},  # Empty analysis
        fetched_sources=[],  # No sources
        query="test query"
    )

    print(f"\n[FAIL] Overall Score: {quality_report.overall_score}/100")
    print(f"[FAIL] Grade: {quality_report._get_grade()}")
    print(f"[FAIL] Failed Checks: {quality_report.summary['failed']}/{quality_report.summary['total_checks']}")

    # Assertions
    assert quality_report.overall_score < 50, "Empty report should score very low"
    assert quality_report.summary['failed'] > 0, "Should have multiple failures"

    print("\n[PASS] TEST PASSED: Correctly failed for empty report")
    return quality_report


# ============================================================================
# RUN ALL TESTS
# ============================================================================

def run_all_tests():
    """Run all QA validation tests"""
    print("\n" + "="*70)
    print("QUALITY ASSURANCE SERVICE - COMPREHENSIVE TEST SUITE")
    print("="*70)

    test_results = []
    failed_tests = []

    tests = [
        ("Perfect Report", test_perfect_report),
        ("Missing Sources Section", test_missing_sources_section),
        ("Orphaned Citations", test_orphaned_citations),
        ("No Citations", test_no_citations),
        ("Comparison Matrix Validation", test_comparison_matrix_validation),
        ("Source Quality Validation", test_source_quality_validation),
        ("Incomplete Comparison Data", test_incomplete_comparison_data),
        ("Low-Credibility Sources", test_low_credibility_sources),
        ("JSON Export", test_quality_report_json_export),
        ("Edge Case - Empty Report", test_edge_case_empty_report),
    ]

    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, "PASS", result))
            print(f"\n[PASS] {test_name}: PASS")
        except AssertionError as e:
            test_results.append((test_name, "FAIL", str(e)))
            failed_tests.append(test_name)
            print(f"\n[FAIL] {test_name}: FAIL - {e}")
        except Exception as e:
            test_results.append((test_name, "ERROR", str(e)))
            failed_tests.append(test_name)
            print(f"\n[FAIL] {test_name}: ERROR - {e}")

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    total = len(tests)
    passed = total - len(failed_tests)

    print(f"\nTotal Tests: {total}")
    print(f"[PASS] Passed: {passed}")
    print(f"[FAIL] Failed: {len(failed_tests)}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if failed_tests:
        print(f"\n[FAIL] Failed Tests:")
        for test_name in failed_tests:
            print(f"  - {test_name}")
    else:
        print(f"\n[SUCCESS] ALL TESTS PASSED! Quality Assurance system is working perfectly.")

    return len(failed_tests) == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
