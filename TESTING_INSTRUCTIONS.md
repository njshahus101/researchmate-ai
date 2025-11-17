# Testing Instructions - ResearchMate AI

**Status:** ADK Web UI is running at http://127.0.0.1:8000

---

## ✅ Fixes Applied in This Session

### 1. API Quota Issue - FIXED
- **Problem:** Information Gatherer was using `gemini-2.0-flash-exp` which hit quota limits
- **Solution:** Switched back to `gemini-2.5-flash-lite`
- **File:** [adk_agents/information_gatherer/agent.py:46](adk_agents/information_gatherer/agent.py#L46)
- **Test result:** ✅ `test_direct_tools.py` completes without quota errors

### 2. Orchestrator Tool Calling - ENHANCED
- **Problem:** Orchestrator was calling `classify_user_query` but NOT calling `gather_information`
- **Solution:**
  - Made system prompt much more directive with explicit "MUST CALL BOTH TOOLS" instructions
  - Enhanced function docstring with "REQUIRED" and "ALWAYS call this function"
  - Added concrete workflow example
- **Files:**
  - [adk_agents/orchestrator/agent.py:285-319](adk_agents/orchestrator/agent.py#L285-L319) - System prompt
  - [adk_agents/orchestrator/agent.py:157-183](adk_agents/orchestrator/agent.py#L157-L183) - Function docstring
- **Status:** ⏳ Ready to test in ADK UI (this is the critical test)

### 3. Direct Tool Calling Architecture - WORKING
- **Confirmed:** The orchestrator's `gather_information()` function DOES execute direct tool calls
- **Evidence:** `test_direct_tools.py` shows `[ORCHESTRATOR]` debug messages appearing
- **What works:**
  - ✅ Orchestrator calls `search_web()` directly
  - ✅ Orchestrator calls `extract_product_info()` / `fetch_web_content()` directly
  - ✅ Orchestrator passes data to Information Gatherer for formatting
  - ✅ Information Gatherer successfully formats response

---

## 🧪 How to Test

### Test 1: Basic Query (Critical Test)
**Goal:** Verify orchestrator calls BOTH tools

1. Open ADK UI: http://127.0.0.1:8000
2. Enter query: `Fetch current price and details of Sony WH-1000XM5`
3. **Expected behavior:**
   - See classification appear (query type, complexity, strategy)
   - See `[ORCHESTRATOR]` messages in terminal showing direct tool calling
   - See final formatted response with information

**What to watch in terminal:**
```
[A2A] Calling Query Classifier for: Fetch current price...
[A2A] Classification complete: comparative - multi-source
[ORCHESTRATOR] Fetching real-time data for: Fetch current price...
[ORCHESTRATOR] Searching web for: Fetch current price and details of Sony WH-1000XM5
[A2A] Calling Information Gatherer to format X fetched results...
[A2A] Information formatting complete
```

**Success criteria:**
- ✅ Both `classify_user_query` AND `gather_information` are called
- ✅ User sees a complete response (not just classification)
- ✅ Terminal shows all `[ORCHESTRATOR]` debug messages

### Test 2: Different Query Types
Try different types of queries to ensure the workflow works consistently:

**Factual Query:**
```
What is the current weather in San Francisco?
```

**Comparative Query:**
```
Compare iPhone 15 Pro vs Samsung Galaxy S24
```

**Product Query:**
```
Best wireless keyboards under $100
```

### Test 3: Check Terminal Logs
After each query, check terminal for:
- Classification results
- `[ORCHESTRATOR]` messages confirming direct tool calling
- Any errors or quota issues

---

## ❌ Known Limitations

### Google Custom Search Not Configured
**Impact:** `search_web()` cannot fetch real URLs from Google

**Current behavior:**
```
[ORCHESTRATOR] Search returned no URLs (status: info)
message: "Google Custom Search not configured. Using Google Search grounding instead."
```

**Workaround:** The system uses a fallback response

**To fix (optional but recommended):**
1. Go to https://programmablesearchengine.google.com/
2. Create a Custom Search Engine
3. Copy the Search Engine ID
4. Add to `.env` file:
   ```
   GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
   ```
5. Restart ADK server:
   ```bash
   # Kill current server (Ctrl+C or kill process)
   venv\Scripts\adk.exe web adk_agents --port 8000 --reload
   ```

---

## 📊 Test Results Template

Use this template to document test results:

```
### Test: [Query text]
**Expected:** Classification → Information Gathering → Response
**Result:** [SUCCESS / PARTIAL / FAILED]

**Terminal output:**
[Paste relevant terminal logs]

**UI Response:**
[Paste or screenshot UI response]

**Issues:**
- [List any issues observed]

**Notes:**
[Additional observations]
```

---

## 🔍 Debugging Tips

### If orchestrator doesn't call gather_information:
1. Check terminal for `[ORCHESTRATOR]` messages
2. If missing, the LLM is still not calling the tool
3. Try adding even more directive language to the system prompt
4. Consider using `gemini-2.0-flash-exp` for orchestrator (more reliable at following instructions, but has quota limits)

### If you see quota errors:
1. Wait 1 minute for quota reset
2. Consider switching to paid tier
3. Use `gemini-2.5-flash-lite` for all agents

### If search returns no results:
1. This is expected - Google Custom Search not configured
2. The fallback should still work and return a response
3. To enable real search, follow "Google Custom Search Not Configured" steps above

---

## 📝 Next Steps After Testing

### If Test 1 SUCCEEDS (orchestrator calls both tools):
1. ✅ Core architecture is working
2. Configure Google Custom Search for real web fetching
3. Test with real product URLs
4. Consider adding more data sources

### If Test 1 FAILS (orchestrator only calls classification):
1. ❌ LLM is still not following tool calling instructions
2. Options:
   - Try `gemini-2.0-flash-exp` for orchestrator (more directive-following but quota limited)
   - Implement forced sequential calling (orchestrator Python code forces both tools)
   - Add tool forcing mechanism in ADK (if available)

---

## 🎯 Critical Question to Answer

**Does the orchestrator LLM call `gather_information` after `classify_user_query`?**

This is THE key question. Everything else is working (proven by `test_direct_tools.py`).

The only unknown is whether the enhanced system prompt is directive enough to force the LLM to call both tools.

**Test now to find out!**

Open http://127.0.0.1:8000 and try: `Fetch current price and details of Sony WH-1000XM5`
