"""
MCP Web Content Fetcher Server

A custom MCP server that fetches full webpage content and extracts clean article text.
Built using Python's requests and BeautifulSoup4 libraries.

This tool elevates ResearchMate AI beyond snippet-based research by accessing
full article content for deep analysis.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
import re
from urllib.parse import urlparse


class WebContentFetcherServer:
    """
    MCP Server for fetching and extracting web content.

    Capabilities:
    - Downloads full webpage HTML
    - Extracts main content (removes nav, ads, etc.)
    - Handles common web issues (timeouts, 404s, encoding)
    - Returns clean article text
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize the Web Content Fetcher.

        Args:
            timeout: Request timeout in seconds (default: 10)
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_content(self, url: str) -> Dict[str, Any]:
        """
        Fetch and extract clean content from a URL.

        Args:
            url: The URL to fetch content from

        Returns:
            Dictionary with status and content:
            {
                "status": "success|error",
                "url": "...",
                "title": "...",
                "content": "...",
                "word_count": 1234,
                "error_message": "..." (if error)
            }
        """
        try:
            # Validate URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return {
                    "status": "error",
                    "url": url,
                    "error_message": "Invalid URL format"
                }

            # Fetch the webpage
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )

            # Check response status
            if response.status_code != 200:
                return {
                    "status": "error",
                    "url": url,
                    "error_message": f"HTTP {response.status_code}"
                }

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title found"

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
                element.decompose()

            # Try to find main content
            main_content = self._extract_main_content(soup)

            if not main_content:
                return {
                    "status": "error",
                    "url": url,
                    "error_message": "Could not extract main content"
                }

            # Clean and format text
            clean_text = self._clean_text(main_content)

            # Calculate word count
            word_count = len(clean_text.split())

            return {
                "status": "success",
                "url": url,
                "title": title_text,
                "content": clean_text,
                "word_count": word_count,
                "domain": parsed.netloc
            }

        except requests.Timeout:
            return {
                "status": "error",
                "url": url,
                "error_message": "Request timeout"
            }
        except requests.RequestException as e:
            return {
                "status": "error",
                "url": url,
                "error_message": f"Request error: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "url": url,
                "error_message": f"Unexpected error: {str(e)}"
            }

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extract main article content from parsed HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            Extracted text content
        """
        # Try common article containers (in order of preference)
        selectors = [
            'article',
            '[role="main"]',
            'main',
            '.article-content',
            '.post-content',
            '.entry-content',
            '#content',
            '.content'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text()

        # Fallback: get all paragraph text
        paragraphs = soup.find_all('p')
        if paragraphs:
            return ' '.join([p.get_text() for p in paragraphs])

        # Last resort: get body text
        body = soup.find('body')
        return body.get_text() if body else ""

    def _clean_text(self, text: str) -> str:
        """
        Clean and format extracted text.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        # Remove repeated punctuation
        text = re.sub(r'([.!?])\1+', r'\1', text)

        return text


# Function wrapper for use as an agent tool
def fetch_web_content(url: str) -> Dict[str, Any]:
    """
    Tool function for fetching web content.

    This function can be directly used as a tool in ADK agents.

    Args:
        url: The URL to fetch content from

    Returns:
        Dictionary with fetched content and metadata
    """
    fetcher = WebContentFetcherServer()
    return fetcher.fetch_content(url)


if __name__ == "__main__":
    # Test the web content fetcher
    fetcher = WebContentFetcherServer()

    # Test with a sample URL
    test_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"

    print(f"🌐 Testing Web Content Fetcher...")
    print(f"📍 URL: {test_url}")

    result = fetcher.fetch_content(test_url)

    if result["status"] == "success":
        print(f"✅ Success!")
        print(f"   Title: {result['title']}")
        print(f"   Word Count: {result['word_count']}")
        print(f"   Content Preview: {result['content'][:200]}...")
    else:
        print(f"❌ Error: {result['error_message']}")
