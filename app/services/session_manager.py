"""
Session Manager - In-Memory Session Tracking
Handles session state, metrics calculation, and final callback triggering logic.
"""

import time
from typing import Dict, List, Optional
from app.models.schemas import ConversationMessage, ExtractedIntelligence

class SessionData:
    """Data structure for tracking a single session"""
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.start_time = time.time()
        self.message_count = 0
        self.scam_detected = False
        self.conversation_history: List[Dict[str, str]] = []
        
        # Accumulated intelligence
        self.bank_accounts = set()
        self.upi_ids = set()
        self.phishing_links = set()
        self.phone_numbers = set()
        self.suspicious_keywords = set()
        
        # Agent notes accumulation
        self.agent_notes_history: List[str] = []
        
        # Final callback tracking
        self.final_callback_sent = False
        self.intelligence_extracted_count = 0  # Track how much intel we've gathered

    def add_message(self, sender: str, text: str):
        """Add a message to the conversation history"""
        self.conversation_history.append({
            "sender": sender,
            "text": text
        })
        self.message_count += 1

    def update_intelligence(self, intelligence: ExtractedIntelligence, agent_notes: str):
        """Update accumulated intelligence from latest analysis"""
        # Add new findings to sets (automatically deduplicates)
        self.bank_accounts.update(intelligence.bankAccounts)
        self.upi_ids.update(intelligence.upiIds)
        self.phishing_links.update(intelligence.phishingLinks)
        self.phone_numbers.update(intelligence.phoneNumbers)
        self.suspicious_keywords.update(intelligence.suspiciousKeywords)
        
        # Track agent notes
        if agent_notes:
            self.agent_notes_history.append(agent_notes)
        
        # Count total intelligence items
        self.intelligence_extracted_count = (
            len(self.bank_accounts) + 
            len(self.upi_ids) + 
            len(self.phishing_links) + 
            len(self.phone_numbers)
        )

    def get_duration_seconds(self) -> int:
        """Calculate engagement duration in seconds"""
        return int(time.time() - self.start_time)

    def get_extracted_intelligence(self) -> ExtractedIntelligence:
        """Get all accumulated intelligence"""
        return ExtractedIntelligence(
            bankAccounts=list(self.bank_accounts),
            upiIds=list(self.upi_ids),
            phishingLinks=list(self.phishing_links),
            phoneNumbers=list(self.phone_numbers),
            suspiciousKeywords=list(self.suspicious_keywords)
        )

    def get_final_agent_notes(self) -> str:
        """Generate comprehensive final agent notes"""
        if not self.agent_notes_history:
            return "Session completed with scam engagement."
        
        # Use the most recent note as primary, with summary
        latest_note = self.agent_notes_history[-1]
        intel_summary = f"Extracted {self.intelligence_extracted_count} intelligence items across {self.message_count} messages."
        
        return f"{latest_note} {intel_summary}"

    def should_send_final_callback(self) -> bool:
        """
        Determine if final callback should be sent.
        
        Criteria:
        1. Scam must be detected
        2. Callback not already sent
        3. At least one of:
           - Significant intelligence extracted (3+ items)
           - Conversation has gone on for a while (5+ messages)
           - Scammer seems to be ending conversation
        """
        if not self.scam_detected or self.final_callback_sent:
            return False
        
        # Send if we have good intelligence
        if self.intelligence_extracted_count >= 3:
            return True
        
        # Send if conversation is substantial
        if self.message_count >= 5:
            return True
        
        return False


class SessionManager:
    """Manages all active sessions in memory"""
    
    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}
    
    def get_or_create_session(self, session_id: str) -> SessionData:
        """Get existing session or create new one"""
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionData(session_id)
        return self._sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session if it exists"""
        return self._sessions.get(session_id)
    
    def mark_callback_sent(self, session_id: str):
        """Mark that final callback has been sent for this session"""
        session = self.get_session(session_id)
        if session:
            session.final_callback_sent = True
    
    def cleanup_old_sessions(self, max_age_seconds: int = 3600):
        """
        Clean up sessions older than max_age_seconds.
        Call this periodically to prevent memory bloat.
        """
        current_time = time.time()
        sessions_to_remove = []
        
        for session_id, session in self._sessions.items():
            if current_time - session.start_time > max_age_seconds:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self._sessions[session_id]
        
        if sessions_to_remove:
            print(f"🧹 Cleaned up {len(sessions_to_remove)} old sessions")


# Global session manager instance
session_manager = SessionManager()
