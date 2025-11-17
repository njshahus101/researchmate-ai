"""
Test script for Google Shopping API integration via SerpApi
"""

import sys
from pathlib import Path
import os

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_servers.price_extractor import PriceExtractorServer

print("="*80)
print("GOOGLE SHOPPING API TEST")
print("="*80)

# Check if API key is set
serpapi_key = os.getenv('SERPAPI_KEY')
if not serpapi_key:
    print("\nWARNING: SERPAPI_KEY environment variable not set!")
    print("To use Google Shopping API:")
    print("  1. Sign up for free at https://serpapi.com/")
    print("  2. Get your API key (100 free searches/month)")
    print("  3. Set environment variable:")
    print("     Windows: set SERPAPI_KEY=your_api_key_here")
    print("     Linux/Mac: export SERPAPI_KEY=your_api_key_here")
    print("\nContinuing with test (will show error if not configured)...\n")

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

    # Search Google Shopping
    results = extractor.search_google_shopping(query, num_results=5)

    # Display results
    if results and results[0].get('status') == 'success':
        print(f"Found {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            print(f"[{i}] {result.get('product_name', 'N/A')[:60]}")
            print(f"    Price: {result.get('price', 'N/A')}")
            print(f"    Seller: {result.get('seller', 'N/A')}")
            if result.get('rating'):
                print(f"    Rating: {result.get('rating')}/5 ({result.get('review_count', 0)} reviews)")
            if result.get('delivery'):
                print(f"    Delivery: {result.get('delivery')}")
            print(f"    Link: {result.get('link', 'N/A')[:70]}...")
            print()

        # Price comparison
        prices = []
        for result in results:
            if result.get('price'):
                import re
                price_match = re.search(r'\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', result['price'])
                if price_match:
                    price_value = float(price_match.group(1).replace(',', ''))
                    seller = result.get('seller', 'Unknown')
                    prices.append((seller, price_value))

        if len(prices) >= 2:
            prices.sort(key=lambda x: x[1])
            print(f"Price Comparison:")
            print(f"  Lowest:  {prices[0][0]} - ${prices[0][1]:.2f}")
            print(f"  Highest: {prices[-1][0]} - ${prices[-1][1]:.2f}")
            diff = prices[-1][1] - prices[0][1]
            pct = (diff / prices[0][1]) * 100
            print(f"  Difference: ${diff:.2f} ({pct:.1f}%)")

    elif results and results[0].get('status') == 'error':
        print(f"[ERROR] {results[0].get('error_message')}")

print(f"\n{'='*80}")
print("TEST COMPLETE")
print(f"{'='*80}")

print("\nSummary:")
print("  - Google Shopping API provides aggregated prices from multiple retailers")
print("  - More reliable than direct scraping (no bot detection)")
print("  - Free tier: 100 searches/month via SerpApi")
print("  - Returns normalized data: price, seller, rating, delivery info")
print("\nNext Steps:")
print("  1. Set up SERPAPI_KEY environment variable")
print("  2. Integrate with orchestrator for multi-source price comparison")
print("  3. Content Analysis Agent can analyze credibility across sources")
