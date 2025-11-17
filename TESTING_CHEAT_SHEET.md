# Content Analysis Agent - Testing Cheat Sheet

## Quick Start (3 Steps)

```bash
# 1. Navigate to orchestrator
cd adk_agents/orchestrator

# 2. Start ADK Web UI
adk web

# 3. Open browser
# http://localhost:8080
```

---

## 5 Best Test Prompts

### 1. Price Comparison (Best for seeing analysis) ⭐
```
Find the current price of Sony WH-1000XM5 headphones from multiple retailers
```
**Shows:** Credibility scores, price conflicts, recommendations

---

### 2. Product Comparison ⭐⭐
```
Compare Sony WH-1000XM5 vs Bose QuietComfort 45 - which is better?
```
**Shows:** Comparison matrix, normalized data, conflict detection

---

### 3. Price Tracking (Shows conflicts) ⭐⭐⭐
```
Find the best price for AirPods Pro 2nd generation
```
**Shows:** Multiple price points, conflict detection, credibility-based recommendations

---

### 4. Review Research
```
What are the reviews saying about the iPhone 15 Pro Max?
```
**Shows:** Fact extraction, confidence levels, source credibility

---

### 5. Simple Product Query
```
What is the price and rating of the PlayStation 5?
```
**Shows:** Basic credibility scoring, simple conflict detection

---

## What to Watch For

### In Terminal:
```
✅ Content Analysis agent loaded
✅ [STEP 5/5] Analyzing content credibility...
✅ [A2A] Calling Content Analysis agent...
✅ [STEP 5/5] OK Analysis complete - X credible sources found
```

### In Browser Response:
```
✅ Credibility scores (X/100)
✅ "Conflict detected" messages
✅ "Recommended based on credibility"
✅ Confidence levels mentioned
✅ Source quality assessment
```

---

## Verify It's Working

Run this one-liner test:
```bash
cd adk_agents/orchestrator && python -c "from agent import analyzer_agent; print(f'✅ Content Analyzer loaded: {analyzer_agent.name}')"
```

Should output:
```
Content Analysis Agent initialized:
  - Role: Credibility assessment and fact extraction
  - Model: gemini-2.5-flash-lite
✅ Content Analyzer loaded: content_analyzer
```

---

## Pipeline Steps (What Happens)

```
Step 1: Classify    → "comparative query"
Step 2: Search      → "Found 5 URLs"
Step 3: Fetch       → "Fetched 2 sources"
Step 4: Format      → "Based on fetched data..."
Step 5: Analyze ✨  → "2 credible sources, 1 conflict" ← NEW
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "SKIP No data to analyze" | Steps 2-3 failed. Check API keys in .env |
| No credibility scores in response | Check terminal logs - analysis ran but wasn't included in format |
| "Analysis failed" error | Check terminal for full error message |
| Agent not loading | Run `python agent.py` to see import errors |

---

## Sample Output You Should See

```
**Sony WH-1000XM5 Price Analysis**

Prices found:
- Amazon: $348.00 (Credibility: 85/100) ← HIGH
- Best Buy: $379.99 (Credibility: 75/100) ← MODERATE

Price Conflict Detected: $31.99 difference

Recommendation: Amazon ($348) based on:
  - Higher credibility score (85 vs 75)
  - More reviews (2,543 vs 892)
  - Consistent with price range

Rating: 4.7/5 (High confidence - 2 sources agree)
```

---

## Full Documentation

- **Testing Guide:** [ADK_UI_TESTING_GUIDE.md](ADK_UI_TESTING_GUIDE.md) (detailed)
- **Quick Start:** [QUICK_START_CONTENT_ANALYSIS.md](QUICK_START_CONTENT_ANALYSIS.md)
- **Architecture:** [A2A_ARCHITECTURE.md](A2A_ARCHITECTURE.md)
- **Complete Summary:** [CONTENT_ANALYSIS_AGENT_SUMMARY.md](CONTENT_ANALYSIS_AGENT_SUMMARY.md)

---

## Stop Server

```bash
Ctrl+C
```

---

## Pro Tips

1. **Use specific product names** (Sony WH-1000XM5, not "good headphones")
2. **Mention "compare" or "price"** to trigger multi-source research
3. **Watch terminal logs** for detailed pipeline execution
4. **Try queries with known price differences** (e.g., Amazon vs Best Buy)
5. **Product comparisons** show the most comprehensive analysis

---

## Success Indicators

✅ Terminal shows: `Content Analysis agent loaded`
✅ Terminal shows: `[STEP 5/5] Analyzing content...`
✅ Terminal shows: `[STEP 5/5] OK Analysis complete - X credible sources found`
✅ Response mentions credibility scores
✅ Response mentions conflicts (if any)
✅ Response includes recommendations based on credibility

---

**That's it!** Your Content Analysis Agent is working if you see STEP 5/5 in the terminal and credibility scores in the response. 🎉
