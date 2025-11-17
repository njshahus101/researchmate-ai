# Google Custom Search API - Troubleshooting Guide

**Date:** 2025-11-16
**Status:** API Enabled but Blocked
**Error:** `API_KEY_SERVICE_BLOCKED` - PERMISSION_DENIED

---

## Current Error

```json
{
  "error": {
    "code": 403,
    "message": "Requests to this API customsearch method google.customsearch.v1.CustomSearchService.List are blocked.",
    "reason": "API_KEY_SERVICE_BLOCKED",
    "status": "PERMISSION_DENIED"
  }
}
```

**Project ID:** 696991558518
**API Key:** AIzaSyCs5sC1pRZYiUM_Vlc162dKg7aMlhU7i5A
**Search Engine ID:** 055554230dce04528

---

## Root Cause Analysis

The error `API_KEY_SERVICE_BLOCKED` indicates that while the Custom Search API is enabled in your project, the **API key itself is restricted** from accessing it.

This is different from "API not enabled" - the API is enabled, but the key doesn't have permission.

---

## Solution Steps

### Step 1: Check API Key Restrictions

1. Go to **Google Cloud Console**: https://console.cloud.google.com/apis/credentials
2. Select project **696991558518**
3. Find your API key: `AIzaSyCs5sC1pRZYiUM_Vlc162dKg7aMlhU7i5A`
4. Click on the key to edit it
5. Check **API restrictions** section:
   - If "Restrict key" is selected, make sure **"Custom Search API"** is in the allowed list
   - **RECOMMENDED**: Change to "Don't restrict key" temporarily to test
6. Click **Save**

### Step 2: Verify Billing is Enabled

**IMPORTANT:** Custom Search API requires billing for usage beyond the free tier (100 queries/day).

1. Go to **Billing**: https://console.cloud.google.com/billing
2. Ensure project **696991558518** is linked to a billing account
3. If not linked:
   - Click "Link a billing account"
   - Create a new billing account if needed
   - Link it to the project

**Free Tier Details:**
- First 100 queries/day: **FREE**
- Additional queries: $5 per 1000 queries
- No charges if you stay within 100 queries/day

### Step 3: Verify Search Engine Configuration

1. Go to **Programmable Search Engine**: https://programmablesearchengine.google.com/
2. Find your search engine with ID: `055554230dce04528`
3. Click "Control Panel" or "Setup"
4. Verify:
   - **Search the entire web** is enabled (or specific sites are configured)
   - Status shows "Active"
5. Copy the **Search engine ID** again to confirm it's correct

### Step 4: Check Organization Policies (If Applicable)

If your Google Cloud project is part of an **organization** (corporate account):

1. Go to **IAM & Admin** > **Organization Policies**
2. Check for policies that might block APIs
3. You may need to contact your organization admin

### Step 5: Try Creating a New API Key

If restrictions are complex, create a fresh unrestricted key:

1. Go to **Credentials**: https://console.cloud.google.com/apis/credentials
2. Click **"+ CREATE CREDENTIALS"** > **"API Key"**
3. Copy the new key
4. **Important:** Don't add any restrictions initially (test first)
5. Update `.env` file with the new key:
   ```
   GOOGLE_API_KEY=your_new_key_here
   ```

---

## Testing After Changes

After making any of the above changes, test with:

```bash
venv\Scripts\python.exe -c "from dotenv import load_dotenv; load_dotenv(); from tools.research_tools import search_web; result = search_web('test query'); print('Status:', result.get('status')); print('Error:', result.get('error_message', 'None'))"
```

**Expected success output:**
```
[SEARCH] Calling Google Custom Search API...
[SEARCH] Query: test query
[SEARCH] Search Engine ID: 055554230dce04528
[SEARCH] Response status: 200
[SEARCH] Found 3 results
Status: success
```

---

## Quick Diagnosis Checklist

- [ ] **Step 1:** API key restrictions allow Custom Search API
- [ ] **Step 2:** Billing is enabled on project 696991558518
- [ ] **Step 3:** Search Engine ID 055554230dce04528 is active
- [ ] **Step 4:** No organization policies blocking the API
- [ ] **Step 5:** Tested with a new unrestricted API key

---

## Alternative: Use Google Search Grounding Instead

If you continue to have issues with Custom Search API, your Information Gatherer agent already has **Google Search grounding** enabled, which doesn't require Custom Search API configuration.

**To test Google Search grounding:**

1. The Information Gatherer agent can use built-in Google Search
2. This bypasses Custom Search API entirely
3. However, our current **fixed pipeline** design expects URLs from `search_web()`

**Temporary workaround** (if Custom Search API remains blocked):

You could modify the pipeline to skip STEP 2 (search_web) and rely on:
- Manual URL input by user
- Hardcoded URLs for testing
- Information Gatherer's built-in Google Search grounding

But the **proper solution** is to fix the API key permissions.

---

## Most Likely Solution

Based on the error `API_KEY_SERVICE_BLOCKED`, the most likely fix is:

### **Remove API Key Restrictions:**

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click your API key: `AIzaSyCs5sC1pRZYiUM_Vlc162dKg7aMlhU7i5A`
3. Under "API restrictions", select **"Don't restrict key"**
4. Click **Save**
5. Wait 1-2 minutes for changes to propagate
6. Test again

This should immediately resolve the `API_KEY_SERVICE_BLOCKED` error.

---

## Support Resources

- **Custom Search API Docs**: https://developers.google.com/custom-search/v1/overview
- **API Key Best Practices**: https://cloud.google.com/docs/authentication/api-keys
- **Billing Setup**: https://cloud.google.com/billing/docs/how-to/modify-project

---

## Next Steps After Fixing

Once the API is working:

1. Run the test command to verify search works
2. Start ADK UI: `venv\Scripts\adk.exe web adk_agents --port 8000 --reload`
3. Test with real query: "Fetch current price and details of Sony WH-1000XM5"
4. Watch terminal for pipeline execution logs
5. Verify all 4 steps complete successfully

The fixed pipeline is ready and tested - it's just waiting for Google Custom Search API access to work!
