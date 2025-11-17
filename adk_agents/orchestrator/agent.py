"""
Research Orchestrator Agent - FIXED PIPELINE Implementation

This agent coordinates the research pipeline using a DETERMINISTIC FIXED PIPELINE:
1. ALWAYS calls Query Classifier agent to analyze the query
2. ALWAYS calls search_web() to get URLs
3. ALWAYS calls extract/fetch tools on the URLs
4. ALWAYS calls Information Gatherer to format results

This eliminates the unpredictability of LLM-based tool calling by using
a fixed sequence of steps executed by Python code.
"""

import os
import sys
import json
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
from tools.research_tools import search_web, fetch_web_content, extract_product_info

# Load environment variables
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Check for API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

print("Initializing orchestrator agent with A2A integration...")

# Create retry config
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Load sub-agents
print("  Loading Query Classifier agent...")
sys.path.insert(0, str(Path(__file__).parent.parent / 'query_classifier'))
from adk_agents.query_classifier.agent import agent as classifier_agent

print("  Loading Information Gatherer agent...")
sys.path.insert(0, str(Path(__file__).parent.parent / 'information_gatherer'))
from adk_agents.information_gatherer.agent import agent as gatherer_agent

# Initialize memory service (simplified version for ADK UI)
class SimpleMemoryService:
    """Simplified memory service for ADK UI context"""
    def __init__(self):
        self.user_memories = {}
        self.research_history = {}

    def get_user_memory(self, user_id: str) -> dict:
        return self.user_memories.get(user_id, {})

    def get_recent_research(self, user_id: str, limit: int = 3) -> list:
        history = self.research_history.get(user_id, [])
        return history[-limit:] if history else []

    def add_research_entry(self, user_id: str, query: str, query_type: str, topics: list):
        if user_id not in self.research_history:
            self.research_history[user_id] = []
        self.research_history[user_id].append({
            "query": query,
            "query_type": query_type,
            "topics": topics
        })

