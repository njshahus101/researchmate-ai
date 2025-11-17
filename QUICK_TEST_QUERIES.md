# Quick Test Queries - Copy & Paste

Use these queries to quickly test all Day 1 improvements.

---

## ✅ Test 1: Full Product Extraction (BEST SUCCESS RATE)

```
Logitech MX Master 3S wireless mouse price and reviews
```

**Expect:** Price, rating, features, images, discount detection

---

## 🔄 Test 2: Query Reformulation

```
WH-1000XM5
```

**Expect:** System finds results with vague query, may reformulate

---

## ⚠️ Test 3: Partial Data (Multi-Source)

```
Sony WH-1000XM5 headphones price Amazon
```

**Expect:** Data from Amazon + Reddit, partial but helpful

---

## ❌ Test 4: Helpful Error Message

```
Nonexistent-Product-XYZ-12345 price
```

**Expect:** Friendly error with suggestions, no crash

---

## 📊 Test 5: Comparative Query

```
Best wireless headphones under $200
```

**Expect:** Multiple products, comparison, ratings

---

## 🎯 Bonus: Sale Price Detection

```
Apple AirPods Pro 2nd generation price
```

**Expect:** Regular price vs sale price, discount shown

---

## 🖱️ Bonus: Specific Model

```
MacBook Air M3 13 inch specs and price
```

**Expect:** Technical specifications, pricing from multiple sources

---

## 🎧 Bonus: Brand Search

```
Sony WH-1000XM5 vs Bose QuietComfort Ultra
```

**Expect:** Comparison between two products

---

# Terminal Commands

## Start Server:
```bash
venv\Scripts\adk.exe web adk_agents --port 8000 --reload
```

## Test in Python:
```bash
venv\Scripts\python.exe test_complete_pipeline.py
```

## Test Product Extraction:
```bash
venv\Scripts\python.exe test_product_extraction.py
```

---

# What to Watch in Terminal

Look for these indicators:

✅ **Success:**
```
[STEP 1/4] OK Classification complete
[STEP 2/4] OK Found 5 URLs
[STEP 3/4] OK Fetched data from 3 sources
[STEP 4/4] OK Formatting complete
[EXTRACT] Extraction complete - Price: $109.99, Rating: 4.5
```

⚠️ **Partial:**
```
[STEP 3/4] OK Fetched data from 1 sources
[EXTRACT] Extraction complete - Price: None, Rating: None
(Still formats helpful response)
```

🔄 **Retry:**
```
[STEP 2/4] WARN Search returned no URLs
[STEP 2/4] Attempting query reformulation...
[STEP 2/4] OK Reformulated query found 5 URLs
```

❌ **Error Handling:**
```
[STEP 3/4] WARN No data fetched from any source
(Returns helpful error message)
```

---

# Quick Demo Script

**1. Open terminal, start server**
**2. Open browser: http://127.0.0.1:8000**
**3. Test Query 1** (Logitech) - show success
**4. Test Query 4** (Nonexistent) - show error handling
**5. Show terminal** - point out pipeline execution

**Done in 2 minutes!** ✅
