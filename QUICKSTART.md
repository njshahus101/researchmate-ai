# ResearchMate AI - Quick Start Guide

Get up and running with ResearchMate AI in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- Google API Key (Gemini)
- Internet connection

## Installation Steps

### 1. Navigate to the Project Directory

```bash
cd researchmate-ai
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your Google API Key:

```
GOOGLE_API_KEY=your_actual_api_key_here
```

**Get your API key:**
1. Go to [Google AI Studio](https://aistudio.google.com/app/api_keys)
2. Create a new API key
3. Copy it to your `.env` file

### 5. Run the Application

```bash
python main.py
```

You should see:

```
============================================================
ResearchMate AI - Interactive Mode
============================================================

Commands:
  - Type your research query
  - Type 'exit' or 'quit' to stop
  - Type 'help' for more information
============================================================

🔍 Enter your research query:
```

## Example Usage

### Example 1: Factual Query

```
🔍 Enter your research query: What is the capital of Japan?

============================================================
RESEARCH RESULTS
============================================================
Status: success
Query Type: factual
Strategy: quick-answer
...
```

### Example 2: Comparative Query

```
🔍 Enter your research query: Best wireless headphones under $200

============================================================
RESEARCH RESULTS
============================================================
Status: success
Query Type: comparative
Strategy: multi-source
...
```

### Example 3: Exploratory Query

```
🔍 Enter your research query: Explain quantum computing for beginners

============================================================
RESEARCH RESULTS
============================================================
Status: success
Query Type: exploratory
Strategy: deep-dive
...
```

## Testing Individual Components

### Test Web Content Fetcher

```bash
python mcp_servers/web_content_fetcher.py
```

### Test Price Extractor

```bash
python mcp_servers/price_extractor.py
```

### Test Memory Service

```bash
python services/memory_service.py
```

### Test Individual Agents

```bash
python agents/query_classifier.py
python agents/information_gatherer.py
python agents/content_analyzer.py
python agents/report_generator.py
```

## Project Structure Overview

```
researchmate-ai/
├── agents/                    # Four core agents
│   ├── query_classifier.py
│   ├── information_gatherer.py
│   ├── content_analyzer.py
│   └── report_generator.py
├── mcp_servers/              # Custom MCP tools
│   ├── web_content_fetcher.py
│   └── price_extractor.py
├── services/                 # Memory and sessions
│   ├── memory_service.py
│   └── session_service.py
├── utils/                    # Utilities
│   ├── logging_config.py
│   └── helpers.py
├── main.py                   # Application entry point
└── requirements.txt          # Dependencies
```

## Common Issues

### Issue: "GOOGLE_API_KEY not found"

**Solution:** Make sure you created a `.env` file with your API key.

### Issue: "Module not found" errors

**Solution:** Make sure you installed dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Import errors

**Solution:** Make sure you're in the project root directory when running:
```bash
cd researchmate-ai
python main.py
```

## Next Steps

1. **Explore the Code**: Check out individual agent files in `agents/`
2. **Customize Agents**: Modify agent instructions in each agent file
3. **Add Tools**: Create custom tools in `tools/` directory
4. **Enable Persistence**: Set `use_database=True` in main.py
5. **Deploy**: Follow deployment guides in the documentation

## Development Mode

For development with auto-reload, you can use:

```bash
# Install development dependencies
pip install watchdog

# Run with auto-reload (custom script needed)
# or just manually restart after changes
```

## Configuration Options

Edit `.env` to customize:

- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR
- `DATABASE_URL`: Database connection string
- `MODEL_NAME`: Gemini model to use
- `RETRY_ATTEMPTS`: Number of retry attempts

## Getting Help

- Check the main [README.md](README.md) for detailed documentation
- Review sample notebooks in `sample/` directory
- Consult [Google ADK documentation](https://google.github.io/adk-docs/)
- Open an issue on GitHub (if applicable)

## What's Next?

The current implementation provides the foundation. To make it fully functional:

1. **Complete Agent Integration**: Wire up all four agents in the pipeline
2. **Implement A2A Communication**: Enable agent-to-agent communication
3. **Add Real MCP Servers**: Implement full MCP protocol support
4. **Deploy to Production**: Use Cloud Run or Agent Engine
5. **Add Web UI**: Build a web interface using ADK web

Happy researching! 🚀
