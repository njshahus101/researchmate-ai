# Observability Testing Guide

## 📋 Quick Start - View Existing Logs

### 1. View Application Logs (Structured JSON)
```bash
# View latest logs
cat logs/researchmate.log

# Or on Windows
type logs\researchmate.log

# View last 20 lines
tail -20 logs/researchmate.log
```

**What you'll see**: JSON-formatted logs with timestamps, trace IDs, and context
```json
{"timestamp": "2025-11-18T14:14:09Z", "level": "INFO", "agent": "test_agent",
 "message": "Completed successful_operation",
 "context": {"duration_seconds": 0.100, "param": "value1"},
 "trace_id": "a66073bf0c9133ff3851c53c86bb0e1c"}
```

### 2. View Error Logs
```bash
cat logs/errors.json
```

**What you'll see**: Detailed error tracking with stack traces
```json
{"timestamp": "2025-11-18T14:14:09Z", "agent": "test_agent",
 "error_type": "RuntimeError", "error_message": "Intentional test error",
 "trace_id": "000bfe90bcab0239...", "context": {...}}
```

### 3. View Observability Dashboard
```bash
python utils/observability_dashboard.py
```

**What you'll see**:
- Pipeline execution metrics
- Operation performance (latency percentiles)
- Success/error rates
- Recent errors with details

### 4. Export Metrics Report
```bash
python utils/observability_dashboard.py --export my_metrics.json
```

## 🧪 Option A: Run End-to-End Test (Recommended First)

This simulates agent operations and generates comprehensive logs:

```bash
python test_observability_end_to_end.py
```

**What it does**:
1. ✅ Tests structured logging (INFO, WARNING, ERROR)
2. ✅ Tests distributed tracing (parent-child spans)
3. ✅ Tests metrics collection (counters, histograms, gauges)
4. ✅ Tests error tracking (with stack traces)
5. ✅ Tests track_operation convenience function
6. 📊 Displays observability dashboard
7. 📁 Exports metrics to JSON

**Expected output**:
```
================================================================================
  RESEARCHMATE AI - END-TO-END OBSERVABILITY TEST
================================================================================

[TEST 1/5] Testing Structured Logging...
[OK] Structured logging test complete

[TEST 2/5] Testing Distributed Tracing...
[OK] Distributed tracing initialized for researchmate-ai
[OK] Distributed tracing test complete

...

ALL OBSERVABILITY TESTS PASSED!
```

**Logs generated**:
- `logs/researchmate.log` - All structured logs
- `logs/errors.json` - Error tracking
- `test_observability_report.json` - Metrics export

## 🚀 Option B: Test with Real Research Query

Run an actual research query through the full pipeline:

```bash
# Start the ADK Web UI
venv/Scripts/adk web adk_agents:orchestrator

# Then visit: http://localhost:8000
# Enter a query like: "Best wireless headphones under $200"
```

**What happens**:
1. Query gets unique ID
2. Orchestrator creates root trace span
3. Each agent logs operations with trace ID
4. Metrics recorded for each step
5. Errors captured if any occur

**Then view the results**:
```bash
# View logs with trace IDs
cat logs/researchmate.log | grep "trace_id"

# View the dashboard
python utils/observability_dashboard.py
```

## 📊 Understanding the Logs

### Structured Log Entry
```json
{
  "timestamp": "2025-11-18T14:14:09.175098Z",  // When it happened
  "level": "INFO",                              // Log level
  "agent": "orchestrator",                      // Which agent
  "message": "Pipeline started",                // What happened
  "context": {                                  // Additional data
    "query": "test query",
    "user_id": "test_user"
  },
  "trace_id": "a66073bf0c9133ff...",           // Trace correlation
  "span_id": "b993a3838dc4b566"                // Span within trace
}
```

### Trace Hierarchy
```
Root Span: fixed_pipeline
  ├─ Child Span: query_classifier.classify
  ├─ Child Span: search_web
  ├─ Child Span: fetch_content
  │  ├─ Child Span: fetch_url_1
  │  └─ Child Span: fetch_url_2
  ├─ Child Span: content_analyzer.analyze
  └─ Child Span: report_generator.generate
```

## 🔍 Searching Logs

### Find all errors:
```bash
cat logs/researchmate.log | grep "ERROR"
```

### Find logs for specific trace:
```bash
cat logs/researchmate.log | grep "a66073bf0c9133ff"
```

### Find logs from specific agent:
```bash
cat logs/researchmate.log | grep "orchestrator"
```

### Find operations that took > 1 second:
```bash
cat logs/researchmate.log | grep "duration_seconds" | grep -E "\"duration_seconds\": [1-9]"
```

## 📈 Dashboard Metrics Explained

### Pipeline Metrics
- **Total Pipeline Executions**: How many queries processed
- **Average Duration**: Typical query processing time
- **P95 Latency**: 95% of queries complete in this time

### Success & Error Rates
- **Success Rate**: % of operations that succeeded
- **Error Breakdown**: Errors categorized by type and agent

### Recent Errors
- Last 5 errors with full context
- Trace IDs for correlation
- Agent and error type

## 🎯 Real-World Usage Examples

### Example 1: Debug Slow Query
```bash
# Run query through system
# Check dashboard for latency metrics

python utils/observability_dashboard.py

# Look for high P95 latency
# Find the trace_id of slow query
# Search logs for that trace_id to see which step was slow

cat logs/researchmate.log | grep "trace_id_here"
```

### Example 2: Investigate Errors
```bash
# Check error summary
python utils/observability_dashboard.py

# View detailed error logs
cat logs/errors.json

# Find related logs using trace_id
cat logs/researchmate.log | grep "error_trace_id"
```

### Example 3: Monitor System Health
```bash
# Export current metrics
python utils/observability_dashboard.py --export metrics_$(date +%Y%m%d).json

# Compare with previous day
# Look for trends in error rates, latency
```

## 🛠️ Troubleshooting

### No logs appearing?
- Check that `logs/` directory exists (created automatically)
- Verify observability is initialized in agents
- Run test: `python test_observability_end_to_end.py`

### Dashboard shows no metrics?
- Run at least one operation first
- Metrics are in-memory (reset on restart)
- Export to JSON for persistence

### Can't find specific log?
- Check timestamp range
- Verify trace_id is correct
- Use grep with regex for flexible search

## 📁 Files Reference

**Log Files:**
- `logs/researchmate.log` - All structured logs (JSON, one per line)
- `logs/errors.json` - Error tracking with stack traces

**Tools:**
- `utils/observability_dashboard.py` - View metrics
- `test_observability_end_to_end.py` - Comprehensive test

**Documentation:**
- `OBSERVABILITY_COMPLETE.md` - Full implementation docs
- `OBSERVABILITY_TESTING_GUIDE.md` - This file

## 🎉 Quick Test Right Now

Run this command to see everything in action:

```bash
python test_observability_end_to_end.py && echo "\n\n=== VIEWING LOGS ===" && cat logs/researchmate.log && echo "\n\n=== VIEWING ERRORS ===" && cat logs/errors.json
```

Then view the dashboard:
```bash
python utils/observability_dashboard.py
```

You should see:
1. ✅ Tests passing
2. 📝 JSON logs with trace IDs
3. ❌ Error logs (intentional test errors)
4. 📊 Dashboard with metrics
5. 📁 Exported report JSON

**Everything is working!** 🎊
