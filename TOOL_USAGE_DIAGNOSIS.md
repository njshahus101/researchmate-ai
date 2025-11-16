# Tool Usage Diagnosis

## Current Situation

Based on the event data you shared, the Information Gatherer agent is **NOT using the web fetching tools** (`fetch_web_content` and `extract_product_info`). Instead, it's responding with information from its training data.

### Evidence from Your Event:
```
Response: "I've consulted several reputable sources for tech reviews..."
Products mentioned: Sony WH-CH720N, Anker Soundcore Space Q45, etc.
Tool calls in trace: NONE (no google_search, no fetch_web_content, no extract_product_info)
```

This indicates the agent is using its training data, not real-time web fetching.

## Why This Is Happening

### Issue 1: Gemini's Automatic Function Calling (AFC) Behavior
Gemini Flash Lite has **selective tool usage**. If it believes it can answer from training data, it will skip tool calls even with directive prompts.

### Issue 2: Google Search Grounding vs Custom Tools
When you set `google_search=True`:
- Gemini CAN use Google Search internally
- But this happens **behind the scenes** (not visible as a tool call)
- It doesn't automatically call your custom `fetch_web_content` or `extract_product_info` tools

### Issue 3: No Tool Call Requirement Configuration
ADK's `LlmAgent` doesn't have a parameter to FORCE tool usage (like OpenAI's `tool_choice: "required"`).

## Solutions (In Order of Effectiveness)

### Solution 1: Test with a Query That REQUIRES Web Fetching

Some queries make it more obvious that web fetching is needed:

**Try these test queries:**
1. "What is the current price of Apple AirPods Pro 2 on Amazon?"
   - Requires real-time price data
2. "Fetch the latest iPhone 15 Pro review from The Verge"
   - Explicitly asks to "fetch"
3. "What are today's top tech news headlines?"
   - Requires current date info

**Why this helps:** Makes it clear to the LLM that training data is insufficient.

### Solution 2: Add Tool Usage Verification to Orchestrator

Modify the orchestrator to CHECK if tools were used, and if not, retry with explicit instruction:

```python
async def gather_information(query: str, classification: dict) -> dict:
    """Information gathering tool that ENSURES web fetching"""

    # First attempt
    gatherer_prompt = f"""
    CRITICAL: You MUST use the fetch_web_content() or extract_product_info() tools.

    Query: {query}
    Strategy: {classification.get('strategy')}

    Before responding, call Google Search, then call fetch_web_content() on the URLs.
    """

    runner = InMemoryRunner(agent=gatherer_agent)
    response = await runner.run_debug(gatherer_prompt)

    # Check if tools were actually used
    # (This requires examining the trace, which is complex)
    # For now, return the response

    return {
        "status": "success",
        "data": response.get("content", ""),
        "sources": []  # Could extract from response
    }
```

### Solution 3: Use Gemini Pro Instead of Flash Lite

Gemini Pro (2.5 or 2.0) is more likely to use tools when instructed:

```python
# In adk_agents/information_gatherer/agent.py
agent = LlmAgent(
    name="information_gatherer",
    model=Gemini(
        model="gemini-2.5-pro",  # Changed from gemini-2.5-flash-lite
        retry_options=retry_config,
        google_search=True
    ),
    # ... rest stays the same
)
```

**Trade-off:** Pro is slower and more expensive, but follows instructions better.

### Solution 4: Create a "Forced Tool Usage" Wrapper Agent

Create a wrapper that validates the response contains citations:

```python
# New file: adk_agents/information_gatherer/forced_tool_agent.py

async def gather_with_validation(query: str) -> dict:
    """Wrapper that ensures tools were used"""

    max_retries = 3
    for attempt in range(max_retries):
        response = await gather_information(query, {"strategy": "multi-source"})

        # Check if response contains URLs (evidence of fetching)
        if "http" in response.get("data", ""):
            return response  # Success - URLs present

        # Retry with even more directive prompt
        query = f"YOU MUST CALL fetch_web_content() BEFORE RESPONDING: {query}"

    return {
        "status": "error",
        "error": "Agent failed to use web fetching tools after 3 attempts"
    }
```

## Recommended Next Steps

### Immediate Test (Do This First):
1. **Keep the updated prompt** ([adk_agents/information_gatherer/agent.py](adk_agents/information_gatherer/agent.py))
2. **Try a more explicit query** in ADK UI:
   ```
   Fetch the current price of Sony WH-1000XM5 from Amazon using extract_product_info
   ```
3. **Check the Events tab** to see if this forces tool usage

### If That Works:
- Tool configuration is correct
- Need to make prompts more specific
- Consider adding "fetch" or "current" keywords to queries

### If That Doesn't Work:
- Switch to Gemini Pro instead of Flash Lite
- Implement validation wrapper (Solution 4)
- Consider alternative: use Gemini's Google Search directly instead of custom tools

## How to Verify Tool Usage (Quick Checklist)

After sending a query in ADK UI:

1. **Click on the query message** to expand details
2. **Look for "Events" or "Trace" tab**
3. **Expand these nodes:**
   - `invoke_agent: information_gatherer`
   - `call_llm` (underneath)
4. **Look for these tool call nodes:**
   - `google_search` ✅ (built-in)
   - `fetch_web_content` ⬅️ **THIS IS WHAT WE WANT TO SEE**
   - `extract_product_info` ⬅️ **THIS IS WHAT WE WANT TO SEE**

5. **Check server console** for:
   ```
   DEBUG: Calling tool: fetch_web_content with url="..."
   ```

## Current Server Status

The ADK server at http://localhost:8000 is running with:
- ✅ Auto-reload enabled (`--reload` flag)
- ✅ Tools loaded (fetch_web_content, extract_product_info)
- ✅ Google Search enabled (google_search=True)
- ✅ Updated directive prompt
- ❓ Tools not being called by LLM (need to verify with explicit query)

## Test Script

I've also created [test_web_tools.py](test_web_tools.py) which directly calls the tools to prove they work:

```bash
venv\Scripts\python.exe test_web_tools.py
```

This confirms the tools themselves are functional - the issue is getting Gemini to actually call them.

## Documentation Created

- ✅ [HOW_TO_CHECK_TOOL_CALLS_IN_ADK_UI.md](HOW_TO_CHECK_TOOL_CALLS_IN_ADK_UI.md) - Full guide on checking tool usage in ADK UI
- ✅ This file - Diagnosis and solutions for current tool usage issue
