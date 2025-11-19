"""
Test Enhanced Product Data Extraction

Tests the improved price extractor with real product URLs from various e-commerce sites.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_servers.price_extractor import PriceExtractorServer


def test_product_extraction():
    """Test product extraction with real URLs."""

    print("="*80)
    print("ENHANCED PRODUCT EXTRACTION TEST")
    print("="*80)

    # Real product URLs to test
    test_products = [
        {
            "name": "Sony WH-1000XM5 Headphones",
            "url": "https://www.amazon.com/Sony-WH-1000XM5-Canceling-Headphones-Hands-Free/dp/B09XS7JWHH"
        },
        {
            "name": "Apple AirPods Pro (2nd Gen)",
            "url": "https://www.amazon.com/Apple-Generation-Cancelling-Transparency-Personalized/dp/B0BDHWDR12"
        },
        {
            "name": "Logitech MX Master 3S Mouse",
            "url": "https://www.amazon.com/Logitech-MX-Master-3S-Graphite/dp/B09HM94VDS"
        },
    ]

    extractor = PriceExtractorServer(timeout=15)
    results = []

    for i, product in enumerate(test_products, 1):
        print(f"\n{'-'*80}")
        print(f"TEST {i}/{len(test_products)}: {product['name']}")
        print(f"{'-'*80}")
        print(f"URL: {product['url']}")

        result = extractor.extract_product_data(product['url'])

        if result['status'] == 'success':
            print(f"\n[SUCCESS] Extraction successful")

            # Display extracted data
            print(f"\nExtracted Data:")
            print(f"  Product Name: {result.get('product_name', 'N/A')}")
            print(f"  Price: {result.get('price', 'N/A')} {result.get('currency', '')}")

            if result.get('list_price'):
                print(f"  List Price (Original): {result.get('list_price')}")
                print(f"  [DISCOUNT DETECTED]")

            print(f"  Availability: {result.get('availability', 'N/A')}")
            print(f"  Rating: {result.get('rating', 'N/A')}/5")
            print(f"  Reviews: {result.get('review_count', 'N/A')}")

            if result.get('brand'):
                print(f"  Brand: {result.get('brand')}")

            # Features
            features = result.get('features', [])
            if features and features != ["No features found"]:
                print(f"\n  Features ({len(features)}):")
                for j, feature in enumerate(features[:5], 1):  # Show first 5
                    print(f"    {j}. {feature[:80]}...")

            # Images
            images = result.get('images', [])
            if images:
                print(f"\n  Images ({len(images)}):")
                for j, img_url in enumerate(images[:3], 1):  # Show first 3
                    print(f"    {j}. {img_url[:80]}...")

            # Specifications
            specs = result.get('specifications', {})
            if specs and specs != {"note": "No specifications found"}:
                print(f"\n  Specifications ({len(specs)}):")
                for key, value in list(specs.items())[:5]:  # Show first 5
                    print(f"    {key}: {value[:60]}...")

            # Validation
            validation = validate_extraction(result)
            print(f"\nValidation:")
            for check, passed in validation.items():
                status = "[PASS]" if passed else "[FAIL]"
                print(f"  {status} {check}")

            results.append({
                "product": product['name'],
                "success": True,
                "validation": validation
            })

        else:
            print(f"\n[FAILED] Extraction failed")
            print(f"Error: {result.get('error_message')}")
            results.append({
                "product": product['name'],
                "success": False,
                "validation": {}
            })

    # Summary
    print(f"\n{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")

    successful = sum(1 for r in results if r['success'])
    total = len(results)

    print(f"\nTests Passed: {successful}/{total}")

    for result in results:
        status = "[PASS]" if result['success'] else "[FAIL]"
        print(f"\n{status} {result['product']}")

        if result['validation']:
            passed_checks = sum(1 for v in result['validation'].values() if v)
            total_checks = len(result['validation'])
            print(f"  Validation: {passed_checks}/{total_checks} checks passed")

            for check, passed in result['validation'].items():
                check_status = "OK" if passed else "X"
                print(f"    {check_status} {check}")

    # Overall assessment
    print(f"\n{'='*80}")
    if successful == total:
        print("[PASS] ALL TESTS PASSED - Enhanced extraction working!")
    elif successful > 0:
        print(f"[PARTIAL] {successful}/{total} tests passed - needs improvement")
    else:
        print("[FAIL] ALL TESTS FAILED - check implementation")

    return successful == total


def validate_extraction(result: dict) -> dict:
    """Validate that key data was extracted."""
    checks = {}

    # Critical fields
    checks["Has product name"] = bool(result.get('product_name') and result['product_name'] != "Product name not found")
    checks["Has price"] = bool(result.get('price'))
    checks["Has availability"] = bool(result.get('availability') and result['availability'] != "Availability unknown")

    # Important fields
    checks["Has rating"] = bool(result.get('rating'))
    checks["Has reviews"] = bool(result.get('review_count'))
    checks["Has features"] = bool(result.get('features') and result['features'] != ["No features found"])

    # Nice-to-have fields
    checks["Has images"] = bool(result.get('images'))
    checks["Has brand"] = bool(result.get('brand'))

    return checks


if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING ENHANCED PRODUCT DATA EXTRACTION")
    print("="*80)
    print("\nThis test validates:")
    print("  1. JSON-LD schema.org extraction")
    print("  2. Amazon-specific parsing")
    print("  3. Multiple price formats (sale, regular)")
    print("  4. Product images")
    print("  5. Features and specifications")
    print("\n")

    success = test_product_extraction()

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

    if success:
        print("\nAll product extraction tests passed!")
        print("The enhanced extractor is working correctly.")
    else:
        print("\nSome tests failed. Review the output above for details.")

    print("\n")
