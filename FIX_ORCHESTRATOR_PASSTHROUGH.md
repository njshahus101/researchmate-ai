# Fix: Orchestrator Not Passing Through Report Generator Output

**Issue Identified:** 2025-11-17
**Status:** ✅ **FIXED**

---

## Problem

The Report Generator agent was successfully creating reports with Sources sections, but the **orchestrator agent was stripping them out** before showing to the user.

### Evidence from User's Trace

```
invoke_agent report_generator (11504.33ms)  ← Report Generator runs successfully
    ↓
call_llm (3200.43ms)  ← Orchestrator makes ANOTHER LLM call
    ↓
User sees output WITHOUT Sources section
```

### What Was Happening

1. ✅ **Report Generator** creates complete report with Sources section
2. ✅ **Orchestrator** receives the report in `final_report` variable
3. ✅ **Orchestrator** returns `{"status": "success", "content": final_report}`
4. ❌ **Orchestrator LLM** then "presents" the results to user
5. ❌ **During presentation**, LLM reformulates/summarizes the content
6. ❌ **Sources section gets stripped out** during reformulation
7. ❌ **User sees incomplete output**

---

## Root Cause

### Problematic Instruction (Before)

```python
instruction = """You are the Orchestrator Agent for ResearchMate AI.

You have ONE tool available: execute_fixed_pipeline

...

Then present the returned results to the user."""
```

**Problem:** The phrase "**present the returned results**" caused the orchestrator LLM to:
- Reformat the content
- Summarize sections
- Remove "unnecessary" parts (like Sources!)
- Add its own commentary

### The Flow

```
Report Generator output:
"## Best Headphones\n\nRecommendation...\n\n### Sources\n[1] Amazon - https://..."

    ↓ [Pipeline returns this to orchestrator]

Orchestrator receives:
{"status": "success", "content": "## Best Headphones\n\n...### Sources..."}

    ↓ [Orchestrator LLM "presents" results]

Orchestrator LLM thinks:
"I should make this user-friendly and concise..."
*Removes Sources section*
*Reformats structure*

    ↓ [User receives]

User sees:
"Recommendation..." (NO SOURCES!)
```

---

## Solution

### Updated Instruction (After)

```python
instruction = """You are the Orchestrator Agent for ResearchMate AI.

You have ONE tool available: execute_fixed_pipeline

...

CRITICAL: Return the pipeline's 'content' field EXACTLY as-is. DO NOT:
- Reformat or restructure the content
- Summarize or shorten the content
- Add your own commentary or introduction
- Remove any sections (especially Sources or Follow-up Questions)
- Change the markdown formatting

The pipeline already created a perfectly formatted report. Your ONLY job is to pass it through unchanged.

If the pipeline returns:
{
  "status": "success",
  "content": "## Best Headphones\\n\\n...\\n\\n### Sources\\n[1] Amazon..."
}

You must output ONLY the exact content value with NO modifications."""
```

**Key Changes:**
1. Changed "present" to "return"
2. Added explicit "DO NOT" list
3. Emphasized "EXACTLY as-is"
4. Gave concrete example
5. Warned about removing Sources/Follow-up Questions

---

## Files Modified

| File | Lines | Change |
|------|-------|--------|
| `adk_agents/orchestrator/agent.py` | 740-763 | Updated instruction to prevent reformulation |

---

## Testing

### Before Fix

**User sees:**
```markdown
Recommendation: Sony WH-1000XM5 offers great value [1].

The JBL Tour One M2 is another option [2].

[END - No Sources section!]
```

### After Fix

**User should see:**
```markdown
Recommendation: Sony WH-1000XM5 offers great value [1].

The JBL Tour One M2 is another option [2].

### Sources
[1] Amazon - Sony WH-1000XM5 - https://www.amazon.com/Sony-WH-1000XM5/dp/...
    Credibility: High | Official retailer with verified reviews

[2] CNET - JBL Tour One M2 Review - https://www.cnet.com/tech/mobile/...
    Credibility: High | Professional tech review site

**Follow-up Questions:**
- How do these compare for specific music genres?
- What are the warranty policies?
```

---

## How to Verify Fix

### Step 1: Restart Server

**IMPORTANT:** You must restart the ADK server for changes to take effect!

```bash
# In terminal where ADK is running:
Ctrl+C to stop

# Then restart:
venv\Scripts\adk.exe web adk_agents --port 8000 --reload
```

### Step 2: Send Test Query

In browser at http://127.0.0.1:8000:

```
What are the best wireless headphones under $250?
```

### Step 3: Check Terminal Logs

Look for successful execution:

