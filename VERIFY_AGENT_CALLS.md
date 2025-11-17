# How to Verify Agent Calls in ADK UI

**Date:** 2025-11-16

This guide shows you how to verify that the `information_gatherer` and `query_classifier` agents are being called during pipeline execution.

---

## Method 1: Watch Terminal Logs (Easiest)

When the ADK UI server is running, **watch the terminal** where you ran:
```bash
venv\Scripts\adk.exe web adk_agents --port 8000 --reload
```

### What to Look For:

After sending a query in the browser, you'll see these **[A2A]** log messages in the terminal:

```
============================================================
FIXED PIPELINE EXECUTION
Query: Sony WH-1000XM5 price
============================================================

[STEP 1/4] Classifying query...
[A2A] Calling Query Classifier for: Sony WH-1000XM5 price...
[A2A] Query Classifier response received              <-- CLASSIFIER CALLED
[A2A] Classification complete: factual - quick-answer
[STEP 1/4] OK Classification complete

[STEP 2/4] Searching web for URLs...
[SEARCH] Calling Google Custom Search API...
[SEARCH] Found 3 results
[STEP 2/4] OK Found 3 URLs

[STEP 3/4] Fetching data from URLs...
[STEP 3/4] OK Fetched data from 3 sources

[STEP 4/4] Formatting results with Information Gatherer...
[A2A] Calling Information Gatherer agent to format results...  <-- GATHERER CALLED
[A2A] Information Gatherer response received          <-- GATHERER RESPONDED
[STEP 4/4] OK Formatting complete

============================================================
PIPELINE COMPLETE
============================================================
```

### Key Indicators:

✅ **`[A2A] Calling Query Classifier...`** - Query Classifier agent is being called
✅ **`[A2A] Query Classifier response received`** - Query Classifier responded
✅ **`[A2A] Calling Information Gatherer...`** - Information Gatherer agent is being called
✅ **`[A2A] Information Gatherer response received`** - Information Gatherer responded

---

## Method 2: ADK UI Debug Trace (Most Detailed)

The ADK UI has a built-in debug/trace viewer that shows the complete execution flow.

### Steps:

1. **Open the ADK UI** in your browser: http://127.0.0.1:8000

2. **Send a query** (e.g., "Sony WH-1000XM5 price")

3. **Look for the Debug/Trace view**:
   - After the response appears, look for a **"View Trace"**, **"Debug"**, or **"Session Details"** link/button
   - This might be in the sidebar, at the top, or near the conversation

4. **Inspect the trace**:
   - The trace shows all agent calls in order
   - You should see entries for:
     - `research_orchestrator` (root agent)
     - `query_classifier` (called by orchestrator)
     - `information_gatherer` (called by orchestrator)

### What the Trace Shows:

- **Agent names** that were called
- **Prompts** sent to each agent
- **Responses** from each agent
- **Tool calls** made by agents
- **Execution timestamps**

---

## Method 3: Check Session Responses (ADK API)

The ADK UI uses a REST API endpoint to fetch session traces.

### Direct API Access:

1. **Get your session ID** from the browser:
   - Open browser DevTools (F12)
   - Look at Network tab
   - Find a request to `/apps/orchestrator/users/user/sessions`
   - Copy the session ID (e.g., `c1443bb7-99ca-47f8-8607-9f7dc15e7d46`)

2. **Access the debug trace**:
   ```
   http://127.0.0.1:8000/debug/trace/session/YOUR_SESSION_ID_HERE
   ```

3. **Look for agent names** in the JSON response:
   - Search for `"query_classifier"`
   - Search for `"information_gatherer"`

---

## Method 4: Enhanced Logging in Code

The orchestrator now has enhanced logging that clearly shows A2A calls.

### Log Patterns to Watch:

**When Query Classifier is called:**
```
[A2A] Calling Query Classifier for: [query text]...
[A2A] Query Classifier response received
```

**When Information Gatherer is called:**
```
[A2A] Calling Information Gatherer agent to format results...
[A2A] Information Gatherer response received
```

These logs appear in:
- Terminal where ADK server is running
- Test script output when running `test_complete_pipeline.py`

---

## Verification Checklist

Use this checklist to confirm both agents are being called:

### For Each Query:

