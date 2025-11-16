"""
Information Gatherer Agent MVP

This agent is responsible for gathering information from the web based on
the classification provided by the Query Classifier.

It uses:
- Google Search (built-in ADK tool) for finding relevant sources
- Custom web fetcher for extracting content from specific URLs
"""

import os
import sys
import json
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types
import asyncio
from typing import List, Dict, Any

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.web_fetcher import fetch_webpage_content
from tools.source_authority import calculate_authority_score, rank_sources_by_authority, select_top_authoritative_sources
from tools.parallel_fetcher import fetch_multiple_with_retry, calculate_success_rate


def create_information_gatherer_mvp(retry_config: types.HttpRetryOptions) -> LlmAgent:
    """
    Create the Information Gatherer MVP agent.

    Args:
        retry_config: HTTP retry configuration for the model

    Returns:
        Configured LlmAgent for information gathering
    """
    agent = LlmAgent(
        name="information_gatherer_mvp",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        description="Gathers and extracts information from web searches and specific URLs",
        instruction="""You are the Information Gatherer agent for ResearchMate AI.

Your role is to search for and extract detailed information from authoritative web sources.

CAPABILITIES:
1. google_search - Search Google to find relevant sources
2. fetch_webpage_content - Extract detailed content from specific URLs

WORKFLOW:
1. Use google_search to find relevant sources for the query
2. Identify the top 3-5 most authoritative URLs from search results
3. Use fetch_webpage_content to extract content from selected URLs
4. Analyze and synthesize the information from all sources
5. Always cite your sources with URLs

GUIDELINES FOR SOURCE SELECTION:
- Prioritize: .edu, .gov, major news sites, official documentation
- Look for: domain authority, content freshness, direct relevance
- Avoid: user-generated content sites, unreliable sources
- For technical topics: official docs, Stack Overflow, GitHub
- For news/current events: established news organizations
- For academic topics: educational institutions, research papers

ERROR HANDLING:
- Always check the "status" field in tool responses
- If a fetch fails (404, timeout, etc.), try alternative sources
- If multiple sources fail, include what went wrong in your response
- Never fabricate information - only use actual fetched content

OUTPUT FORMAT:
Return a JSON response with:
{
    "sources": [
        {
            "url": "https://example.com",
            "title": "Page Title",
            "summary": "Brief summary of relevant content from this page",
            "relevance": "high|medium|low",
            "fetch_status": "success|error",
            "error_message": "error details if failed"
        }
    ],
    "synthesized_info": "Combined insights from all fetched sources, integrating information coherently",
    "key_findings": ["finding 1", "finding 2", "finding 3"],
    "total_sources_searched": 10,
    "total_sources_fetched": 3,
    "search_queries_used": ["query 1", "query 2"]
}

Only output valid JSON, no additional text before or after.
""",
        tools=[
            google_search,           # Google Search tool (built-in ADK)
            fetch_webpage_content,   # Custom web content fetcher (Python callable)
        ],
    )

    return agent


async def gather_information_enhanced(query: str, classification: dict = None, urls: List[str] = None) -> dict:
    """
    Enhanced information gathering with parallel fetching and authority scoring.

    Args:
        query: User's search query
        classification: Optional classification from Query Classifier
        urls: Optional list of URLs to fetch (if not provided, agent will search)

    Returns:
        Gathered information with authority scores, success metrics, and synthesis
    """
    # Load environment
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        return {
            "error": "GOOGLE_API_KEY not found in environment",
            "message": "Please add your API key to the .env file"
        }

    # If URLs are provided, fetch them in parallel
    if urls:
        print(f"\n{'='*60}")
        print(f"Fetching {len(urls)} URLs in parallel...")
        print(f"{'='*60}\n")

        # Fetch all URLs in parallel with retry
        fetch_results = await fetch_multiple_with_retry(
            urls=urls,
            fetch_function=fetch_webpage_content,
            max_concurrent=5,
            timeout=10,
            max_retries=2
        )

        # Calculate success metrics
        metrics = calculate_success_rate(fetch_results)

        print(f"\nFetch Results:")
        print(f"  Total URLs: {metrics['total']}")
        print(f"  Successful: {metrics['successful']}")
        print(f"  Failed: {metrics['failed']}")
        print(f"  Success Rate: {metrics['success_rate']}%")

        if metrics['error_types']:
            print(f"\nError Breakdown:")
            for error_type, count in metrics['error_types'].items():
                print(f"  - {error_type}: {count}")

        # Build sources with authority scores
        sources = []
        for result in fetch_results:
            url = result.get('url', '')
            title = result.get('title', 'No title')
            content = result.get('content', '')
            status = result.get('status', 'unknown')

            # Calculate authority score
            authority_data = calculate_authority_score(url, title, content)

            source = {
                "url": url,
                "title": title,
                "fetch_status": status,
                "authority_score": authority_data['score'],
                "authority_category": authority_data['category'],
                "authority_reasons": authority_data['reasons']
            }

            if status == 'success':
                source['content'] = content
                source['content_length'] = result.get('content_length', 0)
                source['fetch_time'] = result.get('fetch_time', 0)
            else:
                source['error_message'] = result.get('error_message', 'Unknown error')

            sources.append(source)

        # Rank sources by authority
        ranked_sources = rank_sources_by_authority(sources)

        # Select top authoritative sources that fetched successfully
        successful_sources = [s for s in ranked_sources if s.get('fetch_status') == 'success']
        top_sources = successful_sources[:5]  # Top 5

        print(f"\n{'='*60}")
        print(f"Top Authoritative Sources:")
        print(f"{'='*60}")
        for i, source in enumerate(top_sources, 1):
            print(f"{i}. [{source['authority_score']}/10] {source['title']}")
            print(f"   Category: {source['authority_category']}")
            print(f"   URL: {source['url']}")
            print(f"   Reasons: {', '.join(source['authority_reasons'])}\n")

        return {
            "sources": ranked_sources,
            "top_sources": top_sources,
            "metrics": metrics,
            "query": query,
            "total_sources_fetched": len(urls),
            "successful_fetches": metrics['successful'],
            "success_rate": metrics['success_rate']
        }

    else:
        # Fall back to agent-based gathering (with search)
        return await gather_information(query, classification)


