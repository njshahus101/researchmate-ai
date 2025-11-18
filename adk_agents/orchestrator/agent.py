"""
Research Orchestrator Agent - FIXED PIPELINE Implementation

This agent coordinates the research pipeline using a DETERMINISTIC FIXED PIPELINE:
1. ALWAYS calls Query Classifier agent to analyze the query
2. ALWAYS calls search_web() to get URLs
3. ALWAYS calls extract/fetch tools on the URLs
4. ALWAYS calls Information Gatherer to format results
5. ALWAYS calls Content Analysis agent to assess credibility and extract facts
6. ALWAYS calls Report Generator agent to create final tailored report
7. ALWAYS validates output quality with Quality Assurance service

This eliminates the unpredictability of LLM-based tool calling by using
a fixed sequence of steps executed by Python code.
"""

import os
import sys
import json
import time
import uuid
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.genai import types

# Import research tools for FIXED PIPELINE execution
from tools.research_tools import search_web, fetch_web_content, extract_product_info, search_google_shopping

# Import observability utilities
from utils.observability import (
    get_logger,
    get_tracer,
    get_metrics,
    get_error_tracker,
    track_operation
)

# Import persistent session service for conversation history
from services.persistent_session_service import create_persistent_session_service

# Import Quality Assurance service
from services.quality_assurance import QualityAssuranceService

# Load environment variables
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Check for API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# Initialize observability
logger = get_logger("orchestrator")
tracer = get_tracer()
metrics = get_metrics()
error_tracker = get_error_tracker()

logger.info("Initializing orchestrator agent with A2A integration")

# Create retry config
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Load sub-agents
logger.info("Loading sub-agents")
sys.path.insert(0, str(Path(__file__).parent.parent / 'query_classifier'))
from adk_agents.query_classifier.agent import agent as classifier_agent

sys.path.insert(0, str(Path(__file__).parent.parent / 'information_gatherer'))
from adk_agents.information_gatherer.agent import agent as gatherer_agent

sys.path.insert(0, str(Path(__file__).parent.parent / 'content_analyzer'))
from adk_agents.content_analyzer.agent import agent as analyzer_agent

sys.path.insert(0, str(Path(__file__).parent.parent / 'report_generator'))
from adk_agents.report_generator.agent import agent as report_generator_agent

logger.info("All sub-agents loaded successfully")

# Initialize persistent session service for conversation history and user memory
session_service = create_persistent_session_service("orchestrator_sessions")
logger.info("Persistent session service initialized for conversation history")

# Initialize Quality Assurance service
qa_service = QualityAssuranceService()
logger.info("Quality Assurance service initialized for output validation")

