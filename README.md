# ResearchMate AI

An intelligent multi-agent research assistant built with Google's Agent Development Kit (ADK) that transforms how individuals conduct research by automating the entire research workflow.

## Overview

ResearchMate AI uses a sophisticated multi-agent architecture to:
- Understand user intent and query complexity
- Gather information from multiple authoritative sources
- Analyze content credibility and extract insights
- Generate comprehensive reports with citations
- Learn user preferences over time

## Key Features

### Smart Research Stratifier
- **Intelligent Query Triage**: Automatically routes queries based on complexity
- **Comparison Excellence**: Generates structured comparison matrices
- **Contextual Memory**: Builds persistent knowledge graph of research history

### Multi-Agent Architecture
- **Query Classification Agent**: Analyzes queries and determines optimal workflow
- **Information Gathering Agent**: Executes targeted searches and fetches full content
- **Content Analysis Agent**: Evaluates source credibility and extracts key facts
- **Report Generation Agent**: Transforms analyzed data into actionable insights

### Custom MCP Tools
- **Web Content Fetcher**: Downloads and extracts clean article content
- **Price Extractor**: Extracts structured product data for comparisons

## Technology Stack

- **Framework**: Google ADK with A2A Protocol
- **Language**: Python 3.10+
- **LLM**: Gemini 2.0 Flash
- **Agent Communication**: A2A Protocol
- **Tool Integration**: MCP (Model Context Protocol)
- **Storage**: SQLite (MCP file system + in-memory sessions)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/njshahus101/researchmate-ai.git
cd researchmate-ai
```

2. Create and activate virtual environment:

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

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

## Quick Start

```bash
# Run the main application
python main.py
```

## Project Structure

```
researchmate-ai/
├── agents/                 # Core agent implementations
├── mcp_servers/           # Custom MCP tool servers
├── services/              # Memory and session services
├── tools/                 # Custom function tools
├── utils/                 # Logging and helper utilities
└── main.py               # Application entry point
```

## Example Workflows

### Quick Factual Query
**Input**: "What is the capital of Japan?"
**Output**: Direct answer with citation (3 seconds)

### Comparison Research
**Input**: "Best wireless headphones under $200"
**Output**: Comparison matrix with weighted scores (45 seconds)

### Contextual Follow-up
**Input**: "What about battery life on those headphones?"
**Output**: Updated comparison matrix (15 seconds)

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black .
flake8 .
```

## Architecture Concepts

This project demonstrates:
- Multi-Agent Systems with A2A Protocol
- MCP Tool Architecture
- Memory and State Management
- Observability and Logging
- Quality Assurance

## License

Apache 2.0

## Authors

Built for the Google AI Agents Intensive Course Capstone Project
