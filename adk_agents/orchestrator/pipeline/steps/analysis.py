"""
Step 5: Content Analysis

This module handles content analysis for credibility using the Content Analyzer agent.
"""

import json
from google.adk.runners import InMemoryRunner

from ...initialization import analyzer_agent


async def analyze_content_step(query: str, classification: dict, fetched_data: list) -> dict:
    """
    Execute Step 5: Analyze Content for Credibility.

    Args:
        query: User's research query
        classification: Classification results
        fetched_data: Fetched data from sources

    Returns:
        Analysis results as dictionary
    """
    print(f"\n[STEP 5/6] Analyzing content credibility and extracting facts...")

    # Only perform analysis if we have fetched data
    if not fetched_data:
        print(f"[STEP 5/6] SKIP No data to analyze (no sources fetched)")
        return {
            "analysis_summary": {
                "total_sources": 0,
                "credible_sources": 0,
                "note": "No sources were fetched, skipping analysis"
            }
        }

    # Build analysis prompt with fetched data
    analysis_prompt = f"""Analyze the following fetched data for credibility and extract key facts.

Research Query: {query}

Query Type: {classification.get('query_type')}

FETCHED DATA (from {len(fetched_data)} sources):
{json.dumps(fetched_data, indent=2)}

YOUR TASK:
1. Score each source's credibility (0-100)
2. Extract key facts with confidence levels
3. Identify any conflicts between sources
4. Create comparison matrix if this is a product comparison
5. Normalize all data (prices, ratings, specifications)

Return comprehensive analysis in JSON format as specified in your instructions."""

    # Call Content Analysis agent
    print(f"[A2A] Calling Content Analysis agent...")
    analyzer_runner = InMemoryRunner(agent=analyzer_agent)

    try:
        analysis_response = await analyzer_runner.run_debug(analysis_prompt)
        print(f"[A2A] Content Analysis response received")

        # Extract analysis response
        if isinstance(analysis_response, list) and len(analysis_response) > 0:
            last_event = analysis_response[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                analysis_text = last_event.content.parts[0].text
            else:
                analysis_text = str(last_event)
        else:
            analysis_text = str(analysis_response)

        # Try to parse JSON from analysis
        cleaned_analysis = analysis_text.strip()
        if cleaned_analysis.startswith('```json'):
            cleaned_analysis = cleaned_analysis[7:]
        if cleaned_analysis.startswith('```'):
            cleaned_analysis = cleaned_analysis[3:]
        if cleaned_analysis.endswith('```'):
            cleaned_analysis = cleaned_analysis[:-3]
        cleaned_analysis = cleaned_analysis.strip()

        try:
            analysis_json = json.loads(cleaned_analysis)
            print(f"[STEP 5/6] OK Analysis complete - {analysis_json.get('analysis_summary', {}).get('credible_sources', 0)} credible sources found")
        except json.JSONDecodeError:
            # If JSON parsing fails, use text as-is
            analysis_json = {"raw_analysis": cleaned_analysis}
            print(f"[STEP 5/6] OK Analysis complete (raw text format)")

        return analysis_json

    except Exception as e:
        print(f"[STEP 5/6] WARN Analysis failed: {e}")
        return {
            "error": str(e),
            "analysis_summary": {"note": "Content analysis failed, using unanalyzed data"}
        }
