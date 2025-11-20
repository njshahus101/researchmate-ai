"""
Step 6.5: Citation Formatting (Post-Processing)

This module enforces proper citation format after Report Generator creates the content.
It ensures citations match the structured source data exactly, preventing hallucination
and improving quality scores.
"""

import re
from typing import List, Dict, Tuple


def format_citations(
    report: str,
    source_credibility: List[Dict],
    fetched_data: List[Dict] = None
) -> str:
    """
    Post-process the report to ensure proper citation format.

    This function:
    1. Ensures Sources section has proper numbering [1], [2], [3]
    2. Adds credibility indicators (High/Medium/Low)
    3. Matches sources from analysis_json exactly
    4. Removes any hallucinated sources

    Args:
        report: Raw report from Report Generator
        source_credibility: Structured source list from Content Analyzer
        fetched_data: Fallback if source_credibility is empty

    Returns:
        Formatted report with correct citations
    """
    print(f"[POST-PROCESS] Enforcing citation format...")

    # Fallback: Build source list from fetched_data if needed
    if not source_credibility and fetched_data:
        print(f"[POST-PROCESS] Building source list from fetched_data")
        source_credibility = []
        for source in fetched_data:
            source_credibility.append({
                'url': source.get('url', ''),
                'title': source.get('title', source.get('url', 'Unknown Source')),
                'credibility_score': 70,
                'credibility_rationale': 'Source fetched but not analyzed'
            })

    if not source_credibility:
        print(f"[POST-PROCESS] WARN No sources available, skipping formatting")
        return report

    # Extract the main content (everything before Sources section)
    sources_match = re.search(r'#+\s*(?:📚\s*)?Sources?', report, re.MULTILINE | re.IGNORECASE)

    if sources_match:
        # Split at Sources section
        main_content = report[:sources_match.start()].rstrip()
        # Remove everything after Sources heading (we'll rebuild it)
        print(f"[POST-PROCESS] Found existing Sources section at position {sources_match.start()}")
    else:
        # No Sources section found - check for Follow-up Questions and extract main content before it
        followup_match_temp = re.search(r'#+\s*(?:💡\s*)?Follow[-\s]?up Questions?', report, re.MULTILINE | re.IGNORECASE)
        if followup_match_temp:
            main_content = report[:followup_match_temp.start()].rstrip()
            print(f"[POST-PROCESS] No Sources section found, but found Follow-up Questions")
        else:
            main_content = report.rstrip()
            print(f"[POST-PROCESS] No Sources or Follow-up Questions section found - will append")

    # Extract Follow-up Questions section if it exists (can be before or after Sources in original)
    # Look for "Follow-up Questions" with or without heading markers, and capture everything after it
    followup_match = re.search(
        r'(?:^|\n)((?:#+\s*)?(?:💡\s*)?Follow[-\s]?up Questions?:?\s*\n.+)',
        report,
        re.MULTILINE | re.IGNORECASE | re.DOTALL
    )

    followup_section = ""
    if followup_match:
        # Extract the entire Follow-up Questions section including content
        followup_text = followup_match.group(1).strip()
        # Ensure it has proper heading format if it doesn't already
        if not followup_text.startswith('#'):
            followup_section = "\n\n## 💡 Follow-up Questions:\n\n" + re.sub(r'^(?:💡\s*)?Follow[-\s]?up Questions?:?\s*\n?', '', followup_text, flags=re.IGNORECASE)
        else:
            followup_section = "\n\n" + followup_text
        print(f"[POST-PROCESS] Preserved Follow-up Questions section ({len(followup_text)} chars)")

    # Build properly formatted Sources section
    sources_section = "\n\n## 📚 Sources\n\n"

    for i, source_info in enumerate(source_credibility, start=1):
        url = source_info.get('url', 'N/A')
        title = source_info.get('title', f'Source {i}')
        credibility_score = source_info.get('credibility_score', 70)
        credibility_rationale = source_info.get('credibility_rationale', '')

        # Determine credibility level
        if credibility_score >= 80:
            credibility_level = "High"
        elif credibility_score >= 60:
            credibility_level = "Medium"
        else:
            credibility_level = "Low"

        # Format: [1] Title - URL
        sources_section += f"[{i}] {title} - {url}\n"

        # Add credibility with rationale
        if credibility_rationale:
            sources_section += f"Credibility: {credibility_level} | {credibility_rationale}\n"
        else:
            sources_section += f"Credibility: {credibility_level}\n"

        sources_section += "\n"

    # Reconstruct report: main content + formatted sources + follow-up questions
    formatted_report = main_content + sources_section

    if followup_section:
        formatted_report += followup_section

    print(f"[POST-PROCESS] OK Citation formatting complete - {len(source_credibility)} sources")
    return formatted_report


def validate_and_clean_citations(report: str, max_citation: int) -> str:
    """
    Validate that all citations in the text are within valid range.
    Remove any citations that exceed the number of available sources.

    Args:
        report: The report text
        max_citation: Maximum valid citation number

    Returns:
        Cleaned report with only valid citations
    """
    # Find all citations [1], [2], etc.
    citations = re.findall(r'\[(\d+)\]', report)
    invalid_citations = [c for c in citations if int(c) > max_citation]

    if invalid_citations:
        print(f"[POST-PROCESS] WARN Found invalid citations: {invalid_citations}")
        print(f"[POST-PROCESS] Valid range: [1-{max_citation}]")

        # Remove invalid citations from text
        for invalid in set(invalid_citations):
            # Only remove if it's clearly a citation (not in a URL or code block)
            report = re.sub(rf'(?<!\w)\[{invalid}\](?!\w)', '', report)

        print(f"[POST-PROCESS] Removed invalid citations")

    return report
