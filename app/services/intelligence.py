"""
Intelligence Extraction Service
Analyzes messages for scam detection and extracts actionable intelligence.
Uses AI (Gemini) with regex fallback.
"""

import google.generativeai as genai
import json
import re
from typing import List, Dict
from app.core.config import settings
from app.models.schemas import ConversationMessage, ExtractedIntelligence

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

SYSTEM_PROMPT = """
You are a Cybersecurity Intelligence Analyst analyzing potential scam messages.

Analyze the CONVERSATION HISTORY and the LATEST MESSAGE.

YOUR TASKS:
1. SCAM DETECTION: Determine if this is a scam attempt (true/false)
2. SUMMARIZATION: Write a brief "agent_notes" summarizing the scammer's tactics and current state
3. EXTRACTION: Extract all instances of:
   - Bank account numbers (9-18 digits)
   - UPI IDs (format: something@bank)
   - Phone numbers (Indian format)
   - Phishing links (URLs)
   - Suspicious keywords (urgent, verify, blocked, KYC, OTP, etc.)

OUTPUT FORMAT (Must be valid JSON):
{
    "is_scam": boolean,
    "agent_notes": "Brief summary of scammer's current tactics and what they're trying to achieve",
    "extracted_data": {
        "bankAccounts": ["account1", "account2"],
        "upiIds": ["id@bank"],
        "phoneNumbers": ["+91XXXXXXXXXX"],
        "phishingLinks": ["http://example.com"],
        "suspiciousKeywords": ["urgent", "verify"]
    }
}

Be thorough in extraction. Look through the entire conversation history.
"""

def extract_via_regex(text: str) -> Dict:
    """
    Fallback regex extraction when AI fails.
    Extracts patterns for UPI, phone, bank accounts, links, and keywords.
    """
    # 1. UPI IDs (e.g., something@okicici, number@paytm)
    upi_pattern = r"[\w\.\-_]+@[\w]+"
    
    # 2. Indian Phone Numbers (10 digits starting with 6-9, optional +91)
    phone_pattern = r"(?:\+91[\-\s]?)?[6-9]\d{9}\b"
    
    # 3. Phishing Links (http/https)
    link_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+\S*"
    
    # 4. Bank Account Numbers (9 to 18 digits)
    bank_pattern = r"\b\d{9,18}\b"

    # 5. Suspicious Keywords (case-insensitive)
    keyword_pattern = r"(?i)\b(urgent|verify|blocked|suspended|otp|pin|kyc|verify now|account blocked|immediate|action required|confirm|update|expired|deactivated)\b"

    return {
        "bankAccounts": list(set(re.findall(bank_pattern, text))),
        "upiIds": list(set(re.findall(upi_pattern, text))),
        "phoneNumbers": list(set(re.findall(phone_pattern, text))),
        "phishingLinks": list(set(re.findall(link_pattern, text))),
        "suspiciousKeywords": list(set(re.findall(keyword_pattern, text)))
    }

def analyze_message(conversation_history: List[ConversationMessage], current_message_text: str) -> Dict:
    """
    Analyze the conversation and extract intelligence.
    
    Returns:
        {
            "is_scam": bool,
            "agent_notes": str,
            "extracted_intelligence": ExtractedIntelligence
        }
    """
    # Build full transcript
    transcript = ""
    for msg in conversation_history:
        transcript += f"{msg.sender}: {msg.text}\n"
    transcript += f"scammer: {current_message_text}"

    # Try AI extraction first
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nCONVERSATION:\n{transcript}"
        response = model.generate_content(full_prompt)
        
        # Clean and parse JSON
        clean_text = response.text.strip()
        # Remove markdown code blocks if present
        clean_text = clean_text.replace("```json", "").replace("```", "").strip()
        
        ai_data = json.loads(clean_text)
        
        # Validate structure
        extracted_data = ai_data.get("extracted_data", {})
        
        return {
            "is_scam": ai_data.get("is_scam", True),
            "agent_notes": ai_data.get("agent_notes", "Analyzing scammer tactics..."),
            "extracted_intelligence": ExtractedIntelligence(
                bankAccounts=extracted_data.get("bankAccounts", []),
                upiIds=extracted_data.get("upiIds", []),
                phoneNumbers=extracted_data.get("phoneNumbers", []),
                phishingLinks=extracted_data.get("phishingLinks", []),
                suspiciousKeywords=extracted_data.get("suspiciousKeywords", [])
            )
        }
        
    except Exception as e:
        # Fallback to regex extraction
        print(f"⚠️ AI Intelligence Failed: {e}. Using regex fallback.")
        
        regex_data = extract_via_regex(transcript)
        
        return {
            "is_scam": True,  # Default to True in honeypot scenario
            "agent_notes": f"Regex-based analysis. Scammer attempting to extract sensitive information. AI error: {str(e)[:50]}",
            "extracted_intelligence": ExtractedIntelligence(
                bankAccounts=regex_data.get("bankAccounts", []),
                upiIds=regex_data.get("upiIds", []),
                phoneNumbers=regex_data.get("phoneNumbers", []),
                phishingLinks=regex_data.get("phishingLinks", []),
                suspiciousKeywords=regex_data.get("suspiciousKeywords", [])
            )
        }
