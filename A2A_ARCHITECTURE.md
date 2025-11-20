# Agent-to-Agent (A2A) Communication Architecture

## Overview

ResearchMate AI uses **Agent-to-Agent (A2A)** communication protocol where the orchestrator coordinates multiple specialized agents. Each agent is called via `InMemoryRunner` with the A2A protocol, allowing agents to communicate through structured messages.

### Modular Architecture

The orchestrator has been refactored into a **modular pipeline architecture** with:

- **Separate modules** for configuration, initialization, helpers, and pipeline steps
- **4 specialized A2A agents** that handle distinct responsibilities
- **7-step fixed pipeline** that executes deterministically
- **Observability integration** with logging, tracing, metrics, and error tracking
- **Persistent services** for session management and quality assurance
- **Clean separation of concerns** where each module has a single, well-defined purpose

---

## A2A Communication Pattern

### How It Works

```python
# A2A Pattern Example
from google.adk.runners import InMemoryRunner

# 1. Create runner for target agent
runner = InMemoryRunner(agent=target_agent)

# 2. Call agent with prompt
response = await runner.run_debug(prompt)

# 3. Extract structured response
if isinstance(response, list) and len(response) > 0:
    last_event = response[-1]
    if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
        result = last_event.content.parts[0].text
```

This pattern is used throughout the system for **deterministic agent communication**.

---

## Agent Communication Flow

### Complete 7-Step A2A Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                        │
│          (Modular Fixed Pipeline Controller)                 │
│         execute_fixed_pipeline() in orchestrator.py          │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ User Query
                           ▼
        ┌──────────────────────────────────────┐
        │      STEP 1: CLASSIFICATION           │
        │    (classification.py module)         │
        │                                       │
        │  [A2A] Query Classifier Agent         │
        │  - Analyzes query type                │
        │  - Determines complexity              │
        │  - Selects research strategy          │
        │  - Stores in user memory              │
        │  Returns: JSON classification         │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │        STEP 2: WEB SEARCH             │
        │       (search.py module)              │
        │                                       │
        │  search_web() Tool                    │
        │  - Google Custom Search API           │
        │  - Smart Google Shopping integration  │
        │  Returns: List of URLs                │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │         STEP 3: DATA FETCH            │
        │     (data_fetching.py module)         │
        │                                       │
        │  fetch_web_content() or               │
        │  extract_product_info()               │
        │  - Fetches content from URLs          │
        │  Returns: Structured data             │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │         STEP 4: FORMATTING            │
        │      (formatting.py module)           │
        │                                       │
        │  [A2A] Information Gatherer Agent     │
        │  - Formats fetched data               │
        │  - Creates user-friendly response     │
        │  Returns: Formatted text              │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │     STEP 5: CONTENT ANALYSIS          │
        │       (analysis.py module)            │
        │                                       │
        │  [A2A] Content Analysis Agent         │
        │  - Scores source credibility          │
        │  - Extracts facts with confidence     │
        │  - Detects conflicts                  │
        │  - Creates comparison matrix          │
        │  - Normalizes data                    │
        │  Returns: JSON analysis               │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │      STEP 6: REPORT GENERATION        │
        │       (reporting.py module)           │
        │                                       │
        │  [A2A] Report Generator Agent ✨      │
        │  - Creates tailored report            │
        │  - Inline citations [1], [2]...       │
        │  - Sources section with credibility   │
        │  - Follow-up questions                │
        │  Returns: Final formatted report      │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │   STEP 6.5: CITATION POST-PROCESS     │
        │   (citation_formatter.py module)      │
        │                                       │
        │  - Validates citation numbers         │
        │  - Formats source credibility         │
        │  - Ensures proper structure           │
        │  Returns: Clean, validated report     │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │    STEP 7: QUALITY VALIDATION         │
        │    (quality_check.py module)          │
        │                                       │
        │  Quality Assurance Service            │
        │  - Checks completeness                │
        │  - Validates citations                │
        │  - Verifies comparison matrices       │
        │  - Calculates quality score           │
        │  Returns: Quality report (0-100)      │
        └──────────────────────────────────────┘
                           │
                           ▼
                 ┌─────────────────┐
                 │  Final Result   │
                 │  - Professional │
                 │  - Cited        │
                 │  - Analyzed     │
                 │  - Validated    │
                 └─────────────────┘
