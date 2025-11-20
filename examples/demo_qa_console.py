"""
Quick QA Demo for Recording
Shows pipeline with QA validation in clean console output
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Mock tools to avoid real API calls
from test_end_to_end_qa import MockResearchTools
import tools.research_tools as research_tools

research_tools.search_web = MockResearchTools.search_web
research_tools.fetch_web_content = MockResearchTools.fetch_web_content
research_tools.extract_product_info = MockResearchTools.extract_product_info
research_tools.search_google_shopping = MockResearchTools.search_google_shopping

from adk_agents.orchestrator.agent import execute_fixed_pipeline


async def demo():
    print("\n" + "="*70)
    print("QUALITY ASSURANCE DEMO - ResearchMate AI")
    print("="*70)

    query = "Compare prices for Sony WH-1000XM5 headphones"
    print(f"\nQuery: {query}")
    print("\nExecuting research pipeline with QA validation...")
    print("="*70 + "\n")

    # Run pipeline
    result = await execute_fixed_pipeline(
        query=query,
        user_id="demo_user",
        interactive=False
    )

    # Show QA Results
    print("\n" + "="*70)
    print("QUALITY ASSURANCE VALIDATION RESULTS")
    print("="*70)

    quality_report = result.get("quality_report")

    if quality_report:
        print(f"\nOVERALL QUALITY SCORE: {quality_report['overall_score']}/100")
        print(f"GRADE: {quality_report['grade']}")

        summary = quality_report['summary']
        print(f"\nVALIDATION CHECKS:")
        print(f"  Total Checks: {summary['total_checks']}")
        print(f"  Passed: {summary['passed']}")
        print(f"  Warnings: {summary['warnings']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Pass Rate: {summary['pass_rate']:.1f}%")

        print(f"\nRECOMMENDATIONS:")
        for i, rec in enumerate(quality_report['recommendations'][:3], 1):
            print(f"  {i}. {rec}")

        print(f"\nVALIDATION BY CATEGORY:")
        for category, counts in summary['by_category'].items():
            print(f"  {category}:")
            print(f"    Passed: {counts['pass']}, Warnings: {counts['warning']}, Failed: {counts['fail']}")

    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nQuality Assurance system is fully operational!")
    print("Every research output is automatically validated.\n")


if __name__ == "__main__":
    # Suppress most logs for clean demo
    import os
    os.environ['PYTHONWARNINGS'] = 'ignore'

    asyncio.run(demo())
