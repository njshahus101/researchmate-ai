"""
Orchestrator App for ADK Web UI

This file creates the app instance that ADK web can import.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ Error: GOOGLE_API_KEY not found in environment variables")
    print("Please add GOOGLE_API_KEY to .env file")
    exit(1)

# Import and create the app instance
from main import ResearchMateAI

# Create the application instance
print("Initializing ResearchMate AI Orchestrator...")
app_instance = ResearchMateAI()

# Export the app for ADK web
app = app_instance.app

print("✅ Orchestrator app ready for ADK Web UI")
print("   Access at: http://localhost:8000")
