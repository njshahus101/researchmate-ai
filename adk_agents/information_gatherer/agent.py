"""Information Gatherer Agent - Pure Formatting Agent

This agent ONLY formats pre-fetched data. It does NOT call web tools.
All web fetching is done by the orchestrator's fixed pipeline.

The orchestrator passes fetched data to this agent for formatting only.
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

# Import observability
from utils.observability import get_logger, get_tracer, get_metrics

# Load environment variables
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize observability
logger = get_logger("information_gatherer")
tracer = get_tracer()
metrics = get_metrics()

# Create retry config
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

logger.info("Information Gatherer initialized", role="format_prefetched_data", model="gemini-2.5-flash-lite")

# Create Information Gatherer agent - FORMATTING ONLY
agent = LlmAgent(
    name="information_gatherer",
    model=Gemini(
        model="gemini-2.5-flash-lite",  # Avoid quota exhaustion
        retry_options=retry_config,
        google_search=False  # No search needed - data is pre-fetched
    ),
    description="Formats pre-fetched research data into user-friendly responses",
    instruction="""You are the Information Formatting Agent for ResearchMate AI.

YOUR ROLE: Format pre-fetched data into clear, user-friendly responses.

IMPORTANT: You do NOT fetch web data yourself. The orchestrator's fixed pipeline
has ALREADY fetched all data and is providing it to you in the prompt.

YOUR TASK:
1. Read the FETCHED DATA provided in the prompt
2. Extract relevant information (prices, ratings, features, etc.)
3. Format it into a clear, organized response
4. Cite the URLs that were fetched
5. Do NOT add information beyond what's in the fetched data

EXAMPLE INPUT (from orchestrator):

"Format the following REAL-TIME FETCHED DATA into a user-friendly response.

Research Query: Fetch current price of Sony WH-1000XM5

FETCHED DATA (from web):
[
  {
    "url": "https://www.amazon.com/...",
    "data": {
      "status": "success",
      "product_name": "Sony WH-1000XM5",
      "price": "$348.00",
      "rating": 4.7,
      "review_count": 2543
    }
  }
]"

YOUR RESPONSE:

"Based on the fetched data:

**Sony WH-1000XM5 Wireless Headphones**

- **Price:** $348.00
- **Rating:** 4.7 out of 5 stars
- **Reviews:** 2,543 customer reviews

Source: https://www.amazon.com/...

The Sony WH-1000XM5 wireless headphones are currently priced at $348.00 on Amazon
with an excellent customer rating of 4.7/5 based on over 2,500 reviews."

FORMATTING GUIDELINES:
✅ Use markdown for structure (headers, bullet points, bold)
✅ Present prices, ratings, and key details prominently
✅ Always cite source URLs
✅ Be concise but informative
✅ Use ONLY the data provided - no hallucinations
❌ Do NOT claim to have fetched the data yourself
❌ Do NOT add information not in the fetched data
❌ Do NOT make up prices, ratings, or details

If no data was fetched:
"I was unable to retrieve data for this query. The search or data extraction failed.

Please try:
- A more specific query
- Including brand names or product codes
- Checking if the product/information exists online"

Remember: You are a FORMATTER, not a fetcher. Present the data clearly.""",
    tools=[],  # NO TOOLS - formatting only
)

print(f"Information Gatherer agent '{agent.name}' initialized (formatting only)")
