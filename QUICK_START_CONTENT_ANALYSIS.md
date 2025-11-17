# Content Analysis Agent - Quick Start Guide

## What It Does

The Content Analysis Agent evaluates the credibility of research sources and extracts verified facts. It's automatically integrated into the ResearchMate AI pipeline as the final step.

## Pipeline Flow

```
User Query
    ↓
Step 1: Classify Query (type, complexity)
    ↓
Step 2: Search Web (get URLs)
    ↓
Step 3: Fetch Data (extract content)
    ↓
Step 4: Format Results (user-friendly)
    ↓
Step 5: Analyze Content ← YOUR NEW AGENT
    ↓
Complete Answer with Credibility Scores
```

## Quick Test

```bash
# Test the agent standalone
python test_content_analysis_integration.py

# Expected output:
# [OK] Content Analyzer (standalone): PASSED
# Shows credibility scores, conflicts, and extracted facts
```

## What You Get

Every query now returns:

1. **Credibility Scores** (0-100) for each source
   - Amazon: 85/100 (Highly Credible)
   - BestBuy: 75/100 (Moderately Credible)
   - Random blog: 35/100 (Low Credibility)

2. **Extracted Facts** with confidence levels
   - "Price: $348" (95% confidence - HIGH)
   - "Rating: 4.7/5" (95% confidence - HIGH)

3. **Conflict Detection**
   - "Price varies: $348 (Amazon) vs $379 (BestBuy)"
   - "Recommended: $348 (higher credibility)"

4. **Comparison Matrix** (for product queries)
   - Side-by-side feature comparison
   - Normalized prices and ratings

5. **Data Normalization**
   - All prices in USD
   - All ratings on /5 scale
   - Standardized formats

## Files Location

```
adk_agents/
  └── content_analyzer/
      ├── __init__.py
      └── agent.py              ← Main agent implementation

adk_agents/orchestrator/
  └── agent.py                  ← Updated with STEP 5

tests/
  └── test_content_analyzer.py  ← Unit tests

test_content_analysis_integration.py  ← Integration test
CONTENT_ANALYSIS_AGENT_SUMMARY.md    ← Full documentation
```

## Run Full Pipeline

To test with real web search (requires API keys):

1. Ensure `.env` has:
   ```
   GOOGLE_API_KEY=your_key_here
   GOOGLE_SEARCH_ENGINE_ID=your_id_here
   ```

2. Edit `test_content_analysis_integration.py`:
   ```python
   # Uncomment this line (around line 233):
   test2_result = await test_full_pipeline()
   ```

3. Run:
   ```bash
   python test_content_analysis_integration.py
   ```

## Using in Production

The agent is **already integrated**. Just use the orchestrator normally:

```bash
adk web
# The Content Analysis step runs automatically on every query
```

Or programmatically:
```python
from adk_agents.orchestrator.agent import execute_fixed_pipeline

result = await execute_fixed_pipeline("Sony WH-1000XM5 price")

# Result includes:
# - result['content']: Formatted response
# - result['content_analysis']: Credibility scores, facts, conflicts
# - result['pipeline_steps']: Status of all 5 steps
```

## Success Criteria ✓

All requirements completed:

✅ Source credibility scoring (0-100 algorithm)
✅ Fact extraction with confidence levels
✅ Conflict detection and resolution
✅ Comparison matrix for products
✅ Data normalization (prices, ratings, specs)
✅ Confidence levels for all facts
✅ Comprehensive unit tests
✅ Working integration test
✅ Integrated into orchestrator pipeline

## Example Output

Input: "Sony WH-1000XM5 price comparison"

Output includes:
```json
{
  "analysis_summary": {
    "total_sources": 3,
    "credible_sources": 2,
    "conflicts_found": 1
  },
  "source_credibility": [
    {"url": "amazon.com", "score": 85, "level": "Highly Credible"},
    {"url": "bestbuy.com", "score": 75, "level": "Moderately Credible"}
  ],
  "extracted_facts": [
    {
      "fact": "Price: $348.00",
      "confidence": 95,
      "confidence_level": "HIGH"
    }
  ],
  "conflicts": [
    {
      "type": "price",
      "description": "$31.99 difference",
      "recommended": "$348 (higher credibility)"
    }
  ]
}
```

## Need Help?

- Full docs: [CONTENT_ANALYSIS_AGENT_SUMMARY.md](CONTENT_ANALYSIS_AGENT_SUMMARY.md)
- Unit tests: `pytest tests/test_content_analyzer.py -v`
- Integration test: `python test_content_analysis_integration.py`

---

**Status:** ✅ Implementation Complete and Tested