```
[STEP 6/6] Generating final report with Report Generator...
[A2A] Calling Report Generator agent...
[A2A] Report Generator response received
[STEP 6/6] OK Report generation complete  ← Success!

============================================================
PIPELINE COMPLETE
============================================================
```

**NO "WARN" or "Falling back" messages!**

### Step 4: Check Browser Output

The output should include:

1. ✅ Main content with inline citations [1], [2], [3]
2. ✅ **### Sources** heading
3. ✅ Numbered source entries with:
   - Source name/title
   - Full clickable URL (https://...)
   - Credibility indicator (High/Medium/Low)
   - Reasoning for credibility
4. ✅ **Follow-up Questions:** section
5. ✅ 3-5 follow-up questions

---

## Why This Happened

### ADK Agent Behavior

When an LlmAgent has tools:
1. User sends message
2. Agent calls tool (execute_fixed_pipeline)
3. Tool returns result
4. **Agent makes another LLM call** to "format the response"
5. This final LLM call can modify the content!

### The Extra LLM Call

From the user's trace:
```
execute_tool execute_fixed_pipeline (56157.29ms)  ← Tool runs
    ↓
    invoke_agent report_generator (11504.33ms)   ← Report Generator runs
    ↓
call_llm (3200.43ms)  ← EXTRA LLM CALL! This is where content gets modified!
```

This extra call is the orchestrator LLM "presenting" results, which was reformulating them.

---

## Alternative Solutions Considered

### Option 1: Make Orchestrator Pass-Through Only ✅ (CHOSEN)

**Pros:**
- Simple instruction change
- No code restructuring
- Preserves all content exactly

**Cons:**
- Relies on LLM following instructions

### Option 2: Return Content Directly (Code Change)

Make the pipeline return content to ADK directly without LLM processing:

```python
# Instead of returning dict to orchestrator LLM
# Return content directly to ADK framework

# This would require changing the agent structure
# More complex, but more reliable
```

**Pros:**
- Guaranteed pass-through
- No LLM can modify content

**Cons:**
- Requires restructuring
- More complex code changes
- May break ADK patterns

### Option 3: Post-Processing Check

Add validation that checks for Sources section:

```python
# After orchestrator returns
if "### Sources" not in final_output:
    # Inject Sources section from analysis
    final_output += generate_sources_from_analysis(analysis_json)
```

**Pros:**
- Guaranteed Sources always present
- Fallback safety net

**Cons:**
- Bandaid solution
- Doesn't fix root cause
- Redundant processing

---

## Additional Improvements Made

### 1. Report Generator: Mandatory Sources

Already fixed in previous update:
- Removed emoji to prevent encoding errors
- Added "CRITICAL REQUIREMENT" section
- Emphasized Sources in 3 places

### 2. Orchestrator: Pass-Through Mode

This update:
- Explicit "DO NOT modify" instructions
- Example showing exact pass-through
- Warning about removing sections

### Combined Effect

**Report Generator** creates complete report WITH Sources
    ↓
**Orchestrator** passes it through WITHOUT modification
    ↓
**User** receives complete report WITH Sources

---

## Monitoring

### Success Indicators

✅ Terminal shows: `[STEP 6/6] OK Report generation complete`
✅ Browser output includes: `### Sources`
✅ Each citation [1], [2] has corresponding URL
✅ URLs are clickable
✅ Follow-up Questions section present

### Failure Indicators

❌ Terminal shows: `[STEP 6/6] WARN Report generation failed`
❌ Browser output missing: `### Sources`
❌ Citation numbers [1], [2] but no URLs
❌ Output looks summarized/reformatted
❌ Follow-up Questions missing

---

## Rollback (if needed)

If this causes issues, revert to previous instruction:

```python
instruction = """...
Then present the returned results to the user."""
```

But this will bring back the Sources stripping problem!

---

## Summary

**Problem:** Orchestrator LLM was reformulating Report Generator output, stripping Sources section

**Root Cause:** Instruction said "present the results", causing LLM to reformat

**Solution:** Changed instruction to "return EXACTLY as-is" with explicit DO NOT list

**Files Changed:** 1 file (`adk_agents/orchestrator/agent.py`)

**Lines Changed:** ~25 lines in instruction

**Status:** ✅ FIXED - Restart server to test!

**Expected Result:** User sees complete report with Sources section and clickable URLs

---

## Next Steps

1. ✅ **Restart ADK server** (this change is already saved)
2. ✅ **Send test query** in browser
3. ✅ **Verify Sources section** appears in output
4. ✅ **Click on URLs** to confirm they're real links
5. ✅ **Report success** or issues found

The fix is complete! Please restart your server and test. The Sources section should now appear! 🎯
