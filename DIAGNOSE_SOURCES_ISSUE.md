# Diagnosing Missing Sources Section

**Issue:** Citation numbers `[1], [2], [3]` appear in text, but no "### Sources" section with URLs

---

## Step-by-Step Diagnosis

### Step 1: Restart the ADK Server

The updated Report Generator code needs to be loaded. The `--reload` flag doesn't always pick up changes immediately.

**Action:**
```bash
# In your terminal where ADK is running:
# Press Ctrl+C to stop the server

# Then restart:
venv\Scripts\adk.exe web adk_agents --port 8000 --reload
```

**Look for this in terminal output:**
```
Loading Report Generator agent...
Report Generator Agent initialized:
  - Role: Transform analysis into actionable reports
  - Model: gemini-2.5-flash-lite
Report Generator agent 'report_generator' initialized (synthesis & reporting)
```

✅ If you see this, the updated agent is loaded!

---

### Step 2: Send a Test Query

**Test query:**
```
What are the best wireless headphones under $250?
```

---

### Step 3: Check Terminal Logs

Watch your terminal for these key indicators:

#### ✅ Success Indicators (Report Generator Working):

```
[STEP 6/6] Generating final report with Report Generator...
[A2A] Calling Report Generator agent...
[A2A] Report Generator response received
[STEP 6/6] OK Report generation complete
```

**If you see "OK Report generation complete"** → Report Generator ran successfully!

#### ⚠️ Failure Indicators (Falling Back):

```
[STEP 6/6] WARN Report generation failed: [error message]
[STEP 6/6] Falling back to Information Gatherer output
```

**If you see "WARN" and "Falling back"** → Report Generator failed, using Information Gatherer instead!

Common errors:
- `'charmap' codec can't encode character` → Emoji encoding issue (should be fixed now)
- Other errors → Check terminal for details

---

### Step 4: Inspect Browser Output

The output should have this structure at the end:

```markdown
...your product recommendations...

### Sources
[1] CNET Review - https://www.cnet.com/tech/mobile/best-wireless-headphones/
    Credibility: High | Professional tech review site

[2] Amazon - Headphone Listings - https://www.amazon.com/s?k=wireless+headphones
    Credibility: High | Official retailer with verified reviews

[3] TechRadar - Buying Guide - https://www.techradar.com/headphones/best-headphones
    Credibility: High | Established tech publication

**Follow-up Questions:**
- How do these models compare for specific music genres?
- What are the warranty policies for each brand?
```

#### ✅ Sources Section Present
- You'll see "### Sources" heading
- Each `[1], [2], [3]` has a corresponding URL entry
- URLs are clickable (https://...)
- Credibility indicators shown

#### ❌ Sources Section Missing
- Output ends after recommendations
- No "### Sources" heading
- Citation numbers `[1], [2]` in text but nowhere to click
- This means Information Gatherer output (fallback)

---

### Step 5: Common Scenarios

#### Scenario A: Sources Missing, Terminal Shows "OK"

**Diagnosis:** Report Generator ran but didn't include Sources in output

**Possible Causes:**
1. Old agent code still loaded (need to restart server)
2. LLM ignoring instructions (rare with our strong emphasis)

**Solution:**
1. Confirm server restart (Step 1)
2. Check timestamp of agent.py file modified
3. Try clearing browser cache

#### Scenario B: Sources Missing, Terminal Shows "WARN"

**Diagnosis:** Report Generator failed, fallback to Information Gatherer

**Possible Causes:**
1. Encoding error (should be fixed - emoji removed)
2. Other runtime error

**Solution:**
1. Read the error message in terminal
2. If encoding error persists, check for other emoji/special chars
3. Check agent.py for syntax errors

#### Scenario C: Report Generator Not Called At All

**Diagnosis:** STEP 6 never executes

**Possible Causes:**
1. Earlier step failed (STEP 1-5)
2. Orchestrator not updated

**Solution:**
1. Check if you see all 6 steps in terminal
2. Verify orchestrator imports report_generator_agent

---

## Quick Debug Commands

### Check if updated agent file is being used:

```bash
# Check modification time of agent.py
dir adk_agents\report_generator\agent.py

# Should show today's date/time
```

### Check if server is using updated code:

```bash
# Search for "CRITICAL REQUIREMENT" in loaded agent
# This text was added in the fix
python -c "from adk_agents.report_generator.agent import agent; print('CRITICAL REQUIREMENT' in agent.instruction)"

# Should print: True
```

If it prints `False`, the updated code isn't loaded yet. Restart server!

---

## Expected vs Actual Comparison

### Expected Output (Report Generator):

```markdown
Top Recommendation: Sony WH-1000XM5

The Sony WH-1000XM5 offers excellent value at $248 with industry-leading
noise cancellation and 30-hour battery life [1].

### Sources                                          ← THIS SECTION!
[1] Amazon - Sony WH-1000XM5 - https://amazon.com/... ← ACTUAL URL!
    Credibility: High | Official retailer

**Follow-up Questions:**
- How does this compare to Bose?
```

### Actual Output (Information Gatherer - Fallback):

```markdown
Top Recommendation: Sony WH-1000XM5

The Sony WH-1000XM5 offers excellent value at $248 with industry-leading
noise cancellation and 30-hour battery life [1].

[END - No Sources section]                          ← MISSING!
```

---

## Checklist for Resolution

Complete these steps in order:

- [ ] **Step 1:** Stop ADK server (Ctrl+C in terminal)
- [ ] **Step 2:** Verify agent.py was modified (check file date)
- [ ] **Step 3:** Restart server: `venv\Scripts\adk.exe web adk_agents --port 8000 --reload`
- [ ] **Step 4:** Confirm "Report Generator agent initialized" in terminal
- [ ] **Step 5:** Send test query in browser
- [ ] **Step 6:** Watch terminal for STEP 6 logs
- [ ] **Step 7:** Check if terminal says "OK" or "WARN"
- [ ] **Step 8:** Inspect browser output for "### Sources" section

**If Sources still missing after completing all steps:**
- Copy the terminal logs around STEP 6
- Copy the full browser output
- This will help identify the exact issue

---

## Summary

**Root Issue:** Report Generator creates Sources section, but you're seeing Information Gatherer output (fallback)

**Most Likely Cause:** Server hasn't reloaded the updated agent code

**Solution:** Restart the server (Ctrl+C, then re-run adk command)

**How to Verify:** Terminal logs will show "OK" vs "WARN" for STEP 6

**Expected Result:** Browser output includes "### Sources" with clickable URLs

---

## Next Steps

1. **Stop your server** (Ctrl+C)
2. **Restart it** (run adk command again)
3. **Send the same query** again
4. **Check terminal** for "OK" or "WARN" at STEP 6
5. **Report back** what you see!

If Sources still don't appear after server restart, send me:
- Terminal logs for STEP 6
- First/last 50 lines of browser output

We'll get this working! 🎯