memory_service = SimpleMemoryService()

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
    print(f"\n[A2A] Calling Query Classifier for: {query[:50]}...")

    # Get user context from memory
    user_memory = memory_service.get_user_memory(user_id)
    recent_research = memory_service.get_recent_research(user_id, limit=3)

    # Build context string
    context = f"\n\nUser ID: {user_id}"
    if user_memory.get("preferences"):
        context += f"\nUser Preferences: {json.dumps(user_memory['preferences'])}"
    if recent_research:
        context += f"\nRecent Research: {json.dumps(recent_research)}"

    # Call classifier agent via runner (A2A)
    runner = InMemoryRunner(agent=classifier_agent)
    try:
        response = await runner.run_debug(query + context)
        print(f"[A2A] Query Classifier response received")

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

        # Store in memory
        memory_service.add_research_entry(
            user_id,
            query,
            classification.get('query_type', 'unknown'),
            classification.get('key_topics', [])
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

async def execute_fixed_pipeline(query: str, user_id: str = "default") -> dict:
    """
    FIXED PIPELINE: Executes research in a deterministic order.

    This function ALWAYS executes ALL steps in sequence - no LLM decisions:

    STEP 1: Classify query
    STEP 2: Search web for URLs
    STEP 3: Extract data from URLs
    STEP 4: Format results

    Args:
        query: The user's research query
        user_id: User identifier for personalization

    Returns:
        Dictionary with complete research results
    """
    print(f"\n{'='*60}")
    print(f"FIXED PIPELINE EXECUTION")
    print(f"Query: {query}")
    print(f"{'='*60}")

    # ============================================================
    # STEP 1: ALWAYS CLASSIFY QUERY
    # ============================================================
    print(f"\n[STEP 1/4] Classifying query...")
    classification = await classify_user_query(query, user_id)

    if classification.get('error'):
        print(f"[STEP 1/4] X Classification failed: {classification['error']}")
        # Use defaults if classification fails
        classification = {
            "query_type": "factual",
            "research_strategy": "quick-answer",
            "complexity_score": 5,
            "key_topics": []
        }
    else:
        print(f"[STEP 1/4] OK Classification complete")
        print(f"  Type: {classification.get('query_type')}")
        print(f"  Strategy: {classification.get('research_strategy')}")
        print(f"  Complexity: {classification.get('complexity_score')}/10")

    # ============================================================
    # STEP 2: ALWAYS SEARCH WEB
    # ============================================================
    print(f"\n[STEP 2/4] Searching web for URLs...")

    # Try with more results to increase success rate
    search_result = search_web(query, num_results=5)

    if search_result.get('status') == 'success' and search_result.get('urls'):
        print(f"[STEP 2/4] OK Found {len(search_result['urls'])} URLs")
    else:
        print(f"[STEP 2/4] WARN Search returned no URLs (status: {search_result.get('status')})")
        error_msg = search_result.get('error_message') or search_result.get('message', 'Unknown error')
        print(f"  Message: {error_msg}")

        # If search fails, try reformulating the query (query enhancement)
        if 'error' in search_result.get('status', ''):
            print(f"[STEP 2/4] Attempting query reformulation...")
            # Try adding more context to the query
            enhanced_query = f"{query} product review price"
            print(f"  Enhanced query: {enhanced_query}")
            search_result = search_web(enhanced_query, num_results=5)

            if search_result.get('status') == 'success' and search_result.get('urls'):
                print(f"[STEP 2/4] OK Reformulated query found {len(search_result['urls'])} URLs")
            else:
                print(f"[STEP 2/4] WARN Reformulated query also failed")

    # ============================================================
    # STEP 3: ALWAYS FETCH DATA FROM URLs
    # ============================================================
    print(f"\n[STEP 3/4] Fetching data from URLs...")
    fetched_data = []
    failed_urls = []

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

                    # Stop if we have 3 good sources
                    if len(fetched_data) >= 3:
                        print(f"  [INFO] Collected 3 good sources, stopping early")
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
        print(f"[STEP 3/4] OK Fetched data from {len(fetched_data)} sources")
    else:
        print(f"[STEP 3/4] WARN No data fetched from any source")
        if failed_urls:
            print(f"  Failed URLs ({len(failed_urls)}):")
            for url, error in failed_urls[:3]:  # Show first 3
                print(f"    - {url[:50]}... : {error[:40]}...")

    # ============================================================
    # STEP 4: ALWAYS FORMAT RESULTS
    # ============================================================
    print(f"\n[STEP 4/4] Formatting results with Information Gatherer...")

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

        print(f"[STEP 4/4] OK Formatting complete")
        print(f"\n{'='*60}")
        print(f"PIPELINE COMPLETE")
        print(f"{'='*60}\n")

        return {
            "status": "success",
            "content": response_text,
            "classification": classification,
            "sources_fetched": len(fetched_data),
            "pipeline_steps": {
                "classification": "OK Complete",
                "search": f"OK Found {len(urls)} URLs",
                "fetch": f"OK Fetched {len(fetched_data)} sources",
                "format": "OK Complete"
            }
        }

    except Exception as e:
        print(f"[STEP 4/4] X Formatting failed: {e}")
        print(f"\n{'='*60}")
        print(f"PIPELINE FAILED")
        print(f"{'='*60}\n")

        return {
            "status": "error",
            "error": str(e),
            "classification": classification,
            "fetched_data": fetched_data,
            "sources_fetched": len(fetched_data)
        }

# Create a wrapper function that ADK can call as a tool
pipeline_tool = FunctionTool(func=execute_fixed_pipeline)

# Create a SIMPLE orchestrator agent that just wraps the fixed pipeline
# This agent DOES NOT make decisions - it just calls the fixed pipeline
instruction = """You are the Orchestrator Agent for ResearchMate AI.

You have ONE tool available: execute_fixed_pipeline

For EVERY user query, you MUST call execute_fixed_pipeline with:
- query: the user's exact query text
- user_id: "default" (or extract from context if available)

The fixed pipeline will AUTOMATICALLY execute all research steps in order:
1. Classify the query
2. Search the web
3. Fetch data from URLs
4. Format and return results

You do NOT need to make any decisions. Just call the pipeline and present the results.

Example:
User: "Fetch current price of Sony WH-1000XM5"

You should immediately call:
execute_fixed_pipeline(query="Fetch current price of Sony WH-1000XM5", user_id="default")

Then present the returned results to the user."""

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
print("  - Fixed pipeline: Classify -> Search -> Fetch -> Format")
print("  - No LLM decision-making - deterministic execution")
print("Ready for ADK Web UI")

# ADK Web UI looks for 'root_agent' variable
root_agent = agent
