# Report Generator - Quick Start Guide

**For developers who want to understand the Report Generator in 5 minutes.**

---

## What is it?

The **Report Generator Agent** is the final step (STEP 6) in the ResearchMate AI pipeline. It transforms raw analyzed data into professional, tailored reports with:

- ✅ **Format adapted to query type** (factual/comparative/exploratory)
- ✅ **Proper citations** with credibility indicators
- ✅ **Weighted scoring** for comparisons (when user states priorities)
- ✅ **Follow-up questions** to guide further research
- ✅ **Professional markdown** formatting

---

## How does it work?

### Pipeline Flow

```
User asks: "What is the price of Sony WH-1000XM5?"
    ↓
[1] Query Classifier → "factual query"
[2] Search → finds Amazon, BestBuy URLs
[3] Fetch → extracts product data
[4] Information Gatherer → formats data
[5] Content Analyzer → scores credibility
[6] Report Generator → creates final report ← YOU ARE HERE
    ↓
User gets professional report with:
  - Direct answer: "$348 on Amazon"
  - Supporting evidence from sources
  - Citations with credibility scores
  - Follow-up questions
```

### A2A Call

The orchestrator calls Report Generator like this:

```python
# Build prompt with all context
report_prompt = f"""Generate tailored report.

QUERY: {query}
CLASSIFICATION: {classification}
FORMATTED INFO: {info_gatherer_output}
CONTENT ANALYSIS: {credibility_scores}

Generate report following format for: {query_type}
"""

# Call Report Generator via A2A
report_runner = InMemoryRunner(agent=report_generator_agent)
report_response = await report_runner.run_debug(report_prompt)
final_report = [extract text from response]

# Return to user
return {"content": final_report}
```

---

## File Structure

```
adk_agents/
└── report_generator/
    ├── __init__.py         # Package init
    └── agent.py            # Report Generator agent (365 lines)
                            # - Factual format instructions
                            # - Comparative format instructions
                            # - Exploratory format instructions
                            # - Citation rules
                            # - Weighted scoring logic
                            # - Follow-up question rules
```

---

## Report Formats (3 Types)

### 1. Factual → Concise Answer

```markdown
## Sony WH-1000XM5 Current Price

The Sony WH-1000XM5 is priced at **$348** on Amazon.

### Supporting Evidence
- Amazon: $348 (4.7/5, 2,543 reviews)
- BestBuy: $379.99 (4.6/5, 892 reviews)

### Sources
[1] Amazon (Credibility: High - Official retailer)

**Confidence**: High

💡 **Follow-ups**
- How does this compare to Bose QC Ultra?
```

### 2. Comparative → Comparison Matrix

```markdown
## Comparison: Sony WH-1000XM5 vs Bose QC Ultra

### 🎯 Executive Summary
Sony WH-1000XM5 recommended for best value.

### 📊 Comparison Matrix

| Feature | Sony XM5 | Bose QC |
|---------|----------|---------|
| Price   | $348 ⭐⭐ | $429 ⭐  |
| Battery | 30hrs ⭐⭐| 24hrs   |

### 📝 Analysis
**Sony:** Best value, long battery
**Bose:** Premium comfort

💡 **Follow-ups**
- Which is better for travel?
```

### 3. Exploratory → Comprehensive Guide

```markdown
## How Noise Cancellation Works

### 📖 Overview
Active noise cancellation uses microphones...

### 🔑 Key Concepts
1. **Phase Inversion**: Anti-sound waves
2. **Feed-forward ANC**: External mics

### 💡 Applications
- Travel headphones
- Office focus

💡 **Follow-ups**
- What are the limitations of ANC?
```

---

## Key Features Explained

### Citations with Credibility

Every claim is cited:

```markdown
Sony WH-1000XM5 costs $348 [1]

### Sources
[1] Amazon - Product Page
    Credibility: High (85/100)
    Reasoning: Official retailer, verified reviews
```

Credibility scores from Content Analyzer (STEP 5):
- **80-100:** High (official sources, major retailers)
- **60-79:** Medium (established blogs, forums)
- **40-59:** Low (unverified sources)

### Weighted Scoring

When user says "I prioritize battery life":

```markdown
### 🔍 Weighted Scoring

Since you prioritized battery life (×2 weight):

| Product | Battery (×2) | Price (×1) | Total |
|---------|--------------|------------|-------|
| Sony    | 30hrs → 60   | 9/10 → 9   | 69/80 |
| Bose    | 24hrs → 48   | 7/10 → 7   | 55/80 |

Sony wins with battery priority applied.
```

