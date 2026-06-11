# backend/services/context_manager.py
# NEW FILE - Manages conversation context and state

from typing import Dict, Any, Optional, List
from enum import Enum


class ConversationState(Enum):
    """Possible conversation states"""
    IDLE = "idle"
    COLLECTING_PROFILE = "collecting_profile"
    SHOWING_RECOMMENDATIONS = "showing_recommendations"
    AWAITING_SCHEME_SELECTION = "awaiting_scheme_selection"
    CHECKING_ELIGIBILITY = "checking_eligibility"
    SHOWING_DETAILS = "showing_details"
    AWAITING_FOLLOWUP = "awaiting_followup"


class ContextManager:
    """Manages conversation context and state"""
    
    def __init__(self):
        self._contexts = {}  # session_id -> context
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get or create context for session"""
        if session_id not in self._contexts:
            self._contexts[session_id] = {
                "state": ConversationState.IDLE,
                "profile": {},
                "last_shown_schemes": [],
                "current_scheme": None,
                "last_response": "",
                "language": "hinglish",
                "pending_question": None,
                "conversation_history": []
            }
        return self._contexts[session_id]
    
    def update_state(self, session_id: str, state: ConversationState):
        """Update conversation state"""
        context = self.get_context(session_id)
        context["state"] = state
    
    def update_profile(self, session_id: str, updates: Dict[str, Any]):
        """Update user profile"""
        context = self.get_context(session_id)
        context["profile"].update(updates)
    
    def get_profile(self, session_id: str) -> Dict[str, Any]:
        """Get user profile"""
        return self.get_context(session_id).get("profile", {})
    
    def get_missing_fields(self, session_id: str) -> List[str]:
        """Get missing profile fields"""
        profile = self.get_profile(session_id)
        missing = []
        
        if not profile.get("age"):
            missing.append("age")
        if not profile.get("disability") and not profile.get("disability_percentage") and not profile.get("disability_type"):
            missing.append("disability")
        if not profile.get("income"):
            missing.append("income")
        if not profile.get("bpl_status"):
            missing.append("bpl_status")
        
        return missing
    
    def add_to_history(self, session_id: str, user_msg: str, bot_response: str):
        """Add conversation turn to history"""
        context = self.get_context(session_id)
        context["conversation_history"].append({
            "user": user_msg,
            "bot": bot_response,
            "timestamp": None
        })
        # Keep last 10 messages
        if len(context["conversation_history"]) > 10:
            context["conversation_history"] = context["conversation_history"][-10:]
    
    def clear_context(self, session_id: str):
        """Clear conversation context"""
        if session_id in self._contexts:
            del self._contexts[session_id]
    
    def is_new_topic(self, session_id: str, message: str) -> bool:
        """Check if user is starting a new topic"""
        context = self.get_context(session_id)
        
        # If no conversation yet, it's new topic
        if not context["conversation_history"]:
            return True
        
        # Check for greeting
        if any(word in message.lower() for word in ["namaste", "hello", "hi", "नमस्ते"]):
            return True
        
        # Check if user is answering a pending question
        if context["pending_question"]:
            return False
        
        return False


context_manager = ContextManager()