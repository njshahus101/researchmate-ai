# Testing Guide - Query Classifier MVP

This guide shows you how to test the Query Classifier Agent using different methods.

---

## Prerequisites

Make sure you're in the project directory and virtual environment:

```bash
cd C:\Users\niravkumarshah\Downloads\researchmate-ai
venv\Scripts\activate
```

---

## Method 1: Quick Test (Fastest) ⚡

Run the pre-built test file:

```bash
python test_simple.py
```

**What it does:**
- Tests 3 different query types
- Shows classification results
- Takes ~10-15 seconds

**Output:**
```
============================================================
ResearchMate AI - Query Classifier Test
============================================================

Query: What is the capital of Japan?
------------------------------------------------------------
Classification successful!
```

---

## Method 2: Test Your Own Queries 🔧

### Step 1: Edit the test file

Open [test_my_query.py](test_my_query.py) in VS Code

### Step 2: Change the query

```python
# Line 14 - CHANGE THIS
my_query = "Your question here"
```

Examples to try:
- `"How do I cook pasta?"`
- `"Compare iPhone 15 vs Samsung Galaxy S24"`
- `"Explain blockchain technology"`
- `"Latest trends in AI development"`

### Step 3: Run it

```bash
python test_my_query.py
```

**Output:**
```
============================================================
Testing Query: Your question here
============================================================

✅ Classification Successful!

Query Type: comparative
Complexity: 5/10
Strategy: multi-source
Key Topics: iPhone, Samsung, comparison
```

---

## Method 3: ADK Web UI (Best for Interactive Testing) 🌐

The ADK Web UI gives you a **visual chat interface** to test your agent interactively!

### Step 1: Start the ADK Web Server

**Option A - Using the helper script:**
```bash
python run_adk_ui.py
```

**Option B - Direct command:**
```bash
cd query_classifier_app
adk web
```

### Step 2: Open in Browser

The server will start and display:
```
+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://127.0.0.1:8000.                         |
+-----------------------------------------------------------------------------+
```

**Open:** http://localhost:8000

### Step 3: Use the Chat Interface

You'll see a beautiful web interface where you can:

1. **Type any query** in the chat box
2. **See the agent's response** in real-time
3. **View the full conversation history**
4. **Test multiple queries** in sequence

**Example:**

![ADK Web UI](https://storage.googleapis.com/github-repo/kaggle-5days-ai/day1/adk-web-ui.gif)

### Features:

✅ **Real-time streaming** - See responses as they're generated
✅ **Conversation history** - All queries are saved in the session
✅ **Beautiful UI** - Professional chat interface
✅ **Debug info** - See model responses and metadata
✅ **Session management** - Create multiple test sessions

### Stop the Server

Press `Ctrl+C` in the terminal

---

## Method 4: Python REPL (For Quick Experiments) 🐍

### Step 1: Start Python

```bash
python
```

### Step 2: Import and test

```python
>>> import asyncio
>>> from agents.query_classifier_mvp import classify_query
>>>
>>> # Test a query
>>> result = asyncio.run(classify_query("Best laptops for programming"))
>>>
>>> # View results
>>> print(result['query_type'])
comparative
>>>
>>> print(result['complexity_score'])
5
>>>
>>> print(result['reasoning'])
This requires comparing multiple products...
```

### Step 3: Exit

```python
>>> exit()
```

---

## Method 5: VS Code Debugger (For Development) 🐛

### Step 1: Open [test_my_query.py](test_my_query.py) in VS Code

### Step 2: Set a breakpoint

Click to the left of line 18 (the `classify_query` call)

### Step 3: Start debugging

- Press `F5` or click "Run and Debug"
- Choose "Python File"

### Step 4: Step through the code

- `F10` - Step over
- `F11` - Step into
- View variables in the left panel
- Inspect the `result` object

---

## Troubleshooting

### Error: "GOOGLE_API_KEY not found"

**Solution:**
Make sure your [.env](.env) file has your API key:
```
GOOGLE_API_KEY=<<Sample Key from AI Studio>>
```

### Error: "Module not found"

**Solution:**
Make sure you activated the virtual environment:
```bash
venv\Scripts\activate
```

### ADK Web UI - Port 8000 already in use

**Solution:**
Kill the existing process or use a different port:
```bash
adk web --port 8080
```

Then open: http://localhost:8080

### Connection timeout / API errors

**Solution:**
Check your internet connection and API key validity.

---

## Comparing the Methods

| Method | Speed | Interactive | Visual | Best For |
|--------|-------|-------------|--------|----------|
| Quick Test | ⚡⚡⚡ | ❌ | ❌ | Quick verification |
| Custom Query | ⚡⚡ | ❌ | ❌ | Testing specific cases |
| **ADK Web UI** | ⚡ | ✅ | ✅ | **Development & Demo** |
| Python REPL | ⚡⚡ | ✅ | ❌ | Quick experiments |
| VS Code Debug | ⚡ | ✅ | ✅ | Debugging issues |

**Recommendation:** Use **ADK Web UI** for most testing - it's the best experience!

---

## Advanced: Testing with Different Models

Edit [query_classifier_app/agent.py](query_classifier_app/agent.py):

```python
# Try different Gemini models
model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)
# or
model=Gemini(model="gemini-1.5-pro", retry_options=retry_config)
# or
model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config)
```

Then restart ADK web to see the difference!

---

## Next Steps

Once you're comfortable testing the Query Classifier:

1. **Implement Information Gatherer Agent** - Add Google Search
2. **Test the full pipeline** - Connect multiple agents
3. **Add more sophisticated queries** - Test edge cases
4. **Build the web interface** - Create a production UI

See [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) for the full plan!
