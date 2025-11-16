# Query Classifier - Quick Start Guide

## What's Been Completed

The Query Classifier Agent is now **fully functional** with:
- ✓ LLM-based query classification (Gemini 2.5 Flash Lite)
- ✓ Memory Service integration for user context
- ✓ Automatic research history tracking
- ✓ Comprehensive unit tests
- ✓ JSON-structured responses

---

## Quick Test

### 1. Test Basic Classification (No Memory)

```bash
python test_my_query.py
```

Edit the query in `test_my_query.py` line 16:
```python
my_query = "What are the best programming languages to learn in 2025?"
```

### 2. Test with Memory Integration

```bash
python test_memory_integration.py
```

This demonstrates:
- User profile setup with preferences
- Classification with user context
- Research history tracking
- Topic connection building

---

## Usage Examples

### Example 1: Simple Classification

```python
import asyncio
from agents.query_classifier_mvp import classify_query

async def main():
    result = await classify_query("Best laptops under $1000")

    print(f"Type: {result['query_type']}")
    print(f"Complexity: {result['complexity_score']}/10")
    print(f"Strategy: {result['research_strategy']}")
    print(f"Topics: {', '.join(result['key_topics'])}")

asyncio.run(main())
```

### Example 2: With User Context

```python
import asyncio
from agents.query_classifier_mvp import classify_query
from services.memory_service import MemoryService

async def main():
    # Setup memory
    memory = MemoryService("user_memory.json")
    user_id = "john_123"

    # Store user preferences
    memory.store_preference(user_id, "priority_battery_life", True)
    memory.store_preference(user_id, "preferred_brands", ["Dell", "Lenovo"])

    # Classify with context
    result = await classify_query(
        "Best laptops under $1000",
        user_id=user_id,
        memory_service=memory
    )

    # Result will consider user preferences
    print(result['reasoning'])

asyncio.run(main())
```

### Example 3: Building Research History

```python
import asyncio
from agents.query_classifier_mvp import classify_query
from services.memory_service import MemoryService

async def main():
    memory = MemoryService("user_memory.json")
    user_id = "sarah_456"

    queries = [
        "What is machine learning?",
        "Best Python libraries for ML",
        "How to build a neural network"
    ]

    for query in queries:
        result = await classify_query(
            query,
            user_id=user_id,
            memory_service=memory
        )
        print(f"Classified: {query} as {result['query_type']}")

    # Check research history
    history = memory.get_recent_research(user_id)
    print(f"\nTotal queries: {len(history)}")

    # Check related topics
    related = memory.get_related_topics(user_id, "machine learning")
    print(f"Related to ML: {related}")

asyncio.run(main())
```

---

## Understanding Classification Results

### Query Types

1. **factual** - Simple fact-based questions
   - Example: "What is the capital of France?"
   - Strategy: quick-answer
   - Complexity: 1-3

2. **comparative** - Product/service comparisons
   - Example: "Best wireless headphones under $200"
   - Strategy: multi-source
   - Complexity: 4-7

3. **exploratory** - Learning about topics
   - Example: "Explain quantum computing"
   - Strategy: deep-dive
   - Complexity: 6-10

4. **monitoring** - Tracking developments
   - Example: "Latest AI developments"
   - Strategy: multi-source
   - Complexity: varies

### Response Structure

```json
{
    "query_type": "comparative",
    "complexity_score": 6,
    "research_strategy": "multi-source",
    "key_topics": ["laptops", "budget", "performance"],
    "user_intent": "Find best value laptop for budget",
    "estimated_sources": 4,
    "reasoning": "Query requires comparing multiple products..."
}
```

---

## Running Tests

### Unit Tests
```bash
# Run all tests
python -m pytest tests/test_query_classifier.py -v

# Run specific test
python -m pytest tests/test_query_classifier.py::TestQueryClassifier::test_agent_creation_with_memory -v

# Run without API calls
python -m pytest tests/test_query_classifier.py -v -k "not asyncio or test_agent_creation"
```

### Integration Tests
```bash
# Full integration test with memory
python test_memory_integration.py

# Quick single query test
python test_my_query.py
```

---

## Configuration

### Environment Setup

Required in `.env`:
```
GOOGLE_API_KEY=your_api_key_here
```

### Memory Storage

Default storage: `memory_bank.json`

Custom storage:
```python
memory = MemoryService(storage_path="custom_path/memory.json")
```

---

## Common Use Cases

### 1. Research Assistant
```python
# User asks about a topic
query = "Best practices for REST API design"
result = await classify_query(query, user_id="dev_123", memory_service=memory)

# Use classification to determine research depth
if result['complexity_score'] >= 7:
    # Deep dive research
    sources_needed = 10
elif result['complexity_score'] >= 4:
    # Moderate research
    sources_needed = 5
else:
    # Quick answer
    sources_needed = 1
```

### 2. Personalized Recommendations
```python
# Store user preferences
memory.store_preference(user_id, "expertise_level", "beginner")

# Classification considers expertise
result = await classify_query(
    "Explain neural networks",
    user_id=user_id,
    memory_service=memory
)

# Result will adjust complexity based on expertise
```

### 3. Topic Tracking
```python
# After multiple queries, check related topics
related = memory.get_related_topics(user_id, "machine learning")
# Returns: ["python", "neural networks", "tensorflow", ...]

# Use for suggestions
print(f"You might also be interested in: {', '.join(related)}")
```

---

## Performance Tips

1. **Reuse Memory Service**: Create once, use multiple times
   ```python
   memory = MemoryService("memory.json")
   # Use for all queries in session
   ```

2. **Batch Related Queries**: Group similar queries together
   ```python
   queries = ["query1", "query2", "query3"]
   for q in queries:
       result = await classify_query(q, user_id, memory)
       await asyncio.sleep(0.5)  # Small delay to avoid rate limits
   ```

3. **Monitor Memory Size**: Clean up old entries periodically
   ```python
   # Keep only last 100 entries
   history = memory.get_recent_research(user_id, limit=100)
   ```

---

## Troubleshooting

### Error: "GOOGLE_API_KEY not found"
**Solution:** Add API key to `.env` file

### Error: Unicode encoding issues
**Solution:** Use UTF-8 encoding for console output or avoid emojis

### Error: Import errors
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Tests failing with API errors
**Solution:** Check API key and internet connection, or skip async tests:
```bash
pytest -k "not asyncio"
```

---

## Next Steps

With the Query Classifier complete, you can now:

1. **Integrate with Information Gatherer** - Use classification to guide search strategy
2. **Build Orchestrator** - Route queries based on classification
3. **Enhance Memory** - Add more user preference types
4. **Add Analytics** - Track classification patterns over time

---

## Files Overview

```
researchmate-ai/
├── agents/
│   ├── query_classifier.py          # Original template
│   └── query_classifier_mvp.py      # Working implementation ✓
├── services/
│   └── memory_service.py            # Memory Service ✓
├── tests/
│   └── test_query_classifier.py     # Unit tests ✓
├── test_memory_integration.py       # Integration tests ✓
├── test_my_query.py                 # Quick test script ✓
└── QUERY_CLASSIFIER_COMPLETION_SUMMARY.md  # Full documentation ✓
```

---

## Support

For issues or questions:
1. Check [QUERY_CLASSIFIER_COMPLETION_SUMMARY.md](QUERY_CLASSIFIER_COMPLETION_SUMMARY.md) for detailed documentation
2. Review test files for usage examples
3. Check logs in memory service for debugging

---

**Status:** Production Ready ✓
**Last Updated:** November 15, 2025
