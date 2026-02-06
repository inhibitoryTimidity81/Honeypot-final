# Local Testing Guide for Honeypot API

## Quick Start

### 1. Start the Server

Open a PowerShell terminal and run:

```powershell
cd c:\Users\akash\OneDrive\Desktop\Honey-pot\honeypot-agent
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
🚀 Honeypot Agent API Starting...
✅ Ready to engage scammers!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Test Health Check

In a **new** PowerShell terminal:

```powershell
curl http://localhost:8000/
```

Expected output:
```json
{
  "status": "running",
  "service": "Honeypot Agent API",
  "version": "2.0.0",
  "endpoints": {
    "chat": "/api/v1/chat",
    "health": "/api/v1/health"
  }
}
```

### 3. Test Chat Endpoint

#### Option A: Using the test script (Recommended)

```powershell
cd c:\Users\akash\OneDrive\Desktop\Honey-pot\honeypot-agent
.\venv\Scripts\python.exe test_chat.py
```

#### Option B: Using PowerShell directly

```powershell
$headers = @{
    'Content-Type' = 'application/json'
    'x-api-key' = 'team-synapse-password-123'
}

$body = @{
    sessionId = "test-session-001"
    message = @{
        text = "Hello sir, your bank account has been blocked. Please share your account number to verify."
        sender = "scammer"
    }
    conversationHistory = @()
    metadata = @{
        channel = "SMS"
        language = "English"
        locale = "IN"
    }
} | ConvertTo-Json -Depth 10

$response = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/chat' -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

#### Option C: Using the JSON file

```powershell
$headers = @{ 'Content-Type' = 'application/json'; 'x-api-key' = 'team-synapse-password-123' }
$body = Get-Content test_request.json -Raw
$response = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/chat' -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

## Expected Response

You should see a response like:

```json
{
  "status": "success",
  "scamDetected": true,
  "reply": "Kya? Account blocked? But I didn't do anything...",
  "engagementMetrics": {
    "engagementDurationSeconds": 0,
    "totalMessagesExchanged": 2
  },
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": [],
    "phishingLinks": [],
    "phoneNumbers": [],
    "suspiciousKeywords": ["blocked", "verify", "account"]
  },
  "agentNotes": "Scammer using urgency tactics..."
}
```

---

## Multi-Turn Conversation Test

To test a full conversation with intelligence extraction:

```powershell
.\venv\Scripts\python.exe test_multi_turn.py
```

This will:
1. Send 5 messages in sequence
2. Include UPI IDs, phone numbers, and bank accounts
3. Show accumulated intelligence
4. Trigger the final callback

---

## Server Logs

Watch the server terminal for detailed logs:

```
============================================================
[🔴 SCAMMER]: Hello sir, your bank account has been blocked...
Session: test-session-001 | Message #1
[🟢 RAM LAL]: Kya? Account blocked? But I didn't do anything...
[🔍 INTEL]: 0 items | Scam: True
============================================================
```

---

## Testing Intelligence Extraction

Send messages with specific patterns:

### UPI ID Test
```powershell
$body = @{
    sessionId = "test-upi"
    message = @{
        text = "Please send money to scammer@paytm immediately"
        sender = "scammer"
    }
    conversationHistory = @()
} | ConvertTo-Json -Depth 10
```

### Phone Number Test
```powershell
$body = @{
    sessionId = "test-phone"
    message = @{
        text = "Call me at +91 9876543210 for verification"
        sender = "scammer"
    }
    conversationHistory = @()
} | ConvertTo-Json -Depth 10
```

### Bank Account Test
```powershell
$body = @{
    sessionId = "test-bank"
    message = @{
        text = "Transfer to account 123456789012"
        sender = "scammer"
    }
    conversationHistory = @()
} | ConvertTo-Json -Depth 10
```

---

## Testing Final Callback

The final callback is sent to: `https://webhook.site/32301b92-c042-4250-901e-07888d97498d`

To see callbacks:
1. Visit https://webhook.site/32301b92-c042-4250-901e-07888d97498d
2. Run the multi-turn test
3. Check webhook.site for the POST request

The callback triggers when:
- Scam is detected AND
- (3+ intelligence items extracted OR 5+ messages exchanged)

---

## Error Testing

### Invalid API Key
```powershell
$headers = @{ 'Content-Type' = 'application/json'; 'x-api-key' = 'wrong-key' }
# Should return 401 Unauthorized
```

### Missing Required Fields
```powershell
$body = @{ sessionId = "test" } | ConvertTo-Json
# Should return 422 Validation Error
```

---

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use: `netstat -ano | findstr :8000`
- Kill the process: `taskkill /PID <pid> /F`
- Try a different port: `--port 8001`

### No response from API
- Verify server is running: `curl http://localhost:8000/`
- Check firewall settings
- Ensure you're using the correct API key

### Gemini API errors
- Check your API key in `.env`
- Verify you have quota remaining
- Check internet connection

### Import errors
- Make sure you're using the venv: `.\venv\Scripts\python.exe`
- Install dependencies: `.\venv\Scripts\pip.exe install -r requirements.txt`

---

## Quick Test Commands

```powershell
# 1. Start server (Terminal 1)
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 2. Health check (Terminal 2)
curl http://localhost:8000/

# 3. Single message test
.\venv\Scripts\python.exe test_chat.py

# 4. Multi-turn conversation
.\venv\Scripts\python.exe test_multi_turn.py

# 5. Check webhook for callbacks
# Visit: https://webhook.site/32301b92-c042-4250-901e-07888d97498d
```

---

## Next Steps

Once local testing is successful:
1. Deploy to a cloud platform (Railway, Render, Heroku)
2. Update `GUVI_CALLBACK_URL` to the actual evaluation endpoint
3. Submit your deployment URL to the hackathon
