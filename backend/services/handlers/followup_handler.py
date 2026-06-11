# backend/services/handlers/followup_handler.py
"""Handle follow-up responses after scheme details - LLM powered"""

from typing import Tuple, Optional, Dict


class FollowupHandler:
    """Handle yes/no follow-up responses + context-aware scheme queries"""
    
    AFFIRMATIVE = ["हाँ", "हां", "yes", "ji", "haan", "chahiye", "dekhna", "aur", "more", "ha", "ok", "okay", "thik", "ठीक"]
    NEGATIVE = ["नहीं", "nahi", "no", "nhi", "not", "bas", "enough"]
    
    FOLLOWUP_KEYWORDS = {
        "documents": ["document", "दस्तावेज", "dastavej", "paper", "कागज", "kagaj",
                      "kya kya lagega", "kya lagta", "kya chahiye", "kya-kya",
                      "kya lagega", "docs", "doc", "क्या लगेगा", "क्या चाहिए",
                      "documents kya", "dokument", "dastavez"],
        "where": ["kahan", "कहाँ", "where", "kaha", "office", "कार्यालय",
                  "kaaryalay", "address", "पता", "pata", "location", "jagah", "जगह"],
        "how": ["kaise", "कैसे", "how", "process", "प्रक्रिया", "prakriya",
                "apply", "आवेदन", "aavedan", "form", "फॉर्म", "register"],
        "eligibility": ["eligible", "पात्र", "patra", "yogy", "योग्य",
                        "kaun le sakta", "कौन ले सकता", "can i", "kya mai"],
        "benefits": ["kya milta", "क्या मिलता", "benefit", "labh", "लाभ",
                     "fayda", "फायदा", "suvidha", "सुविधा"]
    }
    
    @staticmethod
    def is_affirmative(message: str) -> bool:
        return any(w in message.lower() for w in FollowupHandler.AFFIRMATIVE)
    
    @staticmethod
    def is_negative(message: str) -> bool:
        return any(w in message.lower() for w in FollowupHandler.NEGATIVE)
    
    @staticmethod
    def _detect_followup_type(message: str) -> Optional[str]:
        msg_lower = message.lower()
        for ftype, keywords in FollowupHandler.FOLLOWUP_KEYWORDS.items():
            if any(kw in msg_lower for kw in keywords):
                return ftype
        return None
    
    @staticmethod
    def _get_scheme_detail_for_followup(scheme_id: str, followup_type: str, user_message: str = "") -> Optional[str]:
        """Get specific detail from scheme - LLM se natural response"""
        from backend.database import get_scheme
        from backend.services.response_builder import extract_localized_text
        
        scheme = get_scheme(scheme_id)
        if not scheme:
            return None
        
        scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
        content = scheme.get("content", {})
        
        if followup_type == "documents":
            specific_info = extract_localized_text(content.get("required_documents", {}).get("text"))
            topic = "documents"
        elif followup_type == "where":
            specific_info = extract_localized_text(content.get("application_process", {}).get("where_to_apply"))
            office = extract_localized_text(content.get("office_info", {}).get("text"))
            if office:
                specific_info += f"\nOffice: {office}"
            topic = "location"
        elif followup_type == "how":
            specific_info = extract_localized_text(content.get("application_process", {}).get("how_to_apply"))
            topic = "process"
        elif followup_type == "eligibility":
            specific_info = extract_localized_text(content.get("eligibility", {}).get("text"))
            topic = "eligibility"
        elif followup_type == "benefits":
            specific_info = extract_localized_text(content.get("benefits", {}).get("text"))
            topic = "benefits"
        else:
            return None
        
        if not specific_info:
            return None
        
        # Try LLM
        try:
            from backend.llm.groq_client import generate_scheme_info_response
            documents_list = [specific_info] if followup_type == "documents" else []
            steps_list = [specific_info] if followup_type == "how" else []
            locations_list = [specific_info] if followup_type == "where" else []
            benefits_text = specific_info if followup_type == "benefits" else ""
            
            llm_response = generate_scheme_info_response(
                scheme_name=scheme_name,
                benefits=benefits_text,
                documents=documents_list,
                application_steps=steps_list,
                locations=locations_list,
                intent=f"ask_{topic}"
            )
            if llm_response and len(llm_response.strip()) > 20:
                return llm_response.strip()
        except Exception as e:
            print(f"[LLM] Followup failed: {e}")
        
        # Fallback
        intros = {
            "documents": f"📄 **{scheme_name}** ke liye documents:\n\n{specific_info}",
            "where": f"📍 **{scheme_name}** ke liye yahan apply karein:\n\n{specific_info}",
            "how": f"📝 **{scheme_name}** ki process:\n\n{specific_info}",
            "eligibility": f"✅ **{scheme_name}** ki eligibility:\n\n{specific_info}",
            "benefits": f"🎁 **{scheme_name}** ke benefits:\n\n{specific_info}"
        }
        return intros.get(followup_type, specific_info)
    
    @staticmethod
    def handle(message: str, session_data: Dict, format_recommendations_func) -> Tuple[Optional[str], Optional[str]]:
        state = session_data.get("state")
        
        if state == "showing_details":
            active_scheme_id = session_data.get("active_scheme") or session_data.get("current_scheme_id")
            if active_scheme_id:
                followup_type = FollowupHandler._detect_followup_type(message)
                if followup_type:
                    response = FollowupHandler._get_scheme_detail_for_followup(
                        active_scheme_id, followup_type, message
                    )
                    if response:
                        return (response, "success")
        
        if state != "showing_details":
            return (None, None)
        
        if FollowupHandler.is_affirmative(message):
            recommendations = session_data.get("last_recommendations", [])
            if recommendations:
                session_data["state"] = "showing_recommendations"
                response = format_recommendations_func(recommendations)
                return (response, "success")
        
        elif FollowupHandler.is_negative(message):
            session_data["state"] = "idle"
            session_data["current_scheme_id"] = None
            session_data["active_scheme"] = None
            return ("🙏 Dhanyavaad! Koi aur yojna poochh sakte hain.", "success")
        
        return (None, None)


followup_handler = FollowupHandler()