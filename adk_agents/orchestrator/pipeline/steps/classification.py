"""
Step 1: Query Classification

This module handles query classification by calling the Query Classifier agent.
"""

import json
from google.adk.runners import InMemoryRunner

from ...initialization import logger, classifier_agent, session_service


async def classify_user_query(query: str, user_id: str = "default", query_id: str = None) -> dict:
    """
    Classify a user query to determine research strategy.

    This function calls the Query Classifier agent using A2A protocol.

    Args:
        query: The user's research query
        user_id: User identifier for personalization
        query_id: Optional query ID for tracking

    Returns:
        Dictionary with classification results including query_type,
        research_strategy, complexity_score, and key_topics
    """
    logger.info("Calling Query Classifier via A2A", query_preview=query[:50], query_id=query_id)

    # Get user context from persistent memory
    user_memory = session_service.get_user_memory(user_id)
    recent_research = user_memory.get("research_history", [])[-3:] if user_memory else []

    # Build context string
    context = f"\n\nUser ID: {user_id}"
    if user_memory and user_memory.get("preferences"):
        context += f"\nUser Preferences: {json.dumps(user_memory['preferences'])}"
    if recent_research:
        context += f"\nRecent Research: {json.dumps(recent_research)}"

    # Call classifier agent via runner (A2A)
    runner = InMemoryRunner(agent=classifier_agent)
    try:
        response = await runner.run_debug(query + context)
        logger.info("Query Classifier response received")

        # Extract response
        if isinstance(response, list) and len(response) > 0:
            last_event = response[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                response_text = last_event.content.parts[0].text
            else:
                response_text = str(last_event)
        else:
            response_text = str(response)

        # Parse JSON response with robust error handling
        cleaned_text = response_text.strip()

        # Remove markdown code blocks
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()

        # Handle duplicate JSON responses (LLM sometimes returns classification twice)
        # Find the first complete JSON object
        try:
            # Try to parse the first JSON object
            classification = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            # If parsing fails, try to extract just the first JSON object
            print(f"[A2A] Warning: JSON parsing failed, attempting to extract first valid JSON object...")

            # Find the first opening brace and matching closing brace
            start_idx = cleaned_text.find('{')
            if start_idx == -1:
                raise ValueError("No JSON object found in response")

            brace_count = 0
            end_idx = start_idx

            for i in range(start_idx, len(cleaned_text)):
                if cleaned_text[i] == '{':
                    brace_count += 1
                elif cleaned_text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break

            if brace_count != 0:
                raise ValueError("Malformed JSON - unbalanced braces")

            first_json = cleaned_text[start_idx:end_idx]
            classification = json.loads(first_json)
            print(f"[A2A] Successfully extracted first JSON object (ignored duplicate)")

        # Store in persistent memory
        session_service.store_user_memory(
            user_id,
            "research_history",
            query,
            {
                "query": query,
                "query_type": classification.get('query_type', 'unknown'),
                "topics": classification.get('key_topics', [])
            }
        )

        print(f"[A2A] Classification complete: {classification.get('query_type')} - {classification.get('research_strategy')}")
        return classification

    except Exception as e:
        print(f"[A2A ERROR] Classification failed: {e}")
        return {
            "error": str(e),
            "query_type": "unknown",
            "research_strategy": "quick-answer",
            "complexity_score": 5
        }


async def classify_query_step(query: str, user_id: str = "default", query_id: str = None) -> dict:
    """
    Execute Step 1: Query Classification.

    Args:
        query: User's research query
        user_id: User identifier
        query_id: Query tracking ID

    Returns:
        Classification results
    """
    print(f"\n[STEP 1/6] Classifying query...")
    classification = await classify_user_query(query, user_id, query_id)

    if classification.get('error'):
        print(f"[STEP 1/6] X Classification failed: {classification['error']}")
        # Use defaults if classification fails
        classification = {
            "query_type": "factual",
            "research_strategy": "quick-answer",
            "complexity_score": 5,
            "key_topics": []
        }
    else:
        print(f"[STEP 1/6] OK Classification complete")
        print(f"  Type: {classification.get('query_type')}")
        print(f"  Strategy: {classification.get('research_strategy')}")
        print(f"  Complexity: {classification.get('complexity_score')}/10")

    return classification
