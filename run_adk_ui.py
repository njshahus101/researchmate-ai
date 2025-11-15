"""
Launch ADK Web UI for Query Classifier

This script starts the ADK web interface for interactive testing.

Usage:
    python run_adk_ui.py

Then open: http://localhost:8000 in your browser
"""

import subprocess
import os
import sys


def main():
    """Launch ADK web UI."""

    print("\n" + "="*60)
    print("Starting ADK Web UI for Query Classifier")
    print("="*60)
    print("\nThe web interface will start at: http://localhost:8000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")

    # Change to the query_classifier_app directory
    app_dir = os.path.join(os.path.dirname(__file__), "query_classifier_app")

    try:
        # Start ADK web server
        subprocess.run(
            ["adk", "web"],
            cwd=app_dir,
            check=True
        )
    except KeyboardInterrupt:
        print("\n\nShutting down ADK Web UI...")
    except subprocess.CalledProcessError as e:
        print(f"\nError starting ADK web: {e}")
        print("\nMake sure you're in the virtual environment:")
        print("  venv\\Scripts\\activate")
        sys.exit(1)
    except FileNotFoundError:
        print("\nError: 'adk' command not found.")
        print("\nMake sure you:")
        print("  1. Activated virtual environment: venv\\Scripts\\activate")
        print("  2. Installed google-adk: pip install google-adk")
        sys.exit(1)


if __name__ == "__main__":
    main()
