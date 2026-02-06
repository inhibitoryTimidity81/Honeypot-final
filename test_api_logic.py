"""
Direct API Test - Tests the core logic without running the server
"""

import sys
import json
from app.models.schemas import IncomingRequest, MessageObject, ConversationMessage
from app.services import intelligence, gemini_agent
from app.services.session_manager import session_manager

def test_api_logic():
    print("="*60)
    print("TESTING HONEYPOT API LOGIC")
    print("="*60)
    
    # Create test request
    test_payload = IncomingRequest(
        sessionId="test-session-001",
        message=MessageObject(
            text="Hello sir, your bank account has been blocked. Please share your account number to verify.",
            sender="scammer"
        ),
        conversationHistory=[],
        metadata=None
    )
    
    print(f"\n[🔴 SCAMMER]: {test_payload.message.text}")
    
    # Get session
    session = session_manager.get_or_create_session(test_payload.sessionId)
    print(f"[📊 SESSION]: Created/Retrieved session {test_payload.sessionId}")
    
    # Analyze message
    print("\n[🔍 ANALYZING]: Running intelligence extraction...")
    try:
        analysis = intelligence.analyze_message(
            conversation_history=test_payload.conversationHistory,
            current_message_text=test_payload.message.text
        )
        print(f"[✓ ANALYSIS]: Scam detected: {analysis['is_scam']}")
        print(f"[✓ INTEL]: {json.dumps(analysis['extracted_intelligence'].model_dump(), indent=2)}")
        print(f"[✓ NOTES]: {analysis['agent_notes']}")
    except Exception as e:
        print(f"[✗ ERROR]: Intelligence analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Generate response
    print("\n[🤖 GENERATING]: Creating Ram Lal's response...")
    try:
        agent_reply = gemini_agent.generate_response(
            history=test_payload.conversationHistory,
            current_msg_text=test_payload.message.text
        )
        print(f"[🟢 RAM LAL]: {agent_reply}")
    except Exception as e:
        print(f"[✗ ERROR]: Response generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Update session
    session.add_message("scammer", test_payload.message.text)
    session.add_message("user", agent_reply)
    session.scam_detected = analysis["is_scam"]
    session.update_intelligence(
        intelligence=analysis["extracted_intelligence"],
        agent_notes=analysis["agent_notes"]
    )
    
    print(f"\n[📊 METRICS]:")
    print(f"   Duration: {session.get_duration_seconds()}s")
    print(f"   Messages: {session.message_count}")
    print(f"   Intelligence Items: {session.intelligence_extracted_count}")
    print(f"   Should Send Callback: {session.should_send_final_callback()}")
    
    print("\n" + "="*60)
    print("✅ TEST PASSED - All components working!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = test_api_logic()
    sys.exit(0 if success else 1)