```

---

## A2A Agent Implementations

### 1. Query Classifier Agent (A2A)

**Location:** [adk_agents/query_classifier/agent.py](adk_agents/query_classifier/agent.py)

**A2A Call in Orchestrator:**
```python
# Line 92-193 in orchestrator/agent.py
async def classify_user_query(query: str, user_id: str = "default") -> dict:
    """
    Classify a user query to determine research strategy.
    This function calls the Query Classifier agent using A2A protocol.
    """
    print(f"\n[A2A] Calling Query Classifier for: {query[:50]}...")

    # A2A Communication
    runner = InMemoryRunner(agent=classifier_agent)
    response = await runner.run_debug(query + context)

    # Extract JSON response
    response_text = extract_response_text(response)
    classification = json.loads(cleaned_text)

    print(f"[A2A] Classification complete: {classification.get('query_type')}")
    return classification
```

**Output Format:** JSON with query_type, complexity_score, research_strategy

---

### 2. Information Gatherer Agent (A2A)

**Location:** [adk_agents/information_gatherer/agent.py](adk_agents/information_gatherer/agent.py)

**A2A Call in Orchestrator:**
```python
# Line 399-414 in orchestrator/agent.py
print(f"[A2A] Calling Information Gatherer agent to format results...")
runner = InMemoryRunner(agent=gatherer_agent)

# Build prompt with fetched data
gatherer_prompt = f"""Format the following REAL-TIME FETCHED DATA...
{data_summary}
"""

response = await runner.run_debug(gatherer_prompt)
response_text = extract_response_text(response)

print(f"[STEP 4/5] OK Formatting complete")
```

**Output Format:** User-friendly formatted text

---

### 3. Content Analysis Agent (A2A)

**Location:** [adk_agents/content_analyzer/agent.py](adk_agents/content_analyzer/agent.py)

**A2A Call in Orchestrator:**
```python
# In pipeline/steps/analysis.py
print(f"[A2A] Calling Content Analysis agent...")
analyzer_runner = InMemoryRunner(agent=analyzer_agent)

# Build analysis prompt with fetched data
analysis_prompt = f"""Analyze the following fetched data for credibility...

Research Query: {query}
Query Type: {classification.get('query_type')}

FETCHED DATA (from {len(fetched_data)} sources):
{json.dumps(fetched_data, indent=2)}

YOUR TASK:
1. Score each source's credibility (0-100)
2. Extract key facts with confidence levels
3. Identify any conflicts between sources
4. Create comparison matrix if this is a product comparison
5. Normalize all data (prices, ratings, specifications)
"""

analysis_response = await analyzer_runner.run_debug(analysis_prompt)
analysis_text = extract_response_text(analysis_response)

# Parse JSON analysis
analysis_json = json.loads(cleaned_analysis)

print(f"[STEP 5/6] OK Analysis complete")
```

**Output Format:** Comprehensive JSON with:
- `analysis_summary`: Overview of analysis
- `source_credibility`: Array of credibility scores
- `extracted_facts`: Array of facts with confidence
- `conflicts`: Array of detected conflicts
- `comparison_matrix`: Product comparison table
- `recommendations`: List of recommendations

---

### 4. Report Generator Agent (A2A) ✨ **NEW**

**Location:** [adk_agents/report_generator/agent.py](adk_agents/report_generator/agent.py)

**A2A Call in Orchestrator:**
```python
# In pipeline/steps/reporting.py
print(f"[A2A] Calling Report Generator agent...")
report_runner = InMemoryRunner(agent=report_generator_agent)

