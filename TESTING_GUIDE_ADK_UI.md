# Testing Guide - ADK UI Demo

**Purpose:** Test all Day 1 improvements (enhanced extraction & error handling)
**Date:** 2025-11-16

---

## 🚀 Setup: Start the ADK UI Server

### Step 1: Open Terminal

Open a terminal in your project directory:
```
c:\Users\niravkumarshah\Downloads\researchmate-ai
```

### Step 2: Start the Server

```bash
venv\Scripts\adk.exe web adk_agents --port 8000 --reload
```

**Expected Output:**
```
+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://127.0.0.1:8000.                         |
+-----------------------------------------------------------------------------+
```

### Step 3: Open Browser

Open your browser and go to:
```
http://127.0.0.1:8000
```

You should see the ADK UI interface with a chat window.

---

## 🧪 Test Suite: 5 Test Scenarios

### **Test 1: Successful Product Extraction** ✅

**Goal:** Test enhanced product extraction with full data

**Query to Test:**
```
Logitech MX Master 3S wireless mouse price and reviews
```

**What to Watch in Terminal:**
```
[STEP 1/4] OK Classification complete
  Type: factual
  Strategy: quick-answer

[STEP 2/4] OK Found 5 URLs

[STEP 3/4] Fetching data from URLs...
  [1/5] Extracting product: https://www.amazon.com/...
  [EXTRACT] Attempting JSON-LD extraction...
  [EXTRACT] Using Amazon-specific extraction...
  [EXTRACT] Extraction complete - Price: $109.99, Rating: 4.5
  [1/5] OK Success (useful data)

[STEP 4/4] OK Formatting complete
```

**Expected Response in Browser:**
- Product name: Logitech MX Master 3S
- Price: $109.99 USD
- **List Price:** $119.99 (shows discount)
- Rating: 4.5/5
- Review count: 11,000+
- Features: 5-8 bullet points
- Images: Multiple product images
- Source URLs cited

**What This Tests:**
✅ JSON-LD extraction
✅ Amazon-specific parsing
✅ Sale price detection
✅ Features and images
✅ Multi-source fetching (try 5, keep best 3)

---

### **Test 2: Query Reformulation (Error Recovery)** 🔄

**Goal:** Test automatic query enhancement when search fails

**Query to Test (intentionally vague):**
```
WH-1000XM5
```

**What to Watch in Terminal:**
```
[STEP 2/4] Searching web for URLs...
[SEARCH] Found 5 results
[STEP 2/4] OK Found 5 URLs

OR (if initial search had failed):

[STEP 2/4] WARN Search returned no URLs
[STEP 2/4] Attempting query reformulation...
  Enhanced query: WH-1000XM5 product review price
[STEP 2/4] OK Reformulated query found 5 URLs
```

**Expected Response:**
- Even with vague query, system finds results
- If reformulation happens, you'll see it in logs
- Response includes helpful product info

**What This Tests:**
✅ Query reformulation on failure
✅ Auto-enhancement with keywords
✅ Graceful recovery

---

### **Test 3: Partial Data Handling** ⚠️

**Goal:** Test handling when some URLs fail

**Query to Test:**
```
Sony WH-1000XM5 headphones price Amazon
```

**What to Watch in Terminal:**
```
[STEP 3/4] Fetching data from URLs...
  [1/5] Extracting product: https://www.amazon.com/...
  [1/5] OK Success (useful data)
  [2/5] Fetching content: https://www.reddit.com/...
  [2/5] OK Success (useful data)
  [3/5] Extracting product: https://www.amazon.com/...
  [3/5] WARN Success but no useful data
  [INFO] Collected 3 good sources, stopping early
[STEP 3/4] OK Fetched data from 3 sources
```

**Expected Response:**
- May show price from Reddit discussion
- Cites multiple sources (Amazon + community sites)
- Formatted response even with partial data
- Source URLs included

**What This Tests:**
✅ Content validation (filters low-quality data)
✅ Multiple source fallback
✅ Early stopping when enough data collected
✅ Graceful partial data handling

---

