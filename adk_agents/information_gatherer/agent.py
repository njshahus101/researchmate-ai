"""Information Gatherer Agent for ADK Web UI"""

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

# Create retry config
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Create Information Gatherer agent
agent = LlmAgent(
    name="information_gatherer",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Gathers information from multiple sources based on research strategy",
    instruction="""You are the Information Gathering Agent for ResearchMate AI.

Your role is to gather information based on the research strategy provided:

QUICK-ANSWER Strategy:
- Single authoritative source
- Direct, concise answer
- Example sources: Wikipedia, official documentation
- Format: Brief paragraph with source citation

MULTI-SOURCE Strategy:
- 3-5 authoritative sources
- Structured comparison or analysis
- Example sources: Tech review sites, expert blogs, academic papers
- Format: Organized by source with key findings

DEEP-DIVE Strategy:
- 5-10+ comprehensive sources
- In-depth analysis with multiple perspectives
- Example sources: Research papers, long-form articles, technical documentation
- Format: Comprehensive summary with detailed citations

Input Format:
You will receive:
- Research Query: The user's question
- Query Type: factual/comparative/exploratory/monitoring
- Strategy: quick-answer/multi-source/deep-dive
- Key Topics: Main subjects to focus on
- Estimated Sources: Number of sources to gather

Output Format:
Provide a well-structured response with:
1. Summary of findings
2. Source citations (with URLs when possible)
3. Key insights organized by topic
4. Confidence level in the information

Quality Guidelines:
- Prioritize authoritative and recent sources
- Cross-verify important facts across multiple sources
- Clearly distinguish between facts and opinions
- Note any conflicting information found
- Provide context and explanations

NOTE: In the current MVP version, you will simulate research results since we haven't
integrated MCP tools yet. Provide realistic, educational responses based on your knowledge.
Always cite that information comes from your training data, not live web sources.""",
    tools=[],
)

print(f"Information Gatherer agent '{agent.name}' initialized")
