# Testing Content Analysis Agent via ADK UI

## Step-by-Step Guide to Test with ADK Web UI

### Prerequisites

1. **Google API Keys configured** in `.env`:
   ```bash
   GOOGLE_API_KEY=your_google_api_key_here
   GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
   ```

2. **Virtual environment activated**:
   ```bash
   # On Windows
   venv\Scripts\activate

   # On Mac/Linux
   source venv/bin/activate
   ```

---

## Step 1: Start ADK Web UI

```bash
# Navigate to the orchestrator directory
cd adk_agents/orchestrator

# Launch ADK Web UI
adk web
```

You should see output like:
```
Agent 'research_orchestrator' initialized successfully with FIXED PIPELINE
  - Query Classifier agent loaded
  - Information Gatherer agent loaded
  - Content Analysis agent loaded ✨
  - Fixed pipeline: Classify -> Search -> Fetch -> Format -> Analyze
  - No LLM decision-making - deterministic execution
Ready for ADK Web UI

Starting ADK Web UI...
Open browser at: http://localhost:8080
```

---

## Step 2: Open Browser

Navigate to: **http://localhost:8080**

You should see the ADK Web UI interface with the orchestrator agent ready.

---

## Step 3: Test with Sample Prompts

### Sample Prompt #1: Product Price Comparison (Best for seeing Content Analysis)

**Prompt:**
```
Find the current price of Sony WH-1000XM5 headphones from multiple retailers
```

**What to Expect:**

1. **Pipeline Execution Log** (in terminal):
   ```
   ============================================================
   FIXED PIPELINE EXECUTION
   Query: Find the current price of Sony WH-1000XM5...
   ============================================================

   [STEP 1/5] Classifying query...
   [A2A] Calling Query Classifier for: Find the current price...
   [A2A] Query Classifier response received
   [STEP 1/5] OK Classification complete
     Type: comparative
     Strategy: multi-source
     Complexity: 5/10

   [STEP 2/5] Searching web for URLs...
   [SEARCH] Calling Google Custom Search API...
   [STEP 2/5] OK Found 5 URLs

   [STEP 3/5] Fetching data from URLs...
   [1/5] Extracting product: https://www.amazon.com/...
   [1/5] OK Success (useful data)
   [2/5] Extracting product: https://www.bestbuy.com/...
   [2/5] OK Success (useful data)
   [STEP 3/5] OK Fetched data from 2 sources

   [STEP 4/5] Formatting results with Information Gatherer...
   [A2A] Calling Information Gatherer agent to format results...
   [A2A] Information Gatherer response received
   [STEP 4/5] OK Formatting complete

   [STEP 5/5] Analyzing content credibility and extracting facts... ✨
   [A2A] Calling Content Analysis agent...
   [A2A] Content Analysis response received
   [STEP 5/5] OK Analysis complete - 2 credible sources found ✨

   ============================================================
   PIPELINE COMPLETE
   ============================================================
   ```

2. **UI Response** (in browser):
   The agent will return a formatted response with the Content Analysis embedded:

   ```
   Based on real-time research from multiple sources:

   **Sony WH-1000XM5 Wireless Headphones**

   **Pricing Information:**
   - Amazon: $348.00 USD
   - Best Buy: $379.99 USD
   - Price Range: $348 - $379.99

   **Ratings:**
   - Amazon: 4.7/5 (2,543 reviews)
   - Best Buy: 4.6/5 (892 reviews)

   **Key Features:**
   - Industry-leading Active Noise Cancellation
   - 30-hour battery life
   - Bluetooth 5.2 connectivity
   - Premium sound quality

   **Source Credibility Analysis:**
   - Amazon.com: 85/100 (Highly Credible)
   - BestBuy.com: 75/100 (Moderately Credible)

   **Price Conflict Detected:**
   The price varies by $31.99 between sources. Amazon ($348.00)
   is recommended based on higher credibility score and more reviews.

   ---

   Sources fetched: 2
   All pipeline steps completed successfully
   Content analysis: 2 credible sources, 1 conflict detected
   ```

---

### Sample Prompt #2: Compare Multiple Products

**Prompt:**
```
Compare Sony WH-1000XM5 vs Bose QuietComfort 45 - which is better for noise cancellation?
```

**What to Expect:**

1. **Classification:** "comparative" query type
2. **Search:** Finds URLs for both products
3. **Fetch:** Extracts data from multiple sources for each product
4. **Format:** Creates side-by-side comparison
5. **Analysis:** ✨ NEW
   - Credibility scores for each source
   - Comparison matrix with normalized data
   - Conflict detection (if prices/ratings differ)
   - Recommendations based on credible sources

