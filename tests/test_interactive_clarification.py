"""
Test interactive clarification feature in orchestrator
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
from adk_agents.orchestrator.agent import execute_fixed_pipeline, execute_with_clarification

async def test_interactive_mode():
    """Test orchestrator with interactive clarification"""

    print("="*80)
    print("TESTING INTERACTIVE CLARIFICATION FEATURE")
    print("="*80)

    query = "Find headphones"

    print(f"\nOriginal Query: {query}")
    print("\nThis query is vague. The orchestrator should ask for clarification.\n")
    print("="*80)
    print()

    # STEP 1: Execute in interactive mode (asks for clarification)
    result = await execute_fixed_pipeline(query, interactive=True)

    if result.get('status') == 'awaiting_clarification':
        print("\n" + "="*80)
        print("CLARIFICATION REQUESTED")
        print("="*80)
        print(result.get('clarification_prompt'))

        # Simulate user providing clarification
        print("\n" + "="*80)
        print("SIMULATING USER INPUT")
        print("="*80)
        user_clarification = "I want Sony WH-1000XM5 noise canceling headphones, current price from multiple US retailers, new only under $350"
        print(f"\nUser provides: {user_clarification}\n")

        # STEP 2: Continue with clarification
        print("="*80)
        print("CONTINUING WITH CLARIFIED QUERY")
        print("="*80)

        final_result = await execute_with_clarification(
            original_query=query,
            clarification=user_clarification
        )

        print("\n" + "="*80)
        print("FINAL RESULT WITH CLARIFICATION")
        print("="*80)
        print(f"Status: {final_result.get('status')}")
        if final_result.get('formatted_response'):
            print("\nFormatted Response:")
            print(final_result.get('formatted_response'))
        print()

    else:
        print("\n[ERROR] Expected awaiting_clarification status")
        print(f"Got: {result}")


async def test_non_interactive_mode():
    """Test that non-interactive mode skips clarification"""

    print("\n" + "="*80)
    print("TESTING NON-INTERACTIVE MODE (SKIP CLARIFICATION)")
    print("="*80)

    query = "Find the current price of Sony WH-1000XM5 headphones"

    print(f"\nQuery: {query}")
    print("Interactive mode: False (should proceed directly without asking)\n")
    print("="*80)
    print()

    # Execute in non-interactive mode (default)
    result = await execute_fixed_pipeline(query, interactive=False)

    print("\n" + "="*80)
    print("RESULT (NON-INTERACTIVE)")
    print("="*80)
    print(f"Status: {result.get('status')}")
    print("(Should show complete results, not awaiting_clarification)")
    print()


async def main():
    """Run both tests"""

    # Test 1: Interactive mode
    await test_interactive_mode()

    # Test 2: Non-interactive mode
    await test_non_interactive_mode()

    print("="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)
    print("\nSummary:")
    print("  1. Interactive mode (interactive=True) asks for clarification")
    print("  2. User can provide additional details or press Enter to continue")
    print("  3. Non-interactive mode (interactive=False) skips clarification")
    print("\nFor ADK UI integration:")
    print("  - Set interactive=True to enable clarification prompts")
    print("  - UI should display clarification_prompt to user")
    print("  - User input is passed to execute_with_clarification()")


if __name__ == "__main__":
    asyncio.run(main())
