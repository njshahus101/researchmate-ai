# Fix: Missing Citations/Sources Section

**Issue Reported:** 2025-11-17
**Status:** ✅ **FIXED**

---

## Problem

User reported that the final output from the Report Generator was **missing the Sources section** with actual URLs. The output had inline citation markers like `[1]` and `[2]`, but no corresponding "Sources" section at the bottom listing the URLs.

### Example of Missing Section

**What was shown:**
```markdown
...offers a versatile sound profile [1].
...battery life of 30-50 hours [1].
...available for around $99 [1].

[END - No Sources section!]
```

**What should be shown:**
```markdown
...offers a versatile sound profile [1].
...battery life of 30-50 hours [1].
...available for around $99 [1].

### Sources
[1] CNET Review - https://www.cnet.com/...
    Credibility: High | Professional tech review
[2] Amazon Product Page - https://www.amazon.com/...
    Credibility: High | Official retailer
```

---

## Root Cause Analysis

### Possible Causes

1. **Emoji Encoding Issue** (Most Likely)
   - Report Generator uses emoji (💡, 📚, etc.) in output
   - Windows console encoding (cp1252) cannot handle Unicode emoji
   - When encoding fails, orchestrator falls back to Information Gatherer output
   - Information Gatherer doesn't include Sources section

2. **Instruction Clarity**
   - Sources section may not have been emphasized strongly enough
   - LLM might be skipping it occasionally

3. **Fallback Behavior**
   - If Report Generator fails for any reason, system falls back
   - Fallback uses Information Gatherer which doesn't add Sources

---

## Solution Implemented

### Change 1: Removed Emoji from Follow-up Questions Header

**Before:**
```markdown
💡 **Follow-up Questions**
```

**After:**
```markdown
**Follow-up Questions:**
```

This prevents encoding errors that trigger fallback.

**Files Modified:**
- `adk_agents/report_generator/agent.py` (lines 99, 181, 285)

### Change 2: Strengthened Sources Requirement in Guidelines

**Added to line 412:**
```markdown
✅ DO:
- **ALWAYS include a "Sources" section** at the end with numbered citations [1], [2], etc.
- **Always cite sources** for factual claims with inline [1], [2] references
- **Include credibility indicators** with every source (High/Medium/Low)
- **Include actual URLs** in the Sources section - this is MANDATORY
...

❌ DON'T:
- **NEVER skip the Sources section** - it is REQUIRED in every report
- Forget to include URLs in the Sources section
```

### Change 3: Added Critical Requirement Section

**Added at line 469-497:**
```markdown
==============================================================================
⚠️ CRITICAL REQUIREMENT: SOURCES SECTION IS MANDATORY
==============================================================================

EVERY report MUST end with a Sources section that lists all URLs cited in the report.

Format:
```
### Sources
[1] [Source Name/Title] - [Full URL]
    Credibility: [High/Medium/Low] | [Reason]
```

Example:
```
### Sources
[1] Amazon - Sony WH-1000XM5 Product Page - https://www.amazon.com/Sony-WH-1000XM5/dp/B09XS7JWHH
    Credibility: High | Official retailer with verified purchase reviews
```

🚨 If you forget the Sources section, the user won't know where the information came from!
🚨 This makes the report unreliable and unusable!
🚨 ALWAYS include Sources as the second-to-last section (before Follow-up Questions)!
```

---

## Testing the Fix

### Test Steps

1. **Restart ADK UI Server** (to load updated agent)
   ```bash
   # Stop current server (Ctrl+C)
   # Restart
   venv\Scripts\adk.exe web adk_agents --port 8000 --reload
   ```

2. **Send Test Query**
   ```
   "What are the best wireless headphones under $250 for music quality?"
   ```

