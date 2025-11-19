"""
Test script to verify the web UI fix

This script tests if the execute_fixed_pipeline function properly
handles exceptions and returns error responses.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from adk_agents.orchestrator.agent import execute_fixed_pipeline


async def test_pipeline():
    """Test the pipeline with a simple query"""
    print("="*60)
    print("Testing execute_fixed_pipeline...")
    print("="*60)
    
    try:
        result = await execute_fixed_pipeline(
            query="What is the price of Sony WH-1000XM5 headphones?",
            user_id="test_user_cli",
            session_id=None
        )
        
        print("\n" + "="*60)
        print("RESULT:")
        print("="*60)
        print(f"Status: {result.get('status')}")
        print(f"Session ID: {result.get('session_id')}")
        
        if result.get('status') == 'success':
            print(f"Content length: {len(result.get('content', ''))} characters")
            print(f"Sources fetched: {result.get('sources_fetched')}")
            print("\nFirst 500 chars of content:")
            print(result.get('content', '')[:500])
        else:
            print(f"Error: {result.get('error')}")
            
        print("\n" + "="*60)
        print("TEST COMPLETED SUCCESSFULLY")
        print("="*60)
        
        return result
        
    except Exception as e:
        print("\n" + "="*60)
        print("TEST FAILED WITH EXCEPTION")
        print("="*60)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        import traceback
        traceback.print_exc()
        print("="*60)
        return None


if __name__ == "__main__":
    print("\nStarting Web UI Fix Test...")
    print("This will test if exceptions are properly caught and handled.\n")
    
    result = asyncio.run(test_pipeline())
    
    if result:
        print("\n✅ Test passed - Pipeline returned a result")
        if result.get('status') == 'success':
            print("✅ Pipeline completed successfully")
        else:
            print("⚠️  Pipeline returned an error (but didn't crash)")
    else:
        print("\n❌ Test failed - Pipeline raised an unhandled exception")
