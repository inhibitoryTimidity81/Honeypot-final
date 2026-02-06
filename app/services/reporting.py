"""
Reporting Service - Final Callback to GUVI
Sends the mandatory final result to the GUVI evaluation endpoint.
"""

import requests
from app.core.config import settings
from app.models.schemas import FinalCallbackPayload, ExtractedIntelligence

def send_final_callback(
    session_id: str,
    scam_detected: bool,
    total_messages: int,
    extracted_intelligence: ExtractedIntelligence,
    agent_notes: str
) -> bool:
    """
    Send the final callback to GUVI endpoint.
    
    Args:
        session_id: The session identifier
        scam_detected: Whether scam was detected
        total_messages: Total number of messages exchanged
        extracted_intelligence: All accumulated intelligence
        agent_notes: Final summary notes
        
    Returns:
        True if successful, False otherwise
    """
    
    # Construct the exact payload structure required by GUVI
    payload = FinalCallbackPayload(
        sessionId=session_id,
        scamDetected=scam_detected,
        totalMessagesExchanged=total_messages,
        extractedIntelligence=extracted_intelligence,
        agentNotes=agent_notes
    )
    
    print(f"\n📤 Sending Final Callback for session {session_id}")
    print(f"   Scam Detected: {scam_detected}")
    print(f"   Messages: {total_messages}")
    print(f"   Intelligence Items: {len(extracted_intelligence.bankAccounts) + len(extracted_intelligence.upiIds) + len(extracted_intelligence.phoneNumbers) + len(extracted_intelligence.phishingLinks)}")
    
    try:
        response = requests.post(
            settings.GUVI_CALLBACK_URL,
            json=payload.model_dump(),  # Convert Pydantic model to dict
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Final Callback SUCCESS for {session_id}")
            return True
        else:
            print(f"⚠️ Final Callback REJECTED for {session_id}")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Final Callback TIMEOUT for {session_id}")
        return False
    except Exception as e:
        print(f"❌ Final Callback FAILED for {session_id}: {e}")
        return False
