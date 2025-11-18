# ResearchMate AI - Getting Started Guide

Complete setup guide for running ResearchMate AI with custom Web UI locally.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)
7. [Project Structure](#project-structure)

---

## Prerequisites

### Required Software

- **Python 3.10+** (3.11 or 3.13 recommended)
- **Git** (for cloning the repository)
- **Google API Key** (for Gemini models)

### System Requirements

- Windows 10/11, macOS, or Linux
- 4GB RAM minimum (8GB recommended)
- Internet connection (for web searches and API calls)

---

## Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd researchmate-ai
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Install web UI dependencies
pip install -r web_ui/requirements.txt
```

**Main Dependencies:**
- `google-genai-adk` - Google Agent Development Kit
- `google-generativeai` - Gemini API
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `jinja2` - Template engine
- `requests` - HTTP library
- `beautifulsoup4` - HTML parsing

---

## Configuration

### Step 1: Set Up Google API Key

You need a Google API key to use Gemini models.

**Get Your API Key:**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key

**Set the API Key:**

**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY = "your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GOOGLE_API_KEY=your-api-key-here
```

**macOS/Linux:**
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

**Permanent Setup (Windows):**
1. Open System Properties → Environment Variables
2. Add new user variable:
   - Name: `GOOGLE_API_KEY`
   - Value: `your-api-key-here`

**Permanent Setup (macOS/Linux):**
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

### Step 2: Verify Installation

```bash
python -c "import google.generativeai as genai; print('✓ Google GenAI installed')"
python -c "from google.adk.agents import LlmAgent; print('✓ Google ADK installed')"
python -c "import fastapi; print('✓ FastAPI installed')"
```

All checks should print success messages.

---

## Running the Application

### Option 1: Custom Web UI (Recommended)

The custom Web UI provides the best experience with full control and no reformulation issues.

**Start the server:**

**Windows:**
```bash
# Double-click this file:
start_web_ui.bat

# Or run from command line:
cd web_ui
python app.py
```

**macOS/Linux:**
```bash
cd web_ui
python app.py
```

**Access the UI:**
Open your browser to: **http://localhost:8080**

**Features:**
- ✅ Clean chat interface
- ✅ Conversation history (SQLite)
- ✅ Full Report Generator output with Sources
- ✅ No ADK UI reformulation issues
- ✅ Mobile responsive
- ✅ Markdown rendering with syntax highlighting

### Option 2: ADK UI (Alternative)

If you want to use the official ADK UI:

```bash
venv\Scripts\adk.exe web adk_agents --port 8000 --reload
```

Access at: **http://localhost:8000**

**Note:** ADK UI may have issues with Sources section being stripped due to extra LLM calls. Use Custom Web UI for best results.

---

## Testing

### Test 1: Quick Health Check

Send a simple query to verify the pipeline:

**Query:**
```
What is the price of Sony WH-1000XM5 headphones?
```

**Expected Output:**
- 6-step pipeline execution logs
- Formatted report with pricing information
- ### Sources section with URLs
- Follow-up questions

### Test 2: Interactive Clarification

Test the clarification workflow:

**Query:**
```
Help me choose a telescope. Ask me questions to help with recommendations.
```

**Expected Behavior:**
1. Orchestrator asks 2-3 clarifying questions
2. You provide details (budget, experience, etc.)
3. Orchestrator runs pipeline with combined context
4. Full report generated with all your requirements

### Test 3: Comparative Query

**Query:**
```
Compare Toyota Camry vs Honda Accord 2024
```

**Expected Output:**
- Comparison table
- Weighted scoring
- Pros/cons for each
- Sources with credibility indicators

### Test 4: Exploratory Query

**Query:**
```
How do I get started with astrophotography?
```

**Expected Output:**
- Comprehensive guide
- Multiple sections (equipment, techniques, tips)
- Numerous sources
- Detailed follow-up questions

---

## Troubleshooting

### Issue: "GOOGLE_API_KEY not found"

**Solution:**
```bash
# Verify API key is set
echo %GOOGLE_API_KEY%  # Windows CMD
echo $env:GOOGLE_API_KEY  # Windows PowerShell
echo $GOOGLE_API_KEY  # macOS/Linux

# If empty, set it again (see Configuration section)
```

### Issue: Port Already in Use

**Web UI (port 8080):**
```bash
# Find process using port 8080
netstat -ano | findstr :8080

# Kill the process
taskkill /PID <PID> /F

# Or change port in web_ui/app.py:
# uvicorn.run(..., port=8081)
```

**ADK UI (port 8000):**
```bash
# Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: Module Not Found

```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
pip install -r web_ui/requirements.txt
```

### Issue: Database Errors

```bash
# Delete and recreate database
cd c:\Users\niravkumarshah\Downloads\researchmate-ai
del conversations.db  # Windows
rm conversations.db   # macOS/Linux

# Restart server (will recreate database)
```

### Issue: Sources Section Missing

**If using ADK UI:**
- This is a known limitation of ADK UI's extra LLM reformulation
- **Solution:** Use the Custom Web UI instead

**If using Custom Web UI:**
- Check terminal logs for errors
- Verify Report Generator agent loaded successfully
- Check pipeline completed all 6 steps

### Issue: Slow Response Times

**Causes:**
- Large number of web search results
- Complex queries requiring many sources
- API rate limiting

**Solutions:**
- Normal for first query (cold start)
- Subsequent queries should be faster
- Average time: 30-60 seconds for full pipeline

---

## Project Structure

```
researchmate-ai/
├── adk_agents/                    # Agent implementations
│   ├── orchestrator/              # Main orchestrator agent
│   │   ├── __init__.py
│   │   └── agent.py              # 6-step fixed pipeline
│   ├── query_classifier/          # Query classification agent
│   ├── information_gatherer/      # Data formatting agent
│   ├── content_analyzer/          # Credibility analysis agent
│   └── report_generator/          # Report generation agent (NEW)
│       ├── __init__.py
│       └── agent.py              # 3 report formats + citations
│
├── web_ui/                        # Custom Web UI (NEW)
│   ├── app.py                    # FastAPI backend
│   ├── database.py               # SQLite conversation storage
│   ├── templates/
│   │   └── index.html           # Chat interface
│   ├── static/
│   │   ├── style.css            # Responsive styling
│   │   └── app.js               # Frontend logic
│   ├── requirements.txt         # Web UI dependencies
│   └── README.md                # Web UI documentation
│
├── agents/                        # Original agent prototypes
├── tools/                         # Utility tools
│
├── start_web_ui.bat              # One-click Web UI startup
├── WEB_UI_QUICKSTART.md          # Quick start guide
├── GETTING_STARTED.md            # This file
├── requirements.txt              # Main dependencies
│
└── Documentation files:
    ├── REPORT_GENERATOR_INTEGRATION.md
    ├── CHECKLIST_COMPLETED.md
    ├── FIX_ORCHESTRATOR_PASSTHROUGH.md
    └── ...

Database files (created at runtime):
└── conversations.db              # SQLite conversation history
```

---

## Architecture Overview

### Agent Pipeline (Sequential Workflow)

```
User Query
    ↓
┌─────────────────────────────────────────────────────┐
│  ORCHESTRATOR AGENT (Fixed Pipeline)                │
│                                                      │
│  STEP 1/6: Query Classification (A2A)              │
│  ├─→ Query Classifier Agent                        │
│  └─→ Returns: type, strategy, complexity           │
│                                                      │
│  STEP 2/6: Smart Search                            │
│  ├─→ Google Shopping API (price queries)           │
│  ├─→ SerpAPI (web search)                          │
│  └─→ Returns: URLs                                 │
│                                                      │
│  STEP 3/6: Data Fetching                           │
│  ├─→ Fetch content from URLs                       │
│  └─→ Returns: raw data                             │
│                                                      │
│  STEP 4/6: Information Formatting (A2A)            │
│  ├─→ Information Gatherer Agent                    │
│  └─→ Returns: formatted information                │
│                                                      │
│  STEP 5/6: Content Analysis (A2A)                  │
│  ├─→ Content Analyzer Agent                        │
│  └─→ Returns: credibility scores, facts            │
│                                                      │
│  STEP 6/6: Report Generation (A2A)                 │
│  ├─→ Report Generator Agent                        │
│  └─→ Returns: final formatted report               │
│                                                      │
└─────────────────────────────────────────────────────┘
    ↓
Final Report with:
- Professional markdown formatting
- Inline citations [1], [2], [3]
- ### Sources section with URLs
- Credibility indicators
- Follow-up questions
```

### Web UI Architecture

```
User Browser
    ↓
Custom Web UI (HTML/CSS/JS)
    ↓
FastAPI Server (app.py)
    ↓
execute_fixed_pipeline() ← Direct call, no extra LLM!
    ↓
6-Step Research Pipeline
    ↓
Report Generator Agent
    ↓
Final Report (with Sources intact!)
    ↓
SQLite Database (conversation history)
    ↓
Back to User Browser
```

---

## Key Features

### Report Generator Agent

**Three Report Formats:**
1. **Factual** - Quick answers with evidence
2. **Comparative** - Side-by-side comparison tables
3. **Exploratory** - Comprehensive guides

**Citation System:**
- Inline citations: [1], [2], [3]
- Full Sources section with URLs
- Credibility indicators (High/Medium/Low)
- Source quality reasoning

**Weighted Scoring:**
- Detects user priorities from query
- Applies 2x weight to prioritized criteria
- Fair comparison across options

**Follow-up Questions:**
- 3-5 relevant questions per report
- Tailored to query type
- Helps users dig deeper

### Custom Web UI

**Advantages over ADK UI:**
- ✅ No content reformulation
- ✅ Sources always included
- ✅ Conversation history
- ✅ Full control over rendering
- ✅ Professional design
- ✅ Mobile responsive

---

## Next Steps

1. **✅ Run the Web UI** - Start with `start_web_ui.bat`
2. **🧪 Test Queries** - Try factual, comparative, and exploratory queries
3. **📊 Check Sources** - Verify all reports include Sources section
4. **💾 View History** - Check conversation sidebar
5. **🎨 Customize** - Modify `web_ui/static/style.css` for your branding

---

## Support & Documentation

- **Web UI Guide:** [WEB_UI_QUICKSTART.md](WEB_UI_QUICKSTART.md)
- **Report Generator:** [REPORT_GENERATOR_INTEGRATION.md](REPORT_GENERATOR_INTEGRATION.md)
- **Project Checklist:** [CHECKLIST_COMPLETED.md](CHECKLIST_COMPLETED.md)

---

## Tips for Best Results

### Query Writing

**Good Queries:**
- "What are the best wireless headphones under $250 for music quality?"
- "Compare Toyota Camry vs Honda Accord 2024 for reliability and value"
- "Help me get started with astrophotography for galaxy imaging"

**Tips:**
- Be specific about budget, requirements, priorities
- Use comparative language for comparison reports
- Ask open-ended questions for exploratory reports

### Interactive Clarification

If you want personalized recommendations:
1. Add "ask me questions" to your query
2. Orchestrator will ask clarifying questions
3. Provide details (budget, experience, preferences)
4. Pipeline re-runs with your full context
5. Get tailored recommendations

### Performance

- **First query:** ~30-60 seconds (cold start)
- **Subsequent queries:** ~20-40 seconds
- **Factors:** Number of sources, query complexity, API response times

---

## Development

### Running Tests

```bash
# Validate Report Generator integration
python validate_report_generator.py

# Test specific query types
python test_report_generator.py
```

### Modifying Agents

All agents are in `adk_agents/`:
- Edit `agent.py` files to modify behavior
- Restart server to reload changes
- Check terminal logs for debugging

### Customizing Web UI

**Frontend:**
- HTML: `web_ui/templates/index.html`
- CSS: `web_ui/static/style.css`
- JS: `web_ui/static/app.js`

**Backend:**
- API: `web_ui/app.py`
- Database: `web_ui/database.py`

Changes are auto-reloaded with `--reload` flag.

---

## License

Part of the ResearchMate AI project.

---

**Built with ❤️ using Google ADK, FastAPI, and modern AI technologies**

Last Updated: 2025-11-17
