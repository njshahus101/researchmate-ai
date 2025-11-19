"""
Step 4: Results Formatting

This module handles formatting results using the Information Gatherer agent.
"""

import json
from google.adk.runners import InMemoryRunner

from ...initialization import gatherer_agent


async def format_results_step(
    query: str,
    classification: dict,
    fetched_data: list,
    failed_urls: list,
    search_result: dict
) -> str:
    """
    Execute Step 4: Format Results with Information Gatherer.

    Args:
        query: User's research query
        classification: Classification results
        fetched_data: Fetched data from sources
        failed_urls: List of failed URL attempts
        search_result: Search results

    Returns:
        Formatted response text
    """
    print(f"\n[STEP 4/6] Formatting results with Information Gatherer...")

    # Build prompt with fetched data and helpful context
    if fetched_data:
        data_summary = json.dumps(fetched_data, indent=2)
        success_message = f"Successfully fetched data from {len(fetched_data)} sources"
    else:
        data_summary = "No data fetched"
        # Build helpful error context
        error_context = []
        if not search_result.get('urls'):
            error_context.append("Search found no relevant URLs")
        elif failed_urls:
            error_context.append(f"Tried {len(failed_urls)} URLs but all failed to extract useful data")
        success_message = "No data available. " + ". ".join(error_context)

    gatherer_prompt = f"""Format the following REAL-TIME FETCHED DATA into a user-friendly response.

Research Query: {query}

Query Classification:
- Type: {classification.get('query_type')}
- Strategy: {classification.get('research_strategy')}
- Complexity: {classification.get('complexity_score')}/10

STATUS: {success_message}

FETCHED DATA (from web):
{data_summary}

YOUR TASK:
- Format this fetched data into a clear, organized response
- Include prices, ratings, and details from the data
- Cite the URLs that were fetched
- Do NOT add information beyond what's in the fetched data
- Present it in a user-friendly way

If no data was fetched, provide a helpful response that:
1. Explains what went wrong (search failed, extraction failed, etc.)
2. Suggests more specific query terms
3. Suggests alternative approaches
4. Remains encouraging and helpful

Example helpful response when no data:
"I attempted to research '{query}' but wasn't able to retrieve complete data. This could be because:
- The search didn't find relevant product pages
- Product pages were inaccessible or blocked

Here's what you can try:
- Be more specific (e.g., include brand name, model number)
- Try a different product or query
- Check if the product exists on major retailers like Amazon

I'm ready to help with a refined search when you're ready!\""""

    # Call Information Gatherer to format
    print(f"[A2A] Calling Information Gatherer agent to format results...")
    runner = InMemoryRunner(agent=gatherer_agent)

    response = await runner.run_debug(gatherer_prompt)
    print(f"[A2A] Information Gatherer response received")

    # Extract response text
    if isinstance(response, list) and len(response) > 0:
        last_event = response[-1]
        if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
            response_text = last_event.content.parts[0].text
        else:
            response_text = str(last_event)
    else:
        response_text = str(response)

    print(f"[STEP 4/6] OK Formatting complete")

    return response_text