# Build comprehensive prompt for Report Generator
report_prompt = f"""Generate a tailored report for the user.

QUERY: {query}

CLASSIFICATION:
- Type: {classification.get('query_type')}
- Strategy: {classification.get('research_strategy')}
- Complexity: {classification.get('complexity_score')}/10
- Key Topics: {', '.join(classification.get('key_topics', []))}

AVAILABLE SOURCES (STRICT - Use ONLY these sources with these exact numbers):
[1] Source Title - URL (Credibility: 85/100)
[2] Source Title - URL (Credibility: 75/100)
...

FORMATTED INFORMATION (from Information Gatherer):
{formatted_info}

CONTENT ANALYSIS (credibility scores and extracted facts):
{json.dumps(analysis_json, indent=2)}

YOUR TASK:
Generate a professional report following the format for query type: {classification.get('query_type')}

Requirements:
1. Use the appropriate report format (factual/comparative/exploratory)
2. STRICTLY use ONLY the sources listed above with their exact citation numbers
3. Include credibility indicators in your Sources section (High/Medium/Low based on scores)
4. Apply weighted scoring if user stated priorities in query
5. Generate 3-5 relevant follow-up questions (MANDATORY)
6. Use professional markdown formatting
7. Ensure all claims are cited from the available sources
8. Highlight any conflicts between sources transparently
"""

report_response = await report_runner.run_debug(report_prompt)
final_report = extract_response_text(report_response)

print(f"[STEP 6/6] OK Report generation complete")
```

**Output Format:** Professional markdown report with:
- Executive summary or introduction
- Main findings with inline citations `[1]`, `[2]`, etc.
- **Sources section** with URLs and credibility ratings
- **Follow-up Questions** section (3-5 questions)
- Comparison matrices (for comparative queries)
- Conflict highlights (if sources disagree)
- Professional formatting and structure

---

## Why A2A Communication?

### Benefits of A2A Pattern

1. **Separation of Concerns**
   - Each agent has ONE job and does it well
   - Classifier → classifies queries
   - Gatherer → formats data
   - Analyzer → assesses credibility

2. **Deterministic Execution**
   - Fixed pipeline ensures all steps run in order
   - No LLM decides whether to skip steps
   - Predictable, reliable workflow

3. **Modularity**
   - Easy to swap agents (e.g., different classifier)
   - Easy to add new agents (like Content Analyzer)
   - Easy to test agents independently

4. **Scalability**
   - Agents can be distributed across servers
   - Each agent can use different models
   - Can optimize per-agent resources

5. **Maintainability**
   - Each agent is self-contained
   - Easy to debug (logs show A2A calls)
   - Clear data flow between agents

---

## Modular Orchestrator Architecture

The orchestrator has been refactored from a monolithic `agent.py` file into a **modular, maintainable structure**:

### Core Modules

#### 1. **config.py** - Configuration & Environment
```python
# Centralized configuration
- Project root path resolution
- Environment variable loading (.env)
- API key validation
- Retry configuration for Gemini API
- Session storage paths
```

#### 2. **initialization.py** - Dependency Loading
```python
# Centralized initialization of all dependencies
- Observability setup (logger, tracer, metrics, error_tracker)
- Load all 4 A2A sub-agents (classifier, gatherer, analyzer, report_generator)
- Initialize Persistent Session Service
- Initialize Quality Assurance Service
- Export all components for use in pipeline
```

#### 3. **helpers.py** - Utility Functions
```python
# Helper functions for orchestrator logic
- generate_clarification_prompt(): Creates clarification prompts
- execute_with_clarification(): Handles user clarifications
```

#### 4. **agent.py** - Main Agent Wrapper
```python
# Simple wrapper agent that calls the pipeline
- Creates FunctionTool from execute_fixed_pipeline
- Defines orchestrator agent with instruction
- Agent has ONE job: call execute_fixed_pipeline tool
- No decision-making - just deterministic tool calling
- Exports 'agent' and 'root_agent' for ADK Web UI
```

#### 5. **pipeline/orchestrator.py** - Main Pipeline Controller
```python
async def execute_fixed_pipeline(query, user_id, interactive, session_id):
    """
    FIXED PIPELINE: Executes research in a deterministic order.

    - Generates query_id for tracking
    - Creates or resumes session for conversation persistence
    - Starts distributed trace for observability
    - Executes all 7 steps sequentially
    - Stores results in session history
    - Returns complete result dictionary
    """