# Create A2A tool functions
async def classify_user_query(query: str, user_id: str = "default") -> dict:
    """
    Classify a user query to determine research strategy.

    This function calls the Query Classifier agent using A2A protocol.

    Args:
        query: The user's research query
        user_id: User identifier for personalization

    Returns:
        Dictionary with classification results including query_type,
        research_strategy, complexity_score, and key_topics
    """
    logger.info("Calling Query Classifier via A2A", query_preview=query[:50], query_id=query_id if 'query_id' in locals() else None)

    # Get user context from persistent memory
    user_memory = session_service.get_user_memory(user_id)
    recent_research = user_memory.get("research_history", [])[-3:] if user_memory else []

    # Build context string
    context = f"\n\nUser ID: {user_id}"
    if user_memory and user_memory.get("preferences"):
        context += f"\nUser Preferences: {json.dumps(user_memory['preferences'])}"
    if recent_research:
        context += f"\nRecent Research: {json.dumps(recent_research)}"

    # Call classifier agent via runner (A2A)
    runner = InMemoryRunner(agent=classifier_agent)
    try:
        response = await runner.run_debug(query + context)
        logger.info("Query Classifier response received")

        # Extract response
        if isinstance(response, list) and len(response) > 0:
            last_event = response[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                response_text = last_event.content.parts[0].text
            else:
                response_text = str(last_event)
        else:
            response_text = str(response)

        # Parse JSON response with robust error handling
        cleaned_text = response_text.strip()

        # Remove markdown code blocks
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()

        # Handle duplicate JSON responses (LLM sometimes returns classification twice)
        # Find the first complete JSON object
        try:
            # Try to parse the first JSON object
            classification = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            # If parsing fails, try to extract just the first JSON object
            print(f"[A2A] Warning: JSON parsing failed, attempting to extract first valid JSON object...")

            # Find the first opening brace and matching closing brace
            start_idx = cleaned_text.find('{')
            if start_idx == -1:
                raise ValueError("No JSON object found in response")

            brace_count = 0
            end_idx = start_idx

            for i in range(start_idx, len(cleaned_text)):
                if cleaned_text[i] == '{':
                    brace_count += 1
                elif cleaned_text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break

            if brace_count != 0:
                raise ValueError("Malformed JSON - unbalanced braces")

            first_json = cleaned_text[start_idx:end_idx]
            classification = json.loads(first_json)
            print(f"[A2A] Successfully extracted first JSON object (ignored duplicate)")

        # Store in persistent memory
        session_service.store_user_memory(
            user_id,
            "research_history",
            query,
            {
                "query": query,
                "query_type": classification.get('query_type', 'unknown'),
                "topics": classification.get('key_topics', [])
            }
        )

        print(f"[A2A] Classification complete: {classification.get('query_type')} - {classification.get('research_strategy')}")
        return classification

    except Exception as e:
        print(f"[A2A ERROR] Classification failed: {e}")
        return {
            "error": str(e),
            "query_type": "unknown",
            "research_strategy": "quick-answer",
            "complexity_score": 5
        }

async def execute_with_clarification(original_query: str, clarification: str, user_id: str = "default") -> dict:
    """
    Continue pipeline execution with user-provided clarification.

    Args:
        original_query: The original user query
        clarification: Additional details/clarifications from user
        user_id: User identifier

    Returns:
        Complete research results
    """
    # Merge original query with clarification
    if clarification and clarification.strip():
        enhanced_query = f"{original_query}\n\nAdditional context: {clarification}"
        print(f"\n[CLARIFICATION] User provided additional details:")
        print(f"  {clarification}")
    else:
        enhanced_query = original_query
        print(f"\n[CLARIFICATION] No additional details provided, continuing with original query")

    # Execute pipeline with enhanced query (non-interactive mode)
    return await execute_fixed_pipeline(enhanced_query, user_id, interactive=False)


def generate_clarification_prompt(query: str, classification: dict) -> str:
    """
    Generate a clarification prompt for the user based on query classification.

    Args:
        query: Original user query
        classification: Classification results from Query Classifier

    Returns:
        Formatted clarification prompt
    """
    query_type = classification.get('query_type', 'unknown')
    complexity = classification.get('complexity_score', 5)
    strategy = classification.get('research_strategy', 'quick-answer')
    key_topics = classification.get('key_topics', [])

    clarification = f"""
Query Classification Results:
  • Type: {query_type}
  • Research Strategy: {strategy}
  • Complexity: {complexity}/10
  • Key Topics: {', '.join(key_topics) if key_topics else 'Not specified'}

Would you like to provide additional clarification or details to improve the research?

For example:
  - Specify time period (e.g., "current prices" vs "historical data")
  - Add constraints (e.g., "under $300", "from US retailers only")
  - Clarify intent (e.g., "for comparison" vs "to purchase")
  - Narrow scope (e.g., "new products only" vs "including refurbished")

Type additional details or press Enter to continue with current query.
"""
    return clarification


async def execute_fixed_pipeline(query: str, user_id: str = "default", interactive: bool = False, session_id: str = None) -> dict:
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


    # ============================================================
    # STEP 1: ALWAYS CLASSIFY QUERY
    # ============================================================
    print(f"\n[STEP 1/6] Classifying query...")
    classification = await classify_user_query(query, user_id)

    if classification.get('error'):
        print(f"[STEP 1/6] X Classification failed: {classification['error']}")
        # Use defaults if classification fails
        classification = {
            "query_type": "factual",
            "research_strategy": "quick-answer",
            "complexity_score": 5,
            "key_topics": []
        }
    else:
        print(f"[STEP 1/6] OK Classification complete")
        print(f"  Type: {classification.get('query_type')}")
        print(f"  Strategy: {classification.get('research_strategy')}")
        print(f"  Complexity: {classification.get('complexity_score')}/10")

    # ============================================================
    # STEP 1.5: CLASSIFICATION DISPLAY (NON-BLOCKING)
    # ============================================================
    # Always show classification to help users understand the query analysis
    # In ADK UI, this appears as initial response before continuing with research
    print(f"\n[INFO] Query analyzed - proceeding with research...")

    # Store classification for later use in response
    classification_summary = {
        "type": classification.get('query_type'),
        "strategy": classification.get('research_strategy'),
        "complexity": classification.get('complexity_score')
    }

    # ============================================================
    # STEP 2: SMART SEARCH STRATEGY (Google Shopping API or Web Search)
    # ============================================================
    print(f"\n[STEP 2/6] Determining search strategy...")
    # Check if this is a product price query - use Google Shopping API
    query_type = classification.get('query_type', '').lower()
    is_price_query = 'price' in query_type or 'product' in query_type or \
                     any(word in query.lower() for word in ['price', 'cost', 'buy', 'purchase', 'best deal'])

    google_shopping_data = []
    search_result = {'status': 'pending', 'urls': []}

    if is_price_query:
        print(f"[STEP 2/6] Detected price query - using Google Shopping API...")
        shopping_result = search_google_shopping(query, num_results=5)

        if shopping_result.get('status') == 'success':
            print(f"[STEP 2/6] OK Google Shopping API returned {shopping_result.get('num_results', 0)} results")
            google_shopping_data = shopping_result.get('results', [])

            # Also do regular web search as backup
            print(f"[STEP 2/6] Also searching web for additional sources...")
            search_result = search_web(query, num_results=3)
        else:
            error_msg = shopping_result.get('error_message', 'Unknown error')
            print(f"[STEP 2/6] WARN Google Shopping API failed: {error_msg}")
            print(f"[STEP 2/6] Falling back to web search...")
            search_result = search_web(query, num_results=5)
    else:
        print(f"[STEP 2/6] Using web search for general query...")
        search_result = search_web(query, num_results=5)

    if search_result.get('status') == 'success' and search_result.get('urls'):
        print(f"[STEP 2/6] OK Found {len(search_result['urls'])} URLs")
    else:
        if not google_shopping_data:  # Only warn if we don't have shopping data
            print(f"[STEP 2/6] WARN Search returned no URLs (status: {search_result.get('status')})")
            error_msg = search_result.get('error_message') or search_result.get('message', 'Unknown error')
            print(f"  Message: {error_msg}")

    # ============================================================
    # STEP 3: FETCH DATA (Google Shopping + URLs)
    # ============================================================
    print(f"\n[STEP 3/6] Fetching data from sources...")
    fetched_data = []
    failed_urls = []

    # First, add Google Shopping results if we have them
    if google_shopping_data:
        print(f"[STEP 3/6] Adding {len(google_shopping_data)} Google Shopping results...")
        for i, shopping_item in enumerate(google_shopping_data, 1):
            fetched_data.append({
                'url': shopping_item.get('link', f'google_shopping_result_{i}'),
                'data': {
                    'status': 'success',
                    'source': 'google_shopping',
                    'product_name': shopping_item.get('product_name'),
                    'price': shopping_item.get('price'),
                    'seller': shopping_item.get('seller'),
                    'rating': shopping_item.get('rating'),
                    'review_count': shopping_item.get('review_count'),
                    'delivery': shopping_item.get('delivery'),
                },
                'source': {'title': shopping_item.get('seller', 'Google Shopping')}
            })
        print(f"[STEP 3/6] OK Added {len(google_shopping_data)} Google Shopping results")

    urls = search_result.get('urls', [])
    # Try more URLs but limit fetched data to best 3
    for i, url in enumerate(urls[:5], 1):  # Try up to 5 URLs
        try:
            # Determine if this looks like a product page
            is_product = any(domain in url for domain in ['amazon.com', 'ebay.com', 'bestbuy.com']) or \
                        any(pattern in url for pattern in ['/product', '/dp/', '/item/', '/p/'])

            if is_product:
                print(f"  [{i}/{min(len(urls), 5)}] Extracting product: {url[:60]}...")
                result = extract_product_info(url)
            else:
                print(f"  [{i}/{min(len(urls), 5)}] Fetching content: {url[:60]}...")
                result = fetch_web_content(url)

            if result.get('status') == 'success':
                # Validate that we actually got useful data
                has_content = False
                if is_product:
                    # For products, check if we got price or product name
                    has_content = result.get('price') or result.get('product_name')
                else:
                    # For general content, check if we got meaningful text
                    has_content = result.get('content') and len(result.get('content', '')) > 100

                if has_content:
                    fetched_data.append({
                        'url': url,
                        'data': result,
                        'source': search_result.get('results', [])[i-1] if i-1 < len(search_result.get('results', [])) else {}
                    })
                    print(f"  [{i}/{min(len(urls), 5)}] OK Success (useful data)")

                    # Stop if we have enough sources (including Google Shopping results)
                    total_sources = len(fetched_data)
                    if total_sources >= 8:  # Allow more if we have Google Shopping
                        print(f"  [INFO] Collected {total_sources} sources (including Google Shopping), stopping early")
                        break
                else:
                    print(f"  [{i}/{min(len(urls), 5)}] WARN Success but no useful data")
                    failed_urls.append((url, "No useful data extracted"))
            else:
                error_msg = result.get('error_message', 'Unknown error')
                print(f"  [{i}/{min(len(urls), 5)}] X Failed: {error_msg}")
                failed_urls.append((url, error_msg))

        except Exception as e:
            print(f"  [{i}/{min(len(urls), 5)}] X Exception: {str(e)[:50]}...")
            failed_urls.append((url, str(e)))
            continue

    # Report results
    if fetched_data:
        print(f"[STEP 3/6] OK Fetched data from {len(fetched_data)} sources")
    else:
        print(f"[STEP 3/6] WARN No data fetched from any source")
        if failed_urls:
            print(f"  Failed URLs ({len(failed_urls)}):")
            for url, error in failed_urls[:3]:  # Show first 3
                print(f"    - {url[:50]}... : {error[:40]}...")

    # ============================================================
    # STEP 4: ALWAYS FORMAT RESULTS
    # ============================================================
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

I'm ready to help with a refined search when you're ready!\"
"""

    # Call Information Gatherer to format
    print(f"[A2A] Calling Information Gatherer agent to format results...")
    runner = InMemoryRunner(agent=gatherer_agent)
    try:
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

        # ============================================================
        # STEP 5: ALWAYS ANALYZE CONTENT FOR CREDIBILITY
        # ============================================================
        print(f"\n[STEP 5/6] Analyzing content credibility and extracting facts...")

        # Only perform analysis if we have fetched data
        if fetched_data:
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

            except Exception as e:
                print(f"[STEP 5/6] WARN Analysis failed: {e}")
                analysis_json = {
                    "error": str(e),
                    "analysis_summary": {"note": "Content analysis failed, using unanalyzed data"}
                }

        else:
            print(f"[STEP 5/6] SKIP No data to analyze (no sources fetched)")
            analysis_json = {
                "analysis_summary": {
                    "total_sources": 0,
                    "credible_sources": 0,
                    "note": "No sources were fetched, skipping analysis"
                }
            }

        # ============================================================
        # STEP 6: ALWAYS GENERATE FINAL REPORT
        # ============================================================
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
{response_text}

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

        except Exception as e:
            print(f"[STEP 6/6] WARN Report generation failed: {e}")
            print(f"[STEP 6/6] Falling back to Information Gatherer output")
            # Fallback to the formatted information from Information Gatherer
            final_report = response_text

        # ============================================================
        # STEP 7: ALWAYS VALIDATE OUTPUT QUALITY
        # ============================================================
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

        except Exception as e:
            print(f"[STEP 7/7] WARN Quality validation failed: {e}")
            # Create a minimal quality report
            quality_report = None
            logger.warning("QA validation failed", error=str(e))

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
            "quality_report": quality_report.to_dict() if quality_report else None,  # Quality validation results
            "session_id": session_id,  # Include session ID for reference
            "intermediate_outputs": {
                "information_gatherer": response_text,  # Keep for debugging
            },
            "pipeline_steps": {
                "classification": "OK Complete",
                "search": f"OK Found {len(urls)} URLs",
                "fetch": f"OK Fetched {len(fetched_data)} sources",
                "format": "OK Complete",
                "analysis": "OK Complete" if fetched_data else "SKIP No data",
                "report": "OK Complete",
                "quality_validation": f"OK Complete (Score: {quality_report.overall_score}/100)" if quality_report else "WARN Failed"
            }
        }

    except Exception as e:
        print(f"[STEP 4/6] X Formatting failed: {e}")
        print(f"\n{'='*60}")
        print(f"PIPELINE FAILED AT FORMATTING STEP")
        print(f"{'='*60}\n")

        return {
            "status": "error",
            "error": str(e),
            "classification": classification,
            "fetched_data": fetched_data,
            "sources_fetched": len(fetched_data),
            "session_id": session_id,
            "pipeline_steps": {
                "classification": "OK Complete",
                "search": f"OK Found {len(search_result.get('urls', []))} URLs",
                "fetch": f"OK Fetched {len(fetched_data)} sources",
                "format": f"FAILED: {str(e)}",
                "analysis": "SKIP (formatting failed)",
                "report": "SKIP (formatting failed)"
            }
        }

# Create a wrapper function that ADK can call as a tool
pipeline_tool = FunctionTool(func=execute_fixed_pipeline)

# Create a SIMPLE orchestrator agent that just wraps the fixed pipeline
# This agent DOES NOT make decisions - it just calls the fixed pipeline
instruction = """You are the Orchestrator Agent for ResearchMate AI.

You have ONE tool available: execute_fixed_pipeline

[WARN] WHEN TO RUN THE PIPELINE:

1. **Initial Query**: If the user asks a research question, you can EITHER:
   - Run the pipeline immediately with the query as-is, OR
   - Ask 2-3 clarifying questions first (if the query is very broad or ambiguous)

2. **After Clarification**: If you asked clarifying questions and the user provides additional details:
   - You MUST run the pipeline with a COMBINED query that includes:
     * The original user question
     * PLUS all clarification details provided by the user
   - Build a comprehensive query string that captures everything

3. **Follow-up After Research**: If the pipeline already ran and user asks a new follow-up question:
   - Run the pipeline AGAIN with the new context included

📋 HOW TO COMBINE CONTEXT:

When user provides clarifications, create a detailed query like:
"[Original Question]. Additional context: [User's clarification details]"

Example:
- Original: "Help me with astrophotography setup"
- User clarifies: "Budget $5000, need portability, dark site, no visual observing"
- Combined query to pipeline: "Help me with astrophotography setup for galaxy imaging. Requirements: budget around $5000, must be portable and quick to set up, will observe from dark sites, experienced with telescopes but new to astrophotography, setup does not need to be good for visual observing, only imaging."

The fixed pipeline will AUTOMATICALLY execute all research steps in order:
1. Classify the query
2. Search the web
3. Fetch data from URLs
4. Format results
5. Analyze content credibility and extract facts
6. Generate final tailored report with citations and follow-up questions

🎯 CRITICAL RULES:

1. When calling execute_fixed_pipeline, pass:
   - query: the user's query (original OR combined with clarifications)
   - user_id: "default" (or extract from context if available)

2. ALWAYS run the FULL pipeline from the beginning when you have clarifications
   - Do NOT try to resume from a previous step
   - The pipeline is stateless - each run is fresh with new search results

3. [WARN][WARN][WARN] AFTER THE PIPELINE RETURNS - CRITICAL PASS-THROUGH RULE [WARN][WARN][WARN]

When execute_fixed_pipeline returns a result with "content" field:

🚨 YOU MUST OUTPUT THE EXACT CONTENT STRING WITH ZERO MODIFICATIONS 🚨

The report is ALREADY PERFECTLY FORMATTED by the Report Generator agent.
It ALREADY has:
- Professional markdown formatting
- Inline citations [1], [2], [3]
- ### Sources section with URLs
- Credibility indicators
- Follow-up Questions section

DO NOT:
[FAIL] Summarize or paraphrase the content
[FAIL] Add your own introduction or commentary
[FAIL] Remove ANY sections (especially "### Sources" or "Follow-up Questions")
[FAIL] Reformat the markdown structure
[FAIL] Change headings or organization
[FAIL] Add your own recommendations or thoughts
[FAIL] "Improve" or "clean up" the formatting

[OK] DO: Copy and paste the 'content' field character-for-character

If the pipeline returns:
{
  "status": "success",
  "content": "## Astrophotography Setup\n\n...recommendations...\n\n### Sources\n[1] Amazon...\n\n**Follow-up Questions:**\n- Question 1\n- Question 2"
}

You MUST output ONLY that exact content string. Nothing more, nothing less.

🚨 WARNING: If you modify, summarize, or remove sections like "### Sources", the user will NOT be able to verify the information sources, making the entire research worthless!

📝 EXAMPLES:

Example 1 - Direct execution:
User: "Fetch current price of Sony WH-1000XM5"
You: [Call execute_fixed_pipeline(query="Fetch current price of Sony WH-1000XM5", user_id="default")]
Pipeline returns: {"status": "success", "content": "## Current Price...### Sources\n[1] Amazon..."}
You output to user: [EXACT content from pipeline, including the ### Sources section]

Example 2 - Ask clarifications first:
User: "I need help with astrophotography"
You: [Ask 2-3 clarifying questions about budget, experience, targets, etc.]
User: "Budget $5000, want to image galaxies, need portability"
You: [Call execute_fixed_pipeline(query="Astrophotography setup for galaxy imaging. Budget: $5000, requirement: portable setup, user experienced with telescopes but new to astrophotography", user_id="default")]
Pipeline returns: {"status": "success", "content": "## Astrophotography Setup\n\n...recommendations...\n\n### Sources\n[1] CNET...\n\n**Follow-up Questions:**..."}
You output to user: [EXACT content from pipeline - do NOT summarize, do NOT remove Sources section, do NOT add your own thoughts]

Example 3 - What NOT to do (WRONG):
Pipeline returns: "...recommendations...\n\n### Sources\n[1] Amazon - https://..."
[FAIL] WRONG: "Here's what I found: [summarized recommendations]. You might want to check Amazon."
[OK] CORRECT: [Output the exact content including ### Sources section with full URLs]

═══════════════════════════════════════════════════════════════════════════
📤 OUTPUT FORMAT AFTER PIPELINE COMPLETES
═══════════════════════════════════════════════════════════════════════════

After execute_fixed_pipeline returns, your response to the user MUST be:

result['content']

That's it. Literally just output the value of the 'content' field from the pipeline result.

DO NOT write:
- "Here's what I found:"
- "Based on the research:"
- "I've compiled the following:"
- Any introduction, summary, or commentary

DO write:
[The exact content string from pipeline result, verbatim]

Your output should start with the FIRST CHARACTER of result['content'] and end with the LAST CHARACTER of result['content'].

No prefix. No suffix. No modification. Just the content."""

agent = LlmAgent(
    name="research_orchestrator",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Fixed pipeline orchestrator - executes deterministic research workflow",
    instruction=instruction,
    tools=[pipeline_tool],
)

print(f"Agent '{agent.name}' initialized successfully with FIXED PIPELINE")
print("  - Query Classifier agent loaded")
print("  - Information Gatherer agent loaded")
print("  - Content Analysis agent loaded")
print("  - Report Generator agent loaded")
print("  - Fixed pipeline: Classify -> Search -> Fetch -> Format -> Analyze -> Report")
print("  - No LLM decision-making - deterministic execution")
print("Ready for ADK Web UI")

# ADK Web UI looks for 'root_agent' variable
root_agent = agent
