from pydantic import BaseModel
from typing import List, Optional

# ============================================================================
# INCOMING REQUEST SCHEMA (What the API receives)
# ============================================================================

class MessageObject(BaseModel):
    """The current message from the scammer"""
    text: str
    sender: str = "scammer"

class ConversationMessage(BaseModel):
    """Previous messages in the conversation history"""
    sender: str  # "user" or "scammer"
    text: str

class MessageMetadata(BaseModel):
    """Optional metadata about the message"""
    channel: Optional[str] = "SMS"
    language: Optional[str] = "English"
    locale: Optional[str] = "IN"

class IncomingRequest(BaseModel):
    """
    The exact structure of incoming requests to the /chat endpoint.
    Matches the specification exactly.
    """
    sessionId: str
    message: MessageObject
    conversationHistory: List[ConversationMessage] = []
    metadata: Optional[MessageMetadata] = None

# ============================================================================
# IMMEDIATE RESPONSE SCHEMA (What the API returns NOW)
# ============================================================================

class EngagementMetrics(BaseModel):
    """Metrics about the ongoing engagement"""
    engagementDurationSeconds: int
    totalMessagesExchanged: int

class ExtractedIntelligence(BaseModel):
    """Intelligence extracted from the conversation"""
    bankAccounts: List[str] = []
    upiIds: List[str] = []
    phishingLinks: List[str] = []
    phoneNumbers: List[str] = []
    suspiciousKeywords: List[str] = []

class APIResponse(BaseModel):
    """
    The immediate response returned for every incoming request.
    Includes the agent's reply text and current metrics/intelligence.
    """
    status: str
    scamDetected: bool
    reply: str  # The agent's text response to continue the conversation
    engagementMetrics: EngagementMetrics
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str

# ============================================================================
# FINAL CALLBACK SCHEMA (What gets sent to GUVI endpoint)
# ============================================================================

class FinalCallbackPayload(BaseModel):
    """
    The payload sent to the GUVI final result endpoint.
    Only sent when scam is confirmed and conversation is ending.
    """
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str