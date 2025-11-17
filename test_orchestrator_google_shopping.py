"""
Test the orchestrator with Google Shopping API integration
"""

import sys
from pathlib import Path
import asyncio
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Import orchestrator
from adk_agents.orchestrator.agent import execute_fixed_pipeline

async def test_price_query():
    """Test a product price query that should use Google Shopping API"""

    print("="*80)
    print("TESTING ORCHESTRATOR WITH GOOGLE SHOPPING API")
    print("="*80)

    query = "Find the current price of Sony WH-1000XM5 headphones from multiple retailers"

    print(f"\nQuery: {query}\n")
    print("Expected Behavior:")
    print("  [STEP 2/4] Detected price query - using Google Shopping API...")
    print("  [STEP 2/4] OK Google Shopping API returned 5 results")
    print("  [STEP 3/4] Adding 5 Google Shopping results...")
    print()
    print("="*80)
    print()

    # Run the research pipeline
    result = await execute_fixed_pipeline(query)

    print()
    print("="*80)
    print("RESULT:")
    print("="*80)
    print(result)
    print()

if __name__ == "__main__":
    asyncio.run(test_price_query())
