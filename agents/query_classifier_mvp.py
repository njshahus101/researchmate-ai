"""
Query Classification Agent - MVP Implementation

This is a minimal viable product version that actually works with the LLM.
Includes integration with Memory Service for user context.
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.memory_service import MemoryService


def create_memory_retrieval_tool(memory_service: MemoryService, user_id: str):
    """
    Creates a memory retrieval tool for the agent.

    Args:
        memory_service: Memory service instance
        user_id: User identifier

    Returns:
        Tool function that can be called by the agent
    """
    def get_user_context(query_topics: list = None) -> dict:
        """
        Retrieves user context from memory.

        Args:
            query_topics: Optional list of topics to find related context

        Returns:
            User context including preferences, history, and domain knowledge
        """
        user_memory = memory_service.get_user_memory(user_id)

        context = {
            "preferences": user_memory.get("preferences", {}),
            "recent_research": memory_service.get_recent_research(user_id, limit=5),
            "domain_knowledge": user_memory.get("domain_knowledge", {})
        }

        # Add related topics if query topics are provided
        if query_topics:
            related_topics = []
            for topic in query_topics:
                related = memory_service.get_related_topics(user_id, topic)
                related_topics.extend(related)
            context["related_topics"] = list(set(related_topics))

        return context

    return get_user_context


def create_query_classifier_mvp(retry_config: types.HttpRetryOptions, memory_service: MemoryService = None, user_id: str = "default_user") -> LlmAgent:
    """
    Creates a working MVP Query Classification Agent with Memory Service integration.

    This agent:
    - Analyzes user queries
    - Determines query type (factual, comparative, exploratory, monitoring)
    - Suggests research strategy
    - Extracts key topics
    - Retrieves user context from memory for personalized classification

    Args:
        retry_config: HTTP retry configuration
        memory_service: Optional Memory Service instance for user context
        user_id: User identifier for memory retrieval

    Returns:
        Configured LlmAgent
    """

    # Build instruction with memory context awareness
    instruction = """You are the Query Classification Agent for ResearchMate AI.

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
"""

    # Add memory context instructions if memory service is available
    if memory_service:
        instruction += """

USER CONTEXT AWARENESS:
You have access to user preferences, research history, and domain knowledge.
Consider this context when classifying queries to provide personalized recommendations.

For example:
- If user has researched similar topics before, acknowledge their existing knowledge
- If user has domain expertise, adjust complexity assessment accordingly
- If user has specific preferences, factor them into the research strategy
"""

    instruction += """

IMPORTANT: Always respond with valid JSON in this exact format:
{
    "query_type": "factual|comparative|exploratory|monitoring",
    "complexity_score": 1-10,
    "research_strategy": "quick-answer|multi-source|deep-dive",
    "key_topics": ["topic1", "topic2"],
    "user_intent": "brief description",
    "estimated_sources": 1-10,
    "reasoning": "why you classified it this way"
}

