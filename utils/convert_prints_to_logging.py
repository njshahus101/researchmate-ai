"""
Script to convert print statements to structured logging in orchestrator agent.
"""

import re

def convert_prints_to_logging(file_path):
    """Convert print statements to structured logging."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        # A2A messages
        (r'print\(f"\[A2A\] Calling Query Classifier for: \{query\[:50\]\}\.\.\."\)',
         'logger.info("Calling Query Classifier via A2A", query_preview=query[:50])'),

        (r'print\(f"\[A2A\] Query Classifier response received"\)',
         'logger.info("Query Classifier response received")'),

        (r'print\(f"\[A2A\] Warning: JSON parsing failed, attempting to extract first valid JSON object\.\.\."\)',
         'logger.warning("JSON parsing failed, extracting first valid JSON object")'),

        (r'print\(f"\[A2A\] Successfully extracted first JSON object \(ignored duplicate\)"\)',
         'logger.debug("Successfully extracted first JSON object, ignored duplicate")'),

        (r'print\(f"\[A2A\] Classification complete: \{classification\.get\(\'query_type\'\)\} - \{classification\.get\(\'research_strategy\'\)\}"\)',
         'logger.info("Classification complete", query_type=classification.get("query_type"), research_strategy=classification.get("research_strategy"))'),

        (r'print\(f"\[A2A ERROR\] Classification failed: \{e\}"\)',
         'logger.error("Classification failed", error=str(e))'),

        (r'print\(f"\[A2A\] Calling Information Gatherer agent to format results\.\.\."\)',
         'logger.info("Calling Information Gatherer agent to format results")'),

        (r'print\(f"\[A2A\] Information Gatherer response received"\)',
         'logger.info("Information Gatherer response received")'),

        (r'print\(f"\[A2A\] Calling Content Analysis agent\.\.\."\)',
         'logger.info("Calling Content Analysis agent")'),

        (r'print\(f"\[A2A\] Content Analysis response received"\)',
         'logger.info("Content Analysis response received")'),

        (r'print\(f"\[A2A\] Calling Report Generator agent\.\.\."\)',
         'logger.info("Calling Report Generator agent")'),

        (r'print\(f"\[A2A\] Report Generator response received"\)',
         'logger.info("Report Generator response received")'),

        # CLARIFICATION messages
        (r'print\(f"\\n\[CLARIFICATION\] User provided additional details:"\)',
         'logger.info("User provided clarification details")'),

        (r'print\(f"  \{clarification\}"\)',
         'logger.debug("Clarification", details=clarification)'),

        (r'print\(f"\\n\[CLARIFICATION\] No additional details provided, continuing with original query"\)',
         'logger.info("No clarification provided, continuing with original query")'),

        # STEP messages - replace specific patterns
        (r'print\(f"\\n\[STEP 1/6\] Classifying query\.\.\."\)',
         'logger.info("Step 1/6: Classifying query", step="classify")'),

        (r'print\(f"\[STEP 1/6\] X Classification failed: \{classification\[\'error\'\]\}"\)',
         'logger.error("Step 1/6: Classification failed", error=classification["error"])'),

        (r'print\(f"\[STEP 1/6\] OK Classification complete"\)',
         'logger.info("Step 1/6: Classification complete")'),

        # STEP 2
        (r'print\(f"\\n\[STEP 2/6\] Determining search strategy\.\.\."\)',
         'logger.info("Step 2/6: Determining search strategy", step="search")'),

        (r'print\(f"\[STEP 2/6\] Detected price query - using Google Shopping API\.\.\."\)',
         'logger.info("Detected price query, using Google Shopping API")'),

        (r'print\(f"\[STEP 2/6\] OK Google Shopping API returned \{shopping_result\.get\(\'num_results\', 0\)\} results"\)',
         'logger.info("Google Shopping API returned results", num_results=shopping_result.get("num_results", 0))'),

        (r'print\(f"\[STEP 2/6\] Also searching web for additional sources\.\.\."\)',
         'logger.info("Also searching web for additional sources")'),

        (r'print\(f"\[STEP 2/6\] WARN Google Shopping API failed: \{error_msg\}"\)',
         'logger.warning("Google Shopping API failed", error=error_msg)'),

        (r'print\(f"\[STEP 2/6\] Falling back to web search\.\.\."\)',
         'logger.info("Falling back to web search")'),

        (r'print\(f"\[STEP 2/6\] Using web search for general query\.\.\."\)',
         'logger.info("Using web search for general query")'),

        (r'print\(f"\[STEP 2/6\] OK Found \{len\(search_result\[\'urls\'\]\)\} URLs"\)',
         'logger.info("Found URLs", url_count=len(search_result["urls"]))'),

        (r'print\(f"\[STEP 2/6\] WARN Search returned no URLs \(status: \{search_result\.get\(\'status\'\)\}\)"\)',
         'logger.warning("Search returned no URLs", status=search_result.get("status"))'),

        # STEP 3
        (r'print\(f"\\n\[STEP 3/6\] Fetching data from sources\.\.\."\)',
         'logger.info("Step 3/6: Fetching data from sources", step="fetch")'),

        (r'print\(f"\[STEP 3/6\] Adding \{len\(google_shopping_data\)\} Google Shopping results\.\.\."\)',
         'logger.info("Adding Google Shopping results", count=len(google_shopping_data))'),

        (r'print\(f"\[STEP 3/6\] OK Added \{len\(google_shopping_data\)\} Google Shopping results"\)',
         'logger.info("Added Google Shopping results", count=len(google_shopping_data))'),

        (r'print\(f"\[STEP 3/6\] OK Fetched data from \{len\(fetched_data\)\} sources"\)',
         'logger.info("Fetched data from sources", source_count=len(fetched_data))'),

        (r'print\(f"\[STEP 3/6\] WARN No data fetched from any source"\)',
         'logger.warning("No data fetched from any source")'),

        # STEP 4
        (r'print\(f"\\n\[STEP 4/6\] Formatting results with Information Gatherer\.\.\."\)',
         'logger.info("Step 4/6: Formatting results with Information Gatherer", step="format")'),

        (r'print\(f"\[STEP 4/6\] OK Formatting complete"\)',
         'logger.info("Step 4/6: Formatting complete")'),

        (r'print\(f"\[STEP 4/6\] X Formatting failed: \{e\}"\)',
         'logger.error("Step 4/6: Formatting failed", error=str(e))'),

        # STEP 5
        (r'print\(f"\\n\[STEP 5/6\] Analyzing content credibility and extracting facts\.\.\."\)',
         'logger.info("Step 5/6: Analyzing content credibility", step="analyze")'),

        (r'print\(f"\[STEP 5/6\] WARN Analysis failed: \{e\}"\)',
         'logger.warning("Step 5/6: Analysis failed", error=str(e))'),

        (r'print\(f"\[STEP 5/6\] SKIP No data to analyze \(no sources fetched\)"\)',
         'logger.info("Step 5/6: Skipping analysis, no sources fetched")'),

        # STEP 6
        (r'print\(f"\\n\[STEP 6/6\] Generating final report with Report Generator\.\.\."\)',
         'logger.info("Step 6/6: Generating final report", step="report")'),

        (r'print\(f"\[STEP 6/6\] OK Report generation complete"\)',
         'logger.info("Step 6/6: Report generation complete")'),

        (r'print\(f"\[STEP 6/6\] WARN Report generation failed: \{e\}"\)',
         'logger.warning("Step 6/6: Report generation failed", error=str(e))'),

        (r'print\(f"\[STEP 6/6\] Falling back to Information Gatherer output"\)',
         'logger.info("Falling back to Information Gatherer output")'),

        # Pipeline completion messages
        (r'print\(f"\\n\{\'=\'\*60\}"\)\s*\n\s*print\(f"PIPELINE COMPLETE"\)\s*\n\s*print\(f"\{\'=\'\*60\}\\n"\)',
         'logger.info("Pipeline execution complete", duration_seconds=time.time() - pipeline_start_time)'),

        (r'print\(f"\\n\{\'=\'\*60\}"\)\s*\n\s*print\(f"PIPELINE FAILED AT FORMATTING STEP"\)\s*\n\s*print\(f"\{\'=\'\*60\}\\n"\)',
         'logger.error("Pipeline failed at formatting step")'),

        # INFO messages
        (r'print\(f"\\n\[INFO\] Query analyzed - proceeding with research\.\.\."\)',
         'logger.info("Query analyzed, proceeding with research")'),

        # Agent initialization messages at end of file
        (r'print\(f"Agent \'\{agent\.name\}\' initialized successfully with FIXED PIPELINE"\)',
         'logger.info("Agent initialized successfully", agent_name=agent.name, pipeline_type="FIXED")'),

        (r'print\("  - Query Classifier agent loaded"\)',
         '# Logged earlier'),

        (r'print\("  - Information Gatherer agent loaded"\)',
         '# Logged earlier'),

        (r'print\("  - Content Analysis agent loaded"\)',
         '# Logged earlier'),

        (r'print\("  - Report Generator agent loaded"\)',
         '# Logged earlier'),

        (r'print\("  - Fixed pipeline: Classify -> Search -> Fetch -> Format -> Analyze -> Report"\)',
         'logger.info("Fixed pipeline initialized", steps="Classify->Search->Fetch->Format->Analyze->Report")'),

        (r'print\("  - No LLM decision-making - deterministic execution"\)',
         'logger.info("Pipeline mode", mode="deterministic", llm_decisions=False)'),

        (r'print\("Ready for ADK Web UI"\)',
         'logger.info("Agent ready for ADK Web UI")'),
    ]

    # Apply all replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Converted print statements to logging in {file_path}")

if __name__ == "__main__":
    file_path = r"C:\Users\niravkumarshah\Downloads\researchmate-ai\adk_agents\orchestrator\agent.py"
    convert_prints_to_logging(file_path)
    print("Conversion complete!")