**Expected Output includes:**
```
**Product Comparison: Sony WH-1000XM5 vs Bose QuietComfort 45**

| Feature              | Sony WH-1000XM5  | Bose QC45       |
|---------------------|------------------|-----------------|
| Price               | $348 (Amazon)    | $329 (Amazon)   |
| Rating              | 4.7/5            | 4.5/5           |
| ANC Quality         | Industry-leading | Excellent       |
| Battery Life        | 30 hours         | 24 hours        |

**Credibility Analysis:**
- All price data from Amazon (credibility: 85/100)
- Consistent ratings across sources
- No major conflicts detected

**Recommendation:** Sony WH-1000XM5 for superior ANC and longer battery...
```

---

### Sample Prompt #3: Single Product Research

**Prompt:**
```
What are the reviews saying about the iPhone 15 Pro Max?
```

**What to Expect:**

1. **Classification:** "exploratory" query type
2. **Search:** Finds review sites and forums
3. **Fetch:** Extracts content from tech review sites
4. **Format:** Summarizes key points from reviews
5. **Analysis:** ✨ NEW
   - Credibility scores (tech blogs vs forums)
   - Extracted facts with confidence levels
   - Conflicts if reviews disagree
   - Quotes from credible sources

**Expected Output includes:**
```
**iPhone 15 Pro Max Reviews Summary**

**Key Findings:**
- Camera quality: Exceptional (confidence: 95% - from 3 high-credibility sources)
- Battery life: 25+ hours (confidence: 90% - from TechCrunch, CNET)
- Performance: A17 Pro chip is fastest (confidence: 95%)

**Source Credibility:**
- TechCrunch: 80/100 (Highly Credible)
- CNET: 85/100 (Highly Credible)
- RandomBlog: 40/100 (Low Credibility - excluded from analysis)

**Conflicts:** None detected - sources agree on main points
```

---

### Sample Prompt #4: Factual Query (Less Analysis)

**Prompt:**
```
What is the capital of France?
```

**What to Expect:**

1. **Classification:** "factual" query type (simple)
2. **Search:** Quick search
3. **Fetch:** Minimal data (1-2 sources sufficient)
4. **Format:** Direct answer
5. **Analysis:** ✨ NEW (but minimal)
   - Credibility: Wikipedia (75/100)
   - Fact: "Paris is the capital" (confidence: 100%)
   - Conflicts: None

**Expected Output:**
```
The capital of France is Paris.

**Source Credibility:**
- Wikipedia: 75/100 (Moderately Credible)
- Britannica: 85/100 (Highly Credible)

**Confidence:** 100% (multiple authoritative sources agree)
```

---

### Sample Prompt #5: Price Tracking (Show Conflicts)

**Prompt:**
```
Find the best price for AirPods Pro 2nd generation
```

**What to Expect:**

This is ideal for showing **conflict detection**:

```
**AirPods Pro (2nd Generation) Price Comparison**

**Prices Found:**
- Amazon: $199.99 USD
- Best Buy: $249.99 USD
- Apple Store: $249.00 USD
- Walmart: $189.99 USD

**Credibility Analysis:**
- Amazon: 85/100 (Highly Credible)
- Best Buy: 75/100 (Moderately Credible)
- Apple Store: 90/100 (Highly Credible - official)
- Walmart: 80/100 (Highly Credible)

**Price Conflict Detected:** ✨
Prices range from $189.99 to $249.99 (difference: $60.00)

**Analysis:**
- Walmart ($189.99) and Amazon ($199.99) are likely promotional prices
- Apple Store ($249.00) is the official retail price
- All sources are credible, suggesting legitimate price variation

**Recommended Action:**
Check Walmart ($189.99) if urgent, or wait for Amazon deals ($199.99)
```

---

## What to Look For in the UI

### 1. **Pipeline Execution (Terminal)**

Watch the terminal for the 5-step pipeline:
```
[STEP 1/5] Classifying query...
[STEP 2/5] Searching web for URLs...
[STEP 3/5] Fetching data from URLs...
[STEP 4/5] Formatting results...
[STEP 5/5] Analyzing content credibility... ✨ NEW
```

### 2. **A2A Communication Logs**

