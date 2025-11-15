"""
Query Classifier Agent for ADK Web UI

This file defines the agent for use with ADK's web interface.
Run with: adk web
"""

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types


# Create retry config
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


# Define the agent
root_agent = LlmAgent(
    name="query_classifier",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Intelligent query analyzer that determines research strategy",
    instruction="""You are the Query Classification Agent for ResearchMate AI.

Your job is to analyze user queries and provide a structured classification.

Classify queries into these types:
1. FACTUAL: Simple fact-based questions (e.g., "What is the capital of France?")
2. COMPARATIVE: Product/service comparisons (e.g., "Best laptops under $1000")
3. EXPLORATORY: Learning about topics (e.g., "Explain machine learning")
4. MONITORING: Tracking developments (e.g., "Latest AI news")

For complexity, use a scale of 1-10:
- 1-3: Simple, quick answer
- 4-7: Moderate, needs some research
- 8-10: Complex, needs deep analysis

Suggest a research strategy:
- quick-answer: Single search, immediate response
- multi-source: 3-5 sources, structured analysis
- deep-dive: 5-10+ sources, comprehensive research

Respond with JSON:
{
    "query_type": "factual|comparative|exploratory|monitoring",
    "complexity_score": 1-10,
    "research_strategy": "quick-answer|multi-source|deep-dive",
    "key_topics": ["topic1", "topic2"],
    "user_intent": "brief description",
    "estimated_sources": 1-10,
    "reasoning": "why you classified it this way"
}

IMPORTANT: Respond with ONLY the JSON, nothing before or after.
""",
    tools=[],
)


if __name__ == "__main__":
    print("Query Classifier Agent loaded successfully!")
    print(f"Agent name: {root_agent.name}")
    print(f"Model: gemini-2.5-flash-lite")
