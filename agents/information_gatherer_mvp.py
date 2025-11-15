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
from google.genai import types

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.web_fetcher import fetch_webpage_content


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
        description="Gathers and extracts information from specific web URLs",
        instruction="""You are the Information Gatherer agent for ResearchMate AI.

Your role is to extract detailed information from web pages.

CAPABILITIES:
1. fetch_webpage_content - Extract detailed content from specific URLs

WORKFLOW:
1. When given a query, suggest relevant URLs to fetch based on the topic
2. Use fetch_webpage_content to extract content from the provided or suggested URLs
3. Analyze and summarize the extracted content
4. Always cite your sources with URLs

GUIDELINES:
- For well-known topics, suggest authoritative sources (Wikipedia, official sites, documentation)
- Always check the "status" field in tool responses
- If a fetch fails, explain the error clearly
- Summarize content concisely but informatively
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
            "fetch_status": "success|error"
        }
    ],
    "synthesized_info": "Combined insights from all fetched sources",
    "key_findings": ["finding 1", "finding 2", "finding 3"],
    "total_sources": 1,
    "suggested_urls": ["https://url1.com", "https://url2.com"]
}

ERROR HANDLING:
- If webpage fetch fails, explain the error from the tool response
- Suggest alternative URLs if fetches fail

Only output valid JSON, no additional text before or after.
""",
        tools=[
            fetch_webpage_content,   # Custom web content fetcher (Python callable)
        ],
    )

    return agent


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
