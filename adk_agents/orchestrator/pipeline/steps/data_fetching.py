"""
Step 3: Data Fetching

This module handles fetching data from URLs and Google Shopping results.
"""

from tools.research_tools import fetch_web_content, extract_product_info


def fetch_data_step(google_shopping_data: list, search_result: dict) -> tuple[list, list]:
    """
    Execute Step 3: Fetch Data (Google Shopping + URLs).

    Args:
        google_shopping_data: Google Shopping results from Step 2
        search_result: Web search results from Step 2

    Returns:
        Tuple of (fetched_data, failed_urls)
    """
    print(f"\n[STEP 3/6] Fetching data from sources...")
    fetched_data = []
    failed_urls = []

    # First, add Google Shopping results if we have them
    if google_shopping_data:
        print(f"[STEP 3/6] Adding {len(google_shopping_data)} Google Shopping results...")
        for i, shopping_item in enumerate(google_shopping_data, 1):
            fetched_data.append({
                'url': shopping_item.get('link', f'google_shopping_result_{i}'),
                'data': {
                    'status': 'success',
                    'source': 'google_shopping',
                    'product_name': shopping_item.get('product_name'),
                    'price': shopping_item.get('price'),
                    'seller': shopping_item.get('seller'),
                    'rating': shopping_item.get('rating'),
                    'review_count': shopping_item.get('review_count'),
                    'delivery': shopping_item.get('delivery'),
                },
                'source': {'title': shopping_item.get('seller', 'Google Shopping')}
            })
        print(f"[STEP 3/6] OK Added {len(google_shopping_data)} Google Shopping results")

    urls = search_result.get('urls', [])
    # Try more URLs but limit fetched data to best 3
    for i, url in enumerate(urls[:5], 1):  # Try up to 5 URLs
        try:
            # Determine if this looks like a product page
            is_product = any(domain in url for domain in ['amazon.com', 'ebay.com', 'bestbuy.com']) or \
                        any(pattern in url for pattern in ['/product', '/dp/', '/item/', '/p/'])

            if is_product:
                print(f"  [{i}/{min(len(urls), 5)}] Extracting product: {url[:60]}...")
                result = extract_product_info(url)
            else:
                print(f"  [{i}/{min(len(urls), 5)}] Fetching content: {url[:60]}...")
                result = fetch_web_content(url)

            if result.get('status') == 'success':
                # Validate that we actually got useful data
                has_content = False
                if is_product:
                    # For products, check if we got price or product name
                    has_content = result.get('price') or result.get('product_name')
                else:
                    # For general content, check if we got meaningful text
                    has_content = result.get('content') and len(result.get('content', '')) > 100

                if has_content:
                    fetched_data.append({
                        'url': url,
                        'data': result,
                        'source': search_result.get('results', [])[i-1] if i-1 < len(search_result.get('results', [])) else {}
                    })
                    print(f"  [{i}/{min(len(urls), 5)}] OK Success (useful data)")

                    # Stop if we have enough sources (including Google Shopping results)
                    total_sources = len(fetched_data)
                    if total_sources >= 8:  # Allow more if we have Google Shopping
                        print(f"  [INFO] Collected {total_sources} sources (including Google Shopping), stopping early")
                        break
                else:
                    print(f"  [{i}/{min(len(urls), 5)}] WARN Success but no useful data")
                    failed_urls.append((url, "No useful data extracted"))
            else:
                error_msg = result.get('error_message', 'Unknown error')
                print(f"  [{i}/{min(len(urls), 5)}] X Failed: {error_msg}")
                failed_urls.append((url, error_msg))

        except Exception as e:
            print(f"  [{i}/{min(len(urls), 5)}] X Exception: {str(e)[:50]}...")
            failed_urls.append((url, str(e)))
            continue

    # Report results
    if fetched_data:
        print(f"[STEP 3/6] OK Fetched data from {len(fetched_data)} sources")
    else:
        print(f"[STEP 3/6] WARN No data fetched from any source")
        if failed_urls:
            print(f"  Failed URLs ({len(failed_urls)}):")
            for url, error in failed_urls[:3]:  # Show first 3
                print(f"    - {url[:50]}... : {error[:40]}...")

    return fetched_data, failed_urls
