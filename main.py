"""
ResearchMate AI - Main Launcher

Launches the ResearchMate AI Web UI with the modular orchestrator.
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the ResearchMate AI Web UI"""

    # Check for API key
    from dotenv import load_dotenv
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        print("Please create a .env file with your API key:")
        print("  GOOGLE_API_KEY=your_key_here")
        sys.exit(1)

    print("\n" + "="*80)
    print("ResearchMate AI - Launching Web UI")
    print("="*80)
    print("\nArchitecture:")
    print("  • 4 A2A Agents: Query Classifier, Information Gatherer, Content Analyzer, Report Generator")
    print("  • 7-Step Pipeline: Classification → Search → Fetch → Format → Analyze → Report → QA")
    print("  • Modular Design with Observability & Quality Assurance")
    print("\nStarting server...")
    print("="*80 + "\n")

    # Launch web UI using uvicorn
    try:
        import uvicorn

        # Run the FastAPI app from web_ui/app.py
        uvicorn.run(
            "web_ui.app:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )

    except ImportError:
        print("❌ Error: uvicorn not installed")
        print("\nInstall dependencies:")
        print("  pip install uvicorn fastapi")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down ResearchMate AI...")
        print("="*80 + "\n")


if __name__ == "__main__":
    main()
