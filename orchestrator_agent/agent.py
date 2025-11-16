"""
Orchestrator Agent for ADK Web UI

This module exports the orchestrator agent for the ADK web interface.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from main import ResearchMateAI

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Create the application instance
print("Initializing ResearchMate AI Orchestrator for ADK Web UI...")
app_instance = ResearchMateAI()

# Export the orchestrator agent for ADK
agent = app_instance.orchestrator

print(f"✅ Orchestrator agent ready: {agent.name}")
