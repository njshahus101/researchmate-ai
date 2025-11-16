# Query Classifier Agent - ADK Web UI Guide

## Server Status

✓ **ADK Web UI is running!**

**Access the UI at:** http://127.0.0.1:8080

---

## Quick Start

### 1. Open the Web UI

Open your browser and go to:
```
http://127.0.0.1:8080
```

### 2. Select the Agent

You should see "query_classifier" in the agent list. Click on it to start chatting.

### 3. Start Testing!

Try these example queries:

**Factual Queries:**
- What is the capital of Japan?
- Who invented the telephone?
- When was Python programming language created?

**Comparative Queries:**
- Best wireless headphones under $200
- iPhone vs Android comparison
- Top programming languages for beginners

**Exploratory Queries:**
- Explain quantum computing for beginners
- How does machine learning work?
- What is blockchain technology?

**Monitoring Queries:**
- Latest developments in AI
- Recent news about climate change
- Current trends in web development

---

## What the Agent Does

The Query Classifier will:

1. **Analyze your query** and determine its type
2. **Assign a complexity score** (1-10)
3. **Recommend a research strategy**:
   - quick-answer (1 source)
   - multi-source (3-5 sources)
   - deep-dive (5-10+ sources)
4. **Identify key topics** to research
5. **Explain the reasoning** behind the classification
6. **Suggest next steps** for your research

---

## Example Interaction

**You:** Best laptops under $1000

**Agent Response:**
```
Great question! I'll help you classify this query.

Classification: Comparative

This is a product comparison query where you're looking for
the best option within a specific budget.

Analysis:
- Complexity Score: 6/10 (moderate)
- Research Strategy: Multi-source
- Key Topics: laptops, budget computing, performance, value
- Your Intent: Find best value laptop under $1000
- Recommended Sources: 4-5 tech review sites

Reasoning:
This requires comparing multiple products based on various
criteria (performance, build quality, features, value). It's
more complex than a simple fact lookup but doesn't require
deep technical research.

Next Steps:
I'd recommend searching tech review sites like NotebookCheck,
LaptopMag, and PCMag, then creating a comparison table of
the top 3-5 options based on your priorities.
```

---

## Features

### Current Features ✓
- Real-time query classification
- Conversational, friendly responses
- Detailed analysis with reasoning
- Research strategy recommendations
- Key topic extraction
- Complexity scoring
- Next steps suggestions

### With Memory Service ✓
- Research history tracking
- User preference awareness
- Context from previous queries
- Personalized recommendations

---

## Server Management

### Check Server Status
The server is running in the background. You should see:
```
ADK Web Server started
For local testing, access at http://127.0.0.1:8080
```

### View Server Logs
Server logs show activity in real-time. Check for:
- Agent initialization messages
- Memory Service status
- Request/response logs

### Stop the Server
To stop the server, press `Ctrl+C` in the terminal where it's running,
or close the terminal window.

### Restart the Server
```bash
adk web agents_ui --port 8080
```

---

## Configuration

### Agent Location
```
researchmate-ai/
└── agents_ui/
    └── query_classifier/
        ├── __init__.py
        └── agent.py        # Main agent configuration
```

### Memory Service
- **Enabled:** Yes
- **Storage:** `query_classifier_web_memory.json`
- **Features:**
  - Research history tracking
  - Topic connections
  - User preferences (can be extended)

### Model Configuration
- **Model:** Gemini 2.5 Flash Lite
- **Provider:** Google AI
- **API Key:** From `.env` file

---

## Customization

### Disable Memory Service

Edit `agents_ui/query_classifier/agent.py`:
```python
ENABLE_MEMORY = False  # Change to False
```

### Change Port

```bash
adk web agents_ui --port 8888  # Use different port
```

### Modify Agent Instructions

Edit the `instruction` variable in `agents_ui/query_classifier/agent.py` to customize:
- Response format
- Classification criteria
- Tone and style
- Additional features

---

## Troubleshooting

### Server won't start
**Check:**
- Port 8080 is not already in use
- GOOGLE_API_KEY is set in `.env`
- All dependencies are installed

**Solution:**
```bash
# Use different port
adk web agents_ui --port 8888

# Check dependencies
pip install -r requirements.txt
```

### Agent not responding
**Check:**
- API key is valid
- Internet connection is working
- Browser console for errors

### Memory not working
**Check:**
- Memory Service is enabled in `agent.py`
- `services/memory_service.py` exists
- Storage file has write permissions

---

## Advanced Usage

### Enable Verbose Logging
```bash
adk web agents_ui --port 8080 -v
```

### Enable Auto-reload (for development)
```bash
adk web agents_ui --port 8080 --reload
```

### Custom Session Storage
```bash
adk web agents_ui --port 8080 --session_service_uri="sqlite:///sessions.db"
```

---

## Integration with Other Tools

### Use with Information Gatherer

The Query Classifier can feed into your Information Gatherer agent:

1. Get classification from Query Classifier
2. Use `research_strategy` to determine search depth
3. Use `key_topics` to guide search queries
4. Use `estimated_sources` to know how many sources to fetch

### Export Session Data

Sessions are stored in memory by default. To persist:
- Use `--session_service_uri` with SQLite or database
- Export memory file: `query_classifier_web_memory.json`

---

## Testing Different Query Types

### Factual (Simple)
Expected: Complexity 1-3, quick-answer strategy
```
- What is the boiling point of water?
- When did World War 2 end?
- Who wrote Hamlet?
```

### Comparative (Moderate)
Expected: Complexity 4-7, multi-source strategy
```
- Best noise-cancelling headphones 2024
- Python vs JavaScript for beginners
- Mac vs PC for video editing
```

### Exploratory (Complex)
Expected: Complexity 6-10, deep-dive strategy
```
- Explain neural networks in detail
- How does cryptocurrency mining work?
- What is the philosophy of existentialism?
```

### Monitoring (Current)
Expected: Complexity varies, multi-source with recency
```
- Latest AI research developments
- Recent cybersecurity threats
- Current trends in sustainable energy
```

---

## Next Steps

1. **Test the Agent**: Try different types of queries
2. **Observe Classifications**: See how it categorizes different questions
3. **Check Memory**: Ask related queries to see context awareness
4. **Integrate**: Use classifications to guide your research workflow
5. **Customize**: Modify instructions to fit your use case

---

## Files Reference

- **Agent Code:** [agents_ui/query_classifier/agent.py](agents_ui/query_classifier/agent.py)
- **Memory Storage:** `query_classifier_web_memory.json`
- **Documentation:** This file

---

## Support

For issues:
1. Check server logs for errors
2. Verify API key is valid
3. Review agent configuration
4. Check memory file permissions

For questions about ADK Web UI:
```bash
adk web --help
```

---

**Status:** ✓ Running on http://127.0.0.1:8080
**Agent:** Query Classifier
**Memory:** Enabled
**Ready to test!**
