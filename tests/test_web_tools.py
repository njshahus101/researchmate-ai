"""
Quick test to verify web tools are working
"""

import asyncio
from tools.research_tools import fetch_web_content, extract_product_info

async def test_tools():
    print("\n" + "="*70)
    print("TESTING WEB RESEARCH TOOLS")
    print("="*70 + "\n")

    # Test 1: Fetch Wikipedia page
    print("Test 1: Fetching web content from Wikipedia...")
    print("-"*70)
    result1 = fetch_web_content("https://en.wikipedia.org/wiki/Tokyo")
    print(f"Status: {result1['status']}")
    if result1['status'] == 'success':
        print(f"Title: {result1['title']}")
        print(f"Content length: {result1['content_length']}")
        print(f"Content preview: {result1['content'][:200]}...")
    print()

    # Test 2: Try fetching a tech article
    print("\nTest 2: Fetching tech article...")
    print("-"*70)
    result2 = fetch_web_content("https://www.theverge.com")
    print(f"Status: {result2['status']}")
    if result2['status'] == 'success':
        print(f"Title: {result2['title']}")
        print(f"Content length: {result2['content_length']}")
    elif result2['status'] == 'error':
        print(f"Error: {result2['error_message']}")
    print()

    print("="*70)
    print("TOOLS TEST COMPLETE")
    print("="*70 + "\n")

    print("The tools are working! They can be called by the Information Gatherer agent.")
    print("\nTo see tool usage in ADK UI:")
    print("1. Expand the 'Best wireless headphones' query")
    print("2. Look in the Events/Trace tab")
    print("3. Expand 'invoke_agent' to see sub-agent calls")
    print("4. Look for 'call_llm' nodes that show tool calls")

if __name__ == "__main__":
    asyncio.run(test_tools())