- [ ] Terminal shows `[A2A] Calling Query Classifier...`
- [ ] Terminal shows `[A2A] Query Classifier response received`
- [ ] Terminal shows classification result (e.g., "factual - quick-answer")
- [ ] Terminal shows `[A2A] Calling Information Gatherer...`
- [ ] Terminal shows `[A2A] Information Gatherer response received`
- [ ] Browser shows formatted response (proof Information Gatherer did the formatting)

### Expected Flow:

```
User sends query in browser
    ↓
Orchestrator receives query
    ↓
[STEP 1] Orchestrator calls Query Classifier (A2A)
    ← Query Classifier returns classification
    ↓
[STEP 2] Orchestrator calls search_web() tool
    ← Returns URLs
    ↓
[STEP 3] Orchestrator calls extract/fetch tools
    ← Returns fetched data
    ↓
[STEP 4] Orchestrator calls Information Gatherer (A2A)
    ← Information Gatherer returns formatted response
    ↓
Orchestrator returns final result to user in browser
```

---

## Example Terminal Output

Here's a complete example showing both agents being called:

```
============================================================
FIXED PIPELINE EXECUTION
Query: Sony WH-1000XM5 headphones price Amazon
============================================================

[STEP 1/4] Classifying query...

[A2A] Calling Query Classifier for: Sony WH-1000XM5 headphones price Amazon...

 ### Created new session: debug_session_id

User > Sony WH-1000XM5 headphones price Amazon
query_classifier > {
    "query_type": "factual",
    "complexity_score": 2,
    "research_strategy": "quick-answer",
    "key_topics": ["Sony WH-1000XM5", "price", "Amazon"]
}

[A2A] Query Classifier response received
[A2A] Classification complete: factual - quick-answer
[STEP 1/4] OK Classification complete
  Type: factual
  Strategy: quick-answer
  Complexity: 2/10

[STEP 2/4] Searching web for URLs...
[SEARCH] Calling Google Custom Search API...
[SEARCH] Query: Sony WH-1000XM5 headphones price Amazon
[SEARCH] Search Engine ID: 055554230dce04528
[SEARCH] Response status: 200
[SEARCH] Found 3 results
[STEP 2/4] OK Found 3 URLs

[STEP 3/4] Fetching data from URLs...
  [1/3] Extracting product: https://www.amazon.com/...
  [1/3] OK Success
  [2/3] Fetching content: https://www.reddit.com/...
  [2/3] OK Success
  [3/3] Extracting product: https://www.amazon.com/...
  [3/3] OK Success
[STEP 3/4] OK Fetched data from 3 sources

[STEP 4/4] Formatting results with Information Gatherer...
[A2A] Calling Information Gatherer agent to format results...

 ### Created new session: debug_session_id

User > Format the following REAL-TIME FETCHED DATA...
information_gatherer > Based on the fetched data:

**Sony WH-1000XM5 Deal Mentioned:**

*   **Price:** $311 (originally $499, with a $188 discount)
*   **Source:** Amazon.ca (mentioned on Reddit)

[A2A] Information Gatherer response received
[STEP 4/4] OK Formatting complete

============================================================
PIPELINE COMPLETE
============================================================
```

**Key Evidence:**
- `query_classifier >` shows Query Classifier agent responding
- `information_gatherer >` shows Information Gatherer agent responding
- `[A2A]` logs confirm both agents were called via Agent-to-Agent protocol

---

## Troubleshooting

### If you DON'T see `[A2A]` logs:

1. **Restart the ADK server**:
   ```bash
   # Press Ctrl+C to stop
   venv\Scripts\adk.exe web adk_agents --port 8000 --reload
   ```

2. **Verify the code changes were saved**:
   - Check `adk_agents/orchestrator/agent.py` contains the new log statements
   - Look for `print(f"[A2A] Calling Information Gatherer...")`

3. **Check if server is auto-reloading**:
   - The `--reload` flag should auto-reload on file changes
   - But sometimes a manual restart is needed

### If agents are NOT being called:

1. **Check the pipeline execution logs** - all 4 steps should execute
2. **Review orchestrator agent code** - ensure `execute_fixed_pipeline()` calls both agents
3. **Check for errors** in terminal - agent initialization errors would prevent calls

---

## Summary

**Easiest Method:** Watch the terminal for `[A2A]` log messages while testing in the browser.

You should see:
1. `[A2A] Calling Query Classifier...` - STEP 1
2. `[A2A] Query Classifier response received`
3. `[A2A] Calling Information Gatherer...` - STEP 4
4. `[A2A] Information Gatherer response received`

If you see all four messages, both agents are being called successfully! ✅
