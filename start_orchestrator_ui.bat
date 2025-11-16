@echo off
echo ============================================================
echo ResearchMate AI - Orchestrator Web UI
echo ============================================================
echo.
echo Starting ADK Web UI for the orchestrator agent...
echo.
echo Pipeline: Query Classifier -^> Information Gatherer
echo.
echo The UI will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Run ADK web UI with the clean agents directory
adk web adk_agents --port 8000

pause