Look for A2A calls:
```
[A2A] Calling Query Classifier...
[A2A] Query Classifier response received
[A2A] Calling Information Gatherer agent...
[A2A] Information Gatherer response received
[A2A] Calling Content Analysis agent... ✨ NEW
[A2A] Content Analysis response received ✨ NEW
```

### 3. **Analysis Summary**

In the terminal, you'll see:
```
[STEP 5/5] OK Analysis complete - 2 credible sources found ✨
```

### 4. **Final Result in Browser**

The browser will show:
- Formatted response (from Information Gatherer)
- **NEW:** Credibility scores embedded
- **NEW:** Conflict detection warnings
- **NEW:** Confidence levels for facts
- **NEW:** Source recommendations

---

## Debugging Tips

### If You Don't See Content Analysis:

1. **Check Terminal Logs**
   - Look for `[STEP 5/5]` in the output
   - Verify `Content Analysis agent loaded` at startup

2. **Check for Errors**
   ```
   [STEP 5/5] WARN Analysis failed: ...
   ```
   This indicates the analysis step ran but encountered an error

3. **Check if Data Was Fetched**
   ```
   [STEP 5/5] SKIP No data to analyze (no sources fetched)
   ```
   This means steps 2-3 didn't fetch any data, so analysis was skipped

4. **Verify Agent Loaded**
   At startup, you should see:
   ```
   Content Analysis Agent initialized:
     - Role: Credibility assessment and fact extraction
     - Model: gemini-2.5-flash-lite
   Content Analysis agent 'content_analyzer' initialized
   ```

---

## Advanced Testing

### View Full Analysis JSON

To see the raw analysis JSON, you can modify the orchestrator to print it:

Edit `adk_agents/orchestrator/agent.py` around line 473:

```python
try:
    analysis_json = json.loads(cleaned_analysis)

    # ADD THIS LINE TO SEE FULL JSON:
    print(f"\n[DEBUG] Full Analysis JSON:\n{json.dumps(analysis_json, indent=2)}\n")

    print(f"[STEP 5/5] OK Analysis complete - {analysis_json.get('analysis_summary', {}).get('credible_sources', 0)} credible sources found")
```

Then you'll see the complete analysis structure:
```json
{
  "analysis_summary": {
    "total_sources": 2,
    "credible_sources": 2,
    "conflicts_found": 1,
    "query_type": "comparative"
  },
  "source_credibility": [...],
  "extracted_facts": [...],
  "conflicts": [...],
  "comparison_matrix": {...},
  "recommendations": [...]
}
```

---

## Stopping the Server

Press `Ctrl+C` in the terminal to stop the ADK Web UI.

---

## Troubleshooting

### Issue: "No credible sources found"

**Cause:** Search returned low-quality URLs

**Solution:** Try a more specific query with brand names or product codes

---

### Issue: "STEP 5/5 SKIP No data to analyze"

**Cause:** Steps 2-3 didn't fetch any data

**Possible reasons:**
- No Google Search Engine ID configured
- Search didn't find relevant URLs
- URLs couldn't be fetched (blocked/404)

**Solution:**
- Check `.env` has `GOOGLE_SEARCH_ENGINE_ID`
- Try different query terms

---

### Issue: Agent returns generic response without analysis

**Cause:** LLM formatted the response without including analysis details

**Solution:** The analysis still ran (check terminal logs). The LLM just chose to summarize it differently.

---

## Summary

### Quick Test Workflow:

1. **Start:** `adk web` in `adk_agents/orchestrator/`
2. **Open:** http://localhost:8080
3. **Try this prompt:** "Find the current price of Sony WH-1000XM5 headphones"
4. **Watch terminal:** Look for `[STEP 5/5] Analyzing content...` ✨
5. **Check response:** Should mention credibility scores and conflicts
6. **Stop:** `Ctrl+C`

### Best Prompts to Show Content Analysis:

1. ✅ **"Find prices for [product] from multiple stores"** - Shows conflict detection
2. ✅ **"Compare [product A] vs [product B]"** - Shows comparison matrix
3. ✅ **"What are reviews saying about [product]?"** - Shows fact extraction
4. ✅ **"Best price for [product]"** - Shows credibility scoring

### What Makes a Good Test Query:

- ✓ Mentions specific products with brand/model
- ✓ Implies comparison or price checking
- ✓ Will have multiple sources with potentially different data
- ✗ Too vague ("good headphones")
- ✗ Single source queries ("from Amazon only")

---

**Happy Testing!** 🎉

The Content Analysis Agent will automatically run on every query and add credibility assessment to your research results.
