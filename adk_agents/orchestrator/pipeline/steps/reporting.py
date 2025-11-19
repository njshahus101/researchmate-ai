"""
Step 6: Report Generation

This module handles final report generation using the Report Generator agent.
"""

import json
from google.adk.runners import InMemoryRunner

from ...initialization import report_generator_agent


async def generate_report_step(
    query: str,
    classification: dict,
    formatted_info: str,
    analysis_json: dict
) -> str:
    """
    Execute Step 6: Generate Final Report.

    Args:
        query: User's research query
        classification: Classification results
        formatted_info: Formatted information from Information Gatherer
        analysis_json: Analysis results from Content Analyzer

    Returns:
        Final report text
    """
    print(f"\n[STEP 6/6] Generating final report with Report Generator...")

    # Build comprehensive prompt for Report Generator
    report_prompt = f"""Generate a tailored report for the user.

QUERY: {query}

CLASSIFICATION:
- Type: {classification.get('query_type')}
- Strategy: {classification.get('research_strategy')}
- Complexity: {classification.get('complexity_score')}/10
- Key Topics: {', '.join(classification.get('key_topics', []))}

FORMATTED INFORMATION (from Information Gatherer):
{formatted_info}

CONTENT ANALYSIS (credibility scores and extracted facts):
{json.dumps(analysis_json, indent=2)}

YOUR TASK:
Generate a professional report following the format for query type: {classification.get('query_type')}

Requirements:
1. Use the appropriate report format (factual/comparative/exploratory)
2. Include all citations with credibility indicators
3. Apply weighted scoring if user stated priorities in query
4. Generate 3-5 relevant follow-up questions
5. Use professional markdown formatting
6. Ensure all claims are cited from the content analysis
7. Highlight any conflicts between sources transparently

Remember: You are the final voice to the user. Transform this data into actionable insights!"""

    # Call Report Generator agent
    print(f"[A2A] Calling Report Generator agent...")
    report_runner = InMemoryRunner(agent=report_generator_agent)

    try:
        report_response = await report_runner.run_debug(report_prompt)
        print(f"[A2A] Report Generator response received")

        # Extract report response
        if isinstance(report_response, list) and len(report_response) > 0:
            last_event = report_response[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                final_report = last_event.content.parts[0].text
            else:
                final_report = str(last_event)
        else:
            final_report = str(report_response)

        print(f"[STEP 6/6] OK Report generation complete")
        return final_report

    except Exception as e:
        print(f"[STEP 6/6] WARN Report generation failed: {e}")
        print(f"[STEP 6/6] Falling back to Information Gatherer output")
        # Fallback to the formatted information from Information Gatherer
        return formatted_info
