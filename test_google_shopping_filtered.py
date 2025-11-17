"""
Test Google Shopping API with credibility filtering for major retailers
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

from mcp_servers.price_extractor import PriceExtractorServer

print("="*80)
print("GOOGLE SHOPPING API TEST - MAJOR RETAILERS ONLY")
print("="*80)

# Major trusted retailers
TRUSTED_SELLERS = [
    'amazon', 'walmart', 'best buy', 'target', 'ebay',
    'newegg', 'costco', 'sams club', 'bhphotovideo', 'adorama'
]

def is_trusted_seller(seller_name: str) -> bool:
    """Check if seller is a major trusted retailer."""
    seller_lower = seller_name.lower()
    return any(trusted in seller_lower for trusted in TRUSTED_SELLERS)

# Initialize extractor
extractor = PriceExtractorServer(timeout=15)

# Test queries
test_queries = [
    "Sony WH-1000XM5 headphones",
    "AirPods Pro 2nd generation",
]

for query in test_queries:
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")

    # Search Google Shopping (get more results to filter)
    all_results = extractor.search_google_shopping(query, num_results=20)

    # Filter for trusted sellers only
    trusted_results = []
    for result in all_results:
        if result.get('status') == 'success':
            seller = result.get('seller', '')
            if is_trusted_seller(seller):
                trusted_results.append(result)

    if trusted_results:
        print(f"Found {len(trusted_results)} results from major retailers:\n")

        for i, result in enumerate(trusted_results[:5], 1):
            print(f"[{i}] {result.get('product_name', 'N/A')[:60]}")
            print(f"    Price: {result.get('price', 'N/A')}")
            print(f"    Seller: {result.get('seller', 'N/A')}")
            if result.get('rating'):
                reviews = result.get('review_count', 0)
                reviews_str = f"{reviews:,}" if reviews else "0"
                print(f"    Rating: {result.get('rating')}/5 ({reviews_str} reviews)")
            if result.get('delivery'):
                print(f"    Delivery: {result.get('delivery')}")
            print()

        # Price comparison (trusted sellers only)
        prices = []
        for result in trusted_results:
            if result.get('price'):
                import re
                price_match = re.search(r'\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', result['price'])
                if price_match:
                    price_value = float(price_match.group(1).replace(',', ''))
                    seller = result.get('seller', 'Unknown')
                    # Filter out suspiciously low prices (likely used/refurbished)
                    if price_value > 50:  # Reasonable minimum for these products
                        prices.append((seller, price_value))

        if len(prices) >= 2:
            prices.sort(key=lambda x: x[1])
            print(f"Price Comparison (Major Retailers):")
            print(f"  Lowest:  {prices[0][0]} - ${prices[0][1]:.2f}")
            print(f"  Highest: {prices[-1][0]} - ${prices[-1][1]:.2f}")
            diff = prices[-1][1] - prices[0][1]
            pct = (diff / prices[0][1]) * 100
            print(f"  Difference: ${diff:.2f} ({pct:.1f}%)")
            print(f"\n  [RECOMMENDATION] Best price: {prices[0][0]} at ${prices[0][1]:.2f}")

    else:
        print(f"[WARNING] No results found from major retailers")
        print(f"Available sellers in all results:")
        for result in all_results[:10]:
            if result.get('status') == 'success':
                print(f"  - {result.get('seller', 'Unknown')}: {result.get('price', 'N/A')}")

print(f"\n{'='*80}")
print("TEST COMPLETE")
print(f"{'='*80}")

print("\nFiltering Strategy:")
print("  - Only show results from major trusted retailers")
print("  - Filter out suspiciously low prices (likely used/refurbished)")
print("  - Compare prices across credible sources")
print("\nTrusted Retailers:")
for seller in TRUSTED_SELLERS:
    print(f"  - {seller.title()}")
