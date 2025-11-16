"""
Research Orchestrator Agent - Full A2A Integration for ADK UI

This agent coordinates the research pipeline using Agent-to-Agent (A2A) protocol:
1. Calls Query Classifier agent to analyze the query
2. Calls Information Gatherer agent based on classification
3. Synthesizes and presents results
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.genai import types

# Load environment variables
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Check for API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

print("Initializing orchestrator agent with A2A integration...")

# Create retry config
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Load sub-agents
print("  Loading Query Classifier agent...")
sys.path.insert(0, str(Path(__file__).parent.parent / 'query_classifier'))
from adk_agents.query_classifier.agent import agent as classifier_agent

print("  Loading Information Gatherer agent...")
sys.path.insert(0, str(Path(__file__).parent.parent / 'information_gatherer'))
from adk_agents.information_gatherer.agent import agent as gatherer_agent

# Initialize memory service (simplified version for ADK UI)
class SimpleMemoryService:
    """Simplified memory service for ADK UI context"""
    def __init__(self):
        self.user_memories = {}
        self.research_history = {}

    def get_user_memory(self, user_id: str) -> dict:
        return self.user_memories.get(user_id, {})

    def get_recent_research(self, user_id: str, limit: int = 3) -> list:
        history = self.research_history.get(user_id, [])
        return history[-limit:] if history else []

    def add_research_entry(self, user_id: str, query: str, query_type: str, topics: list):
        if user_id not in self.research_history:
            self.research_history[user_id] = []
        self.research_history[user_id].append({
            "query": query,
            "query_type": query_type,
            "topics": topics
        })

memory_service = SimpleMemoryService()

# Create A2A tool functions
async def classify_user_query(query: str, user_id: str = "default") -> dict:
    """
    Classify a user query to determine research strategy.

    This function calls the Query Classifier agent using A2A protocol.

    Args:
        query: The user's research query
        user_id: User identifier for personalization

    Returns:
        Dictionary with classification results including query_type,
        research_strategy, complexity_score, and key_topics
    """
    print(f"\n[A2A] Calling Query Classifier for: {query[:50]}...")

    # Get user context from memory
    user_memory = memory_service.get_user_memory(user_id)
    recent_research = memory_service.get_recent_research(user_id, limit=3)

    # Build context string
    context = f"\n\nUser ID: {user_id}"
    if user_memory.get("preferences"):
        context += f"\nUser Preferences: {json.dumps(user_memory['preferences'])}"
    if recent_research:
        context += f"\nRecent Research: {json.dumps(recent_research)}"

    # Call classifier agent via runner (A2A)
    runner = InMemoryRunner(agent=classifier_agent)
    try:
        response = await runner.run_debug(query + context)

        # Extract response
        if isinstance(response, list) and len(response) > 0:
            last_event = response[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                response_text = last_event.content.parts[0].text
            else:
                response_text = str(last_event)
        else:
            response_text = str(response)

        # Parse JSON response
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()

        classification = json.loads(cleaned_text)

        # Store in memory
        memory_service.add_research_entry(
            user_id,
            query,
            classification.get('query_type', 'unknown'),
            classification.get('key_topics', [])
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

async def gather_information(query: str, classification: dict) -> dict:
    """
    Gather information from multiple sources based on research strategy.

    This function calls the Information Gatherer agent using A2A protocol.

    Args:
        query: The user's research query
        classification: Classification results from Query Classifier

    Returns:
        Dictionary with gathered information including sources and content
    """
    print(f"\n[A2A] Calling Information Gatherer with strategy: {classification.get('research_strategy')}...")

    # Build context for information gatherer
    gatherer_prompt = f"""Research Query: {query}

Query Classification:
- Type: {classification.get('query_type', 'unknown')}
- Strategy: {classification.get('research_strategy', 'quick-answer')}
- Key Topics: {', '.join(classification.get('key_topics', []))}
- Estimated Sources: {classification.get('estimated_sources', 3)}

Please gather information according to the {classification.get('research_strategy', 'quick-answer')} strategy.
Provide sources with URLs, titles, and key findings."""

    # Call gatherer agent via runner (A2A)
    runner = InMemoryRunner(agent=gatherer_agent)
    try:
        response = await runner.run_debug(gatherer_prompt)

        # Extract response
        if isinstance(response, list) and len(response) > 0:
            last_event = response[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                response_text = last_event.content.parts[0].text
            else:
                response_text = str(last_event)
        else:
            response_text = str(response)

        print(f"[A2A] Information gathering complete")
        return {
            "status": "success",
            "content": response_text,
            "strategy": classification.get('research_strategy')
        }

    except Exception as e:
        print(f"[A2A ERROR] Information gathering failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

# Create function tools from async functions
classify_tool = FunctionTool(func=classify_user_query)
gather_tool = FunctionTool(func=gather_information)

# Create orchestrator agent with A2A tools
instruction = """You are the Orchestrator Agent for ResearchMate AI.

Your role is to coordinate the research pipeline using specialized agents via A2A protocol:
1. Query Classifier Agent - analyzes queries and determines strategy
2. Information Gatherer Agent - searches and retrieves information

WORKFLOW:
When a user asks a research question:

1. Call classify_user_query with the query to get classification
2. Based on the research_strategy:
   - If "quick-answer": Call gather_information for concise response
   - If "multi-source": Call gather_information for structured analysis
   - If "deep-dive": Call gather_information for comprehensive research
3. Synthesize results and provide a comprehensive response

OUTPUT FORMAT:
Provide clear, structured responses:
- Query Analysis (type, complexity, strategy)
- Key Topics Identified
- Research Results (organized by topic/source)
- Summary of Findings
- Additional Recommendations (if applicable)

Be conversational, helpful, and thorough. Always explain what you're doing and show
the classification results before presenting the gathered information.

Example:
User: "Best wireless headphones under $200"

Your response should:
1. Call classify_user_query
2. Explain: "I've classified this as a COMPARATIVE query (complexity 6/10) requiring MULTI-SOURCE research"
3. Call gather_information
4. Present organized findings from multiple sources
5. Provide summary and recommendations"""

agent = LlmAgent(
    name="research_orchestrator",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Research pipeline orchestrator that coordinates query classification and information gathering via A2A",
    instruction=instruction,
    tools=[classify_tool, gather_tool],
)

print(f"Agent '{agent.name}' initialized successfully with A2A integration")
print("  - Query Classifier agent loaded")
print("  - Information Gatherer agent loaded")
print("  - A2A tools configured")
print("Ready for ADK Web UI")
