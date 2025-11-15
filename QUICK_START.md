# Quick Start - Testing Your Query Classifier

## 🚀 Three Ways to Test (Pick One)

### 1️⃣ **Quickest Test** (10 seconds)

```bash
cd C:\Users\niravkumarshah\Downloads\researchmate-ai
venv\Scripts\activate
python test_simple.py
```

### 2️⃣ **Your Own Query** (30 seconds)

```bash
# Edit test_my_query.py (line 14) with your question
python test_my_query.py
```

### 3️⃣ **ADK Web UI** (Best! Visual Interface) ⭐

```bash
python run_adk_ui.py
```

Then open: **http://localhost:8000**

---

## 📺 What the ADK Web UI Looks Like

The ADK Web UI gives you a **ChatGPT-like interface** where you can:

1. Type any question
2. See the classification in real-time
3. Try multiple queries
4. View full JSON responses

**Example queries to try:**
- "What is machine learning?"
- "Best smartphones under $500"
- "Explain quantum computing for beginners"
- "Latest AI news"

---

## 🛠️ From VS Code

### Terminal Method:
1. Open Terminal in VS Code (`Ctrl + ~`)
2. Run: `venv\Scripts\activate`
3. Run: `python test_simple.py`

### With ADK UI:
1. Open Terminal in VS Code
2. Run: `python run_adk_ui.py`
3. Open browser to http://localhost:8000

---

## 📖 Need More Details?

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing instructions!
