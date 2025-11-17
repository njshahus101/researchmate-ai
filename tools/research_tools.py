"""
Research Tools - FunctionTool wrappers for web fetching and price extraction

These tools are designed to be used by the Information Gatherer agent for
real web-based research.
"""

import sys
from pathlib import Path
from typing import Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.web_fetcher import fetch_webpage_content
from mcp_servers.price_extractor import PriceExtractorServer


# Initialize price extractor
_price_extractor = PriceExtractorServer(timeout=10)


def fetch_web_content(url: str) -> Dict:
    """
    Fetch and extract main content from a webpage.

    This tool retrieves a webpage, extracts its title and main text content,
    and returns structured data.

    Args:
        url: The URL to fetch content from (must start with http:// or https://)

    Returns:
        Dictionary with status and content information:
        - Success: {
            "status": "success",
            "url": "https://example.com",
            "title": "Page Title",
            "content": "Main text content...",
            "content_length": 1234
          }
        - Error: {
            "status": "error",
            "error_message": "Description of what went wrong",
            "url": "https://example.com"
          }

    Example:
        result = fetch_web_content("https://example.com")
        if result["status"] == "success":
            print(result["title"])
            print(result["content"])
    """
    return fetch_webpage_content(url, timeout=10)


def extract_product_info(url: str) -> Dict:
    """
    Extract structured product data from a product page URL.

    This tool specializes in extracting:
    - Product name and price
    - Specifications and features
    - Ratings and reviews
    - Availability information

    Useful for comparative research on products like electronics, gadgets, etc.

    Args:
        url: Product page URL (e.g., Amazon, Best Buy, tech review sites)

    Returns:
        Dictionary with product data:
        {
            "status": "success|error",
            "product_name": "Product Name",
            "price": "$99.99",
            "currency": "USD",
            "availability": "In Stock",
            "rating": 4.5,
            "review_count": 123,
            "features": ["Feature 1", "Feature 2"],
            "specifications": {...},
            "error_message": "..." (if error)
        }

    Example:
        result = extract_product_info("https://www.amazon.com/product/...")
        if result["status"] == "success":
            print(f"{result['product_name']}: {result['price']}")
            print(f"Rating: {result['rating']}/5")
    """
    return _price_extractor.extract_product_data(url)


def search_web(query: str, num_results: int = 5) -> Dict:
    """
    Search the web using Google Custom Search and return URLs.

    This tool performs a Google search and returns a list of URLs that can then
    be passed to fetch_web_content() or extract_product_info().

    Args:
        query: Search query (e.g., "Sony WH-1000XM5 Amazon")
        num_results: Number of results to return (default: 5)

    Returns:
        Dictionary with search results:
        {
            "status": "success|error",
            "query": "original search query",
            "results": [
                {
                    "title": "Result title",
                    "url": "https://example.com/...",
                    "snippet": "Brief description..."
                },
                ...
            ],
            "urls": ["https://url1.com", "https://url2.com", ...],
            "error_message": "..." (if error)
        }

    Example:
        result = search_web("Sony WH-1000XM5 Amazon price")
        if result["status"] == "success":
            # Get the first Amazon URL
            amazon_urls = [url for url in result["urls"] if "amazon.com" in url]
            if amazon_urls:
                product_info = extract_product_info(amazon_urls[0])
    """
    import requests
    import os

    # Get API keys from environment
    google_api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    # If no custom search configured, return helpful message
    if not search_engine_id:
        return {
            "status": "info",
            "query": query,
            "message": "Google Custom Search not configured. Using Google Search grounding instead.",
            "suggestion": f"Search for: '{query}' and use the URLs from grounding results",
            "results": [],
            "urls": []
        }

    try:
        # Google Custom Search API
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": google_api_key,
            "cx": search_engine_id,
            "q": query,
            "num": min(num_results, 10)  # Max 10 per request
        }

        print(f"[SEARCH] Calling Google Custom Search API...")
        print(f"[SEARCH] Query: {query}")
        print(f"[SEARCH] Search Engine ID: {search_engine_id}")

        response = requests.get(url, params=params, timeout=10)

        print(f"[SEARCH] Response status: {response.status_code}")

        # Check for HTTP errors
        if response.status_code != 200:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            error_msg = error_data.get('error', {}).get('message', response.text)
            print(f"[SEARCH] API Error: {error_msg}")
            return {
                "status": "error",
                "query": query,
                "error_message": f"Google Search API error ({response.status_code}): {error_msg}",
                "results": [],
                "urls": []
            }

        response.raise_for_status()

        data = response.json()

        results = []
        urls = []

        for item in data.get("items", []):
            result = {
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", "")
            }
            results.append(result)
            urls.append(result["url"])

        print(f"[SEARCH] Found {len(urls)} results")

        return {
            "status": "success",
            "query": query,
            "results": results,
            "urls": urls,
            "count": len(results)
        }

    except Exception as e:
        print(f"[SEARCH] Exception: {type(e).__name__}: {str(e)}")
        return {
            "status": "error",
            "query": query,
            "error_message": f"Search failed: {str(e)}",
            "results": [],
            "urls": []
        }


# For backward compatibility
def search_google_shopping(query: str, num_results: int = 5) -> Dict:
    """
    Search Google Shopping for product prices from multiple retailers.

    This tool uses Google Shopping API (via SerpApi) to get aggregated product
    prices from 100+ retailers including Amazon, Walmart, Best Buy, Target, etc.

    Benefits:
    - 95%+ success rate (no bot detection like Amazon scraping)
    - Multi-source prices in single API call
    - Normalized data format
    - Fast response (1-2 seconds)

    Args:
        query: Product search query (e.g., "Sony WH-1000XM5 headphones")
        num_results: Number of results to return (default: 5)

    Returns:
        Dictionary with status and shopping results:
        - Success: {
            "status": "success",
            "query": "Sony WH-1000XM5 headphones",
            "num_results": 5,
            "results": [
                {
                    "product_name": "Sony WH-1000XM5...",
                    "price": "$299.99",
                    "seller": "Amazon.com",
                    "rating": 4.7,
                    "review_count": 12000,
                    "link": "https://...",
                    "delivery": "Free delivery"
                },
                ...
            ]
        }
        - Error: {
            "status": "error",
            "error_message": "SERPAPI_KEY not configured..."
        }

    Example:
        result = search_google_shopping("Sony WH-1000XM5 headphones")
        if result["status"] == "success":
            for item in result["results"]:
                print(f"{item['seller']}: {item['price']}")

    Note:
        Requires SERPAPI_KEY environment variable to be set.
        Free tier: 100 searches/month (sufficient for demo/testing)
        Sign up: https://serpapi.com/
    """
    results = _price_extractor.search_google_shopping(query, num_results)

    # Check if first result is an error
    if results and results[0].get("status") == "error":
        return {
            "status": "error",
            "error_message": results[0].get("error_message"),
            "query": query
        }

    # Success - format the response
    return {
        "status": "success",
        "query": query,
        "num_results": len(results),
        "results": results
    }


def search_and_fetch(query: str, num_results: int = 3) -> Dict:
    """
    Deprecated: Use search_web() instead.
    """
    return search_web(query, num_results)


__all__ = [
    "search_web",
    "fetch_web_content",
    "extract_product_info",
    "search_google_shopping",
    "search_and_fetch",  # Deprecated, kept for compatibility
]
