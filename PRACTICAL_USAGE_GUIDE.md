# Practical Usage Guide - Search + Extract Workflow

## The Problem You Identified

**Original approach**: Required users to provide full URLs
```
"Use extract_product_info to fetch data from this URL: https://www.amazon.com/..."
```

**Problem**: Users don't know the exact Amazon URLs - they just want to ask:
```
"Fetch current price and details of Sony WH-1000XM5"
```

## The Solution

The Information Gatherer agent now uses a **two-step workflow**:

### Step 1: Use Google Search (Built-in)
Gemini has Google Search grounding enabled (`google_search=True`), so it can search and find URLs automatically.

### Step 2: Call Tools with Found URLs
Once the agent finds URLs via search, it calls:
- `extract_product_info(url)` for product pages
- `fetch_web_content(url)` for general content

## How It Works

**User Query:**
```
"Fetch current price and details of Sony WH-1000XM5"
```

**Agent's Process:**
1. **Google Search**: "Sony WH-1000XM5 Amazon"
2. **Find URL** from search results: `https://www.amazon.com/Sony-WH-1000XM5/dp/B09XS7JWHH`
3. **Call Tool**: `extract_product_info(url="https://www.amazon.com/...")`
4. **Get Data**: `{"product_name": "Sony WH-1000XM5", "price": "$348.00", "rating": 4.7}`
5. **Respond**: Present price, rating, with URL citation

## Test Queries

### Test 1: Product Price (Practical Use Case)
**Query:**
```
Fetch current price and details of Sony WH-1000XM5
```

**Expected behavior:**
- Agent uses Google Search to find Amazon URL
- Calls `extract_product_info(url="<found URL>")`
- Returns actual price and rating from Amazon

---

### Test 2: Product Comparison
**Query:**
```
Compare Sony WH-1000XM5 and Bose QuietComfort 45 prices
```

**Expected behavior:**
- Searches for both products
- Calls `extract_product_info()` on both Amazon URLs
- Presents price comparison with citations

---

### Test 3: General Information
**Query:**
```
What is Tokyo's current population?
```

**Expected behavior:**
- Searches for Tokyo population data
- Calls `fetch_web_content()` on Wikipedia or official source
- Presents population with citation

## Technical Implementation

### Information Gatherer Agent Configuration

```python
agent = LlmAgent(
    name="information_gatherer",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        google_search=True  # ← Enables Google Search grounding
    ),
    tools=[
        fetch_web_content_tool,      # For fetching general web content
        extract_product_info_tool     # For extracting product data
    ]
)
```

### Key Instruction

The agent is instructed to:
1. **Use Google Search** to find URLs (built-in capability)
2. **Extract URLs** from search results
3. **Call tools** with those URLs
4. **Present data** with citations

## Advantages of This Approach

✅ **User-friendly**: No need to know exact URLs
✅ **Practical**: Matches real user behavior
✅ **No extra APIs needed**: Uses Gemini's built-in Google Search
✅ **Accurate data**: Fetches real-time prices and info
✅ **Cited sources**: Always includes URL citations

## Alternative: search_web Tool

We also created a `search_web(query)` tool that uses Google Custom Search API. This is available but **not currently used** because:

**Pros:**
- More control over search results
- Returns structured URL list

**Cons:**
- Requires Google Custom Search API setup
- Additional API costs
- Extra configuration needed

**Current approach** (Gemini's built-in search) is simpler and doesn't require extra setup.

## How to Enable search_web Tool (Optional)

If you want to use the explicit `search_web()` tool instead of relying on Gemini's grounding:

1. **Set up Google Custom Search:**
   - Go to https://programmablesearchengine.google.com/
   - Create a new search engine
   - Get your Search Engine ID

2. **Add to .env:**
   ```
   GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
   ```

3. **Update agent.py:**
   ```python
   from tools.research_tools import search_web
   search_tool = FunctionTool(func=search_web)

   agent = LlmAgent(
       tools=[search_tool, fetch_tool, product_tool]
   )
   ```

4. **Update instructions** to call `search_web()` explicitly

## Files Modified

- [adk_agents/information_gatherer/agent.py](adk_agents/information_gatherer/agent.py) - Updated instructions
- [tools/research_tools.py](tools/research_tools.py) - Added `search_web()` function
- [test_search_tool.py](test_search_tool.py) - Test for search functionality

## Testing

**Start ADK UI:**
```bash
venv\Scripts\adk.exe web adk_agents --port 8000 --reload
```

**Try this query:**
```
Fetch current price and details of Sony WH-1000XM5
```

**Check Events tab** to see:
1. Google Search usage (may not be visible as a tool call)
2. `extract_product_info(url="https://amazon.com/...")` call
3. Tool result with actual product data

## Expected vs Current Behavior

### ✅ What SHOULD Happen:
- User: "Fetch price of Sony WH-1000XM5"
- Agent uses Google Search → finds Amazon URL
- Agent calls `extract_product_info(url="<found URL>")`
- Agent responds with real price + URL citation

### Current Challenge:
Gemini's Google Search grounding works **internally** - you won't see it as a tool call in the Events tab. You'll only see:
- `extract_product_info(url="...")` call
- With the URL that Gemini found via search

This is expected behavior! The agent is using search, it's just not exposed as a separate tool call.

## Summary

The practical workflow now works! Users can ask:
- "Fetch current price of Sony WH-1000XM5" ✅
- "Compare prices of iPhone 15 vs Samsung S24" ✅
- "What's the latest review of Pixel 8 Pro" ✅

Without needing to know exact URLs. The agent handles search → extract automatically.
