"""
Step 2: Search Strategy

This module handles intelligent search strategy determination and execution.
"""

from tools.research_tools import search_web, search_google_shopping


def search_step(query: str, classification: dict) -> tuple[list, dict]:
    """
    Execute Step 2: Smart Search Strategy (Google Shopping API or Web Search).

    Args:
        query: User's research query
        classification: Classification results from Step 1

    Returns:
        Tuple of (google_shopping_data, search_result)
    """
    print(f"\n[STEP 2/6] Determining search strategy...")

    # Check if this is a product price query - use Google Shopping API
    query_type = classification.get('query_type', '').lower()
    is_price_query = 'price' in query_type or 'product' in query_type or \
                     any(word in query.lower() for word in ['price', 'cost', 'buy', 'purchase', 'best deal'])

    google_shopping_data = []
    search_result = {'status': 'pending', 'urls': []}

    if is_price_query:
        print(f"[STEP 2/6] Detected price query - using Google Shopping API...")
        shopping_result = search_google_shopping(query, num_results=5)

        if shopping_result.get('status') == 'success':
            print(f"[STEP 2/6] OK Google Shopping API returned {shopping_result.get('num_results', 0)} results")
            google_shopping_data = shopping_result.get('results', [])

            # Also do regular web search as backup
            print(f"[STEP 2/6] Also searching web for additional sources...")
            search_result = search_web(query, num_results=3)
        else:
            error_msg = shopping_result.get('error_message', 'Unknown error')
            print(f"[STEP 2/6] WARN Google Shopping API failed: {error_msg}")
            print(f"[STEP 2/6] Falling back to web search...")
            search_result = search_web(query, num_results=5)
    else:
        print(f"[STEP 2/6] Using web search for general query...")
        search_result = search_web(query, num_results=5)

    if search_result.get('status') == 'success' and search_result.get('urls'):
        print(f"[STEP 2/6] OK Found {len(search_result['urls'])} URLs")
    else:
        if not google_shopping_data:  # Only warn if we don't have shopping data
            print(f"[STEP 2/6] WARN Search returned no URLs (status: {search_result.get('status')})")
            error_msg = search_result.get('error_message') or search_result.get('message', 'Unknown error')
            print(f"  Message: {error_msg}")

    return google_shopping_data, search_result
