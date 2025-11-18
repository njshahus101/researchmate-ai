"""
Quick QA Integration Verification

Simply checks that:
1. QA service can be imported
2. QA validation produces results
3. Quality scores are in valid range
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.quality_assurance import QualityAssuranceService, validate_research_output


def verify_qa_service():
    """Verify QA service works correctly"""

    # Sample data for testing
    sample_report = """## Test Report

This is a test report with proper citations [1][2].

### Key Findings
- Finding 1 from source [1]
- Finding 2 from source [2]

### Sources
[1] Amazon - https://amazon.com (Credibility: 85/100)
[2] CNET - https://cnet.com (Credibility: 80/100)

**Follow-up Questions:**
- Question 1?
- Question 2?
"""

    sample_classification = {
        "query_type": "comparative",
        "research_strategy": "multi-source",
        "complexity_score": 5
    }

    sample_analysis = {
        "analysis_summary": {
            "total_sources": 2,
            "credible_sources": 2
        },
        "source_credibility": [
            {"url": "https://amazon.com", "credibility_score": 85},
            {"url": "https://cnet.com", "credibility_score": 80}
        ],
        "comparison_matrix": {
            "applicable": False
        }
    }

    sample_sources = [
        {"url": "https://amazon.com", "data": {"status": "success"}},
        {"url": "https://cnet.com", "data": {"status": "success"}}
    ]

    print("\n" + "="*60)
    print("QA INTEGRATION VERIFICATION")
    print("="*60)

    try:
        # Test QA service
        qa_service = QualityAssuranceService()
        print("\n[OK] QA Service initialized")

        # Run validation
        quality_report = qa_service.validate_output(
            final_report=sample_report,
            classification=sample_classification,
            analysis_json=sample_analysis,
            fetched_sources=sample_sources,
            query="test query"
        )

        print("[OK] QA validation completed")

        # Check results
        assert quality_report.overall_score >= 0 and quality_report.overall_score <= 100
        print(f"[OK] Quality score in valid range: {quality_report.overall_score}/100")

        assert len(quality_report.validation_results) > 0
        print(f"[OK] Validation results generated: {len(quality_report.validation_results)} checks")

        assert len(quality_report.recommendations) > 0
        print(f"[OK] Recommendations generated: {len(quality_report.recommendations)}")

        # Test JSON export
        report_dict = quality_report.to_dict()
        assert 'overall_score' in report_dict
        assert 'grade' in report_dict
        print("[OK] JSON export working")

        # Summary
        print("\n" + "="*60)
        print("VERIFICATION RESULTS")
        print("="*60)
        print(f"\nQuality Score: {quality_report.overall_score}/100")
        print(f"Grade: {quality_report._get_grade()}")
        print(f"Total Checks: {quality_report.summary['total_checks']}")
        print(f"Passed: {quality_report.summary['passed']}")
        print(f"Warnings: {quality_report.summary['warnings']}")
        print(f"Failed: {quality_report.summary['failed']}")

        print(f"\nTop Recommendation: {quality_report.recommendations[0]}")

        print("\n" + "="*60)
        print("[SUCCESS] QA INTEGRATION VERIFIED SUCCESSFULLY")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = verify_qa_service()
    sys.exit(0 if success else 1)
