# How to Check Tool Calls in ADK UI

This guide shows you how to verify that the Information Gatherer agent is actually using Google Search and web fetching tools when processing queries.

## Quick Start

1. **Start ADK UI**:
   ```bash
   adk web adk_agents --port 8000
   ```

2. **Open browser**: Navigate to `http://localhost:8000`

3. **Send a test query**: Try "Best wireless headphones under $200"

## Method 1: Using the Events Tab (Primary Method)

### Step-by-Step Instructions:

1. **Locate your query in the UI**:
   - After sending a query, you'll see it listed in the chat interface
   - The query will show the orchestrator's final response

2. **Expand the query details**:
   - Click on your query message to expand it
   - Look for an **"Events"** or **"Trace"** tab/button
   - Click to open the execution trace

3. **Navigate the trace tree**:
   ```
   Root: research_orchestrator (your query)
   └─ invoke_agent: information_gatherer
      └─ call_llm (this is where tool calls happen)
         ├─ Tool Call: google_search
         │  └─ Result: [search results with URLs]
         ├─ Tool Call: fetch_web_content
         │  └─ Result: {"status": "success", "title": "...", "content": "..."}
         └─ Tool Call: extract_product_info
            └─ Result: {"status": "success", "product_name": "...", "price": "..."}
   ```

4. **What to look for**:
   - **google_search** nodes: Shows search queries and returned URLs
   - **fetch_web_content** nodes: Shows fetched webpage content
   - **extract_product_info** nodes: Shows extracted product data
   - Check the **Result** under each tool call for actual fetched data

### Visual Navigation:

```
[Query: "Best wireless headphones under $200"]
  │
  ├─ [▼] Events/Trace (Click here!)
  │    │
  │    └─ [▼] invoke_agent: information_gatherer (Expand this!)
  │         │
  │         └─ [▼] call_llm (Expand this!)
  │              │
  │              ├─ [🔧] google_search: "best wireless headphones under $200 2024"
  │              │    └─ [✓] Result: [...URLs...]
  │              │
  │              ├─ [🔧] fetch_web_content: "https://example.com/review"
  │              │    └─ [✓] Result: {"status": "success", "title": "...", ...}
  │              │
  │              └─ [🔧] extract_product_info: "https://amazon.com/product/..."
  │                   └─ [✓] Result: {"product_name": "...", "price": "$199.99", ...}
```

## Method 2: Check Server Logs (Console Output)

When you run `adk web`, the console shows detailed logs:

### What to look for in logs:

```
INFO: Information Gatherer tools loaded:
  - fetch_web_content (web page fetching)
  - extract_product_info (product data extraction)

[During query processing, you might see:]
DEBUG: Calling tool: google_search with query="..."
DEBUG: Tool result: [URLs...]
DEBUG: Calling tool: fetch_web_content with url="..."
DEBUG: Tool result: {"status": "success", ...}
```

### Enable verbose logging (if needed):

Add this to your agent.py to see more detailed tool call information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Method 3: Check the Response Content

Even without looking at traces, you can verify tool usage by checking if the response contains:

### ✅ Signs tools ARE being used:
- Actual URLs cited (e.g., "According to https://example.com...")
- Real prices from web pages (e.g., "$199.99 on Amazon")
- Recent dates/data that wouldn't be in training data
- Specific product specifications from real product pages
- Direct quotes from fetched web content

### ❌ Signs tools are NOT being used:
- Generic responses without URLs
- Vague information without specifics
- "I don't have access to real-time data" (should never say this!)
- Information that seems outdated or generic

## Testing Examples

### Test Query 1: Quick Answer (Should use Google Search + fetch_web_content)
**Query**: "What is Tokyo's population?"

**Expected tool calls**:
1. `google_search("Tokyo population 2024")`
2. `fetch_web_content("https://wikipedia.org/wiki/Tokyo")` or similar

**Expected response**: Should cite actual URL and give current population figure

---

### Test Query 2: Product Comparison (Should use all tools)
**Query**: "Best wireless headphones under $200"

**Expected tool calls**:
1. `google_search("best wireless headphones under $200 2024")`
2. `extract_product_info("https://amazon.com/product/...")` (for each product)
3. `fetch_web_content("https://wirecutter.com/reviews/...")` (for reviews)

**Expected response**:
- Comparison table with actual products
- Real prices from fetched pages
- Ratings and specs from actual product pages
- URLs cited for each recommendation

---

### Test Query 3: Deep Research (Should use multiple fetches)
**Query**: "Compare iPhone 15 Pro vs Samsung S24 Ultra"

**Expected tool calls**:
1. `google_search("iPhone 15 Pro vs Samsung S24 Ultra comparison 2024")`
2. `extract_product_info("https://apple.com/iphone-15-pro")`
3. `extract_product_info("https://samsung.com/s24-ultra")`
4. `fetch_web_content("https://theverge.com/comparison/...")` (multiple review sites)

**Expected response**: Detailed comparison with real specs and prices from fetched data

## Troubleshooting

### Issue: No tool calls visible in Events tab

**Possible causes**:
1. **ADK UI version**: Some versions hide tool calls by default
2. **Need to expand nodes**: Click on all expandable nodes in the trace tree
3. **Check different tabs**: Look for "Events", "Trace", "Debug", or "Details" tabs

**Solution**:
- Try expanding ALL nodes in the trace tree
- Check server console logs as backup
- Verify tools are loaded (check startup logs)

### Issue: Tools are called but returning errors

**Check**:
- Tool result in trace shows `"status": "error"`
- Check error message in result
- Common issues:
  - Network timeouts (increase timeout in research_tools.py)
  - Invalid URLs (check the URLs being fetched)
  - Website blocking requests (some sites block automated requests)

**Solution**:
```python
# In tools/research_tools.py, increase timeout:
def fetch_web_content(url: str) -> Dict:
    return fetch_webpage_content(url, timeout=30)  # Increased from 10
```

### Issue: Agent not using tools at all

**Symptoms**: No tool calls in trace, generic responses

**Solution**:
1. Check that tools are listed in agent initialization logs
2. Verify the updated prompt in [adk_agents/information_gatherer/agent.py](adk_agents/information_gatherer/agent.py)
3. Try a very directive query: "Use Google Search to find and fetch the best wireless headphones under $200"
4. Check if model is using `google_search=True` (verify in agent.py line 43)

## Summary Checklist

Use this checklist to verify tools are working:

- [ ] Started ADK UI and opened in browser
- [ ] Sent test query (e.g., "Best wireless headphones under $200")
- [ ] Opened Events/Trace tab for the query
- [ ] Expanded `invoke_agent: information_gatherer` node
- [ ] Expanded `call_llm` node underneath
- [ ] Saw `google_search` tool call with search results
- [ ] Saw `fetch_web_content` or `extract_product_info` tool calls
- [ ] Verified tool results show actual fetched data
- [ ] Response includes cited URLs and real data from web

If all checkboxes are checked, your web fetching integration is working! 🎉

## Quick Verification Command

You can also run the standalone test to verify tools work:

```bash
venv\Scripts\python.exe test_web_tools.py
```

This directly calls the tools and shows their output, confirming they're functional before testing in ADK UI.
