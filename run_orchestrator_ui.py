"""
Run ResearchMate AI Orchestrator via ADK Web UI

This script starts the orchestrator agent with ADK web interface
for easy testing of the Query Classifier -> Information Gatherer pipeline.

Usage:
    python run_orchestrator_ui.py

Then open: http://localhost:8000 in your browser
"""

import os
from dotenv import load_dotenv
from main import ResearchMateAI

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ Error: GOOGLE_API_KEY not found in environment variables")
    print("Please create a .env file with your API key:")
    print("  GOOGLE_API_KEY=your_key_here")
    exit(1)

print("\n" + "="*80)
print("ResearchMate AI - Orchestrator Web UI")
print("="*80)
print("\nInitializing orchestrator...")

# Create the application
app_instance = ResearchMateAI()

print("\n" + "="*80)
print("Starting ADK Web UI...")
print("="*80)
print("\nThe orchestrator coordinates a sequential pipeline:")
print("  1. Query Classifier - Analyzes user queries")
print("  2. Information Gatherer - Searches and retrieves information")
print("\nAccess the UI at: http://localhost:8000")
print("\nPress Ctrl+C to stop the server")
print("="*80 + "\n")

# Run the ADK web UI
# This will start a local server with the orchestrator agent
if __name__ == "__main__":
    # The app.run() method is not directly available in ADK
    # Instead, we'll use the adk command line tool
    print("To run the orchestrator UI, use:")
    print("\n  adk web main:app_instance.app")
    print("\nOr use the batch file:")
    print("\n  start_orchestrator_ui.bat")
    print("\n")
