"""
Multi-Turn Conversation Test
Tests a complete scam conversation with intelligence extraction and final callback
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:8000/api/v1/chat"
API_KEY = "team-synapse-password-123"
SESSION_ID = f"test-multi-{int(time.time())}"

# Conversation script
conversation = [
    "Hello sir, your bank account has been blocked due to suspicious activity.",
    "You need to verify your account immediately or it will be permanently closed.",
    "Please share your account number for verification.",
    "Also send money to scammer@paytm for verification fee of Rs. 100.",
    "Call me at +91 9876543210 if you have any issues.",
    "Transfer to account number 123456789012 urgently.",
    "Click this link to verify: http://fake-bank.com/verify"
]

print("="*70)
print("HONEYPOT API - MULTI-TURN CONVERSATION TEST")
print("="*70)
print(f"Session ID: {SESSION_ID}\n")

conversation_history = []
total_intelligence = {
    "bankAccounts": set(),
    "upiIds": set(),
    "phoneNumbers": set(),
    "phishingLinks": set(),
    "suspiciousKeywords": set()
}

for i, scammer_message in enumerate(conversation, 1):
    print(f"\n{'='*70}")
    print(f"TURN {i}/{len(conversation)}")
    print(f"{'='*70}")
    print(f"\n[🔴 SCAMMER]: {scammer_message}")
    
    # Build payload
    payload = {
        "sessionId": SESSION_ID,
        "message": {
            "text": scammer_message,
            "sender": "scammer"
        },
        "conversationHistory": conversation_history.copy(),
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
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
            
            print(f"[🟢 RAM LAL]: {data['reply']}")
            
            # Update conversation history
            conversation_history.append({
                "sender": "scammer",
                "text": scammer_message
            })
            conversation_history.append({
                "sender": "user",
                "text": data['reply']
            })
            
            # Accumulate intelligence
            intel = data['extractedIntelligence']
            total_intelligence["bankAccounts"].update(intel['bankAccounts'])
            total_intelligence["upiIds"].update(intel['upiIds'])
            total_intelligence["phoneNumbers"].update(intel['phoneNumbers'])
            total_intelligence["phishingLinks"].update(intel['phishingLinks'])
            total_intelligence["suspiciousKeywords"].update(intel['suspiciousKeywords'])
            
            # Show metrics
            print(f"\n[📊 METRICS]:")
            print(f"   Messages: {data['engagementMetrics']['totalMessagesExchanged']}")
            print(f"   Duration: {data['engagementMetrics']['engagementDurationSeconds']}s")
            print(f"   Scam Detected: {data['scamDetected']}")
            
            # Show accumulated intelligence
            total_items = (
                len(total_intelligence["bankAccounts"]) +
                len(total_intelligence["upiIds"]) +
                len(total_intelligence["phoneNumbers"]) +
                len(total_intelligence["phishingLinks"])
            )
            
            print(f"\n[🎯 ACCUMULATED INTELLIGENCE] ({total_items} items):")
            if total_intelligence["bankAccounts"]:
                print(f"   💳 Bank Accounts: {list(total_intelligence['bankAccounts'])}")
            if total_intelligence["upiIds"]:
                print(f"   💰 UPI IDs: {list(total_intelligence['upiIds'])}")
            if total_intelligence["phoneNumbers"]:
                print(f"   📞 Phone Numbers: {list(total_intelligence['phoneNumbers'])}")
            if total_intelligence["phishingLinks"]:
                print(f"   🔗 Phishing Links: {list(total_intelligence['phishingLinks'])}")
            if total_intelligence["suspiciousKeywords"]:
                keywords = list(total_intelligence['suspiciousKeywords'])[:5]  # Show first 5
                print(f"   🚨 Keywords: {keywords}...")
            
            print(f"\n[📝 NOTES]: {data['agentNotes']}")
            
            # Wait a bit between messages
            if i < len(conversation):
                time.sleep(2)
        
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(response.text)
            break
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        break

# Final summary
print(f"\n\n{'='*70}")
print("CONVERSATION COMPLETE - FINAL SUMMARY")
print(f"{'='*70}")
print(f"\n[📊 TOTAL MESSAGES]: {len(conversation_history)}")
print(f"[🎯 TOTAL INTELLIGENCE ITEMS]: {total_items}")
print(f"\n[💳 Bank Accounts]: {list(total_intelligence['bankAccounts'])}")
print(f"[💰 UPI IDs]: {list(total_intelligence['upiIds'])}")
print(f"[📞 Phone Numbers]: {list(total_intelligence['phoneNumbers'])}")
print(f"[🔗 Phishing Links]: {list(total_intelligence['phishingLinks'])}")

print(f"\n{'='*70}")
print("CHECK FINAL CALLBACK")
print(f"{'='*70}")
print("\nIf the conversation triggered a final callback, check:")
print("https://webhook.site/32301b92-c042-4250-901e-07888d97498d")
print("\nCallback triggers when:")
print("  - Scam detected = True")
print("  - 3+ intelligence items OR 5+ messages exchanged")
print(f"{'='*70}\n")
