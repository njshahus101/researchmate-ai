@echo off
echo ============================================================
echo Starting ADK Web UI for Query Classifier
echo ============================================================
echo.
echo The web interface will be available at:
echo http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

cd query_classifier_app
call ..\venv\Scripts\activate.bat
adk web --port 8000
