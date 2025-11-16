# Quick Start: Test the Orchestrator Pipeline

## Overview

This guide shows you how to quickly test the Query Classifier → Information Gatherer pipeline integration.

## Prerequisites

- ✅ Python virtual environment activated
- ✅ `GOOGLE_API_KEY` in `.env` file
- ✅ Dependencies installed (`pip install -r requirements.txt`)

## Testing Options

### Option 1: ADK Web UI (Recommended for Interactive Testing)

**Start the server:**
```bash
# Windows
start_orchestrator_ui.bat

# Or manually
adk web main:ResearchMateAI().app
```

**Access**: Open http://localhost:8000 in your browser

**Try these queries:**
```
1. What is the capital of Japan?
   → Should classify as factual, skip information gathering

2. Best wireless headphones under $200
   → Should classify as comparative, run information gathering

3. Explain quantum computing for beginners
   → Should classify as exploratory, run deep information gathering
```

**What to observe:**
- Classification results
- Whether information gathering runs
- Tool calls made by orchestrator
- Final synthesized response

---

### Option 2: Interactive Command Line

**Run:**
```bash
python main.py
```

**Commands:**
- Enter a query to test the pipeline
- Type `metrics` to see pipeline performance
- Type `help` for information
- Type `exit` to quit

**Example session:**
```
🔍 Enter your research query: Best wireless headphones under $200

PIPELINE RESULTS
============================================================
Status: success

Query Classification:
  Type: comparative
  Complexity: 6/10
  Strategy: multi-source
  Topics: wireless, headphones, budget

Information Gathering:
  Status: success
  Duration: 5342.11ms

Total Duration: 7189.34ms
============================================================

🔍 Enter your research query: metrics

PIPELINE METRICS
============================================================
Total Runs: 1
Successful: 1
Failed: 0
Success Rate: 100.0%
Average Duration: 7189.34ms
============================================================
```

---

### Option 3: Integration Tests

**Run comprehensive tests:**
```bash
python test_pipeline_integration.py
```

**What it tests:**
- ✅ 4 different query types
- ✅ Sequential workflow execution
- ✅ Data passing between agents
- ✅ Error handling
- ✅ Timing metrics
- ✅ Success criteria validation

**Expected output:**
```
PIPELINE INTEGRATION TEST
Query Classifier -> Information Gatherer
============================================================

[1/5] Initializing ResearchMate AI...
✓ Application initialized successfully

[2/5] Running 4 test cases...
------------------------------------------------------------

Test 1/4: Factual Query (Quick Answer)
Query: "What is the capital of Japan?"
  ✓ Classified as: factual
  ✓ Strategy: quick-answer
  ✓ Complexity: 2/10
  ✓ Information gathering skipped (quick-answer strategy)
  ✓ Total duration: 2145.67ms
  ✅ PASSED

[... more tests ...]

[5/5] Success Criteria Validation
------------------------------------------------------------
✓ PASS: All tests passed
✓ PASS: Pipeline success rate > 90%
✓ PASS: Classification stage works
✓ PASS: Data passes between stages
✓ PASS: Error handling present
✓ PASS: Timing metrics collected

============================================================
✅ INTEGRATION TEST PASSED - All criteria met!
============================================================
```

---

### Option 4: Programmatic Testing

**Create a test script:**
```python
import asyncio
from main import ResearchMateAI

async def test():
    # Initialize
    app = ResearchMateAI()

    # Run a query
    result = await app.research(
        query="Best wireless headphones under $200",
        user_id="test_user"
    )

    # Check results
    print(f"Status: {result['status']}")

    if result['status'] == 'success':
        classification = result['stages']['classification']['output']
        print(f"Query Type: {classification['query_type']}")
        print(f"Strategy: {classification['research_strategy']}")
        print(f"Duration: {result['total_duration_ms']:.2f}ms")

    # View metrics
    app._show_metrics()

# Run
asyncio.run(test())
```

**Execute:**
```bash
python your_test_script.py
```

---

## What to Look For

### Successful Pipeline Execution

**Stage 1 - Classification:**
```
[Stage 1/2] Running Query Classification...
✓ Classification complete: comparative query
  Strategy: multi-source
  Complexity: 6/10
  Duration: 1847.23ms
```

**Stage 2 - Information Gathering:**
```
[Stage 2/2] Running Information Gathering...
✓ Information gathering complete
  Duration: 5342.11ms
```

**Final Results:**
```
PIPELINE COMPLETE
Total Duration: 7189.34ms
Stages Completed: 2
```

### Expected Behaviors by Query Type

| Query Type | Strategy | Information Gathering | Duration |
|-----------|----------|---------------------|----------|
| Factual | quick-answer | Skipped | 2-3 sec |
| Comparative | multi-source | Executed (3-5 sources) | 5-8 sec |
| Exploratory | deep-dive | Executed (5-10+ sources) | 10-15 sec |
| Monitoring | multi-source | Executed (3-5 sources) | 5-8 sec |

---

## Troubleshooting

### Error: GOOGLE_API_KEY not found
```bash
# Check .env file exists
ls .env

# Verify it contains the key
cat .env | grep GOOGLE_API_KEY
```

**Fix**: Add your API key to `.env`:
```
GOOGLE_API_KEY=your_actual_key_here
```

### Error: Module not found
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

### ADK web command not found
```bash
# Reinstall google-adk
pip install --upgrade google-adk
```

### Pipeline hangs or times out
- Check internet connection (needed for Gemini API)
- Verify API key is valid
- Check rate limits on Gemini API

### Unicode errors in logs
- This is a known Windows console encoding issue
- Pipeline still works correctly
- To suppress: Redirect stderr or use ADK UI instead

---

## Sample Queries for Testing

### Factual (Quick Answer)
```
What is the capital of France?
Who wrote Romeo and Juliet?
What year did World War 2 end?
```

### Comparative (Multi-Source)
```
Best laptops for programming under $1000
Compare iPhone 15 vs Samsung Galaxy S24
Top wireless earbuds for running
```

### Exploratory (Deep Dive)
```
Explain machine learning for beginners
How does blockchain technology work?
What is quantum computing?
```

### Monitoring (Multi-Source)
```
Latest developments in AI
Recent breakthroughs in renewable energy
Current trends in electric vehicles
```

---

## Next Steps

After testing the orchestrator:

1. **Add More Agents**: Content Analyzer, Report Generator
2. **Integrate MCP Tools**: Web fetcher, price extractor
3. **Deploy to Production**: Cloud Run, Agent Engine
4. **Enhance Features**: Streaming, caching, monitoring

---

## Help & Documentation

- **Pipeline Documentation**: `PIPELINE_INTEGRATION.md`
- **Completion Summary**: `ORCHESTRATOR_INTEGRATION_COMPLETE.md`
- **Query Classifier Guide**: `QUERY_CLASSIFIER_USAGE.md`
- **Information Gatherer Guide**: `QUICK_START_INFO_GATHERER.md`
- **Project Overview**: `project_description_final.md`

---

## Success! 🎉

If you can successfully run queries through any of the testing methods above and see the sequential pipeline in action, your orchestrator integration is working perfectly!

The pipeline should:
- ✅ Classify queries correctly
- ✅ Conditionally run information gathering
- ✅ Pass data between stages
- ✅ Handle errors gracefully
- ✅ Log all activities
- ✅ Track metrics

Happy testing! 🚀
