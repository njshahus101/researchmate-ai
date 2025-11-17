"""
Demo: Content Analysis Agent analyzing Google Shopping results
Shows how credibility scoring, conflict detection, and comparison works
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

from mcp_servers.price_extractor import PriceExtractorServer

print("="*80)
print("DEMO: Content Analysis with Google Shopping API")
print("="*80)

# Major trusted retailers with credibility scores
RETAILER_CREDIBILITY = {
    'amazon': 85,
    'best buy': 82,
    'walmart': 80,
    'target': 78,
    'newegg': 75,
    'costco': 82,
    'bhphotovideo': 80,
    'adorama': 78,
    'ebay': 65,  # Lower due to marketplace (varies by seller)
}

def get_credibility_score(seller_name: str) -> int:
    """Get credibility score for a seller."""
    seller_lower = seller_name.lower()
    for retailer, score in RETAILER_CREDIBILITY.items():
        if retailer in seller_lower:
            return score
    return 50  # Unknown seller default

def is_major_retailer(seller_name: str) -> bool:
    """Check if seller is a major retailer."""
    seller_lower = seller_name.lower()
    return any(retailer in seller_lower for retailer in RETAILER_CREDIBILITY.keys())

# Initialize extractor
extractor = PriceExtractorServer(timeout=15)

# Test query
query = "Sony WH-1000XM5 headphones"

print(f"\n{'='*80}")
print(f"User Query: Find the best price for {query}")
print(f"{'='*80}\n")

print("[STEP 1] Searching Google Shopping API...")
all_results = extractor.search_google_shopping(query, num_results=20)

# Filter for major retailers and reasonable prices
print("\n[STEP 2] Filtering for credible sources...")
credible_results = []
for result in all_results:
    if result.get('status') == 'success':
        seller = result.get('seller', '')
        price = result.get('price', '')

        # Extract numeric price
        import re
        price_match = re.search(r'\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', price)
        if price_match:
            price_value = float(price_match.group(1).replace(',', ''))

            # Filter: major retailers + reasonable price range (new products)
            if is_major_retailer(seller) and 200 <= price_value <= 500:
                credibility = get_credibility_score(seller)
                result['credibility_score'] = credibility
                result['price_numeric'] = price_value
                credible_results.append(result)

print(f"Found {len(credible_results)} credible results (major retailers, reasonable prices)")

# Sort by credibility score
credible_results.sort(key=lambda x: x['credibility_score'], reverse=True)

print("\n[STEP 3] Content Analysis - Credibility Assessment")
print(f"{'='*80}\n")

for i, result in enumerate(credible_results[:5], 1):
    print(f"[{i}] {result.get('seller', 'Unknown')}")
    print(f"    Product: {result.get('product_name', 'N/A')[:60]}")
    print(f"    Price: {result.get('price', 'N/A')}")
    print(f"    Credibility Score: {result.get('credibility_score')}/100")
    if result.get('rating'):
        reviews = result.get('review_count', 0)
        reviews_str = f"{reviews:,}" if reviews else "0"
        print(f"    Rating: {result.get('rating')}/5 ({reviews_str} reviews)")

    # Credibility reasoning
    score = result.get('credibility_score')
    if score >= 80:
        reasoning = "HIGH - Major verified retailer with strong reputation"
    elif score >= 70:
        reasoning = "MEDIUM-HIGH - Established retailer with good track record"
    else:
        reasoning = "MEDIUM - Marketplace platform, seller reputation varies"
    print(f"    Credibility: {reasoning}")
    print()

# Price analysis
print(f"\n[STEP 4] Price Conflict Detection")
print(f"{'='*80}\n")

prices = [(r['seller'], r['price_numeric']) for r in credible_results]
if len(prices) >= 2:
    prices.sort(key=lambda x: x[1])

    min_price = prices[0][1]
    max_price = prices[-1][1]
    avg_price = sum(p[1] for p in prices) / len(prices)
    variance = ((max_price - min_price) / min_price) * 100

    print(f"Price Statistics:")
    print(f"  Lowest:  {prices[0][0]} - ${prices[0][1]:.2f}")
    print(f"  Highest: {prices[-1][0]} - ${prices[-1][1]:.2f}")
    print(f"  Average: ${avg_price:.2f}")
    print(f"  Variance: {variance:.1f}%")

    # Conflict severity
    if variance < 5:
        severity = "LOW"
        explanation = "Prices are consistent across retailers"
    elif variance < 15:
        severity = "MEDIUM"
        explanation = "Some price variation, but within normal range"
    else:
        severity = "HIGH"
        explanation = "Significant price differences detected"

    print(f"\n  Conflict Severity: {severity}")
    print(f"  Explanation: {explanation}")
    print(f"  Recommendation: Compare features and return policies")

# Comparison Matrix
print(f"\n[STEP 5] Comparison Matrix")
print(f"{'='*80}\n")

print(f"{'Retailer':<20} {'Price':<12} {'Credibility':<15} {'Rating':<15} {'Delivery':<15}")
print("-" * 77)

for result in credible_results[:5]:
    retailer = result.get('seller', 'Unknown')[:19]
    price = f"${result.get('price_numeric', 0):.2f}"
    credibility = f"{result.get('credibility_score')}/100"
    rating = f"{result.get('rating', 'N/A')}/5" if result.get('rating') else 'N/A'
    delivery = result.get('delivery', 'N/A')[:14]

    print(f"{retailer:<20} {price:<12} {credibility:<15} {rating:<15} {delivery:<15}")

# Winner determination
print(f"\n[STEP 6] Recommendation")
print(f"{'='*80}\n")

if credible_results:
    # Best overall: balance of price and credibility
    best_value = max(credible_results, key=lambda x: (
        x['credibility_score'] * 0.4 +  # 40% weight on credibility
        (1 - (x['price_numeric'] - min_price) / (max_price - min_price)) * 100 * 0.6  # 60% weight on price
    ))

    print(f"Best Value (Price + Credibility): {best_value['seller']}")
    print(f"  Price: {best_value['price']}")
    print(f"  Credibility: {best_value['credibility_score']}/100")
    print(f"  Rating: {best_value.get('rating', 'N/A')}/5")
    print(f"\n  Why: Excellent balance of competitive pricing ({best_value['price']}) " +
          f"and high credibility (score: {best_value['credibility_score']}/100)")

print(f"\n{'='*80}")
print("DEMO COMPLETE")
print(f"{'='*80}")

print("\nKey Insights:")
print("  - Google Shopping API provides multi-source data")
print("  - Content Analysis evaluates credibility of each seller")
print("  - Price conflicts are detected and severity assessed")
print("  - Comparison matrix shows all key attributes")
print("  - Recommendation balances price and credibility")
print("\nThis demonstrates how the Content Analysis Agent would process")
print("Google Shopping results to provide intelligent product recommendations.")
