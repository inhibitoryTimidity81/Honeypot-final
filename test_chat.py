"""
Simple Chat Test - Tests a single message to the Honeypot API
"""

import requests
import json

# Configuration
API_URL = "http://localhost:8000/api/v1/chat"
API_KEY = "team-synapse-password-123"

# Test request
payload = {
    "sessionId": "test-session-001",
    "message": {
        "text": "Hello sir, your bank account has been blocked. Please share your account number to verify.",
        "sender": "scammer"
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

print("="*70)
print("HONEYPOT API - SINGLE MESSAGE TEST")
print("="*70)
print(f"\n[📤 SENDING]: {payload['message']['text']}\n")

try:
    response = requests.post(
        API_URL,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print("✅ SUCCESS!")
        print("="*70)
        print(f"\n[🟢 RAM LAL REPLIED]: {data['reply']}\n")
        print(f"[🔍 SCAM DETECTED]: {data['scamDetected']}")
        print(f"[📊 MESSAGES]: {data['engagementMetrics']['totalMessagesExchanged']}")
        print(f"[⏱️  DURATION]: {data['engagementMetrics']['engagementDurationSeconds']}s")
        
        intel = data['extractedIntelligence']
        print(f"\n[🎯 INTELLIGENCE EXTRACTED]:")
        print(f"   Bank Accounts: {len(intel['bankAccounts'])} - {intel['bankAccounts']}")
        print(f"   UPI IDs: {len(intel['upiIds'])} - {intel['upiIds']}")
        print(f"   Phone Numbers: {len(intel['phoneNumbers'])} - {intel['phoneNumbers']}")
        print(f"   Phishing Links: {len(intel['phishingLinks'])} - {intel['phishingLinks']}")
        print(f"   Keywords: {intel['suspiciousKeywords']}")
        
        print(f"\n[📝 AGENT NOTES]: {data['agentNotes']}")
        
        print("\n" + "="*70)
        print("FULL RESPONSE:")
        print("="*70)
        print(json.dumps(data, indent=2))
        
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ CONNECTION ERROR!")
    print("\nIs the server running?")
    print("Start it with:")
    print("  .\\venv\\Scripts\\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
