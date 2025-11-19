"""
Configuration and environment setup for the Orchestrator Agent.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.genai import types

# Determine project root
project_root = Path(__file__).parent.parent.parent

# Load environment variables
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Check for API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# Create retry config for Gemini API calls
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Session storage configuration
orchestrator_sessions_dir = str(project_root / "orchestrator_sessions")
