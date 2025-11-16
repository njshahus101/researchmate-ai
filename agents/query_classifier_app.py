"""
Query Classifier Agent - ADK Web UI Application

This script sets up the Query Classifier Agent to run in the ADK Web UI.
You can interact with the agent through a chat interface and optionally
enable Memory Service integration.

Usage:
    adk web agents/query_classifier_app.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.memory_service import MemoryService


# Load environment variables
load_dotenv()

# Configuration
ENABLE_MEMORY = True  # Set to False to disable memory integration
MEMORY_STORAGE_PATH = "query_classifier_memory.json"
DEFAULT_USER_ID = "adk_web_user"

# Create retry config
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Initialize Memory Service if enabled
memory_service = None
if ENABLE_MEMORY:
    memory_service = MemoryService(storage_path=MEMORY_STORAGE_PATH)
    print(f"[+] Memory Service enabled (storage: {MEMORY_STORAGE_PATH})")
else:
    print("[!] Memory Service disabled")


def create_query_classifier_agent() -> LlmAgent:
    """
    Creates the Query Classification Agent for ADK Web UI.

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
    if ENABLE_MEMORY:
        instruction += """

USER CONTEXT AWARENESS:
You have access to user preferences, research history, and domain knowledge from previous interactions.
Consider this context when classifying queries to provide personalized recommendations.

For example:
- If user has researched similar topics before, acknowledge their existing knowledge
- If user has domain expertise, adjust complexity assessment accordingly
- If user has specific preferences, factor them into the research strategy

The user's research history will be automatically provided with each query.
"""

    instruction += """

RESPONSE FORMAT:
Provide a friendly response that includes:
1. A brief greeting/acknowledgment
2. Your classification results in a clear, readable format
3. An explanation of why you classified it this way
4. Suggestions for how to proceed with the research

Use this JSON structure in your response (but make it conversational):
- Query Type: factual|comparative|exploratory|monitoring
- Complexity Score: 1-10
- Research Strategy: quick-answer|multi-source|deep-dive
- Key Topics: [list of topics]
- User Intent: brief description
- Estimated Sources: 1-10
- Reasoning: why you classified it this way

Keep your tone helpful, professional, and friendly.
"""

    agent = LlmAgent(
        name="query_classifier",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        description="Intelligent query analyzer that determines research strategy with user context awareness",
        instruction=instruction,
        tools=[],
    )

    return agent


# Create the agent
root_agent = create_query_classifier_agent()


# Session setup with memory integration
def on_session_start(session_id: str):
    """Called when a new session starts."""
    print(f"[+] New session started: {session_id}")

    if ENABLE_MEMORY:
        # Initialize user in memory if needed
        user_memory = memory_service.get_user_memory(DEFAULT_USER_ID)
        print(f"[+] User memory loaded for: {DEFAULT_USER_ID}")

        # Show some stats
        history = memory_service.get_recent_research(DEFAULT_USER_ID, limit=5)
        print(f"[+] Research history entries: {len(history)}")


def process_message_with_context(message: str) -> str:
    """
    Process user message and add memory context.

    Args:
        message: User's input message

    Returns:
        Message with user context appended
    """
    if not ENABLE_MEMORY:
        return message

    # Get user context
    user_memory = memory_service.get_user_memory(DEFAULT_USER_ID)
    recent_research = memory_service.get_recent_research(DEFAULT_USER_ID, limit=3)

    # Build context string
    context_parts = []

    if user_memory.get("preferences"):
        prefs = user_memory["preferences"]
        if prefs:
            context_parts.append(f"User Preferences: {list(prefs.keys())}")

    if recent_research:
        recent_queries = [entry['query'] for entry in recent_research]
        context_parts.append(f"Recent Queries: {recent_queries}")

    if user_memory.get("domain_knowledge"):
        domains = user_memory["domain_knowledge"]
        if domains:
            expertise = [f"{domain}={info['expertise_level']}" for domain, info in domains.items()]
            context_parts.append(f"Expertise: {', '.join(expertise)}")

    if context_parts:
        context_str = "\n\n[User Context from Memory]\n" + "\n".join(context_parts)
        return message + context_str

    return message


def store_classification_result(query: str, response: str):
    """
    Store the classification result in memory.

    Args:
        query: Original user query
        response: Agent's response
    """
    if not ENABLE_MEMORY:
        return

    # Try to extract classification from response
    # This is a simple heuristic - you might want to improve this
    query_type = "unknown"
    topics = []

    # Simple extraction
    if "factual" in response.lower():
        query_type = "factual"
    elif "comparative" in response.lower():
        query_type = "comparative"
    elif "exploratory" in response.lower():
        query_type = "exploratory"
    elif "monitoring" in response.lower():
        query_type = "monitoring"

    # Extract topics (simple approach - split query into words)
    topics = [word.strip() for word in query.lower().split() if len(word) > 4][:5]

    # Store in memory
    memory_service.add_research_entry(
        DEFAULT_USER_ID,
        query,
        query_type,
        topics
    )

    print(f"[+] Stored classification: {query_type} with topics: {topics}")


# Example usage instructions
if __name__ == "__main__":
    print("\n" + "="*60)
    print("QUERY CLASSIFIER AGENT - ADK WEB UI")
    print("="*60)
    print("\nTo start the agent in ADK Web UI, run:")
    print("\n  adk web agents/query_classifier_app.py")
    print("\nThen open the URL shown in your browser.")
    print("\nMemory Service:", "ENABLED" if ENABLE_MEMORY else "DISABLED")
    print(f"Storage Path: {MEMORY_STORAGE_PATH if ENABLE_MEMORY else 'N/A'}")
    print("\nTry asking queries like:")
    print("  - What is the capital of France?")
    print("  - Best wireless headphones under $200")
    print("  - Explain quantum computing for beginners")
    print("  - Latest developments in AI")
    print("\n" + "="*60 + "\n")
