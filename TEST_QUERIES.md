# Test Queries for Tool Usage Verification

Use these queries in the ADK UI to test if the Information Gatherer agent is actually using the web fetching tools.

## Test 1: Direct URL Test (Easiest to Verify)

**Query:**
```
Use extract_product_info to fetch data from this URL: https://www.amazon.com/Sony-WH-1000XM5-Headphones-Hands-Free-WH1000XM5/dp/B09XS7JWHH
```

**Expected behavior:**
1. Agent should call `extract_product_info(url="https://www.amazon.com/Sony-WH-1000XM5-Headphones-Hands-Free-WH1000XM5/dp/B09XS7JWHH")`
2. Response should include actual price from Amazon
3. Events tab should show the tool call

**What to check:**
- Open Events tab → expand `invoke_agent: information_gatherer` → expand `call_llm`
- Look for `extract_product_info` tool call node
- Check the result shows `"status": "success"` and actual product data

---

## Test 2: Simple Price Check (Requires Google Search + Tool)

**Query:**
```
What is the current price of the Sony WH-1000XM5 on Amazon? Use the extract_product_info tool.
```

**Expected behavior:**
1. Agent uses Google Search to find Amazon URL
2. Agent calls `extract_product_info(url="<found URL>")`
3. Response includes real price and URL citation

**What to check:**
- Events tab should show `google_search` usage (if visible)
- Should show `extract_product_info` tool call with a URL parameter
- Response should cite the actual Amazon URL

---

## Test 3: Web Content Fetch (Tests fetch_web_content)

**Query:**
```
Use fetch_web_content to get information from https://en.wikipedia.org/wiki/Tokyo
```

**Expected behavior:**
1. Agent calls `fetch_web_content(url="https://en.wikipedia.org/wiki/Tokyo")`
2. Response includes content from Wikipedia
3. Response cites the Wikipedia URL

**What to check:**
- Events tab shows `fetch_web_content` tool call
- Tool result shows `"status": "success"` and content from Wikipedia
- Response includes facts from the fetched content (like population, area, etc.)

---

## Test 4: Product Comparison (Most Complex)

**Query:**
```
Compare Sony WH-1000XM5 and Bose QuietComfort 45. Use extract_product_info for both products.
```

**Expected behavior:**
1. Google Search for both products
2. Call `extract_product_info(url=...)` for Sony
3. Call `extract_product_info(url=...)` for Bose
4. Present comparison with real prices from both

**What to check:**
- Events tab shows TWO separate `extract_product_info` calls
- Each tool call has a different Amazon URL
- Response includes real prices for both products

---

## How to Check Tool Calls in ADK UI

After sending any of the above queries:

1. **Find your query** in the chat interface
2. **Click to expand** the query details
3. **Navigate to Events/Trace tab**
4. **Expand the tree:**
   ```
   [▼] invoke_agent: information_gatherer
       [▼] call_llm
           [🔧] extract_product_info  ← YOU SHOULD SEE THIS!
               [✓] Result: {"status": "success", ...}
   ```

5. **Check the tool parameters:**
   - Should show `url="https://..."` (CORRECT)
   - Should NOT show `product_name=...` or `platform=...` (INCORRECT)

6. **Check the tool result:**
   - Should show `"status": "success"`
   - Should show actual data (price, product_name, etc.)
   - If `"status": "error"`, check the `"error_message"`

---

## Troubleshooting

### If you DON'T see tool calls:

**Problem:** Agent is not calling tools at all

**Solutions:**
1. Try Test 1 (direct URL) - this is the most explicit
2. Check server logs for errors
3. Verify tools are loaded (check startup logs for "Information Gatherer tools loaded")
4. Try switching to `gemini-2.5-pro` in [adk_agents/information_gatherer/agent.py](adk_agents/information_gatherer/agent.py:43)

### If tool calls have wrong parameters:

**Problem:** Agent is calling `extract_product_info(product_name=..., platform=...)` instead of `extract_product_info(url=...)`

**Solution:** The updated prompt should fix this, but if it persists:
1. Refresh the ADK UI page
2. Start a new chat session
3. Verify the server reloaded (check logs for "Information Gatherer agent 'information_gatherer' initialized")

### If tool calls fail with errors:

**Problem:** Tool is called correctly but returns `"status": "error"`

**Check:**
1. Look at the error message in the tool result
2. Common issues:
   - Network timeout → increase timeout in [tools/research_tools.py](tools/research_tools.py:55)
   - Invalid URL → check the URL format
   - Website blocking → some sites block automated requests

---

## Expected Server Log Output

When tools are working correctly, you should see:

```
INFO: Information Gatherer tools loaded:
  - fetch_web_content (web page fetching)
  - extract_product_info (product data extraction)
Information Gatherer agent 'information_gatherer' initialized

[When query is processed:]
DEBUG: Calling tool: extract_product_info with url="https://amazon.com/..."
DEBUG: Tool result: {"status": "success", "product_name": "...", "price": "$..."}
```

If you don't see the "Calling tool" lines, the agent is not using the tools.

---

## Quick Verification Script

You can also verify tools work directly with:

```bash
venv\Scripts\python.exe test_web_tools.py
```

This confirms the tools themselves are functional, independent of the LLM calling them.