```

#### 6. **pipeline/steps/** - Modular Step Implementations

Each step is isolated in its own module for maintainability:

- **classification.py**: Query classification (Step 1)
  - `classify_query_step()`: Calls Query Classifier agent
  - User memory integration for personalization
  - Robust JSON parsing with fallbacks

- **search.py**: Web search (Step 2)
  - `search_step()`: Google Custom Search API
  - Smart Google Shopping integration
  - URL collection and validation

- **data_fetching.py**: Data extraction (Step 3)
  - `fetch_data_step()`: Fetch content from URLs
  - Product info extraction
  - Error handling for failed URLs

- **formatting.py**: Result formatting (Step 4)
  - `format_results_step()`: Calls Information Gatherer agent
  - User-friendly response generation

- **analysis.py**: Content analysis (Step 5)
  - `analyze_content_step()`: Calls Content Analysis agent
  - Credibility scoring
  - Fact extraction and conflict detection

- **reporting.py**: Report generation (Step 6)
  - `generate_report_step()`: Calls Report Generator agent
  - Professional markdown report with citations
  - Source prioritization by credibility

- **citation_formatter.py**: Citation validation (Step 6.5)
  - `format_citations()`: Ensures proper citation format
  - `validate_and_clean_citations()`: Removes invalid citations
  - Adds credibility indicators to sources

- **quality_check.py**: Quality validation (Step 7)
  - `quality_check_step()`: Validates output completeness
  - Citation validation
  - Comparison matrix verification
  - Quality score calculation (0-100)

### Benefits of Modular Structure

1. **Separation of Concerns**: Each module has ONE clear responsibility
2. **Easy Testing**: Test individual steps in isolation
3. **Maintainability**: Changes to one step don't affect others
4. **Readability**: ~100-200 lines per module vs 600+ line monolith
5. **Reusability**: Steps can be reused in other pipelines
6. **Debugging**: Easy to identify which step failed
7. **Extensibility**: Add new steps without touching existing code

---

## A2A Message Flow Example

### Real Query: "Sony WH-1000XM5 price"

```
USER → ORCHESTRATOR
  Query: "Sony WH-1000XM5 price"

ORCHESTRATOR → CLASSIFIER (A2A)
  Message: "Sony WH-1000XM5 price\n\nUser ID: default"

CLASSIFIER → ORCHESTRATOR (A2A Response)
  Response: {
    "query_type": "comparative",
    "complexity_score": 5,
    "research_strategy": "multi-source",
    "key_topics": ["Sony WH-1000XM5", "price"]
  }

ORCHESTRATOR → WEB SEARCH (Tool)
  Query: "Sony WH-1000XM5 price"

WEB SEARCH → ORCHESTRATOR (Tool Response)
  Response: {
    "urls": ["amazon.com/...", "bestbuy.com/..."],
    "count": 5
  }

ORCHESTRATOR → DATA FETCH (Tool)
  URLs: ["amazon.com/...", "bestbuy.com/..."]

DATA FETCH → ORCHESTRATOR (Tool Response)
  Response: [
    {"url": "amazon.com", "data": {"price": "$348", ...}},
    {"url": "bestbuy.com", "data": {"price": "$379.99", ...}}
  ]

ORCHESTRATOR → GATHERER (A2A)
  Message: "Format the following REAL-TIME FETCHED DATA...\n[data]"

GATHERER → ORCHESTRATOR (A2A Response)
  Response: "Based on the fetched data:\n\n**Sony WH-1000XM5**\n..."

ORCHESTRATOR → ANALYZER (A2A) ✨
  Message: "Analyze the following fetched data...\n[data]"

ANALYZER → ORCHESTRATOR (A2A Response) ✨
  Response: {
    "analysis_summary": {
      "total_sources": 2,
      "credible_sources": 2,
      "conflicts_found": 1
    },
    "source_credibility": [
      {"url": "amazon.com", "score": 85, "level": "Highly Credible"},
      {"url": "bestbuy.com", "score": 75, "level": "Moderately Credible"}
    ],
    "extracted_facts": [...],
    "conflicts": [
      {
        "type": "price",
        "description": "$31.99 difference",
        "recommended": "$348 (higher credibility)"
      }
    ]
  }

