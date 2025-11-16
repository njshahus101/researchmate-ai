# Next Steps - Tool Usage Integration

## Current Status

✅ **Completed:**
- Information Gatherer agent with web fetching tools created
- Tools integrated: `fetch_web_content()` and `extract_product_info()`
- Updated agent instructions to force tool usage
- Fixed parameter issues (tools need URLs, not product names)
- Created comprehensive documentation

📝 **Documentation Created:**
- [HOW_TO_CHECK_TOOL_CALLS_IN_ADK_UI.md](HOW_TO_CHECK_TOOL_CALLS_IN_ADK_UI.md) - How to verify tools in UI
- [TOOL_USAGE_DIAGNOSIS.md](TOOL_USAGE_DIAGNOSIS.md) - Why tools aren't being called
- [TEST_QUERIES.md](TEST_QUERIES.md) - Test queries to verify tool usage

⚠️ **Current Issue:**
- Gemini Flash Lite is NOT using the web fetching tools
- Agent responds with training data instead of calling tools
- When prompted to use tools, agent hallucinates wrong parameters

## Immediate Action Required

### Option 1: Restart ADK Server (Recommended)

The server needs to reload the updated Information Gatherer agent:

```bash
# Stop current server (Ctrl+C in the terminal, or kill the process)
# Then restart:
venv\Scripts\adk.exe web adk_agents --port 8000 --reload
```

After restart:
1. Go to http://localhost:8000
2. Start a **NEW chat session**
3. Try Test Query 1 from [TEST_QUERIES.md](TEST_QUERIES.md):

```
Use extract_product_info to fetch data from this URL: https://www.amazon.com/Sony-WH-1000XM5-Headphones-Hands-Free-WH1000XM5/dp/B09XS7JWHH
```

### Option 2: Switch to Gemini Pro (More Reliable)

If Test Query 1 still doesn't work after restart, Gemini Flash Lite may be too aggressive at skipping tools.

**Edit [adk_agents/information_gatherer/agent.py](adk_agents/information_gatherer/agent.py:43):**

```python
# Change from:
model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config, google_search=True),

# To:
model=Gemini(model="gemini-2.5-pro", retry_options=retry_config, google_search=True),
```

Then restart the server.

**Trade-off:** Pro is slower and costs more, but follows tool usage instructions better.

## How to Verify Tool Usage

After restarting and sending a test query:

1. **Check Events Tab:**
   - Expand your query in the UI
   - Click "Events" or "Trace" tab
   - Expand: `invoke_agent: information_gatherer` → `call_llm`
   - Look for `extract_product_info` or `fetch_web_content` tool calls

2. **Check Server Logs:**
   - Look for lines like:
     ```
     [A2A] Calling Information Gatherer with strategy: ...
     ```
   - Check for tool call activity in the logs

3. **Check Response Content:**
   - Response should cite actual URLs
   - Should include real prices/data fetched from web
   - Should NOT say "based on available information"

## Expected vs Actual Behavior

### ✅ What SHOULD Happen (Expected):

**Query:** "Use extract_product_info to fetch data from this URL: https://www.amazon.com/..."

**Expected Flow:**
1. Orchestrator calls `classify_user_query()`
2. Orchestrator calls `gather_information()`
3. Information Gatherer calls `extract_product_info(url="https://www.amazon.com/...")`
4. Tool returns `{"status": "success", "product_name": "...", "price": "$...", ...}`
5. Agent presents price and product data from tool result

**Events Tab Shows:**
```
invoke_agent: information_gatherer
  └─ call_llm
      └─ extract_product_info(url="https://www.amazon.com/...")
          └─ Result: {"status": "success", "price": "$348.00", ...}
```

### ❌ What's HAPPENING Now (Actual):

**Behavior 1:** Agent responds with training data, no tool calls
- Events tab shows no `extract_product_info` calls
- Response includes generic product info from training data

**Behavior 2:** Agent tries to call tool with wrong parameters
- Events tab shows `extract_product_info(product_name="...", platform="...")`
- This fails because those parameters don't exist

## Troubleshooting

### If tools still aren't called after restart:

1. **Verify tools are loaded:**
   - Check server startup logs for:
     ```
     Information Gatherer tools loaded:
       - fetch_web_content (web page fetching)
       - extract_product_info (product data extraction)
     ```

2. **Try the direct tool test:**
   ```bash
   venv\Scripts\python.exe test_web_tools.py
   ```
   - This verifies tools work outside of LLM context

3. **Check ADK version:**
   - Some ADK versions have issues with function calling
   - Consider updating: `pip install -U google-adk`

4. **Enable debug logging:**
   - Add to top of [adk_agents/information_gatherer/agent.py](adk_agents/information_gatherer/agent.py):
     ```python
     import logging
     logging.basicConfig(level=logging.DEBUG)
     ```

### If tool calls fail with errors:

Check the error in the tool result:
- **Timeout errors:** Increase timeout in [tools/research_tools.py](tools/research_tools.py:55)
- **Invalid URL:** Verify the URL format is correct
- **403/blocking:** Some sites block automated requests

## Alternative: Use Grounding Instead of Custom Tools

If we can't get custom tools to work reliably, we can use Gemini's built-in Google Search grounding:

**Pros:**
- Built directly into Gemini, always works
- Automatic source citations
- No custom tool configuration needed

**Cons:**
- Less control over what's fetched
- Can't extract structured product data
- May not fetch from specific URLs

This is already enabled with `google_search=True`, but the agent is using it inconsistently.

## Summary

**Quick Test:**
1. Restart ADK server
2. Open new chat session
3. Try: `Use extract_product_info to fetch data from this URL: https://www.amazon.com/Sony-WH-1000XM5-Headphones-Hands-Free-WH1000XM5/dp/B09XS7JWHH`
4. Check Events tab for tool call

**If that doesn't work:**
- Switch to `gemini-2.5-pro` instead of `flash-lite`
- Consider using only Google Search grounding without custom tools

**Files to Check:**
- [adk_agents/information_gatherer/agent.py](adk_agents/information_gatherer/agent.py) - Agent configuration
- [tools/research_tools.py](tools/research_tools.py) - Tool implementations
- [TEST_QUERIES.md](TEST_QUERIES.md) - More test queries to try
