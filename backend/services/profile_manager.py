# backend/services/profile_manager.py
"""Manage user profiles"""
 
from typing import Dict, List
 
 
class ProfileManager:
 
    @staticmethod
    def get_missing_fields(profile: Dict) -> List[str]:
        """
        Only age is truly required.
        Everything else is optional — we show schemes with partial info.
        """
        missing = []
        if "age" not in profile:
            missing.append("age")
        return missing
 
    @staticmethod
    def is_profile_complete(profile: Dict) -> bool:
        """Profile is 'complete' if we have at least age."""
        return "age" in profile
 
    @staticmethod
    def get_field_question(field: str, profile: Dict) -> str:
        lang = profile.get("language", "hinglish")
        questions = {
            "age": {
                "hi": "आपकी उम्र क्या है?",
                "hinglish": "Aapki age kitni hai?",
                "en": "How old are you?",
            },
        }
        q = questions.get(field, {})
        return q.get(lang, q.get("hinglish", f"Please provide your {field}"))
 
 
profile_manager = ProfileManager()