"""
Simple test to verify Report Generator is called by orchestrator
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner

load_dotenv()

from adk_agents.orchestrator.agent import agent as orchestrator_agent

async def test_simple():
    print("\n" + "="*80)
    print("SIMPLE REPORT GENERATOR TEST")
    print("="*80)

    query = "What is the current price of Sony WH-1000XM5 headphones?"
    print(f"\nQuery: {query}")
    print("\nExecuting pipeline...\n")

    runner = InMemoryRunner(agent=orchestrator_agent)

    try:
        response = await runner.run_debug(query)

        # Extract response
        if isinstance(response, list) and len(response) > 0:
            last_event = response[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                final_output = last_event.content.parts[0].text
            else:
                final_output = str(last_event)
        else:
            final_output = str(response)

        print("\n" + "="*80)
        print("FINAL OUTPUT:")
        print("="*80)
        print(final_output[:2000])  # First 2000 chars
        if len(final_output) > 2000:
            print(f"\n... (truncated, total length: {len(final_output)} chars)")
        print("="*80)

        # Check if output looks like Report Generator output
        is_report_format = any(marker in final_output for marker in [
            "##", "###", "**", "Sources", "source", "[1]", "Follow-up", "Evidence"
        ])

        has_price = "$" in final_output
        has_product = "Sony" in final_output or "WH-1000XM5" in final_output

        print("\nCHECKS:")
        print(f"  Report format (markdown): {'PASS' if is_report_format else 'FAIL'}")
        print(f"  Contains price: {'PASS' if has_price else 'FAIL'}")
        print(f"  Contains product: {'PASS' if has_product else 'FAIL'}")

        if is_report_format and has_price and has_product:
            print("\n✓ SUCCESS: Report Generator is working!")
            return True
        else:
            print("\nX FAILURE: Output doesn't match expected format")
            return False

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_simple())
    sys.exit(0 if success else 1)
