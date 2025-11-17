"""
MCP Price Extractor Server

A custom MCP server that extracts structured product data from web pages.
Specializes in finding prices, specifications, and product details for comparison research.

Enhanced Features:
- JSON-LD schema.org extraction
- Amazon-specific parsing
- Multiple price formats (regular, sale, discount)
- Product images
- Enhanced error handling
"""

import requests
from bs4 import BeautifulSoup
import re
import json
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

    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[Dict]:
        """
        Extract JSON-LD structured data (schema.org).

        Many e-commerce sites embed product data in JSON-LD format.
        This is the most reliable extraction method.
        """
        scripts = soup.find_all('script', type='application/ld+json')

        for script in scripts:
            try:
                data = json.loads(script.string)

                # Handle both single objects and arrays
                if isinstance(data, list):
                    # Find Product schema in array
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'Product':
                            return item
                elif isinstance(data, dict):
                    # Check if it's a Product or contains a Product
                    if data.get('@type') == 'Product':
                        return data
                    # Sometimes nested in @graph
                    if '@graph' in data:
                        for item in data['@graph']:
                            if isinstance(item, dict) and item.get('@type') == 'Product':
                                return item
            except (json.JSONDecodeError, AttributeError):
                continue

        return None

    def _extract_from_json_ld(self, json_ld: Dict) -> Dict[str, Any]:
        """Extract product data from JSON-LD Product schema."""
        extracted = {}

        # Name
        extracted['name'] = json_ld.get('name', '')

        # Price - handle various formats
        if 'offers' in json_ld:
            offers = json_ld['offers']
            if isinstance(offers, list):
                offers = offers[0]
            if isinstance(offers, dict):
                extracted['price'] = offers.get('price')
                extracted['currency'] = offers.get('priceCurrency')
                extracted['availability'] = offers.get('availability', '').split('/')[-1]

                # Check for sale price vs regular price
                if 'priceSpecification' in offers:
                    spec = offers['priceSpecification']
                    if isinstance(spec, dict):
                        extracted['regular_price'] = spec.get('price')

        # Rating
        if 'aggregateRating' in json_ld:
            rating = json_ld['aggregateRating']
            if isinstance(rating, dict):
                extracted['rating'] = rating.get('ratingValue')
                extracted['review_count'] = rating.get('reviewCount') or rating.get('ratingCount')

        # Description/Features
        if 'description' in json_ld:
            extracted['description'] = json_ld['description']

        # Images
        if 'image' in json_ld:
            images = json_ld['image']
            if isinstance(images, list):
                extracted['images'] = images[:3]  # First 3 images
            elif isinstance(images, str):
                extracted['images'] = [images]

        # Brand
        if 'brand' in json_ld:
            brand = json_ld['brand']
            if isinstance(brand, dict):
                extracted['brand'] = brand.get('name', '')
            else:
                extracted['brand'] = brand

        return extracted

    def _is_amazon_url(self, url: str) -> bool:
        """Check if URL is an Amazon product page."""
        return 'amazon.com' in url or 'amazon.' in urlparse(url).netloc

    def _extract_amazon_specific(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Amazon-specific extraction using known selectors."""
        data = {}

        # Amazon product title
        title_elem = soup.find('span', id='productTitle')
        if title_elem:
            data['name'] = title_elem.get_text().strip()

        # Amazon prices - handle multiple price formats
        # Regular price
        price_whole = soup.find('span', class_='a-price-whole')
        price_fraction = soup.find('span', class_='a-price-fraction')
        if price_whole:
            price_str = price_whole.get_text().strip()
            if price_fraction:
                price_str += price_fraction.get_text().strip()
            data['price'] = f"${price_str.replace(',', '')}"
            data['currency'] = 'USD'

        # List price (original price before discount)
        list_price = soup.find('span', class_='a-price a-text-price')
        if list_price:
            price_text = list_price.get_text().strip()
            data['list_price'] = price_text

        # Availability
        availability_elem = soup.find('div', id='availability')
        if availability_elem:
            avail_text = availability_elem.get_text().strip()
            data['availability'] = avail_text

        # Rating
        rating_elem = soup.find('span', class_='a-icon-alt')
        if rating_elem:
            rating_text = rating_elem.get_text()
            match = re.search(r'(\d+\.?\d*)\s*out of\s*5', rating_text)
            if match:
                data['rating'] = float(match.group(1))

        # Review count
        review_elem = soup.find('span', id='acrCustomerReviewText')
        if review_elem:
            review_text = review_elem.get_text()
            match = re.search(r'([\d,]+)', review_text)
            if match:
                data['review_count'] = int(match.group(1).replace(',', ''))

        # Features (bullet points)
        feature_bullets = soup.find('div', id='feature-bullets')
        if feature_bullets:
            features = []
            for li in feature_bullets.find_all('li', class_='a-spacing-mini'):
                span = li.find('span', class_='a-list-item')
                if span:
                    feature_text = span.get_text().strip()
                    if feature_text and len(feature_text) > 10:
                        features.append(feature_text)
            if features:
                data['features'] = features

        # Product images
        image_block = soup.find('div', id='altImages')
        if image_block:
            images = []
            for img in image_block.find_all('img')[:5]:  # First 5 images
                src = img.get('src', '')
                if src and 'sprite' not in src:  # Avoid sprite images
                    images.append(src)
            if images:
                data['images'] = images

        return data

    def extract_product_data(self, url: str) -> Dict[str, Any]:
        """
        Extract structured product data from a URL.

        Uses multiple extraction strategies:
        1. JSON-LD structured data (most reliable)
        2. Site-specific selectors (Amazon, etc.)
        3. Generic HTML parsing (fallback)

        Args:
            url: Product page URL

        Returns:
            Dictionary with product data:
            {
                "status": "success|error",
                "product_name": "...",
                "price": "$99.99",
                "list_price": "$129.99",  # Original price (if on sale)
                "currency": "USD",
                "availability": "In Stock",
                "specifications": {...},
                "rating": 4.5,
                "review_count": 123,
                "features": [...],
                "images": [...],
                "brand": "...",
                "description": "...",
                "error_message": "..." (if error)
            }
        """
        try:
            print(f"[EXTRACT] Fetching product page: {url[:60]}...")

            # Fetch the page
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )

            if response.status_code != 200:
                print(f"[EXTRACT] HTTP error: {response.status_code}")
                return {
                    "status": "error",
                    "url": url,
                    "error_message": f"HTTP {response.status_code}"
                }

            soup = BeautifulSoup(response.content, 'html.parser')
            result = {"status": "success", "url": url}

            # STRATEGY 1: Try JSON-LD first (most reliable)
            print(f"[EXTRACT] Attempting JSON-LD extraction...")
            json_ld = self._extract_json_ld(soup)
            if json_ld:
                print(f"[EXTRACT] Found JSON-LD data")
                json_ld_data = self._extract_from_json_ld(json_ld)
                result.update(json_ld_data)

            # STRATEGY 2: Site-specific extraction (for known sites like Amazon)
            if self._is_amazon_url(url):
                print(f"[EXTRACT] Using Amazon-specific extraction...")
                amazon_data = self._extract_amazon_specific(soup)
                # Merge, preferring Amazon-specific data
                for key, value in amazon_data.items():
                    if value:  # Only update if value exists
                        result[key] = value

            # STRATEGY 3: Generic extraction (fallback)
            print(f"[EXTRACT] Applying generic extraction...")
            if 'name' not in result or not result.get('name'):
                result['product_name'] = self._extract_product_name(soup)
            else:
                result['product_name'] = result.pop('name', '')

            if 'price' not in result or not result.get('price'):
                price_data = self._extract_price(soup)
                result.update(price_data)

            if 'availability' not in result or not result.get('availability'):
                result['availability'] = self._extract_availability(soup)

            if 'rating' not in result or not result.get('rating'):
                rating_data = self._extract_rating(soup)
                result.update(rating_data)

            if 'features' not in result or not result.get('features'):
                result['features'] = self._extract_features(soup)

            # Always try to get specifications
            result['specifications'] = self._extract_specifications(soup)

            # Add domain
            result['domain'] = urlparse(url).netloc

            print(f"[EXTRACT] Extraction complete - Price: {result.get('price')}, Rating: {result.get('rating')}")
            return result

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
