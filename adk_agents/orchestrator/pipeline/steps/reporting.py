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
    analysis_json: dict,
    fetched_data: list = None
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

    # Extract structured source list with credibility scores for strict citation control
    source_credibility = analysis_json.get('source_credibility', [])

    # VALIDATION & FALLBACK: If source_credibility is missing/empty, build from fetched_data
    if not source_credibility and fetched_data:
        print(f"[STEP 6/6] WARN source_credibility missing - building from fetched_data")
        source_credibility = []
        for source in fetched_data:
            source_credibility.append({
                'url': source.get('url', ''),
                'title': source.get('title', source.get('url', 'Unknown Source')),
                'credibility_score': 70,  # Default moderate credibility
                'credibility_rationale': 'Source fetched but not analyzed by Content Analyzer'
            })
        print(f"[STEP 6/6] Built fallback source list with {len(source_credibility)} sources")

    structured_sources = []

    for i, source_info in enumerate(source_credibility, start=1):
        structured_sources.append({
            'citation_number': i,
            'url': source_info.get('url', 'N/A'),
            'title': source_info.get('title', f'Source {i}'),
            'credibility_score': source_info.get('credibility_score', 'N/A'),
            'credibility_rationale': source_info.get('credibility_rationale', '')
        })

    # Build structured sources section for the prompt
    if structured_sources:
        sources_section = "AVAILABLE SOURCES (STRICT - Use ONLY these sources with these exact numbers):\n"

        # Separate sources by credibility level for better guidance
        high_cred = [s for s in structured_sources if s['credibility_score'] >= 80]
        medium_cred = [s for s in structured_sources if 60 <= s['credibility_score'] < 80]
        low_cred = [s for s in structured_sources if s['credibility_score'] < 60]

        for src in structured_sources:
            sources_section += f"\n[{src['citation_number']}] {src['title']}\n"
            sources_section += f"    URL: {src['url']}\n"
            sources_section += f"    Credibility: {src['credibility_score']}/100\n"
            if src['credibility_rationale']:
                sources_section += f"    Rationale: {src['credibility_rationale']}\n"

        total_sources = len(structured_sources)

        # Build source prioritization guidance
        prioritization_guidance = f"\n📊 SOURCE DISTRIBUTION: {len(high_cred)} High-Credibility | {len(medium_cred)} Medium-Credibility | {len(low_cred)} Low-Credibility\n"
        if high_cred:
            prioritization_guidance += f"⭐ PRIORITIZE: Use sources [{', '.join(str(s['citation_number']) for s in high_cred)}] for main claims (High credibility ≥80)\n"
        if medium_cred:
            prioritization_guidance += f"📝 SECONDARY: Use sources [{', '.join(str(s['citation_number']) for s in medium_cred)}] for supporting information (Medium credibility 60-79)\n"
        if low_cred:
            prioritization_guidance += f"⚠️  CAUTION: Use sources [{', '.join(str(s['citation_number']) for s in low_cred)}] only for supplementary/corroborative details (Low credibility <60)\n"

        citation_constraint = f"""
CRITICAL CITATION REQUIREMENTS:
- You MUST ONLY cite sources numbered [1] through [{total_sources}]
- DO NOT create, invent, or hallucinate any additional sources
- DO NOT use citation numbers outside the range [1-{total_sources}]
- Every claim must be backed by one of these {total_sources} sources
- In your Sources section, list EXACTLY these {total_sources} sources with their URLs and credibility ratings
- Any deviation from these sources will result in quality validation failure

SOURCE PRIORITIZATION STRATEGY:
{prioritization_guidance}
- Base your PRIMARY findings and recommendations on HIGH-CREDIBILITY sources (≥80)
- Use MEDIUM-CREDIBILITY sources (60-79) for supporting details and additional context
- Use LOW-CREDIBILITY sources (<60) sparingly, only for corroboration or anecdotal perspectives
- When sources conflict, give more weight to higher-credibility sources in your analysis
- The quality score of your report will be weighted by which sources you cite most frequently
"""
        print(f"[STEP 6/6] Strict source control: {total_sources} sources ({len(high_cred)} high-cred, {len(medium_cred)} medium-cred, {len(low_cred)} low-cred)")
    else:
        sources_section = "WARNING: No structured sources available from Content Analysis.\n"
        citation_constraint = "\nNote: Limited source data available. Be explicit about limitations in your report.\n"
        print(f"[STEP 6/6] WARN No structured sources found in analysis_json")

    # Build comprehensive prompt for Report Generator
    report_prompt = f"""Generate a tailored report for the user.

QUERY: {query}

CLASSIFICATION:
- Type: {classification.get('query_type')}
- Strategy: {classification.get('research_strategy')}
- Complexity: {classification.get('complexity_score')}/10
- Key Topics: {', '.join(classification.get('key_topics', []))}

{sources_section}
{citation_constraint}

FORMATTED INFORMATION (from Information Gatherer):
{formatted_info}

CONTENT ANALYSIS (credibility scores and extracted facts):
{json.dumps(analysis_json, indent=2)}

YOUR TASK:
Generate a professional report following the format for query type: {classification.get('query_type')}

Requirements:
1. Use the appropriate report format (factual/comparative/exploratory)
2. STRICTLY use ONLY the sources listed above with their exact citation numbers
3. Include credibility indicators in your Sources section (High/Medium/Low based on scores)
4. Apply weighted scoring if user stated priorities in query
5. Generate 3-5 relevant follow-up questions (MANDATORY - see format below)
6. Use professional markdown formatting
7. Ensure all claims are cited from the available sources
8. Highlight any conflicts between sources transparently

SOURCES SECTION FORMAT (copy exactly from the available sources above):
## 📚 Sources

[1] Source Title - URL
Credibility: High/Medium/Low | Rationale from credibility_rationale

[2] Source Title - URL
Credibility: High/Medium/Low | Rationale from credibility_rationale

... (continue for all sources)

FOLLOW-UP QUESTIONS FORMAT (MANDATORY - must appear after Sources):
## 💡 Follow-up Questions:

1. [Deeper dive question related to findings]
2. [Practical next steps or implementation question]
3. [Alternative options or comparative question]
4. [Clarification or specification question]
5. [Future-oriented or trending question]

🚨 CRITICAL: Your report MUST include BOTH the Sources section AND the Follow-up Questions section!

Remember: You are the final voice to the user. Transform this data into actionable insights while STRICTLY adhering to the provided sources!"""

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
