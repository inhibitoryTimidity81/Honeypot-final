"""
API Endpoints - Main Chat Endpoint
Handles incoming scam messages, generates responses, and manages callbacks.
"""

from fastapi import APIRouter, Header, HTTPException, BackgroundTasks
from app.models.schemas import IncomingRequest, APIResponse, EngagementMetrics
from app.services import gemini_agent, intelligence, reporting
from app.services.session_manager import session_manager
from app.core.config import settings

router = APIRouter()

@router.post("/chat", response_model=APIResponse)
async def chat_endpoint(
    payload: IncomingRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(None)
):
    """
    Main chat endpoint for the Honeypot Agent.
    
    Receives a message from a potential scammer, analyzes it, generates a response,
    and returns immediate metrics while potentially triggering a final callback.
    """
    
    # 1. Security Check
    if x_api_key != settings.YOUR_SECRET_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    # 2. Get or Create Session
    session = session_manager.get_or_create_session(payload.sessionId)
    
    # 3. Log Incoming Message
    print(f"\n{'='*60}")
    print(f"[🔴 SCAMMER]: {payload.message.text}")
    print(f"Session: {payload.sessionId} | Message #{session.message_count + 1}")
    
    # 4. Analyze Message for Intelligence
    analysis = intelligence.analyze_message(
        conversation_history=payload.conversationHistory,
        current_message_text=payload.message.text
    )
    
    # 5. Generate Agent Response
    agent_reply = gemini_agent.generate_response(
        history=payload.conversationHistory,
        current_msg_text=payload.message.text
    )
    
    # 6. Update Session State
    session.add_message("scammer", payload.message.text)
    session.add_message("user", agent_reply)  # Ram Lal is the "user"
    session.scam_detected = analysis["is_scam"]
    session.update_intelligence(
        intelligence=analysis["extracted_intelligence"],
        agent_notes=analysis["agent_notes"]
    )
    
    # 7. Log Outgoing Message
    print(f"[🟢 RAM LAL]: {agent_reply}")
    print(f"[🔍 INTEL]: {session.intelligence_extracted_count} items | Scam: {session.scam_detected}")
    
    # 8. Check if Final Callback Should Be Sent
    if session.should_send_final_callback():
        print(f"[📤 CALLBACK]: Triggering final callback for {payload.sessionId}")
        
        # Add background task to send final callback
        background_tasks.add_task(
            reporting.send_final_callback,
            session_id=payload.sessionId,
            scam_detected=session.scam_detected,
            total_messages=session.message_count,
            extracted_intelligence=session.get_extracted_intelligence(),
            agent_notes=session.get_final_agent_notes()
        )
        
        # Mark callback as sent to avoid duplicates
        session_manager.mark_callback_sent(payload.sessionId)
    
    # 9. Return Immediate Response
    response = APIResponse(
        status="success",
        scamDetected=session.scam_detected,
        reply=agent_reply,
        engagementMetrics=EngagementMetrics(
            engagementDurationSeconds=session.get_duration_seconds(),
            totalMessagesExchanged=session.message_count
        ),
        extractedIntelligence=session.get_extracted_intelligence(),
        agentNotes=analysis["agent_notes"]
    )
    
    print(f"{'='*60}\n")
    
    return response


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Honeypot Agent API",
        "version": "2.0"
    }