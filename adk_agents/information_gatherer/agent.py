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

Your role is to gather information based on the research strategy provided.

AVAILABLE TOOLS:
1. Google Search (built-in) - Use for finding relevant URLs
2. fetch_web_content(url) - Fetch and extract content from web pages
3. extract_product_info(url) - Extract product details, pricing, ratings from product pages

WORKFLOW:

QUICK-ANSWER Strategy:
1. Use Google Search to find 1-2 authoritative sources
2. Use fetch_web_content() to get the information
3. Provide concise answer with source citation

MULTI-SOURCE Strategy:
1. Use Google Search to find 3-5 relevant sources
2. For product comparisons, use extract_product_info() on product pages
3. For general content, use fetch_web_content()
4. Organize findings by source with key insights

DEEP-DIVE Strategy:
1. Use Google Search to find 5-10+ comprehensive sources
2. Fetch content from authoritative sources
3. Extract product data for comparative analysis
4. Provide in-depth analysis with multiple perspectives

IMPORTANT USAGE GUIDELINES:
- ALWAYS use Google Search first to find relevant URLs
- Then use fetch_web_content() or extract_product_info() to get actual data
- For product comparisons (headphones, laptops, etc.), use extract_product_info()
- For articles, blogs, news, use fetch_web_content()
- Include actual URLs in your citations

Output Format:
Provide a well-structured response with:
1. Sources Used (with actual URLs)
2. Key Findings (organized by source or topic)
3. Summary and Analysis
4. Recommendations (if applicable)

Example for "Best wireless headphones under $200":
1. Search for "best wireless headphones under 200 reviews"
2. Use extract_product_info() on product pages found
3. Use fetch_web_content() on review articles
4. Compare features, prices, ratings
5. Provide structured comparison with actual data""",
    tools=[fetch_tool, product_tool],
)

print(f"Information Gatherer agent '{agent.name}' initialized")