Only output valid JSON, no additional text before or after.
"""

    agent = LlmAgent(
        name="query_classifier_mvp",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        description="Intelligent query analyzer that determines research strategy with user context awareness",
        instruction=instruction,
        tools=[],  # Tools will be added in future versions
    )

    return agent


async def classify_query(query: str, user_id: str = "default_user", memory_service: MemoryService = None) -> dict:
    """
    Classify a single query using the MVP agent with user context.

    Args:
        query: User's research query
        user_id: User identifier for memory retrieval
        memory_service: Optional Memory Service instance

    Returns:
        Classification results as dictionary
    """
    # Load environment
    load_dotenv()

    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        return {
            "error": "GOOGLE_API_KEY not found in environment",
            "message": "Please add your API key to the .env file"
        }

    # Create retry config
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )

    # Create agent with memory service
    agent = create_query_classifier_mvp(retry_config, memory_service, user_id)

    # Create runner
    runner = InMemoryRunner(agent=agent)

    # Get user context if memory service is available
    user_context_str = ""
    if memory_service:
        user_memory = memory_service.get_user_memory(user_id)
        recent_research = memory_service.get_recent_research(user_id, limit=3)

        user_context_str = "\n\nUser Context:"
        if user_memory.get("preferences"):
            user_context_str += f"\nPreferences: {json.dumps(user_memory['preferences'], indent=2)}"
        if recent_research:
            user_context_str += f"\nRecent Research: {json.dumps(recent_research, indent=2)}"
        if user_memory.get("domain_knowledge"):
            user_context_str += f"\nDomain Knowledge: {json.dumps(user_memory['domain_knowledge'], indent=2)}"

    try:
        # Run the query
        print(f"\n{'='*60}")
        print(f"Classifying Query: {query}")
        if user_context_str:
            print(f"User ID: {user_id}")
        print(f"{'='*60}\n")

        # Combine query with user context
        query_with_context = query + user_context_str if user_context_str else query

        response = await runner.run_debug(query_with_context)

        # run_debug returns a list of Event objects
        # Get the last event which contains the agent's response
        if isinstance(response, list) and len(response) > 0:
            last_event = response[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                response_text = last_event.content.parts[0].text
            else:
                response_text = str(last_event)
        else:
            response_text = str(response)

        print(f"Raw Response:\n{response_text}\n")

        # Try to parse as JSON
        try:
            # Clean the response - remove markdown code blocks if present
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]  # Remove ```json
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]  # Remove ```
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]  # Remove ```
            cleaned_text = cleaned_text.strip()

            classification = json.loads(cleaned_text)

            print(f"{'='*60}")
            print(f"Classification Results:")
            print(f"{'='*60}")
            print(f"Query Type: {classification.get('query_type', 'N/A')}")
            print(f"Complexity: {classification.get('complexity_score', 'N/A')}/10")
            print(f"Strategy: {classification.get('research_strategy', 'N/A')}")
            print(f"Topics: {', '.join(classification.get('key_topics', []))}")
            print(f"Intent: {classification.get('user_intent', 'N/A')}")
            print(f"Sources Needed: {classification.get('estimated_sources', 'N/A')}")
            print(f"\nReasoning: {classification.get('reasoning', 'N/A')}")
            print(f"{'='*60}\n")

            # Store in memory if memory service is available
            if memory_service:
                memory_service.add_research_entry(
                    user_id,
                    query,
                    classification.get('query_type', 'unknown'),
                    classification.get('key_topics', [])
                )
                print(f"[+] Stored classification in memory for user: {user_id}\n")

            return classification

        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse JSON response: {e}")
            # Return a structured response anyway
            return {
                "query_type": "unknown",
                "raw_response": response_text,
                "error": "Could not parse JSON",
                "message": "Agent responded but not in JSON format"
            }

    except Exception as e:
        print(f"Error during classification: {e}")
        return {
            "error": str(e),
            "message": "Classification failed"
        }


async def test_classifier():
    """Test the classifier with various query types."""

    test_queries = [
        # Factual
        "What is the capital of Japan?",

        # Comparative
        "Best wireless headphones under $200",

        # Exploratory
        "Explain quantum computing for beginners",

        # Monitoring
        "Latest developments in AI agents",
    ]

    print("\n" + "="*60)
    print("TESTING QUERY CLASSIFIER MVP")
    print("="*60)

    results = []

    for query in test_queries:
        result = await classify_query(query)
        results.append({
            "query": query,
            "classification": result
        })

        # Small delay between requests
        import asyncio
        await asyncio.sleep(1)

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['query']}")
        if 'error' not in result['classification']:
            print(f"   Type: {result['classification'].get('query_type', 'N/A')}")
            print(f"   Strategy: {result['classification'].get('research_strategy', 'N/A')}")
        else:
            print(f"   Error: {result['classification'].get('error', 'Unknown error')}")

    print("\n" + "="*60)
    print("✅ Testing Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    import asyncio

    # Run the test
    asyncio.run(test_classifier())
