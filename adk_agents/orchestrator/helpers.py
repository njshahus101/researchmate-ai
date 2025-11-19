"""
Helper functions for the orchestrator agent.
"""


def generate_clarification_prompt(query: str, classification: dict) -> str:
    """
    Generate a clarification prompt for the user based on query classification.

    Args:
        query: Original user query
        classification: Classification results from Query Classifier

    Returns:
        Formatted clarification prompt
    """
    query_type = classification.get('query_type', 'unknown')
    complexity = classification.get('complexity_score', 5)
    strategy = classification.get('research_strategy', 'quick-answer')
    key_topics = classification.get('key_topics', [])

    clarification = f"""
Query Classification Results:
  • Type: {query_type}
  • Research Strategy: {strategy}
  • Complexity: {complexity}/10
  • Key Topics: {', '.join(key_topics) if key_topics else 'Not specified'}

Would you like to provide additional clarification or details to improve the research?

For example:
  - Specify time period (e.g., "current prices" vs "historical data")
  - Add constraints (e.g., "under $300", "from US retailers only")
  - Clarify intent (e.g., "for comparison" vs "to purchase")
  - Narrow scope (e.g., "new products only" vs "including refurbished")

Type additional details or press Enter to continue with current query.
"""
    return clarification


async def execute_with_clarification(original_query: str, clarification: str, user_id: str = "default") -> dict:
    """
    Continue pipeline execution with user-provided clarification.

    Args:
        original_query: The original user query
        clarification: Additional details/clarifications from user
        user_id: User identifier

    Returns:
        Complete research results
    """
    # Import here to avoid circular dependency
    from .pipeline.orchestrator import execute_fixed_pipeline

    # Merge original query with clarification
    if clarification and clarification.strip():
        enhanced_query = f"{original_query}\n\nAdditional context: {clarification}"
        print(f"\n[CLARIFICATION] User provided additional details:")
        print(f"  {clarification}")
    else:
        enhanced_query = original_query
        print(f"\n[CLARIFICATION] No additional details provided, continuing with original query")

    # Execute pipeline with enhanced query (non-interactive mode)
    return await execute_fixed_pipeline(enhanced_query, user_id, interactive=False)
