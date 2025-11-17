# Interactive Clarification Feature

## Overview

The orchestrator now supports **interactive clarification** - after classifying a query, it can ask the user for additional details before proceeding with research. This helps:

✅ **Improve result quality** - More specific queries get better results
✅ **Save API calls** - Clarify requirements upfront rather than re-querying
✅ **Guide users** - Show what information would be helpful
✅ **Handle vague queries** - Turn "Find headphones" into specific requirements

---

## How It Works

### Standard Flow (Interactive Mode Disabled)

```
User Query → Classify → Search → Extract → Format → Analyze → Results
```

### Interactive Flow (Interactive Mode Enabled)

```
User Query → Classify → ASK FOR CLARIFICATION → User Input → Search → Extract → Format → Analyze → Results
                              ↓
                    User can add details or press Enter
```

---

## Usage

### Method 1: Single-Step Execution (Non-Interactive)

```python
from adk_agents.orchestrator.agent import execute_fixed_pipeline

# Execute without asking for clarification
result = await execute_fixed_pipeline(
    query="Find headphones",
    interactive=False  # Default
)
```

### Method 2: Two-Step Execution (Interactive)

```python
from adk_agents.orchestrator.agent import execute_fixed_pipeline, execute_with_clarification

# STEP 1: Ask for clarification
result = await execute_fixed_pipeline(
    query="Find headphones",
    interactive=True
)

if result['status'] == 'awaiting_clarification':
    # Display clarification prompt to user
    print(result['clarification_prompt'])

    # Get user input
    user_input = input("Additional details (or press Enter): ")

    # STEP 2: Continue with clarification
    final_result = await execute_with_clarification(
        original_query="Find headphones",
        clarification=user_input
    )
```

---

## Example: Interactive Mode

### User Query (Vague)
```
"Find headphones"
```

### Orchestrator Response
```
Query Classification Results:
  • Type: product
  • Research Strategy: multi-source
  • Complexity: 3/10
  • Key Topics: headphones

Would you like to provide additional clarification or details to improve the research?

For example:
  - Specify time period (e.g., "current prices" vs "historical data")
  - Add constraints (e.g., "under $300", "from US retailers only")
  - Clarify intent (e.g., "for comparison" vs "to purchase")
  - Narrow scope (e.g., "new products only" vs "including refurbished")

Type additional details or press Enter to continue with current query.
```

### User Provides Clarification
```
"I want Sony WH-1000XM5 noise canceling headphones, current price from multiple US retailers, new only under $350"
```

### Enhanced Query
```
Find headphones

Additional context: I want Sony WH-1000XM5 noise canceling headphones, current price from multiple US retailers, new only under $350
```

### Result
The orchestrator now searches with much more specific criteria:
- ✅ Specific model: Sony WH-1000XM5
- ✅ Feature: Noise canceling
- ✅ Time: Current prices
- ✅ Location: US retailers
- ✅ Condition: New only
- ✅ Budget: Under $350

This produces **much better results** than the vague "Find headphones" query!

---

## ADK UI Integration

### For ADK UI Developers

The ADK UI should handle the interactive flow:

```python
# When user submits a query

# 1. Execute with interactive=True
result = await execute_fixed_pipeline(query, interactive=True)

# 2. Check if clarification is needed
if result['status'] == 'awaiting_clarification':
    # Display clarification prompt in UI
    ui.show_clarification_dialog(
        classification=result['classification'],
        prompt=result['clarification_prompt']
    )

    # Wait for user input
    user_clarification = ui.get_user_input()

    # 3. Continue with clarification
    final_result = await execute_with_clarification(
        original_query=result['query'],
        clarification=user_clarification
    )

    # 4. Display final results
    ui.display_results(final_result)
else:
    # No clarification needed, display results directly
    ui.display_results(result)
```

### UI Design Recommendations

**Clarification Dialog:**
```
┌─────────────────────────────────────────────┐
│ Query Classification                        │
├─────────────────────────────────────────────┤
│ Type: product                               │
│ Strategy: multi-source                      │
│ Complexity: 3/10                            │
│ Key Topics: headphones                      │
├─────────────────────────────────────────────┤
│ Would you like to add more details?         │
│                                             │
│ Suggested clarifications:                   │
│  • Specific brand or model                  │
│  • Price range                              │
│  • Condition (new/used)                     │
│  • Location preference                      │
│                                             │
│ [Text input box]                            │
│                                             │
│ [Continue]  [Skip - use original query]     │
└─────────────────────────────────────────────┘
```

---

## Configuration Options

### Enable/Disable Globally

You can set a default in your ADK UI configuration:

```python
# config.py
ENABLE_INTERACTIVE_CLARIFICATION = True  # or False
```

### Per-Query Control

```python
# User can toggle clarification mode
result = await execute_fixed_pipeline(
    query=user_query,
    interactive=user_preference_for_clarification
)
```

### Smart Auto-Detection (Recommended)

Enable clarification only for vague/ambiguous queries:

```python
async def smart_execute(query: str):
    # First classify
    result = await execute_fixed_pipeline(query, interactive=True)

    # Auto-skip clarification for specific queries
    if result['status'] == 'awaiting_clarification':
        classification = result['classification']
        complexity = classification.get('complexity_score', 5)

        # Skip clarification if query is already specific
        if complexity >= 6 and len(query.split()) >= 5:
            # Query is complex and specific enough
            return await execute_with_clarification(query, "")

    return result
```

