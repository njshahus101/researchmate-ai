# ResearchMate AI - Custom Web UI

A professional, standalone web interface for ResearchMate AI with full control over the research pipeline.

## Features

✅ **Clean Chat Interface** - Modern, responsive design
✅ **Markdown Rendering** - Formatted output with syntax highlighting
✅ **Clickable URLs** - Sources section with verified links
✅ **Conversation History** - SQLite database storage
✅ **Loading Indicators** - Real-time feedback
✅ **Mobile-Responsive** - Works on all devices
✅ **Copy/Export** - Easy text selection and copying

## Why Custom Web UI?

This custom UI solves the ADK UI limitation where an extra LLM call was stripping the Sources section from reports. By calling the orchestrator directly:

- ✅ **No extra LLM calls** - Direct pipeline execution
- ✅ **Sources always included** - Full Report Generator output
- ✅ **Better control** - Custom styling and features
- ✅ **Standalone** - No need to run ADK UI

## Installation

No additional dependencies needed! All required packages are already in your venv:

- FastAPI
- Uvicorn
- Jinja2
- Google ADK

## Running the Web UI

### Option 1: Using Python directly

```bash
cd web_ui
python app.py
```

### Option 2: Using uvicorn

```bash
cd web_ui
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

The server will start on **http://localhost:8080**

## Usage

1. **Open your browser** to http://localhost:8080
2. **Type your research query** in the input box
3. **Press Enter** or click the send button
4. **Wait for results** - The orchestrator will:
   - Classify your query
   - Search the web
   - Fetch data from sources
   - Analyze content credibility
   - Generate a formatted report with Sources
5. **View results** - Markdown-formatted report with:
   - Professional formatting
   - Inline citations [1], [2], [3]
   - ### Sources section with URLs
   - Credibility indicators
   - Follow-up questions

## Features in Detail

### Conversation History

All conversations are saved to `conversations.db` (SQLite database) in the project root.

- View past conversations in the sidebar
- Click to load previous sessions
- Conversations persist across restarts

### Markdown Support

The UI fully supports markdown:
- **Bold**, *italic*, `code`
- Headings, lists, tables
- Code blocks with syntax highlighting
- Links (open in new tab)
- Block quotes

### Mobile Responsive

The UI works great on mobile devices:
- Responsive layout
- Touch-friendly buttons
- Collapsible sidebar

## Architecture

```
User Browser
    ↓
Web UI (HTML/CSS/JS)
    ↓
FastAPI Server (app.py)
    ↓
execute_fixed_pipeline() function
    ↓
6-Step Research Pipeline
    ↓
Report Generator Agent
    ↓
Final Report (with Sources!)
    ↓
Back to User Browser
```

## Key Files

- **app.py** - FastAPI backend, calls orchestrator directly
- **database.py** - SQLite schema and queries
- **templates/index.html** - Main chat interface
- **static/style.css** - Responsive styling
- **static/app.js** - Frontend logic
- **conversations.db** - SQLite database (created on first run)

## API Endpoints

- `GET /` - Main chat interface
- `POST /api/chat` - Send message, get response
- `GET /api/sessions` - List all conversations
- `GET /api/sessions/{id}` - Get specific conversation
- `POST /api/sessions` - Create new conversation
- `DELETE /api/sessions/{id}` - Delete conversation
- `GET /api/health` - Health check

## Troubleshooting

### Port already in use

If port 8080 is already in use:

```bash
# Option 1: Use a different port
uvicorn app:app --port 8081

# Option 2: Find and kill process on port 8080
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

### Database errors

If you encounter database issues, reset the database:

```bash
# Delete the database file
del ..\conversations.db

# Restart the server (will recreate database)
python app.py
```

### Import errors

Make sure you're running from the web_ui directory:

```bash
cd c:\Users\niravkumarshah\Downloads\researchmate-ai\web_ui
python app.py
```

## Development

To modify the UI:

1. **HTML** - Edit `templates/index.html`
2. **CSS** - Edit `static/style.css`
3. **JavaScript** - Edit `static/app.js`
4. **Backend** - Edit `app.py`

The server auto-reloads when files change (with `--reload` flag).

## Future Enhancements

Possible improvements:

- [ ] Export conversations to PDF
- [ ] User authentication
- [ ] Share conversations via link
- [ ] Dark/light theme toggle
- [ ] Voice input
- [ ] Streaming responses
- [ ] Citation tooltips
- [ ] Search conversations

## License

Part of the ResearchMate AI project.

---

**Built with ❤️ using FastAPI, SQLite, and modern web technologies**