ORCHESTRATOR → USER
  Final Result: {
    "status": "success",
    "content": "Based on the fetched data...",
    "content_analysis": {...},
    "pipeline_steps": {
      "classification": "OK Complete",
      "search": "OK Found 5 URLs",
      "fetch": "OK Fetched 2 sources",
      "format": "OK Complete",
      "analysis": "OK Complete"
    }
  }
```

---

## A2A Error Handling

Each A2A call includes error handling:

```python
try:
    # A2A call
    runner = InMemoryRunner(agent=target_agent)
    response = await runner.run_debug(prompt)
    print(f"[A2A] {agent_name} response received")

    # Process response
    result = extract_and_parse_response(response)
    print(f"[STEP X/5] OK {step_name} complete")

except Exception as e:
    print(f"[STEP X/5] WARN {step_name} failed: {e}")
    # Return fallback/default result
    result = get_default_result()
```

The pipeline continues even if one agent fails, ensuring resilience.

---

## Testing A2A Communication

### Unit Test Pattern

```python
@pytest.mark.asyncio
async def test_agent_a2a_communication():
    """Test A2A communication with agent"""
    from google.adk.runners import InMemoryRunner
    from adk_agents.content_analyzer.agent import agent

    # Create runner
    runner = InMemoryRunner(agent=agent)

    # Build test prompt
    prompt = "Test prompt with data..."

    # Call agent via A2A
    response = await runner.run_debug(prompt)

    # Verify response
    assert response is not None
    assert len(response) > 0
```

### Integration Test

See: [test_content_analysis_integration.py](test_content_analysis_integration.py)

Tests the full A2A pipeline from orchestrator through all agents.

---

## Agent Directory Structure

```
adk_agents/
├── orchestrator/                    ← MODULAR ORCHESTRATOR
│   ├── __init__.py                 ← Package initialization
│   ├── agent.py                    ← Main agent wrapper (calls pipeline)
│   ├── config.py                   ← Configuration & environment
│   ├── initialization.py           ← Loads sub-agents & services
│   ├── helpers.py                  ← Utility functions
│   │
│   └── pipeline/                   ← PIPELINE IMPLEMENTATION
│       ├── __init__.py
│       ├── orchestrator.py         ← Main execute_fixed_pipeline()
│       │
│       └── steps/                  ← MODULAR STEP IMPLEMENTATIONS
│           ├── __init__.py
│           ├── classification.py   ← Step 1: Query classification
│           ├── search.py           ← Step 2: Web search
│           ├── data_fetching.py    ← Step 3: Data extraction
│           ├── formatting.py       ← Step 4: Result formatting
│           ├── analysis.py         ← Step 5: Content analysis
│           ├── reporting.py        ← Step 6: Report generation
│           ├── citation_formatter.py ← Step 6.5: Citation validation
│           └── quality_check.py    ← Step 7: Quality validation
│
├── query_classifier/
│   ├── __init__.py
│   └── agent.py                    ← A2A Agent #1 (Classification)
│
├── information_gatherer/
│   ├── __init__.py
│   └── agent.py                    ← A2A Agent #2 (Formatting)
│
├── content_analyzer/
│   ├── __init__.py
│   └── agent.py                    ← A2A Agent #3 (Analysis)
│
└── report_generator/               ← NEW ✨
    ├── __init__.py
    └── agent.py                    ← A2A Agent #4 (Report Generation)