### **Test 4: Complete Failure with Helpful Error** ❌

**Goal:** Test user-friendly error messages

**Query to Test (non-existent product):**
```
XYZ-Nonexistent-Product-12345 price
```

**What to Watch in Terminal:**
```
[STEP 2/4] Searching web for URLs...
[STEP 2/4] OK Found 0-2 URLs (or search fails)

[STEP 3/4] Fetching data from URLs...
  [1/2] Fetching content: ...
  [1/2] X Failed: HTTP 404
  [2/2] Fetching content: ...
  [2/2] WARN Success but no useful data
[STEP 3/4] WARN No data fetched from any source
  Failed URLs (2):
    - https://... : HTTP 404
    - https://... : No useful data extracted
```

**Expected Response in Browser:**
```
I attempted to research 'XYZ-Nonexistent-Product-12345 price'
but wasn't able to retrieve complete data.

This could be because:
- The search didn't find relevant product pages
- Product pages were inaccessible or blocked

Here's what you can try:
- Be more specific (e.g., include brand name, model number)
- Try a different product or query
- Check if the product exists on major retailers like Amazon

I'm ready to help with a refined search when you're ready!
```

**What This Tests:**
✅ Helpful error messages
✅ Actionable suggestions
✅ Encouraging tone
✅ No crashes (graceful handling)

---

### **Test 5: Comparative Query (Multiple Products)** 📊

**Goal:** Test handling multiple products in one query

**Query to Test:**
```
Best wireless headphones under $200
```

**What to Watch in Terminal:**
```
[STEP 1/4] OK Classification complete
  Type: comparative
  Strategy: multi-source

[STEP 2/4] OK Found 5 URLs

[STEP 3/4] Fetching data from URLs...
  [1/5] Extracting product: ...
  [2/5] Extracting product: ...
  [3/5] Fetching content: ...
  [INFO] Collected 3 good sources, stopping early

[STEP 4/4] OK Formatting complete
```

**Expected Response:**
- List of multiple headphone options
- Prices for each
- Ratings and reviews
- Comparison of features
- Source URLs for each product

**What This Tests:**
✅ Comparative query classification
✅ Multiple product extraction
✅ Multi-source aggregation
✅ Comparative formatting

---

## 📊 Detailed Testing Checklist

Use this checklist while testing each query:

### For Each Test Query:

**In Terminal (Watch for):**
- [ ] Classification logs `[STEP 1/4]`
- [ ] Search logs `[STEP 2/4]` with URL count
- [ ] Extraction logs `[EXTRACT]` with price/rating
- [ ] Formatting logs `[STEP 4/4]`
- [ ] No crashes or exceptions

**In Browser (Check for):**
- [ ] Response appears (not empty)
- [ ] Product names shown
- [ ] Prices displayed
- [ ] Ratings/reviews included (if available)
- [ ] Source URLs cited
- [ ] Well-formatted markdown
- [ ] Helpful if data is missing

---

## 🎯 Key Features to Verify

### 1. Enhanced Product Extraction

**Test Query:** `Logitech MX Master 3S`

**Verify:**
- ✅ Product name extracted
- ✅ Price shown (regular and sale if applicable)
- ✅ Rating and review count
- ✅ Features list (5+ items)
- ✅ Images referenced
- ✅ Brand name

### 2. Error Handling

**Test Query:** `Nonexistent-Product-XYZ`

**Verify:**
- ✅ No crash or error page
- ✅ Helpful error message
- ✅ Specific suggestions provided
- ✅ Encouraging tone

### 3. Query Reformulation

**Test Query:** `WH-1000XM5` (vague)

**Verify:**
- ✅ System finds results anyway
- ✅ Terminal shows reformulation (if needed)
- ✅ Auto-adds context keywords

### 4. Multi-Source Fetching

**Test Query:** `Sony WH-1000XM5 price`

**Verify:**
- ✅ Tries 5 URLs (check terminal)
- ✅ Stops at 3 good sources
- ✅ Cites multiple sources
- ✅ Combines data intelligently

---

## 🔍 Advanced Testing

