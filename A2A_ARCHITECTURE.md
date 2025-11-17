# Agent-to-Agent (A2A) Communication Architecture

## Overview

ResearchMate AI uses **Agent-to-Agent (A2A)** communication protocol where the orchestrator coordinates multiple specialized agents. Each agent is called via `InMemoryRunner` with the A2A protocol, allowing agents to communicate through structured messages.

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

### Complete 5-Step A2A Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                        │
│             (Fixed Pipeline Controller)                      │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ User Query
                           ▼
        ┌──────────────────────────────────────┐
        │         STEP 1: CLASSIFICATION        │
        │                                       │
        │  [A2A] Query Classifier Agent         │
        │  - Analyzes query type                │
        │  - Determines complexity              │
        │  - Selects research strategy          │
        │  Returns: JSON classification         │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │         STEP 2: WEB SEARCH            │
        │                                       │
        │  search_web() Tool                    │
        │  - Google Custom Search API           │
        │  Returns: List of URLs                │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │         STEP 3: DATA FETCH            │
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
        │                                       │
        │  [A2A] Information Gatherer Agent     │
        │  - Formats fetched data               │
        │  - Creates user-friendly response     │
        │  Returns: Formatted text              │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │     STEP 5: CONTENT ANALYSIS ✨       │
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
                 ┌─────────────────┐
                 │  Final Result   │
                 │  - Formatted    │
                 │  - Analyzed     │
                 │  - Verified     │
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

### 3. Content Analysis Agent (A2A) ✨ **NEW**

**Location:** [adk_agents/content_analyzer/agent.py](adk_agents/content_analyzer/agent.py)

**A2A Call in Orchestrator:**
```python
# Line 439-471 in orchestrator/agent.py
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

print(f"[STEP 5/5] OK Analysis complete - {analysis_json.get('analysis_summary', {}).get('credible_sources', 0)} credible sources found")
```

**Output Format:** Comprehensive JSON with:
- `analysis_summary`: Overview of analysis
- `source_credibility`: Array of credibility scores
- `extracted_facts`: Array of facts with confidence
- `conflicts`: Array of detected conflicts
- `comparison_matrix`: Product comparison table
- `recommendations`: List of recommendations

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
├── orchestrator/
│   ├── __init__.py
│   └── agent.py              ← Coordinates A2A calls
│
├── query_classifier/
│   ├── __init__.py
│   └── agent.py              ← A2A Agent #1
│
├── information_gatherer/
│   ├── __init__.py
│   └── agent.py              ← A2A Agent #2
│
└── content_analyzer/         ← NEW
    ├── __init__.py
    └── agent.py              ← A2A Agent #3 ✨
```

Each agent:
- Exports an `agent` variable
- Is imported by orchestrator
- Is called via `InMemoryRunner` (A2A)
- Returns structured output

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

## Summary

✅ **A2A Communication** used throughout ResearchMate AI
✅ **3 specialized agents** communicate via A2A protocol:
   1. Query Classifier
   2. Information Gatherer
   3. Content Analysis ✨ (newly added)

✅ **Fixed pipeline** ensures deterministic A2A message flow
✅ **InMemoryRunner** handles all agent-to-agent communication
✅ **Error handling** at each A2A boundary
✅ **Modular architecture** makes adding new agents straightforward

The Content Analysis Agent is fully integrated into this A2A architecture and follows the same communication patterns as the existing agents.