```

### Architecture Principles

**Each A2A Agent:**
- Exports an `agent` variable
- Is imported by `orchestrator/initialization.py`
- Is called via `InMemoryRunner` (A2A protocol)
- Returns structured output (JSON or text)
- Is stateless and independent

**Each Pipeline Step:**
- Has a single, well-defined responsibility
- Imports dependencies from `initialization.py`
- Returns a specific data type (dict, list, str, etc.)
- Handles errors gracefully with fallbacks
- Logs progress with step numbers (e.g., `[STEP 3/6]`)

---

## Adding New A2A Agents

To add a new agent to the A2A pipeline:

1. **Create agent directory**
   ```bash
   mkdir adk_agents/new_agent
   ```

2. **Create agent.py**
   ```python
   from google.adk.agents import LlmAgent
   from google.adk.models.google_llm import Gemini

   agent = LlmAgent(
       name="new_agent",
       model=Gemini(model="gemini-2.5-flash-lite"),
       description="What this agent does",
       instruction="Detailed instructions...",
       tools=[]
   )
   ```

3. **Import in orchestrator**
   ```python
   print("  Loading New Agent...")
   sys.path.insert(0, str(Path(__file__).parent.parent / 'new_agent'))
   from adk_agents.new_agent.agent import agent as new_agent
   ```

4. **Add A2A call in pipeline**
   ```python
   print(f"[A2A] Calling New Agent...")
   runner = InMemoryRunner(agent=new_agent)
   response = await runner.run_debug(prompt)
   result = extract_response(response)
   print(f"[A2A] New Agent complete")
   ```

---

## Supporting Services & Infrastructure

The orchestrator integrates with several supporting services for enhanced functionality:

### 1. Persistent Session Service

**Location:** [services/persistent_session_service.py](services/persistent_session_service.py)

**Purpose:** Manages conversation history and user memory across sessions

**Features:**
- **Session Management**: Create, resume, and track user sessions
- **Message History**: Store user and assistant messages with metadata
- **User Memory**: Persist user preferences, research history, and topics
- **Conversation Context**: Maintain context across multiple queries
- **File-based Storage**: JSON files stored in `orchestrator_sessions/`

**Usage in Pipeline:**
```python
# Initialize in initialization.py
session_service = create_persistent_session_service(orchestrator_sessions_dir)

# Create or resume session
session_id = session_service.create_session(user_id=user_id, title=query[:50])

# Store messages
session_service.add_message(session_id, "user", query, metadata={"query_id": query_id})
session_service.add_message(session_id, "assistant", final_report, metadata={...})

# Get user memory for personalization
user_memory = session_service.get_user_memory(user_id)
recent_research = user_memory.get("research_history", [])[-3:]

# Store in user memory
session_service.store_user_memory(user_id, "research_history", query, {
    "query": query,
    "query_type": classification.get('query_type'),
    "topics": classification.get('key_topics', [])
})
```

**Benefits:**
- Personalized responses based on user history
- Conversation context for follow-up questions
- User preference learning over time
- Session resumption after interruptions

---

### 2. Quality Assurance Service

**Location:** [services/quality_assurance.py](services/quality_assurance.py)

**Purpose:** Validates output quality and completeness

**Features:**
- **Completeness Check**: Verifies all required sections exist
- **Citation Validation**: Ensures citations are properly formatted and numbered
- **Comparison Matrix Validation**: Checks for comparison tables in comparative queries
- **Quality Scoring**: Calculates overall quality score (0-100)
- **Detailed Feedback**: Provides specific improvement suggestions

**Usage in Pipeline:**
```python
# Initialize in initialization.py
qa_service = QualityAssuranceService()

# In pipeline/steps/quality_check.py
quality_report = qa_service.validate_output(
    final_report=final_report,
    classification=classification,
    analysis_json=analysis_json,
    fetched_data=fetched_data,
    query=query
)

# Quality report includes:
# - overall_score: 0-100
# - completeness_score: 0-100
# - citation_score: 0-100
# - comparison_matrix_score: 0-100
# - issues: List of problems found
# - recommendations: List of improvements
```

**Quality Metrics:**
- **Completeness (40% weight)**: Checks for sources section, follow-up questions, main content
- **Citations (30% weight)**: Validates citation format, numbering, source references
- **Comparison Matrix (30% weight)**: Verifies comparison table for comparative queries
- **Overall Score**: Weighted average with grade (A/B/C/D/F)

---

### 3. Observability Integration

**Location:** [utils/observability.py](utils/observability.py)

**Purpose:** Comprehensive logging, tracing, metrics, and error tracking

#### Components:

**A. Structured Logger**
```python
logger = get_logger("orchestrator")

