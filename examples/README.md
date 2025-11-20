# ResearchMate AI - Example Demos

This folder contains demonstration scripts that showcase specific features of ResearchMate AI.

## Demo Scripts

### 1. Content Analysis with Google Shopping
**File:** `demo_content_analysis_with_google_shopping.py`

Demonstrates how the Content Analysis Agent evaluates product results from Google Shopping:
- Source credibility scoring (Amazon, Best Buy, Walmart, etc.)
- Price conflict detection and variance analysis
- Comparison matrix generation
- Best value recommendation algorithm

**Requirements:**
- `SERPAPI_KEY` environment variable (for Google Shopping API)

**Usage:**
```bash
python examples/demo_content_analysis_with_google_shopping.py
```

**Example Output:**
- Credibility assessment for each seller (High/Medium/Low)
- Price statistics (lowest, highest, average, variance)
- Conflict severity analysis
- Visual comparison matrix
- Recommended best value option

---

### 2. Observability Dashboard
**File:** `demo_observability.py`

Demonstrates the observability system for tracking agent operations:
- Span tracking for multi-agent workflows
- Performance metrics (latency, success rates)
- Error tracking and logging
- Visual dashboard generation

**Usage:**
```bash
python examples/demo_observability.py
```

**Features:**
- Real-time operation tracking
- Performance bottleneck identification
- Error rate monitoring
- Agent communication visualization

---

### 3. Quality Assurance Console
**File:** `demo_qa_console.py`

Interactive demonstration of the Quality Assurance system:
- Citation validation
- Completeness checks
- Source quality assessment (citation-weighted credibility)
- Comparison matrix validation
- Overall quality scoring (0-100) with letter grades (A/B/C/D/F)

**Usage:**
```bash
python examples/demo_qa_console.py
```

**What It Shows:**
- Detailed validation results by category
- Citation-weighted credibility calculation
- Quality score breakdown
- Actionable recommendations for improvement

---

## Running the Demos

### Prerequisites
1. Set up your `.env` file with required API keys:
   ```bash
   GOOGLE_API_KEY=your_google_api_key
   SERPAPI_KEY=your_serpapi_key  # Optional, for demo 1 only
   ```

2. Activate your virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Notes
- These demos are standalone scripts that can run independently
- They're designed for educational purposes to understand system internals
- For production usage, use the main application (`python main.py`) or Web UI
- Some demos may generate console output with detailed logging

## Contributing
When adding new demo scripts:
1. Use the `demo_*.py` naming convention
2. Add comprehensive docstrings at the top of the file
3. Update this README with a description and usage instructions
4. Keep demos focused on a single feature or concept
