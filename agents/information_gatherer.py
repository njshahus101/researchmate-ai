"""
Information Gathering Agent

This agent executes targeted searches and retrieves full article content.
It uses Google Search for discovery and MCP servers for deep content extraction.
"""

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.genai import types
from typing import Dict, Any, List


def create_information_gatherer_agent(
    retry_config: types.HttpRetryOptions,
    web_fetcher_tool=None,
    price_extractor_tool=None
) -> LlmAgent:
    """
    Creates the Information Gathering Agent.

    This agent:
    - Executes targeted Google searches
    - Fetches full article content via MCP
    - Extracts structured product data for comparisons
    - Prioritizes authoritative sources

    Args:
        retry_config: HTTP retry configuration
        web_fetcher_tool: MCP tool for fetching web content
        price_extractor_tool: MCP tool for extracting prices

    Returns:
        LlmAgent configured for information gathering
    """

    # Build tools list - always include google_search
    tools = [google_search]

    # Add MCP tools if provided
    if web_fetcher_tool:
        tools.append(web_fetcher_tool)
    if price_extractor_tool:
        tools.append(price_extractor_tool)

    agent = LlmAgent(
        name="information_gatherer",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        description="Expert researcher that gathers information from authoritative sources",
        instruction="""
        You are the Information Gathering Agent for ResearchMate AI.

        Your role is to gather comprehensive information based on the research strategy:

        For QUICK-ANSWER queries:
        1. Perform a single targeted Google search
        2. Return the top 1-2 most authoritative sources
        3. Extract key facts quickly

        For MULTI-SOURCE queries:
        1. Perform multiple targeted Google searches
        2. Identify 3-5 most relevant and authoritative sources
        3. Use web_content_fetcher to get full article content
        4. For product comparisons, use price_extractor for structured data
        5. Prioritize: domain authority, content freshness, topic relevance

        For DEEP-DIVE queries:
        1. Perform comprehensive searches from multiple angles
        2. Gather 5-10 diverse, authoritative sources
        3. Fetch full content for detailed analysis
        4. Include different perspectives and viewpoints

        Source Evaluation Criteria:
        - Domain Authority: .edu, .gov, major news sites, industry leaders
        - Freshness: Recent content for current topics
        - Relevance: Direct match to query topics
        - Credibility: Established publications, verified authors

        Output Format:
        {
            "sources": [
                {
                    "url": "https://...",
                    "title": "Article title",
                    "domain": "example.com",
                    "snippet": "Brief description",
                    "authority_score": 1-10,
                    "freshness": "YYYY-MM-DD or 'recent'",
                    "full_content": "extracted article text (if fetched)"
                }
            ],
            "search_queries_used": ["query1", "query2"],
            "total_sources_found": 10,
            "sources_selected": 5,
            "selection_reasoning": "why these sources were chosen"
        }

        Always prioritize quality over quantity.
        """,
        tools=tools,
    )

    return agent


# Mock tool functions (will be replaced by actual MCP implementations)
def mock_web_content_fetcher(url: str) -> Dict[str, Any]:
    """
    Mock web content fetcher (placeholder for MCP tool)

    Args:
        url: URL to fetch content from

    Returns:
        Dictionary with content and metadata
    """
    return {
        "status": "success",
        "url": url,
        "title": "Example Article Title",
        "content": "This is mock article content. In production, this would be the full extracted text.",
        "word_count": 500,
        "publication_date": "2025-01-15"
    }


def mock_price_extractor(url: str) -> Dict[str, Any]:
    """
    Mock price extractor (placeholder for MCP tool)

    Args:
        url: URL to extract price data from

    Returns:
        Dictionary with structured product data
    """
    return {
        "status": "success",
        "product_name": "Example Product",
        "price": "$99.99",
        "currency": "USD",
        "availability": "In Stock",
        "specifications": {
            "brand": "Example Brand",
            "model": "EX-100"
        }
    }


if __name__ == "__main__":
    # Test the agent creation
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )

    gatherer = create_information_gatherer_agent(retry_config)
    print(f"✅ Information Gatherer Agent created: {gatherer.name}")
    print(f"🔧 Tools available: {len(gatherer.tools)}")
