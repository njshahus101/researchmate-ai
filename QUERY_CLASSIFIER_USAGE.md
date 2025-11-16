# Query Classifier - Usage Guide

## Two Versions for Different Use Cases

### 1. Machine-to-Machine (Agent Integration) - Pure JSON
**File:** `agents/query_classifier_mvp.py`

**Use Case:** Other agents in your ResearchMate AI system

**Response Format:** Pure JSON
```json
{
    "query_type": "comparative",
    "complexity_score": 6,
    "research_strategy": "multi-source",
    "key_topics": ["wireless headphones", "budget", "audio quality"],
    "user_intent": "Find best value headphones under $200",
    "estimated_sources": 4,
    "reasoning": "..."
}
```

**Usage Example:**
```python
from agents.query_classifier_mvp import classify_query
from services.memory_service import MemoryService

# Create memory service
memory = MemoryService("memory.json")

# Classify query
result = await classify_query(
    "Best laptops under $1000",
    user_id="user_123",
    memory_service=memory
)

# Use in Information Gatherer
if result['research_strategy'] == 'multi-source':
    sources_needed = result['estimated_sources']
    topics = result['key_topics']
    # Fetch from multiple sources...
```

---

### 2. Human-Facing (ADK Web UI) - Natural Language + JSON
**File:** `agents_ui/query_classifier/agent.py`

**Use Case:** Interactive testing, demonstrations, human users

**Response Format:** Conversational explanation + JSON summary

**Example Response:**
```
Great question! I'll help you classify this query.

**Classification: Comparative**

This is a product comparison query where you're looking for
the best option within a specific budget.

**Analysis:**
- Complexity Score: 6/10 (moderate)
- Research Strategy: Multi-source
- Key Topics: wireless headphones, budget audio
- Your Intent: Find best value headphones under $200
- Recommended Sources: 4-5 reliable tech review sites

**Reasoning:**
This requires comparing multiple products based on various
criteria. It's more complex than a simple fact lookup but
doesn't require deep technical research.

**Next Steps:**
I'd recommend searching tech review sites like RTINGS and
Wirecutter, then creating a comparison table.

```json
{
    "query_type": "comparative",
    "complexity_score": 6,
    "research_strategy": "multi-source",
    "key_topics": ["wireless headphones", "budget", "audio quality"],
    "user_intent": "Find best value headphones under $200",
    "estimated_sources": 4
}
```
```

---

## Testing Memory Integration

### Via ADK Web UI:

1. **Start the server:**
```bash
adk web agents_ui --port 8080
```

2. **Open browser:** http://127.0.0.1:8080

3. **Select:** query_classifier

4. **Test with related queries:**
```
Query 1: "Best wireless headphones under $200"
Query 2: "Sony WH-1000XM5 battery life"
Query 3: "Compare Sony vs Bose headphones"
```

The agent will:
- Remember your previous queries
- Show related topics in responses
- Build connections between topics

### Via Python Script (Programmatic):

```python
import asyncio
from agents.query_classifier_mvp import classify_query
from services.memory_service import MemoryService

async def test_memory():
    memory = MemoryService("test_memory.json")
    user_id = "test_user"

    # First query
    result1 = await classify_query(
        "Best noise-cancelling headphones",
        user_id=user_id,
        memory_service=memory
    )

    # Second query - will have context from first
    result2 = await classify_query(
        "Sony WH-1000XM5 review",
        user_id=user_id,
        memory_service=memory
    )

    # Check memory
    history = memory.get_recent_research(user_id)
    print(f"Research history: {len(history)} entries")

    related = memory.get_related_topics(user_id, "headphones")
    print(f"Related topics: {related}")

asyncio.run(test_memory())
```

---

## Multi-Agent Architecture

### How Query Classifier Fits:

```
┌─────────────────────────────────────────────────────────┐
│ User: "Best laptops for video editing under $1500"     │
└───────────────────┬─────────────────────────────────────┘
                    ▼
        ┌───────────────────────┐
        │  Query Classifier     │
        │  (query_classifier    │
        │   _mvp.py)            │
        └──────────┬────────────┘
                   │ Returns JSON:
                   │ {
                   │   "query_type": "comparative",
                   │   "complexity_score": 7,
                   │   "research_strategy": "multi-source",
                   │   "key_topics": ["laptops", "video editing",
                   │                  "budget", "performance"],
                   │   "estimated_sources": 5
                   │ }
                   ▼
        ┌───────────────────────┐
        │ Information Gatherer  │◄── Uses research_strategy
        │                       │◄── Uses key_topics
        └──────────┬────────────┘◄── Uses estimated_sources
                   │
                   │ Fetches 5 sources about
                   │ laptops for video editing
                   ▼
        ┌───────────────────────┐
        │  Content Analyzer     │◄── Uses complexity_score
        │                       │    (deeper analysis for 7/10)
        └──────────┬────────────┘
                   │
                   │ Structured analysis
                   ▼
        ┌───────────────────────┐
        │  Report Generator     │◄── Uses user_intent
        │                       │◄── Uses query_type
        └──────────┬────────────┘
                   │
                   │ Final report
                   ▼
        ┌───────────────────────────────────────┐
        │ "Here are the top 5 laptops for      │
        │  video editing under $1500..."        │
        └───────────────────────────────────────┘
```

---

## Key Differences Summary

| Feature | MVP (Agent-to-Agent) | Web UI (Human-Facing) |
|---------|---------------------|----------------------|
| **File** | `agents/query_classifier_mvp.py` | `agents_ui/query_classifier/agent.py` |
| **Output** | Pure JSON | Natural Language + JSON |
| **Purpose** | Multi-agent system | Testing & demonstrations |
| **Memory** | Full integration | Full integration |
| **Usage** | `classify_query()` function | ADK Web UI chat |
| **Parsing** | Direct JSON parsing | Extract JSON from markdown |

---

## Recommendation for Your Multi-Agent System

**Use `query_classifier_mvp.py` for:**
- ✓ Information Gatherer integration
- ✓ Content Analyzer integration
- ✓ Orchestrator routing
- ✓ Automated workflows
- ✓ Programmatic access

**Use ADK Web UI for:**
- ✓ Manual testing
- ✓ Demonstrations
- ✓ User feedback
- ✓ Debugging classifications
- ✓ Training/onboarding

---

## Testing Both Approaches

### 1. Test JSON-only (for agents):
```bash
python test_my_query.py
```

### 2. Test with memory integration:
```bash
python test_memory_integration.py
```

### 3. Test Web UI:
```bash
adk web agents_ui --port 8080
# Then open http://127.0.0.1:8080
```

---

## Next Agent Integration

When building the **Information Gatherer**, you'll use:

```python
from agents.query_classifier_mvp import classify_query

# Get classification
classification = await classify_query(user_query, user_id, memory)

# Use the structured data
strategy = classification['research_strategy']
topics = classification['key_topics']
sources_needed = classification['estimated_sources']

# Route accordingly
if strategy == 'quick-answer':
    result = await fetch_single_source(topics[0])
elif strategy == 'multi-source':
    results = await fetch_multiple_sources(topics, sources_needed)
elif strategy == 'deep-dive':
    results = await comprehensive_research(topics, sources_needed)
```

---

**Bottom Line:** You have BOTH natural language (for humans) AND pure JSON (for agents). This hybrid approach gives you the best of both worlds! 🎯
