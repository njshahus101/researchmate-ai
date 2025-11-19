"""
Step 7: Quality Assurance

This module handles output quality validation using the QA service.
"""

from ...initialization import qa_service, logger


def quality_check_step(
    final_report: str,
    classification: dict,
    analysis_json: dict,
    fetched_data: list,
    query: str
):
    """
    Execute Step 7: Validate Output Quality.

    Args:
        final_report: The final report text
        classification: Classification results
        analysis_json: Analysis results
        fetched_data: Fetched data from sources
        query: User's original query

    Returns:
        Quality report object or None if validation fails
    """
    print(f"\n[STEP 7/7] Validating output quality with QA service...")

    try:
        quality_report = qa_service.validate_output(
            final_report=final_report,
            classification=classification,
            analysis_json=analysis_json,
            fetched_sources=fetched_data,
            query=query
        )

        print(f"[STEP 7/7] OK Quality validation complete")
        print(f"  Quality Score: {quality_report.overall_score}/100 ({quality_report._get_grade()})")
        print(f"  Passed: {quality_report.summary['passed']}/{quality_report.summary['total_checks']} checks")

        if quality_report.summary['failed'] > 0:
            print(f"  [WARN]  Failed: {quality_report.summary['failed']} check(s)")
        if quality_report.summary['warnings'] > 0:
            print(f"  [WARN]  Warnings: {quality_report.summary['warnings']} check(s)")

        # Show top recommendations
        if quality_report.recommendations:
            print(f"  Top Recommendation: {quality_report.recommendations[0]}")

        return quality_report

    except Exception as e:
        print(f"[STEP 7/7] WARN Quality validation failed: {e}")
        logger.warning("QA validation failed", error=str(e))
        return None
