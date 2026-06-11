# backend/services/session_manager.py
# UPDATED - Added profile storage

from typing import Dict, Any, Optional
from backend.database import get_session, save_session


class SessionManager:
    """Manages user sessions with profile storage"""
    
    def __init__(self):
        self._sessions = {}  # In-memory cache
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session data including profile"""
        if session_id in self._sessions:
            return self._sessions[session_id]
        
        # Try to load from database
        db_session = get_session(session_id)
        if db_session:
            db_session.pop("_id", None)
            self._sessions[session_id] = db_session
            return db_session
        
        # Create new session with profile
        new_session = {
            "session_id": session_id,
            "profile": {},
            "last_shown_schemes": [],
            "selected_scheme": None,
            "conversation_state": "idle",
            "language": "hinglish"
        }
        self._sessions[session_id] = new_session
        return new_session
    
    def save_session(self, session_id: str, session_data: Dict[str, Any]):
        """Save session data including profile"""
        self._sessions[session_id] = session_data
        save_session(session_id, session_data)
    
    def update_profile(self, session_id: str, profile_updates: Dict[str, Any]):
        """Update user profile in session"""
        session = self.get_session(session_id)
        if "profile" not in session:
            session["profile"] = {}
        session["profile"].update(profile_updates)
        self.save_session(session_id, session)
    
    def get_profile(self, session_id: str) -> Dict[str, Any]:
        """Get user profile from session"""
        session = self.get_session(session_id)
        return session.get("profile", {})
    
    def clear_session(self, session_id: str):
        """Clear session data"""
        if session_id in self._sessions:
            del self._sessions[session_id]
        save_session(session_id, {"session_id": session_id, "profile": {}})


session_manager = SessionManager()