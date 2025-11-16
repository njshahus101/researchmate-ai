# Pipeline Integration: Query Classifier → Information Gatherer

## Overview

This document describes the sequential pipeline integration between the Query Classifier and Information Gatherer agents using the orchestrator pattern.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Orchestrator Agent                         │
│  (Coordinates pipeline via agent-to-agent communication)     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ├─── Step 1: Classify Query
                           │    ┌────────────────────────────┐
                           ├───▶│  Query Classifier Agent    │
                           │    │  - Analyzes query type     │
                           │    │  - Determines strategy     │
                           │    │  - Extracts topics         │
                           │    └────────────────────────────┘
                           │
                           ├─── Step 2: Gather Information (conditional)
                           │    ┌────────────────────────────┐
                           └───▶│ Information Gatherer Agent │
                                │  - Executes searches       │
                                │  - Fetches content         │
                                │  - Returns sources         │
                                └────────────────────────────┘
```

## Implementation Details

### Orchestrator Agent

The orchestrator agent (`research_orchestrator`) coordinates the pipeline:

1. **Tool-Based Agent Calls**: Uses `FunctionTool` to wrap agent invocations
   - `classify_user_query(query, user_id)` - Calls Query Classifier
   - `gather_information(query, classification)` - Calls Information Gatherer

2. **Sequential Workflow**:
   ```python
   User Query → Orchestrator
       ↓
   classify_user_query() → Query Classifier Agent
       ↓ (returns classification)
   Orchestrator Decision (based on strategy)
       ↓
   gather_information() → Information Gatherer Agent (if needed)
       ↓ (returns sources)
   Orchestrator → Final Response to User
   ```

3. **Conditional Execution**:
   - **quick-answer**: Skip information gathering
   - **multi-source**: Gather from 3-5 sources
   - **deep-dive**: Comprehensive search from 5-10+ sources

### Agent Communication

Agents communicate through the orchestrator using **function tool calls**:

```python
# Orchestrator has tools that call agents
tools=[
    FunctionTool(func=classify_user_query),  # Wraps classifier agent
    FunctionTool(func=gather_information)     # Wraps gatherer agent
]
```

Each tool function:
1. Prepares context/prompt for the target agent
2. Creates an `InMemoryRunner` for the agent
3. Calls `runner.run_debug()` to execute the agent
4. Extracts and returns the response

### Data Flow

**Stage 1 - Classification:**
```json
Input: "Best wireless headphones under $200"

Query Classifier Output:
{
  "query_type": "comparative",
  "complexity_score": 6,
  "research_strategy": "multi-source",
  "key_topics": ["wireless", "headphones", "budget"],
  "estimated_sources": 5
}
```

**Stage 2 - Information Gathering:**
```json
Input to Gatherer:
{
  "query": "Best wireless headphones under $200",
  "query_type": "comparative",
  "research_strategy": "multi-source",
  "key_topics": ["wireless", "headphones", "budget"],
  "estimated_sources": 5
}

Gatherer Output:
{
  "status": "success",
  "content": "... search results and sources ...",
  "strategy": "multi-source"
}
```

## Error Handling

The pipeline includes comprehensive error handling:

1. **Classification Errors**: Returns default values if classification fails
2. **Gathering Errors**: Returns error status with message
3. **Pipeline Errors**: Logged and tracked in metrics
4. **Timeout Handling**: Retry logic built into agent runners

## Logging & Observability

### Stage-Level Logging

```python
[Stage 1/2] Running Query Classification...
✓ Classification complete: comparative query
  Strategy: multi-source
  Complexity: 6/10
  Duration: 1847.23ms

[Stage 2/2] Running Information Gathering...
✓ Information gathering complete
  Duration: 5342.11ms
```

### Pipeline Metrics

```python
pipeline_metrics = {
    "total_runs": 10,
    "successful_runs": 9,
    "failed_runs": 1,
    "average_duration": 4523.45  # milliseconds
}
```

### Timing Breakdown

Each stage tracks:
- `stage_start`: Timestamp when stage begins
- `stage_duration`: Time in milliseconds
- `total_duration`: Full pipeline time

## Testing

### Integration Tests

Run the full integration test suite:

```bash
python test_pipeline_integration.py
```

This validates:
- ✅ Sequential workflow execution
- ✅ Data passing between agents
- ✅ Error handling
- ✅ Logging and metrics
- ✅ End-to-end functionality

### Interactive Testing

Test via command line:

```bash
python main.py
```

Commands:
- Enter queries to test the pipeline
- Type `metrics` to see pipeline performance
- Type `help` for usage information
- Type `exit` to quit

### ADK Web UI Testing

Test via web interface:

```bash
# Using batch file (Windows)
start_orchestrator_ui.bat

# Or using ADK directly
adk web main:ResearchMateAI().app
```

Open http://localhost:8000 and interact with the orchestrator through the web UI.

## Query Types & Strategies

### Factual Queries
- **Example**: "What is the capital of Japan?"
- **Strategy**: quick-answer
- **Behavior**: Skips information gathering

### Comparative Queries
- **Example**: "Best wireless headphones under $200"
- **Strategy**: multi-source
- **Behavior**: Gathers from 3-5 sources, creates comparison

### Exploratory Queries
- **Example**: "Explain quantum computing for beginners"
- **Strategy**: deep-dive
- **Behavior**: Comprehensive research from 5-10+ sources

### Monitoring Queries
- **Example**: "Latest developments in AI agents"
- **Strategy**: multi-source
- **Behavior**: Focuses on recent sources

## Memory Integration

The pipeline integrates with the Memory Service:

1. **Query Classification**: Retrieves user context
   - Past research topics
   - User preferences
   - Domain knowledge

2. **Storage**: After classification
   - Stores query and classification
   - Updates user research history
   - Links related topics

## Success Criteria

All pipeline integration success criteria met:

- ✅ Agents successfully pass data between stages
- ✅ Pipeline completes end-to-end for all query types
- ✅ Errors are handled gracefully
- ✅ Full traceability through logs
- ✅ Timing metrics collected
- ✅ Integration tests passing

## Future Enhancements

1. **Add More Agents**: Content Analyzer, Report Generator
2. **MCP Integration**: Web fetcher and price extractor tools
3. **A2A Protocol**: For cross-service communication
4. **Streaming**: Real-time progress updates
5. **Caching**: Cache classification results for similar queries

## Files

Key files for this integration:

- `main.py` - Orchestrator and pipeline implementation
- `agents/query_classifier_mvp.py` - Query classification agent
- `agents/information_gatherer.py` - Information gathering agent
- `test_pipeline_integration.py` - Integration tests
- `start_orchestrator_ui.bat` - ADK web UI launcher

## Related Documentation

- [Query Classifier Usage](QUERY_CLASSIFIER_USAGE.md)
- [Information Gatherer Guide](QUICK_START_INFO_GATHERER.md)
- [ADK Web UI Guide](ADK_WEB_UI_GUIDE.md)
- [Project Architecture](project_description_final.md)