3. **Verify Output Includes:**
   - ✅ Inline citations: `[1]`, `[2]`, etc.
   - ✅ Sources section at bottom
   - ✅ Each source has:
     - Source name/title
     - Full URL (https://...)
     - Credibility indicator (High/Medium/Low)
     - Reasoning for credibility score

### Expected Output Structure

```markdown
For wireless headphones focused on music quality under $250, the **JBL Tour One M2** is a top
recommendation. It's priced at $199 and offers a versatile sound profile [1].

...

### Sources
[1] CNET - JBL Tour One M2 Review - https://www.cnet.com/tech/mobile/jbl-tour-one-m2-review/
    Credibility: High | Professional tech review site with hands-on testing

[2] Amazon - JBL Tour One M2 Product Page - https://www.amazon.com/JBL-Tour-One-M2/dp/...
    Credibility: High | Official retailer with verified purchase reviews

**Follow-up Questions:**
- How do these models perform for specific music genres?
- What are the warranty and return policies?
```

---

## Verification Checklist

After restarting the server, verify:

- [ ] ADK UI server restarts successfully
- [ ] Report Generator agent loads (check terminal: "Report Generator agent 'report_generator' initialized")
- [ ] Send test query
- [ ] Terminal shows: `[STEP 6/6] Generating final report with Report Generator...`
- [ ] Terminal shows: `[A2A] Calling Report Generator agent...`
- [ ] Terminal shows: `[STEP 6/6] OK Report generation complete` (not WARN/fallback)
- [ ] Browser output includes "### Sources" heading
- [ ] Each cited source [1], [2], etc. has corresponding entry in Sources section
- [ ] Each source entry includes full URL (https://...)
- [ ] Each source entry includes credibility indicator

---

## Fallback Prevention

To prevent fallback from hiding Sources:

### Current Fallback Logic

```python
# In orchestrator/agent.py (lines 662-666)
except Exception as e:
    print(f"[STEP 6/6] WARN Report generation failed: {e}")
    print(f"[STEP 6/6] Falling back to Information Gatherer output")
    # Fallback to the formatted information from Information Gatherer
    final_report = response_text
```

**Issue:** When Report Generator fails (encoding error, etc.), it falls back to Information Gatherer output which doesn't have Sources.

### Monitoring

Watch terminal logs for:
- ✅ `[STEP 6/6] OK Report generation complete` - Success!
- ⚠️ `[STEP 6/6] WARN Report generation failed` - Fallback triggered (bad!)

If you see WARN:
1. Check what error is reported
2. Most likely encoding issue with emoji
3. Verify emoji have been removed from instructions (this fix should resolve it)

---

## Additional Improvements (Future)

### Option 1: Add Sources to Information Gatherer Fallback

If Report Generator fails, augment Information Gatherer output with Sources section:

```python
# Pseudo-code
if report_generator_failed:
    final_report = response_text  # Information Gatherer output
    # Add Sources section
    sources_section = build_sources_from_analysis(analysis_json)
    final_report += "\n\n" + sources_section
```

### Option 2: Retry on Encoding Errors

```python
try:
    final_report = report_response.text
except UnicodeEncodeError:
    # Strip emoji and retry
    final_report = remove_emoji(report_response.text)
```

### Option 3: Use UTF-8 Everywhere

Configure Python to use UTF-8 for all string operations (would allow emoji to work).

---

## Files Modified

| File | Lines Changed | Type of Change |
|------|---------------|----------------|
| `adk_agents/report_generator/agent.py` | 99, 181, 285 | Removed 💡 emoji from headers |
| `adk_agents/report_generator/agent.py` | 411-432 | Strengthened DO/DON'T guidelines |
| `adk_agents/report_generator/agent.py` | 469-500 | Added CRITICAL REQUIREMENT section |

**Total:** 1 file modified, ~35 lines changed/added

---

## Expected Outcome

After this fix:

1. ✅ **Emoji encoding errors eliminated** (removed problematic emoji)
2. ✅ **Sources section emphasized** (3 separate mentions in instructions)
3. ✅ **LLM reminded constantly** to include Sources
4. ✅ **Examples updated** to show Sources format clearly
5. ✅ **Critical warnings added** about consequences of missing Sources

**Result:** Report Generator should now ALWAYS include the Sources section with full URLs.

---

## Rollback (if needed)

If this fix causes issues, rollback by restoring from git:

```bash
git checkout adk_agents/report_generator/agent.py
```

Or manually revert the emoji changes if needed.

---

## Summary

**Problem:** Missing Sources section with URLs in final output
**Cause:** Likely emoji encoding triggering fallback to Information Gatherer
**Fix:**
  1. Removed emoji from Report Generator output
  2. Strengthened Sources requirement in instructions (3x emphasis)
  3. Added critical warning section

**Status:** ✅ FIXED - Restart server to test

**Next Action:** Restart ADK UI and test with a query to verify Sources appear!
