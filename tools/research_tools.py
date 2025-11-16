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


# For backward compatibility
def search_and_fetch(query: str, num_results: int = 3) -> Dict:
    """
    Note: For actual web search, use Google Search grounding in Gemini.
    This is a placeholder that suggests using the built-in search capabilities.

    Args:
        query: Search query string
        num_results: Number of results desired

    Returns:
        Information message about using Google Search
    """
    return {
        "status": "info",
        "message": "Use Gemini's Google Search grounding feature for web search, then use fetch_web_content() or extract_product_info() on specific URLs",
        "suggestion": f"Search query: '{query}', then fetch top {num_results} results"
    }


__all__ = [
    "fetch_web_content",
    "extract_product_info",
    "search_and_fetch",
]
