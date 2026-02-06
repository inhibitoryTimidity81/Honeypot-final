import requests
import json
import time
import sys

# Configuration
API_URL = "http://127.0.0.1:8002/api/v1/chat"
API_KEY = "12345" # Matches defaults if not changed, else user needs to update
# Note: In a real scenario, we'd read this from .env or require user input. 
# For this script, we'll try a common default or just rely on the user having set it up.
# However, the code uses `settings.YOUR_SECRET_API_KEY`. 
# We will assume the user has set "12345" or similar, or we can read .env locally.

def read_api_key():
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("YOUR_SECRET_API_KEY"):
                    return line.split("=")[1].strip().strip('"')
    except:
        return "secret_key_123" # Fallback

SECRET_KEY = read_api_key()


# Set up logging to file
log_file = "verification_results.txt"
def log(msg):
    print(msg)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# Clear previous log
with open(log_file, "w") as f:
    f.write("--- Verification Log ---\n")

def  test_scam_flow():
    session_id = f"test-session-{int(time.time())}"
    log(f"🚀 Starting Test Session: {session_id}")

    # 1. First Message
    payload_1 = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Your bank account ending 8822 is blocked. Click http://bit.ly/scam to verify.",
            "timestamp": "2026-01-21T10:15:30Z"
        },
        "conversationHistory": [],
        "metadata": {"channel": "SMS", "language": "en"}
    }

    log("\n📨 Sending Message 1...")
    try:
        response = requests.post(
            API_URL, 
            json=payload_1, 
            headers={"x-api-key": SECRET_KEY},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        log("✅ Response 1 Received:")
        log(json.dumps(data, indent=2))
        
        if not data.get("scamDetected"):
            log("❌ Scam NOT detected in first message!")
        else:
            log("✅ Scam properly detected.")

        if not data.get("responseMessage"):
            log("❌ No response message received!")
        else:
            log(f"🗣️ Agent Reply: {data['responseMessage']}")

    except Exception as e:
        log(f"❌ Request 1 Failed: {e}")
        return

    # 2. Second Message (Conversational)
    # Simulate adding the previous turn to history
    history = [
        {"sender": "scammer", "text": payload_1["message"]["text"], "timestamp": "..."}
    ]
    # We ideally append the agent's reply too, but the API spec for Input only asks for "previous messages". 
    # Usually this implies the full history including User (Agent) replies if the platform tracks it.
    # The prompt says: "Previous messages are now included in conversationHistory."
    # Let's add the agent reply to history to be realistic.
    history.append({
        "sender": "user", 
        "text": data["responseMessage"], 
        "timestamp": "..."
    })

    payload_2 = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Sir, this is urgent. Provide OTP 5544 to stop blocking.",
            "timestamp": "2026-01-21T10:17:10Z"
        },
        "conversationHistory": history,
        "metadata": {"channel": "SMS", "language": "en"}
    }

    log("\n📨 Sending Message 2...")
    try:
        response = requests.post(
            API_URL, 
            json=payload_2, 
            headers={"x-api-key": SECRET_KEY},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        log("✅ Response 2 Received:")
        log(json.dumps(data, indent=2))
        
        # Check extraction
        extracted = data.get("extractedIntelligence", {})
        if extracted.get("phishingLinks"):
             log(f"🔍 Extracted Links: {extracted['phishingLinks']}")
        
    except Exception as e:
        log(f"❌ Request 2 Failed: {e}")

if __name__ == "__main__":
    try:
        log("⏳ Waiting 3s for server to stabilize...")
        time.sleep(3)
        test_scam_flow()
    except Exception as e:
        log(f"CRITICAL SCRIPT ERROR: {e}")
