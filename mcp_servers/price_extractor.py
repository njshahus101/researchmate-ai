"""
MCP Price Extractor Server

A custom MCP server that extracts structured product data from web pages.
Specializes in finding prices, specifications, and product details for comparison research.
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse


class PriceExtractorServer:
    """
    MCP Server for extracting structured product data.

    Capabilities:
    - Extract prices in multiple currencies
    - Extract product specifications
    - Extract availability information
    - Extract ratings and reviews
    - Return structured JSON data
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize the Price Extractor.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Currency patterns
        self.currency_patterns = {
            'USD': r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            'EUR': r'€\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            'GBP': r'£\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            'INR': r'₹\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        }

    def extract_product_data(self, url: str) -> Dict[str, Any]:
        """
        Extract structured product data from a URL.

        Args:
            url: Product page URL

        Returns:
            Dictionary with product data:
            {
                "status": "success|error",
                "product_name": "...",
                "price": "$99.99",
                "currency": "USD",
                "availability": "In Stock",
                "specifications": {...},
                "rating": 4.5,
                "review_count": 123,
                "features": [...],
                "error_message": "..." (if error)
            }
        """
        try:
            # Fetch the page
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )

            if response.status_code != 200:
                return {
                    "status": "error",
                    "url": url,
                    "error_message": f"HTTP {response.status_code}"
                }

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract components
            product_name = self._extract_product_name(soup)
            price_data = self._extract_price(soup)
            availability = self._extract_availability(soup)
            specifications = self._extract_specifications(soup)
            rating_data = self._extract_rating(soup)
            features = self._extract_features(soup)

            return {
                "status": "success",
                "url": url,
                "product_name": product_name,
                "price": price_data.get("price"),
                "currency": price_data.get("currency"),
                "availability": availability,
                "specifications": specifications,
                "rating": rating_data.get("rating"),
                "review_count": rating_data.get("review_count"),
                "features": features,
                "domain": urlparse(url).netloc
            }

        except requests.Timeout:
            return {
                "status": "error",
                "url": url,
                "error_message": "Request timeout"
            }
        except Exception as e:
            return {
                "status": "error",
                "url": url,
                "error_message": f"Error: {str(e)}"
            }

    def _extract_product_name(self, soup: BeautifulSoup) -> str:
        """Extract product name from common locations."""
        # Try h1 first
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()

        # Try title
        title = soup.find('title')
        if title:
            return title.get_text().strip()

        return "Product name not found"

    def _extract_price(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract price and currency."""
        # Common price selectors
        price_selectors = [
            '[class*="price"]',
            '[id*="price"]',
            '[itemprop="price"]',
            '.product-price',
            '#price',
        ]

        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text()

                # Try each currency pattern
                for currency, pattern in self.currency_patterns.items():
                    match = re.search(pattern, text)
                    if match:
                        price_str = match.group(0)
                        return {
                            "price": price_str,
                            "currency": currency,
                            "raw_value": match.group(1)
                        }

        return {"price": None, "currency": None}

    def _extract_availability(self, soup: BeautifulSoup) -> str:
        """Extract availability status."""
        availability_keywords = {
            'in stock': 'In Stock',
            'available': 'Available',
            'out of stock': 'Out of Stock',
            'unavailable': 'Unavailable',
            'pre-order': 'Pre-order',
            'coming soon': 'Coming Soon',
        }

        # Search in common locations
        text = soup.get_text().lower()

        for keyword, status in availability_keywords.items():
            if keyword in text:
                return status

        return "Availability unknown"

    def _extract_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract product specifications from tables or lists."""
        specs = {}

        # Try to find specification tables
        tables = soup.find_all('table', class_=re.compile(r'spec|detail|feature', re.I))

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    if key and value:
                        specs[key] = value

        # Try to find specification lists
        if not specs:
            spec_divs = soup.find_all('div', class_=re.compile(r'spec|detail', re.I))
            for div in spec_divs:
                dt_elements = div.find_all('dt')
                dd_elements = div.find_all('dd')

                for dt, dd in zip(dt_elements, dd_elements):
                    key = dt.get_text().strip()
                    value = dd.get_text().strip()
                    if key and value:
                        specs[key] = value

        return specs if specs else {"note": "No specifications found"}

    def _extract_rating(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract product rating and review count."""
        rating_data = {"rating": None, "review_count": None}

        # Look for rating patterns
        rating_pattern = r'(\d+(?:\.\d+)?)\s*(?:out of|\/)\s*5'
        review_count_pattern = r'(\d+(?:,\d{3})*)\s*(?:reviews?|ratings?)'

        text = soup.get_text()

        rating_match = re.search(rating_pattern, text, re.I)
        if rating_match:
            rating_data["rating"] = float(rating_match.group(1))

        review_match = re.search(review_count_pattern, text, re.I)
        if review_match:
            count_str = review_match.group(1).replace(',', '')
            rating_data["review_count"] = int(count_str)

        return rating_data

    def _extract_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract key product features."""
        features = []

        # Look for feature lists
        feature_lists = soup.find_all(['ul', 'ol'], class_=re.compile(r'feature|highlight|benefit', re.I))

        for ul in feature_lists[:3]:  # Limit to first 3 lists
            items = ul.find_all('li')
            for item in items[:10]:  # Limit to 10 items per list
                feature_text = item.get_text().strip()
                if feature_text and len(feature_text) > 10:  # Filter out short/empty items
                    features.append(feature_text)

        return features if features else ["No features found"]


# Function wrapper for use as an agent tool
def extract_product_info(url: str) -> Dict[str, Any]:
    """
    Tool function for extracting product data.

    This function can be directly used as a tool in ADK agents.

    Args:
        url: Product page URL

    Returns:
        Dictionary with extracted product data
    """
    extractor = PriceExtractorServer()
    return extractor.extract_product_data(url)


if __name__ == "__main__":
    # Test the price extractor
    extractor = PriceExtractorServer()

    # Test with a sample product URL (example)
    test_url = "https://www.amazon.com/dp/B08N5WRWNW"  # Example product

    print(f"💰 Testing Price Extractor...")
    print(f"📍 URL: {test_url}")

    result = extractor.extract_product_data(test_url)

    if result["status"] == "success":
        print(f"✅ Success!")
        print(f"   Product: {result['product_name']}")
        print(f"   Price: {result['price']} {result['currency']}")
        print(f"   Availability: {result['availability']}")
        print(f"   Rating: {result['rating']}")
    else:
        print(f"❌ Error: {result['error_message']}")