# Structured logging with context
logger.info("Starting pipeline", query_id=query_id, user_id=user_id)
logger.error("Step failed", step="classification", error=str(e))
```

**Features:**
- Structured JSON logging
- Contextual information (query_id, user_id, etc.)
- Log levels (DEBUG, INFO, WARN, ERROR)
- File and console output

**B. Distributed Tracer**
```python
tracer = get_tracer()

# Trace entire pipeline execution
with tracer.trace_span("fixed_pipeline", {
    "query": query[:100],
    "user_id": user_id,
    "query_id": query_id
}):
    # Execute pipeline steps...
```

**Features:**
- Distributed tracing across services
- Performance timing for each operation
- Span attributes for debugging
- Parent-child span relationships

**C. Metrics Collection**
```python
metrics = get_metrics()

# Track pipeline executions
metrics.increment_counter("pipeline_start_total", labels={"user_id": user_id})
metrics.increment_counter("pipeline_success_total", labels={"query_type": "comparative"})
metrics.record_histogram("pipeline_duration_seconds", duration)
```

**Metrics Types:**
- **Counters**: Pipeline starts, successes, failures
- **Histograms**: Duration, latency distributions
- **Gauges**: Active sessions, queue depth
- **Labels**: user_id, query_type, step_name for filtering

**D. Error Tracker**
```python
error_tracker = get_error_tracker()

# Track exceptions with context
error_tracker.capture_exception(e, context={
    "query_id": query_id,
    "step": "classification",
    "user_id": user_id
})
```

**Features:**
- Exception tracking with full stack traces
- Contextual information for debugging
- Error rate monitoring
- Integration with error reporting services (optional)

#### Benefits of Observability:

1. **Debugging**: Quickly identify which step failed and why
2. **Performance Monitoring**: Track pipeline execution times
3. **User Behavior**: Analyze query patterns and user preferences
4. **Alerting**: Set up alerts for high error rates or slow responses
5. **Optimization**: Identify bottlenecks and optimize slow steps
6. **Accountability**: Full audit trail of all operations

---

## Summary

### Core Architecture

✅ **A2A Communication** used throughout ResearchMate AI
✅ **4 specialized agents** communicate via A2A protocol:
   1. **Query Classifier** - Analyzes query type and complexity
   2. **Information Gatherer** - Formats fetched data into user-friendly responses
   3. **Content Analyzer** - Scores source credibility and extracts facts
   4. **Report Generator** - Creates professional reports with citations ✨

✅ **7-step fixed pipeline** ensures deterministic execution:
   1. Classification (A2A)
   2. Web Search (Tool)
   3. Data Fetching (Tool)
   4. Formatting (A2A)
   5. Content Analysis (A2A)
   6. Report Generation (A2A)
   6.5. Citation Post-Processing (Service)
   7. Quality Validation (Service)

### Modular Design

✅ **Orchestrator refactored** into modular structure:
   - `config.py` - Configuration management
   - `initialization.py` - Dependency loading
   - `helpers.py` - Utility functions
   - `agent.py` - Main agent wrapper
   - `pipeline/orchestrator.py` - Pipeline controller
   - `pipeline/steps/` - Individual step modules (8 modules)

✅ **Supporting services** integrated:
   - **Persistent Session Service** - Conversation history and user memory
   - **Quality Assurance Service** - Output validation with quality scoring
   - **Observability** - Structured logging, tracing, metrics, error tracking

### Architecture Benefits

✅ **Separation of Concerns** - Each module has one clear responsibility
✅ **InMemoryRunner** handles all agent-to-agent communication
✅ **Error handling** at each A2A boundary with fallbacks
✅ **Modular architecture** makes adding new agents/steps straightforward
✅ **Observability** enables debugging, monitoring, and optimization
✅ **Quality Assurance** ensures high-quality, validated outputs
✅ **Session Persistence** enables conversation context and personalization

### Evolution

The orchestrator has evolved from a **monolithic 600+ line file** to a **modular, maintainable architecture** with:
- Clear separation between pipeline controller and step implementations
- 4 specialized A2A agents working together
- Comprehensive observability and quality assurance
- Session management for conversation continuity
- ~100-200 lines per module for better readability and testing

This architecture demonstrates best practices for building reliable, maintainable, and observable multi-agent systems.