### Follow-up Questions

Generated based on query type:

- **Factual:** Comparative questions, trends, where to buy
- **Comparative:** Deep-dive winner, alternatives, scenarios
- **Exploratory:** Subtopics, implementation, examples

---

## Testing

### Quick Validation (30 seconds)

```bash
python validate_report_generator.py
```

Checks:
- ✅ Files exist
- ✅ Agent imports successfully
- ✅ Orchestrator loads Report Generator
- ✅ STEP 6 is in pipeline
- ✅ All report formats defined

### Integration Tests (5 minutes)

```bash
python test_report_generator.py
```

Tests:
1. Factual query (price lookup)
2. Comparative query (product comparison)
3. Exploratory query (concept explanation)

### Live Test via UI

```bash
venv\Scripts\adk.exe web adk_agents --port 8000
```

Open http://localhost:8000 and ask:
- "What is the price of Sony WH-1000XM5?"
- "Compare Sony WH-1000XM5 vs Bose QC Ultra"
- "How does noise cancellation work?"

**Watch terminal for:**
```
[STEP 6/6] Generating final report...
[A2A] Calling Report Generator agent...
[STEP 6/6] OK Report generation complete
```

---

## Common Questions

### Q: Where is the agent defined?

**A:** `adk_agents/report_generator/agent.py` lines 45-365

### Q: How is it called?

**A:** Via A2A in `adk_agents/orchestrator/agent.py` lines 613-672

### Q: What does it receive as input?

**A:**
1. Original query
2. Classification (query_type, strategy, complexity)
3. Formatted information (from Information Gatherer)
4. Content analysis (credibility scores, extracted facts)

### Q: What does it output?

**A:** A markdown-formatted report tailored to the query type

### Q: What if it fails?

**A:** Falls back to Information Gatherer output (orchestrator line 670-672)

### Q: Can I customize report formats?

**A:** Yes! Edit the instruction in `agent.py` lines 54-360

---

## Debugging

### Check if Report Generator is loaded

```bash
python -c "from adk_agents.orchestrator.agent import agent; print('Loaded:', agent.name)"
```

Expected:
```
Report Generator Agent initialized...
Orchestrator initialized...
Loaded: research_orchestrator
```

### Check terminal logs

When running queries, you should see:

```
[STEP 6/6] Generating final report with Report Generator...
[A2A] Calling Report Generator agent...
[A2A] Report Generator response received
[STEP 6/6] OK Report generation complete
```

If STEP 6 doesn't appear → Check orchestrator imports (line 67-69)

### Enable debug mode

Add to orchestrator `execute_fixed_pipeline`:

```python
print(f"DEBUG: Report prompt:\n{report_prompt}")  # Before A2A call
print(f"DEBUG: Final report:\n{final_report}")     # After A2A call
```

---

## Architecture

```
┌────────────────────────────────────────────────┐
│         Orchestrator (orchestrator/agent.py)    │
│                                                 │
│  execute_fixed_pipeline():                     │
│    [1] classify_query() → query_classifier     │
│    [2] search_web() → URLs                     │
│    [3] fetch_data() → raw content              │
│    [4] gatherer.run() → formatted info         │
│    [5] analyzer.run() → credibility scores     │
│    [6] reporter.run() → FINAL REPORT ✨        │
│         ↑                                       │
│         └─────────────────────────┐            │
└───────────────────────────────────┼────────────┘
                                    │
                         ┌──────────▼─────────────┐
                         │  Report Generator       │
                         │  (report_generator/)    │
                         │                         │
                         │  - Analyzes query type  │
                         │  - Selects format       │
                         │  - Adds citations       │
                         │  - Generates follow-ups │
                         │  - Returns markdown     │
                         └─────────────────────────┘
```

---

## Next Steps

1. ✅ **Validate:** `python validate_report_generator.py`
2. ✅ **Test:** `python test_report_generator.py`
3. ✅ **Try Live:** `adk web adk_agents --port 8000`
4. ✅ **Read Docs:** [REPORT_GENERATOR_INTEGRATION.md](REPORT_GENERATOR_INTEGRATION.md)

---

**Quick Reference:**
- Agent code: `adk_agents/report_generator/agent.py`
- Integration: `adk_agents/orchestrator/agent.py` lines 613-672
- Tests: `test_report_generator.py`
- Validation: `validate_report_generator.py`
- Full docs: `REPORT_GENERATOR_INTEGRATION.md`

**Questions?** Check [REPORT_GENERATOR_INTEGRATION.md](REPORT_GENERATOR_INTEGRATION.md) for comprehensive documentation.
