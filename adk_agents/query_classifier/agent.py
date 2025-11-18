"""Query Classifier Agent for ADK Web UI"""

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

# Import observability
from utils.observability import get_logger, get_tracer, get_metrics

# Load environment variables
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize observability
logger = get_logger("query_classifier")
tracer = get_tracer()
metrics = get_metrics()

# Create retry config
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Create Query Classifier agent
agent = LlmAgent(
    name="query_classifier",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Analyzes user queries and determines research strategy",
    instruction="""You are the Query Classification Agent for ResearchMate AI.

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

After classification, ALWAYS delegate to the information_gatherer agent to execute the research.
Be concise and accurate in your classification.""",
    tools=[],
)

logger.info("Query Classifier agent initialized", agent_name=agent.name)
