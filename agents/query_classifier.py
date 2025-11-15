"""
Query Classification Agent

This agent serves as the intelligent router that analyzes user queries to determine
intent, complexity, and optimal workflow. It retrieves relevant context from the
Memory Bank and makes strategic decisions about resource allocation.
"""

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types
from typing import Dict, Any


def create_query_classifier_agent(retry_config: types.HttpRetryOptions) -> LlmAgent:
    """
    Creates the Query Classification Agent.

    This agent analyzes queries and categorizes them into:
    - Factual: Simple fact-based questions
    - Comparative: Product/service comparisons
    - Exploratory: Deep research topics
    - Monitoring: Tracking topics over time

    Args:
        retry_config: HTTP retry configuration for the model

    Returns:
        LlmAgent configured for query classification
    """

    agent = LlmAgent(
        name="query_classifier",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        description="Intelligent query analyzer that determines research strategy",
        instruction="""
        You are the Query Classification Agent for ResearchMate AI.

        Your role is to analyze user queries and determine:
        1. Query Type: factual, comparative, exploratory, or monitoring
        2. Complexity Score: 1-10 (simple to complex)
        3. Research Strategy: quick-answer, multi-source, or deep-dive
        4. Key Topics: Main subjects to research
        5. User Intent: What the user is trying to accomplish

        Classification Guidelines:

        FACTUAL (Complexity 1-3):
        - Simple fact-based questions
        - Single correct answer
        - Example: "What is the capital of France?"
        - Strategy: quick-answer (single search)

        COMPARATIVE (Complexity 4-7):
        - Comparing products, services, or options
        - Decision-oriented research
        - Example: "Best wireless headphones under $200"
        - Strategy: multi-source (3-5 sources, structured comparison)

        EXPLORATORY (Complexity 6-10):
        - Learning new topics
        - Understanding complex concepts
        - Example: "Explain quantum computing for beginners"
        - Strategy: deep-dive (comprehensive multi-source analysis)

        MONITORING (Complexity varies):
        - Tracking topics over time
        - Staying updated on developments
        - Example: "Latest AI research developments"
        - Strategy: multi-source with recency prioritization

        Output Format (JSON):
        {
            "query_type": "factual|comparative|exploratory|monitoring",
            "complexity_score": 1-10,
            "research_strategy": "quick-answer|multi-source|deep-dive",
            "key_topics": ["topic1", "topic2"],
            "user_intent": "brief description",
            "estimated_sources": 1-10,
            "reasoning": "why you classified it this way"
        }

        Be concise and accurate in your classification.
        """,
        tools=[],  # Will add memory retrieval tool later
    )

    return agent


# Example usage function for testing
def classify_query_example():
    """Example of how to use the Query Classifier Agent"""

    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )

    classifier = create_query_classifier_agent(retry_config)

    # Example queries to test
    example_queries = [
        "What is the capital of Japan?",
        "Best wireless headphones under $200",
        "Explain quantum computing for beginners",
        "Latest developments in AI research",
    ]

    return classifier, example_queries


if __name__ == "__main__":
    # Test the agent creation
    classifier, queries = classify_query_example()
    print(f"✅ Query Classifier Agent created: {classifier.name}")
    print(f"📝 Example queries to test: {len(queries)}")
