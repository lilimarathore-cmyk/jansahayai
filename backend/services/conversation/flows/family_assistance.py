# ============================================
# FILE: backend/services/conversation/flows/family_assistance.py
# UPDATED with YES/NO helpers
# ============================================

from typing import Tuple, Optional, Dict
from backend.database import get_scheme
from backend.services.response_builder import format_scheme_full_details, extract_localized_text
from backend.services.conversation.extractors import Extractors
from backend.services.conversation.eligibility import EligibilityChecker

class FamilyAssistanceFlow:
    
    @staticmethod
    def handle(message: str, session_id: str, user_data: Dict, user_sessions: Dict) -> Tuple[Optional[str], Optional[str]]:
        
        # Step 1: Awaiting BPL Status
        if user_data["step"] == "awaiting_bpl":
            bpl_status = Extractors.extract_bpl_status(message)
            if bpl_status:
                user_data["bpl_status"] = bpl_status
                user_data["step"] = "awaiting_age"
                user_sessions[session_id] = user_data
                return (f"✅ BPL सूची में नाम {bpl_status} नोट कर लिया गया।\n\nकृपया बताएं, मृतक की **आयु** कितनी थी? (18-60 वर्ष के बीच)", "needs_slot")
            else:
                return ("कृपया 'हाँ' या 'नहीं' में बताएं। क्या परिवार का नाम BPL सूची में है?", "needs_slot")
        
        # Step 2: Awaiting Age
        if user_data["step"] == "awaiting_age":
            age = Extractors.extract_age(message)
            if age:
                user_data["age"] = age
                user_data["step"] = "completed"
                user_sessions[session_id] = user_data
                
                is_eligible, reason = EligibilityChecker.check_eligibility(
                    "cg_scheme_007", age=age, bpl_status=user_data.get("bpl_status"))
                
                scheme = get_scheme("cg_scheme_007")
                if scheme:
                    full_details = format_scheme_full_details(scheme)
                    scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
                    
                    if is_eligible:
                        response = f"✅ **आप {scheme_name} के लिए पात्र हैं!**\n\n{full_details}"
                    else:
                        response = f"❌ **आप {scheme_name} के लिए पात्र नहीं हैं।**\n\n**कारण:**\n{reason}\n\n{full_details}"
                    
                    user_data["last_active_scheme_id"] = "cg_scheme_007"
                    return (response, "success")
                return ("योजना की जानकारी उपलब्ध नहीं है।", "error")
            else:
                return ("कृपया मृतक की **आयु** बताएं (18-60 वर्ष के बीच):", "needs_slot")
        
        return (None, None)