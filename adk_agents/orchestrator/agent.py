"""
Research Orchestrator Agent - Simple Version for ADK UI
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

# Load environment variables
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Check for API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

print("Initializing orchestrator agent...")

# Create retry config
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Create agent
agent = LlmAgent(
    name="research_orchestrator",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Research pipeline orchestrator that explains Query Classifier and Information Gatherer workflow",
    instruction="""You are a helpful research assistant that explains how a multi-agent research pipeline works.

When users ask questions, explain how our two-stage pipeline would process their query:

Stage 1 - Query Classification:
- Determines query type (factual, comparative, exploratory, monitoring)
- Assigns complexity (1-10)
- Chooses strategy (quick-answer, multi-source, deep-dive)

Stage 2 - Information Gathering:
- Searches authoritative sources
- Fetches content
- Compiles results

Be friendly and educational. For the query 'Best wireless headphones under $200', you would explain:
- Type: Comparative
- Complexity: 5-6/10
- Strategy: Multi-source
- Would search tech review sites and compile comparison

Keep responses concise and helpful.""",
    tools=[],
)

print(f"Agent '{agent.name}' initialized successfully")
print("Ready for ADK Web UI")
