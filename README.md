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

### Option 1: Web UI (Recommended - Easiest!)

**Windows:**
```bash
# Simply double-click: start_web_ui.bat
# Or run:
cd web_ui
python app.py
```

**macOS/Linux:**
```bash
cd web_ui
python app.py
```

Then open your browser to **http://localhost:8080**

### Option 2: Command Line Interface

```bash
# Run the main application
python main.py
```

**See [WEB_UI_QUICKSTART.md](WEB_UI_QUICKSTART.md) for detailed Web UI instructions**

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

## Quality Assurance System

ResearchMate AI includes a comprehensive quality assurance framework that validates every research report and provides an overall quality score (0-100) with letter grades (A/B/C/D/F).

### How Quality Scores Are Calculated

The overall quality score reflects **confidence in the research response** based on four weighted categories:

| Category | Weight | What It Measures |
|----------|--------|------------------|
| **Source Quality** | **35%** | Citation-weighted credibility - measures which sources the report actually relies on |
| **Citations** | 25% | Proper citation format, matching sources, no hallucinations |
| **Completeness** | 20% | Required sections present, content length, markdown structure |
| **Comparison** | 20% | Comparison matrix quality (for comparative queries only) |

### Citation-Weighted Credibility (Key Innovation)

Unlike traditional systems that just check if high-quality sources exist, ResearchMate AI measures **which sources are actually used** in the report:

**How It Works:**
1. Content Analyzer assigns credibility scores (0-100) to each source
2. Report Generator is guided to prioritize high-credibility sources for main claims
3. Quality Assurance counts how many times each source [1], [2], [3] is cited in the report body
4. Weighted credibility = Σ(citation_frequency × credibility_score)

**Example Scenario:**
- Sources: [1] Nature (90 cred), [2] Science (85 cred), [3] Reddit (50 cred)
- Report cites [1] 10×, [2] 5×, [3] 2×
- **Weighted credibility: 82/100** ✓ High confidence (86% citations from high-cred sources)

If the same report cited [3] 15× and [1] + [2] only 2×:
- **Weighted credibility: 55/100** ⚠️ Low confidence (88% citations from low-cred sources)
- **Overall quality drops to B grade**, signaling to users to treat findings with more caution

### Source Credibility Levels

- **High Credibility (80-100)**: Academic journals, government sites, established news outlets
- **Medium Credibility (60-79)**: Industry blogs, review sites, established forums
- **Low Credibility (<60)**: Anonymous forums, unverified user posts, promotional content

### Quality Grades

- **A (90-100)**: Excellent - High confidence, comprehensive, well-cited
- **B (80-89)**: Good - Solid research with minor areas for improvement
- **C (70-79)**: Acceptable - Meets basic standards but needs improvement
- **D (60-69)**: Needs Improvement - Missing key elements or low source quality
- **F (<60)**: Poor Quality - Significant issues that undermine reliability

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
- Citation-Weighted Quality Assurance (measures actual source usage, not just availability)

## License

Apache 2.0

## Authors

Built for the Google AI Agents Intensive Course Capstone Project
