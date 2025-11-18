# ResearchMate AI - Web UI Quick Start Guide

## Starting the Web UI

### Option 1: Double-click the startup script (EASIEST)

Simply **double-click** this file:
```
start_web_ui.bat
```

The server will start automatically and show you the URL.

### Option 2: Using Command Prompt

1. Open Command Prompt (cmd)
2. Navigate to the project directory:
   ```
   cd c:\Users\niravkumarshah\Downloads\researchmate-ai
   ```
3. Run the startup script:
   ```
   start_web_ui.bat
   ```

### Option 3: Manual start

1. Open Command Prompt (cmd)
2. Navigate to the web_ui directory:
   ```
   cd c:\Users\niravkumarshah\Downloads\researchmate-ai\web_ui
   ```
3. Run the app:
   ```
   python app.py
   ```

## Accessing the Web UI

Once the server is running, open your browser to:

**http://localhost:8080**

You should see:
- Welcome screen with ResearchMate AI logo
- Example queries you can click
- Chat input box at the bottom

## Using the Web UI

1. **Type your research query** or click an example
2. **Press Enter** or click the send button
3. **Wait for the pipeline to execute** (you'll see a loading indicator)
4. **View the results** with:
   - Professional markdown formatting
   - Inline citations [1], [2], [3]
   - ### Sources section with clickable URLs
   - Credibility indicators for each source
   - Follow-up questions

## Stopping the Server

Press **Ctrl+C** in the terminal window where the server is running.

## Features

- ✅ **Conversation History** - All chats saved to database
- ✅ **Full Report Generator Output** - Sources section always included
- ✅ **No ADK UI needed** - Standalone application
- ✅ **Mobile Responsive** - Works on all devices
- ✅ **Dark Theme** - Professional appearance

## Troubleshooting

### Port already in use

If you see an error about port 8080 being in use:

1. Stop any other server on port 8080
2. Or edit `web_ui/app.py` and change the port:
   ```python
   uvicorn.run(
       "app:app",
       host="0.0.0.0",
       port=8081,  # Change to 8081 or any other port
       reload=True
   )
   ```

### Browser shows "Can't connect"

Make sure the server is running. You should see:
```
Uvicorn running on http://0.0.0.0:8080
```

### Database errors

If you encounter database issues, delete the database file:
```
del conversations.db
```

Then restart the server (it will recreate the database).

## Server Logs

When a query is processed, you'll see logs like:

```
[WEB UI] Processing query: What are the best headphones...
[STEP 1/6] Classifying query...
[STEP 2/6] Determining search strategy...
[STEP 3/6] Fetching data from sources...
[STEP 4/6] Formatting results...
[STEP 5/6] Analyzing content credibility...
[STEP 6/6] Generating final report...
[WEB UI] Pipeline completed successfully
```

This shows the complete 6-step research pipeline executing.

## Comparison: ADK UI vs Custom Web UI

| Feature | ADK UI | Custom Web UI |
|---------|--------|---------------|
| Sources section | Sometimes stripped | ✅ Always included |
| Extra LLM calls | Yes | ❌ No |
| Customizable | Limited | ✅ Full control |
| Conversation history | No | ✅ Yes (SQLite) |
| Standalone | No | ✅ Yes |
| Mobile responsive | Basic | ✅ Fully responsive |

## Next Steps

- Try different types of queries (factual, comparative, exploratory)
- Check the conversation history in the sidebar
- View the Sources section with clickable URLs
- Share the URL with teammates for testing

---

**Enjoy using ResearchMate AI!** 🎉
