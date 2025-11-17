# SerpApi Setup Guide - Quick Start

## Get Your Free API Key (2 minutes)

### Step 1: Sign Up

1. Go to: **https://serpapi.com/users/sign_up**
2. Enter your email
3. Choose password
4. Click "Sign Up" (no credit card required!)

### Step 2: Get API Key

1. After signup, you'll see your **Dashboard**
2. Your **API Key** is displayed prominently
3. Click "Copy" to copy your API key

Example API key format:
```
abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

### Step 3: Set Environment Variable

**Windows (Command Prompt)**:
```cmd
set SERPAPI_KEY=your_actual_api_key_here
```

**Windows (PowerShell)**:
```powershell
$env:SERPAPI_KEY="your_actual_api_key_here"
```

**Windows (Permanent - Recommended)**:
1. Press `Win + R`
2. Type `sysdm.cpl` and press Enter
3. Click "Advanced" tab → "Environment Variables"
4. Under "User variables", click "New"
5. Variable name: `SERPAPI_KEY`
6. Variable value: Paste your API key
7. Click OK → OK → OK

**Linux/Mac**:
```bash
export SERPAPI_KEY=your_actual_api_key_here

# Make it permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export SERPAPI_KEY=your_actual_api_key_here' >> ~/.bashrc
source ~/.bashrc
```

### Step 4: Verify Setup

Run the test:
```bash
python test_google_shopping.py
```

You should see:
```
Found 5 results:

[1] Sony WH-1000XM5 Wireless Industry Leading Noise Canceling...
    Price: $299.99
    Seller: Amazon.com
    ...
```

---

## Free Tier Details

✅ **100 searches per month** (free forever)
✅ **No credit card required**
✅ **No expiration**
✅ **Resets monthly**

---

## Check Your Usage

Visit: **https://serpapi.com/dashboard**

You'll see:
- Searches this month: X / 100
- Searches remaining: X
- Next reset date

---

## Troubleshooting

### "SERPAPI_KEY not configured"

The environment variable isn't set. Re-do Step 3.

**Quick test (Windows)**:
```cmd
echo %SERPAPI_KEY%
```

**Quick test (Linux/Mac)**:
```bash
echo $SERPAPI_KEY
```

Should print your API key. If blank, it's not set.

### "Invalid SERPAPI_KEY"

1. Double-check you copied the full key (no spaces)
2. Regenerate key at https://serpapi.com/dashboard
3. Make sure you're using the correct environment variable name: `SERPAPI_KEY` (not `SERP_API_KEY` or `SERPAPI`)

### Restart Required

After setting environment variables **permanently** (Windows System Properties), you may need to:
1. Close all Command Prompts / PowerShell windows
2. Close VSCode / IDE
3. Reopen them

The new variable won't be available in already-open terminals.

---

## That's It!

You now have:
✅ Free SerpApi account
✅ API key configured
✅ 100 Google Shopping searches per month
✅ Ready to use with ResearchMate AI

**Next**: Run `python test_google_shopping.py` to see it in action!
