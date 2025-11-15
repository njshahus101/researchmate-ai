# How to Run ADK Web UI

## ✅ Easy Method (Recommended for VS Code)

### Step 1: Open VS Code Terminal

Press `` Ctrl + ` `` (backtick) or go to **Terminal > New Terminal**

### Step 2: Navigate to project directory

```powershell
cd C:\Users\niravkumarshah\Downloads\researchmate-ai
```

### Step 3: Run the batch file

```powershell
.\start_web_ui.bat
```

### Step 4: Open browser

Go to: **http://localhost:8000**

### Step 5: Start chatting!

Type your questions in the chat interface and see the classifications!

---

## 🛑 To Stop the Server

Press `Ctrl + C` in the terminal where the server is running

---

## 🔧 Alternative: Manual Steps

If the batch file doesn't work, run these commands one by one:

```powershell
# 1. Go to project directory
cd C:\Users\niravkumarshah\Downloads\researchmate-ai

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Go to the app folder
cd query_classifier_app

# 4. Start ADK web
adk web
```

Then open http://localhost:8000

---

## ❌ Troubleshooting

### "adk: command not found"

Make sure you activated the virtual environment first:
```powershell
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal prompt.

### Port 8000 already in use

Use a different port:
```powershell
adk web --port 8080
```

Then open http://localhost:8080

### Module import errors

Make sure google-adk is installed:
```powershell
pip install google-adk
```

---

## 💡 Quick Test Without Web UI

If you just want to test quickly without the web interface:

```powershell
cd C:\Users\niravkumarshah\Downloads\researchmate-ai
venv\Scripts\activate
python test_my_query.py
```

This runs a simple test script you can edit!