---

## API Reference

### `execute_fixed_pipeline()`

```python
async def execute_fixed_pipeline(
    query: str,
    user_id: str = "default",
    interactive: bool = False
) -> dict:
    """
    Execute research pipeline with optional clarification.

    Args:
        query: User's research query
        user_id: User identifier for personalization
        interactive: If True, asks for clarifications after classification

    Returns:
        If interactive=False: Complete research results
        If interactive=True and clarification needed:
            {
                "status": "awaiting_clarification",
                "query": str,
                "classification": dict,
                "clarification_prompt": str
            }
    """
```

### `execute_with_clarification()`

```python
async def execute_with_clarification(
    original_query: str,
    clarification: str,
    user_id: str = "default"
) -> dict:
    """
    Continue pipeline execution with user-provided clarification.

    Args:
        original_query: The original user query
        clarification: Additional details from user (can be empty)
        user_id: User identifier

    Returns:
        Complete research results
    """
```

### `generate_clarification_prompt()`

```python
def generate_clarification_prompt(
    query: str,
    classification: dict
) -> str:
    """
    Generate a clarification prompt based on query classification.

    Args:
        query: Original user query
        classification: Classification results from Query Classifier

    Returns:
        Formatted clarification prompt string
    """
```

---

## Benefits

### 1. Better Results

**Before (vague query):**
```
Query: "Find headphones"
Result: Mixed results from consumer headphones to professional studio equipment
```

**After (with clarification):**
```
Query: "Find headphones"
Clarification: "Sony WH-1000XM5, noise canceling, current price, US retailers, under $350"
Result: Specific prices for Sony WH-1000XM5 from Walmart, Best Buy, Amazon, etc.
```

### 2. Reduced API Calls

Without clarification:
1. Initial vague search → poor results
2. User refines query
3. Second search → better results
**Total: 2 searches**

With clarification:
1. Ask for details upfront
2. Single specific search → good results
**Total: 1 search (saves 50% API calls)**

### 3. User Guidance

Clarification prompts **educate users** on what details help:
- Time period
- Price constraints
- Location preferences
- Product conditions

### 4. Handling Ambiguity

Some queries have multiple valid interpretations:
- "Find iPhone" → Which model? New/used? Prices/reviews/specs?

Clarification resolves ambiguity **before** wasting resources on wrong interpretation.

---

## Testing

### Test Script

```bash
python test_interactive_clarification.py
```

### Expected Output

```
TESTING INTERACTIVE CLARIFICATION FEATURE
==========================================

Original Query: Find headphones

[STEP 1/5] Classifying query...
[STEP 1/5] OK Classification complete
  Type: product
  Strategy: multi-source
  Complexity: 3/10

[CLARIFICATION] Asking for user clarification...

Query Classification Results:
  • Type: product
  • Research Strategy: multi-source
  • Complexity: 3/10
  • Key Topics: headphones

Would you like to provide additional clarification or details to improve the research?

SIMULATING USER INPUT
User provides: Sony WH-1000XM5, noise canceling, current price, US retailers, under $350

CONTINUING WITH CLARIFIED QUERY

[CLARIFICATION] User provided additional details:
  Sony WH-1000XM5, noise canceling, current price, US retailers, under $350

[STEP 1/5] Classifying query...
[STEP 2/5] Detected price query - using Google Shopping API...
[STEP 2/5] OK Google Shopping API returned 5 results
...
```

---

## Status

✅ **IMPLEMENTED**
✅ **TESTED**
⏳ **PENDING**: ADK UI integration

### Files Modified

1. **adk_agents/orchestrator/agent.py**
   - Added `generate_clarification_prompt()` function
   - Added `execute_with_clarification()` function
   - Updated `execute_fixed_pipeline()` with `interactive` parameter
   - Added STEP 1.5: Optional interactive clarification

2. **test_interactive_clarification.py** (NEW)
   - Test script demonstrating interactive mode
   - Test script for non-interactive mode
   - Example UI integration code

3. **INTERACTIVE_CLARIFICATION_FEATURE.md** (NEW)
   - This documentation file

---

## Next Steps

### For Users

Enable in your ADK UI or script:
```python
result = await execute_fixed_pipeline(query, interactive=True)
```

### For ADK UI Developers

1. Add clarification dialog to UI
2. Check for `status: "awaiting_clarification"`
3. Display `clarification_prompt` to user
4. Call `execute_with_clarification()` with user input

### Optional Enhancements

1. **Smart suggestions**: Use LLM to generate specific clarification questions based on query type
2. **Pre-filled options**: Offer common clarifications as buttons ("Under $300", "New only", etc.)
3. **History learning**: Remember user preferences (e.g., always prefer US retailers)
4. **Multi-turn clarification**: Allow multiple rounds of refinement

---

## Summary

The interactive clarification feature makes the orchestrator **more intelligent** by:
- ✅ Asking for details **before** searching (saves time and API calls)
- ✅ Guiding users on **what details help**
- ✅ Resolving **ambiguous queries** upfront
- ✅ Producing **better quality results**

It's **optional** (disabled by default for backward compatibility) and easy to integrate into existing ADK UI workflows.
