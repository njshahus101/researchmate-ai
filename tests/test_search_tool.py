"""
Quick test to verify search_web tool works
"""

from tools.research_tools import search_web

def test_search():
    print("\n" + "="*70)
    print("TESTING SEARCH_WEB TOOL")
    print("="*70 + "\n")

    # Test search
    print("Test: Searching for 'Sony WH-1000XM5 Amazon'...")
    print("-"*70)

    result = search_web("Sony WH-1000XM5 Amazon", num_results=5)

    print(f"Status: {result['status']}")

    if result['status'] == 'success':
        print(f"Found {result['count']} results")
        print("\nURLs found:")
        for i, url in enumerate(result['urls'], 1):
            print(f"  {i}. {url}")

        print("\nFull results:")
        for i, res in enumerate(result['results'], 1):
            print(f"\n  Result {i}:")
            print(f"    Title: {res['title']}")
            print(f"    URL: {res['url']}")
            print(f"    Snippet: {res['snippet'][:100]}...")

        # Check for Amazon URLs
        amazon_urls = [url for url in result['urls'] if 'amazon.com' in url]
        print(f"\n\nAmazon URLs found: {len(amazon_urls)}")
        if amazon_urls:
            print(f"First Amazon URL: {amazon_urls[0]}")

    elif result['status'] == 'info':
        print(f"Message: {result['message']}")
        print(f"Suggestion: {result['suggestion']}")
        print("\nℹ️  To enable Google Custom Search:")
        print("   1. Go to https://programmablesearchengine.google.com/")
        print("   2. Create a new search engine")
        print("   3. Add GOOGLE_SEARCH_ENGINE_ID to your .env file")

    else:
        print(f"Error: {result.get('error_message', 'Unknown error')}")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_search()
