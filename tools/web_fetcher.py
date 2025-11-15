"""
Web Content Fetcher Tool

Provides functions for fetching and extracting content from web pages.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict
import time


def fetch_webpage_content(url: str, timeout: int = 10) -> Dict:
    """Fetches and extracts main content from a webpage.

    This function retrieves a webpage, extracts its title and main text content,
    and returns structured data. It handles common errors gracefully.

    Args:
        url: The URL to fetch content from (must start with http:// or https://)
        timeout: Maximum time in seconds to wait for response (default: 10)

    Returns:
        Dictionary with status and content information:
        - Success: {
            "status": "success",
            "url": "https://example.com",
            "title": "Page Title",
            "content": "Main text content...",
            "content_length": 1234,
            "fetch_time": 0.5
          }
        - Error: {
            "status": "error",
            "error_message": "Description of what went wrong",
            "url": "https://example.com"
          }
    """
    start_time = time.time()

    try:
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return {
                "status": "error",
                "error_message": "Invalid URL format. URL must start with http:// or https://",
                "url": url
            }

        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=timeout)

        # Check for HTTP errors
        if response.status_code == 404:
            return {
                "status": "error",
                "error_message": "Page not found (404)",
                "url": url
            }
        elif response.status_code == 403:
            return {
                "status": "error",
                "error_message": "Access forbidden (403). The website may be blocking automated requests.",
                "url": url
            }
        elif response.status_code >= 400:
            return {
                "status": "error",
                "error_message": f"HTTP error {response.status_code}",
                "url": url
            }

        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title = soup.title.string.strip() if soup.title else "No title found"

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Extract main content - try common content containers first
        main_content = None
        content_selectors = [
            'article',
            'main',
            '[role="main"]',
            '.content',
            '.main-content',
            '#content',
            '#main-content',
            'body'
        ]

        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        if not main_content:
            main_content = soup.body if soup.body else soup

        # Get text and clean it up
        text = main_content.get_text(separator=' ', strip=True)

        # Clean up excessive whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        content = ' '.join(lines)

        # Limit content length for LLM processing (first 10000 chars)
        if len(content) > 10000:
            content = content[:10000] + "... [content truncated]"

        fetch_time = time.time() - start_time

        return {
            "status": "success",
            "url": url,
            "title": title,
            "content": content,
            "content_length": len(content),
            "fetch_time": round(fetch_time, 2)
        }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "error_message": f"Request timed out after {timeout} seconds",
            "url": url
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "error_message": "Failed to connect to the website. Check your internet connection or the URL.",
            "url": url
        }
    except requests.exceptions.TooManyRedirects:
        return {
            "status": "error",
            "error_message": "Too many redirects. The URL may be misconfigured.",
            "url": url
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}",
            "url": url
        }


def search_and_fetch(query: str, num_results: int = 3) -> Dict:
    """Performs a web search and fetches content from top results.

    Note: This is a placeholder. For production, integrate with Google Search API
    or use the built-in google_search tool in ADK.

    Args:
        query: Search query string
        num_results: Number of top results to fetch (default: 3, max: 5)

    Returns:
        Dictionary with search results and fetched content
    """
    # Limit num_results
    num_results = min(num_results, 5)

    return {
        "status": "info",
        "message": "Use the google_search tool for searching, then fetch_webpage_content for specific URLs",
        "suggestion": f"First search for: '{query}', then use fetch_webpage_content on the URLs returned"
    }