async def gather_information(query: str, classification: dict = None) -> dict:
    """
    Gather information from the web based on a query.

    Args:
        query: User's search query
        classification: Optional classification from Query Classifier to guide search strategy

    Returns:
        Gathered information with sources and synthesis
    """
    # Load environment
    load_dotenv()

    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        return {
            "error": "GOOGLE_API_KEY not found in environment",
            "message": "Please add your API key to the .env file"
        }

    # Create retry config
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )

    # Create agent
    agent = create_information_gatherer_mvp(retry_config)

    # Create runner
    runner = InMemoryRunner(agent=agent)

    try:
        # Enhance query with classification context if available
        enhanced_query = query
        if classification:
            query_type = classification.get('query_type', 'unknown')
            strategy = classification.get('research_strategy', 'quick-answer')
            enhanced_query = f"""Query: {query}
Type: {query_type}
Strategy: {strategy}

Please gather information accordingly."""

        print(f"\n{'='*60}")
        print(f"Gathering Information for: {query}")
        if classification:
            print(f"Query Type: {classification.get('query_type', 'N/A')}")
            print(f"Strategy: {classification.get('research_strategy', 'N/A')}")
        print(f"{'='*60}\n")

        # Run the agent
        response = await runner.run_debug(enhanced_query)

        # Extract response from Event list
        if isinstance(response, list) and len(response) > 0:
            last_event = response[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                response_text = last_event.content.parts[0].text
            else:
                response_text = str(last_event)
        else:
            response_text = str(response)

        print(f"Raw Response:\n{response_text}\n")

        # Try to parse as JSON
        try:
            # Clean the response - remove markdown code blocks if present
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()

            result = json.loads(cleaned_text)

            print(f"{'='*60}")
            print(f"Information Gathering Results:")
            print(f"{'='*60}")
            print(f"Total Sources: {result.get('total_sources', 'N/A')}")
            print(f"\nKey Findings:")
            for i, finding in enumerate(result.get('key_findings', []), 1):
                print(f"{i}. {finding}")

            print(f"\nSources:")
            for source in result.get('sources', []):
                print(f"  - {source.get('title', 'N/A')} ({source.get('url', 'N/A')})")
                print(f"    Relevance: {source.get('relevance', 'N/A')}")

            print(f"\nSynthesized Info:")
            print(f"{result.get('synthesized_info', 'N/A')}")
            print(f"{'='*60}\n")

            return result

        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse JSON response: {e}")
            return {
                "sources": [],
                "synthesized_info": response_text,
                "key_findings": [],
                "total_sources": 0,
                "raw_response": response_text,
                "error": "Could not parse JSON",
                "message": "Agent responded but not in expected JSON format"
            }

    except Exception as e:
        print(f"Error during information gathering: {e}")
        return {
            "error": str(e),
            "message": "Information gathering failed"
        }


async def test_information_gatherer():
    """Test the information gatherer with sample queries."""

    test_queries = [
        {
            "query": "What is machine learning?",
            "classification": {
                "query_type": "factual",
                "research_strategy": "quick-answer"
            }
        },
        {
            "query": "Best laptops for programming under $1000",
            "classification": {
                "query_type": "comparative",
                "research_strategy": "multi-source"
            }
        },
    ]

    for test in test_queries:
        print(f"\n\n{'#'*60}")
        print(f"TEST: {test['query']}")
        print(f"{'#'*60}")

        result = await gather_information(
            test['query'],
            test.get('classification')
        )

        if "error" in result:
            print(f"\n[ERROR] {result.get('error')}")
            print(f"Message: {result.get('message', '')}")
        else:
            print(f"\n[SUCCESS] Information gathered from {result.get('total_sources', 0)} sources")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_information_gatherer())