### Test Agent Communication

**Enable in Terminal:**
Watch for `[A2A]` prefixes to verify agents are called:

```
[A2A] Calling Query Classifier for: ...
[A2A] Query Classifier response received
[A2A] Classification complete: factual - quick-answer

[A2A] Calling Information Gatherer agent to format results...
[A2A] Information Gatherer response received
```

**Verify:**
- [ ] Query Classifier called
- [ ] Information Gatherer called
- [ ] Both agents respond
- [ ] Clean A2A communication

---

## 📸 Screenshot Opportunities

Take screenshots for your capstone demo:

1. **Successful Extraction:**
   - Query: `Logitech MX Master 3S`
   - Show: Price, rating, features, images

2. **Error Handling:**
   - Query: `Nonexistent-Product`
   - Show: Helpful error message

3. **Terminal Logs:**
   - Show: Pipeline execution with all 4 steps

4. **Multi-Source:**
   - Query: `Sony WH-1000XM5`
   - Show: Data from Amazon + Reddit

---

## 🎬 Demo Script (3-Minute Presentation)

### Minute 1: Introduction
**Say:** "ResearchMate AI is a multi-agent research assistant with enhanced product extraction."

**Show:** ADK UI interface
**Query:** `Logitech MX Master 3S wireless mouse`

### Minute 2: Show Features
**Point out in response:**
- Product name and price
- **Sale price vs. list price** (discount detection)
- Rating and review count
- Features extracted
- Multiple source URLs

**Show terminal:** Point out pipeline steps executing

### Minute 3: Error Handling
**Query:** `Nonexistent-Product-12345`

**Show:** Helpful error message with suggestions

**Conclude:** "The system never crashes and always provides helpful guidance."

---

## 🐛 Troubleshooting

### If ADK UI doesn't load:

**Check:**
1. Server is running (terminal shows "started")
2. Port 8000 is not already in use
3. Browser URL is exactly: `http://127.0.0.1:8000`

**Fix:**
```bash
# Stop any existing server (Ctrl+C)
# Restart fresh
venv\Scripts\adk.exe web adk_agents --port 8000 --reload
```

### If queries fail:

**Check terminal logs for:**
- `[SEARCH] Response status: 200` ✅ (good)
- `[SEARCH] Response status: 403` ❌ (API issue)

**If Google Search API fails:**
- Check `.env` has `GOOGLE_API_KEY` and `GOOGLE_SEARCH_ENGINE_ID`
- See `GOOGLE_SEARCH_API_TROUBLESHOOTING.md`

### If extraction fails:

**Check terminal for:**
- `[EXTRACT] Extraction complete - Price: $XX.XX` ✅ (good)
- `[EXTRACT] Extraction complete - Price: None` ⚠️ (Amazon blocked)

**Try:**
- Different product (like Logitech instead of Sony)
- More specific query with brand name

---

## ✅ Success Criteria

After testing all 5 queries, you should see:

- ✅ All 4 pipeline steps execute every time
- ✅ At least one query returns complete product data
- ✅ Error queries show helpful messages
- ✅ Terminal logs are clear and informative
- ✅ No crashes or exceptions
- ✅ Both agents (Classifier + Gatherer) are called

---

## 🎉 Ready to Demo!

**Best Queries for Live Demo:**

1. **"Logitech MX Master 3S wireless mouse"** - Shows complete extraction
2. **"Sony WH-1000XM5 headphones price"** - Shows multi-source
3. **"Best wireless keyboards under $100"** - Shows comparative
4. **"Nonexistent-Product-XYZ"** - Shows error handling

**Demo Flow:**
1. Start server
2. Open browser to ADK UI
3. Run Query #1 (show success)
4. Run Query #4 (show error handling)
5. Show terminal logs (pipeline execution)

**Highlight:**
- "All 4 steps execute every time (deterministic)"
- "Enhanced extraction gets price, rating, features"
- "Graceful error handling with helpful suggestions"
- "Production-ready multi-agent system"

---

**Happy Testing!** 🚀

All improvements from Day 1 are ready to showcase!
