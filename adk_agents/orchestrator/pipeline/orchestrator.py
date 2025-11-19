"""
Main Pipeline Orchestrator

This module contains the main execute_fixed_pipeline function that coordinates
all pipeline steps in a deterministic sequence.
"""

import time
import uuid

from ..initialization import logger, tracer, metrics, session_service
from .steps import (
    classify_query_step,
    search_step,
    fetch_data_step,
    format_results_step,
    analyze_content_step,
    generate_report_step,
    quality_check_step,
)


async def execute_fixed_pipeline(
    query: str,
    user_id: str = "default",
    interactive: bool = False,
    session_id: str = None
) -> dict:
    """
    FIXED PIPELINE: Executes research in a deterministic order.

    This function ALWAYS executes ALL steps in sequence - no LLM decisions:

    STEP 0: (Optional) Ask for clarifications
    STEP 1: Classify query
    STEP 2: Search web for URLs
    STEP 3: Extract data from URLs
    STEP 4: Format results
    STEP 5: Analyze content credibility and extract facts
    STEP 6: Generate tailored report with citations and follow-up questions
    STEP 7: Validate output quality (completeness, citations, comparison matrices)

    Args:
        query: The user's research query
        user_id: User identifier for personalization
        interactive: If True, asks user for clarifications after classification
        session_id: Optional session ID for conversation persistence

    Returns:
        Dictionary with complete research results including final report
    """
    # Generate unique query ID for tracking
    query_id = str(uuid.uuid4())
    pipeline_start_time = time.time()

    # Create or resume session for conversation persistence
    if not session_id:
        session_id = session_service.create_session(user_id=user_id, title=query[:50])
        logger.info("Created new session", session_id=session_id, user_id=user_id)

    # Store user query in session
    session_service.add_message(session_id, "user", query, metadata={"query_id": query_id})

    # Start distributed trace for entire pipeline
    with tracer.trace_span("fixed_pipeline", {
        "query": query[:100],  # Truncate for trace attributes
        "user_id": user_id,
        "query_id": query_id,
        "interactive": str(interactive)
    }):
        logger.info(
            "Starting fixed pipeline execution",
            query_id=query_id,
            user_id=user_id,
            query=query,
            interactive=interactive
        )

        # Record pipeline start metric
        metrics.increment_counter("pipeline_start_total", labels={"user_id": user_id})

    try:
        # ============================================================
        # STEP 1: CLASSIFY QUERY
        # ============================================================
        classification = await classify_query_step(query, user_id, query_id)

        # ============================================================
        # STEP 1.5: CLASSIFICATION DISPLAY (NON-BLOCKING)
        # ============================================================
        print(f"\n[INFO] Query analyzed - proceeding with research...")

        # Store classification for later use in response
        classification_summary = {
            "type": classification.get('query_type'),
            "strategy": classification.get('research_strategy'),
            "complexity": classification.get('complexity_score')
        }

        # ============================================================
        # STEP 2: SMART SEARCH STRATEGY
        # ============================================================
        google_shopping_data, search_result = search_step(query, classification)

        # ============================================================
        # STEP 3: FETCH DATA
        # ============================================================
        fetched_data, failed_urls = fetch_data_step(google_shopping_data, search_result)

        # ============================================================
        # STEP 4: FORMAT RESULTS
        # ============================================================
        response_text = await format_results_step(
            query,
            classification,
            fetched_data,
            failed_urls,
            search_result
        )

        # ============================================================
        # STEP 5: ANALYZE CONTENT
        # ============================================================
        analysis_json = await analyze_content_step(query, classification, fetched_data)

        # ============================================================
        # STEP 6: GENERATE FINAL REPORT
        # ============================================================
        final_report = await generate_report_step(
            query,
            classification,
            response_text,
            analysis_json
        )

        # ============================================================
        # STEP 7: VALIDATE OUTPUT QUALITY
        # ============================================================
        quality_report = quality_check_step(
            final_report,
            classification,
            analysis_json,
            fetched_data,
            query
        )

        print(f"\n{'='*60}")
        print(f"PIPELINE COMPLETE - 7/7 STEPS FINISHED")
        print(f"{'='*60}\n")

        # Store assistant's response in session
        session_service.add_message(
            session_id,
            "assistant",
            final_report,
            metadata={
                "query_id": query_id,
                "sources_fetched": len(fetched_data),
                "classification": classification.get('query_type'),
                "pipeline_duration_seconds": time.time() - pipeline_start_time,
                "quality_score": quality_report.overall_score if quality_report else None,
                "quality_grade": quality_report._get_grade() if quality_report else None
            }
        )
        logger.info("Stored assistant response in session", session_id=session_id)

        return {
            "status": "success",
            "content": final_report,  # Return the final report from Report Generator
            "classification": classification,
            "sources_fetched": len(fetched_data),
            "content_analysis": analysis_json,
            "quality_report": quality_report.to_dict() if quality_report else None,
            "session_id": session_id,  # Include session ID for reference
            "intermediate_outputs": {
                "information_gatherer": response_text,  # Keep for debugging
            },
            "pipeline_steps": {
                "classification": "OK Complete",
                "search": f"OK Found {len(search_result.get('urls', []))} URLs",
                "fetch": f"OK Fetched {len(fetched_data)} sources",
                "format": "OK Complete",
                "analysis": "OK Complete" if fetched_data else "SKIP No data",
                "report": "OK Complete",
                "quality_validation": f"OK Complete (Score: {quality_report.overall_score}/100)" if quality_report else "WARN Failed"
            }
        }

    except Exception as e:
        print(f"[PIPELINE ERROR] Pipeline failed: {e}")
        print(f"\n{'='*60}")
        print(f"PIPELINE FAILED")
        print(f"{'='*60}\n")

        return {
            "status": "error",
            "error": str(e),
            "classification": classification if 'classification' in locals() else {},
            "fetched_data": fetched_data if 'fetched_data' in locals() else [],
            "sources_fetched": len(fetched_data) if 'fetched_data' in locals() else 0,
            "session_id": session_id,
            "pipeline_steps": {
                "classification": "OK Complete" if 'classification' in locals() else "FAILED",
                "search": f"OK Found {len(search_result.get('urls', []))} URLs" if 'search_result' in locals() else "FAILED",
                "fetch": f"OK Fetched {len(fetched_data)} sources" if 'fetched_data' in locals() else "FAILED",
                "format": f"FAILED: {str(e)}",
                "analysis": "SKIP (earlier step failed)",
                "report": "SKIP (earlier step failed)"
            }
        }
