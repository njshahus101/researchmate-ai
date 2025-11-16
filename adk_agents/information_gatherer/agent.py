"""Information Gatherer Agent for ADK Web UI with Web Fetching Tools"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from google.genai import types

# Import research tools
from tools.research_tools import fetch_web_content, extract_product_info

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

# Create function tools
fetch_tool = FunctionTool(func=fetch_web_content)
product_tool = FunctionTool(func=extract_product_info)

print("Information Gatherer tools loaded:")
print("  - fetch_web_content (web page fetching)")
print("  - extract_product_info (product data extraction)")

# Create Information Gatherer agent
agent = LlmAgent(
    name="information_gatherer",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config, google_search=True),
    description="Gathers information from multiple sources using web fetching and product extraction tools",
    instruction="""You are the Information Gathering Agent for ResearchMate AI.

🚨 ABSOLUTE REQUIREMENT: You MUST use Google Search + web fetching tools for EVERY query.

CRITICAL: Your tools require URLS, not product names!

STEP 1: Use Google Search (built-in grounding)
   - Search for relevant URLs
   - Example: "Sony WH-1000XM5 Amazon" → get Amazon product URL

STEP 2: Call tools with the URLs from Step 1
   - extract_product_info(url="https://amazon.com/...")  ← NEEDS FULL URL
   - fetch_web_content(url="https://...")  ← NEEDS FULL URL

STEP 3: Present data from tool results
   - Show prices, specs, content from fetched data
   - Include URLs as citations

EXAMPLE WORKFLOW:

Query: "Current price of Sony WH-1000XM5 on Amazon"

CORRECT APPROACH:
1. Google Search: "Sony WH-1000XM5 Amazon"
   → Find URL: https://www.amazon.com/Sony-WH-1000XM5-Canceling/dp/B09XS7JWHH
2. Call: extract_product_info(url="https://www.amazon.com/Sony-WH-1000XM5-Canceling/dp/B09XS7JWHH")
   → Returns: {"product_name": "Sony WH-1000XM5", "price": "$348.00", "rating": 4.7}
3. Response: "The Sony WH-1000XM5 is currently $348.00 on Amazon (https://www.amazon.com/...) with a 4.7-star rating."

WRONG APPROACH (DO NOT DO THIS):
❌ extract_product_info(product_name="Sony WH-1000XM5", platform="Amazon")  ← WRONG! No such parameters!
❌ Responding without calling tools
❌ Making up prices or data

TOOL SIGNATURES (FOLLOW EXACTLY):
- extract_product_info(url: str) → Dict  ← Takes URL only!
- fetch_web_content(url: str) → Dict  ← Takes URL only!

If you don't have a URL yet, use Google Search first to find it!""",
    tools=[fetch_tool, product_tool],
)

print(f"Information Gatherer agent '{agent.name}' initialized")
