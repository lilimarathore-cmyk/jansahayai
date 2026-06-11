# ============================================
# FILE: backend/services/conversation/responses/continuation.py
# Continuation Menu Responses - FIXED for Old Age
# ============================================

from typing import Tuple, Dict

class ContinuationResponse:
    
    @staticmethod
    def show_widow_menu(user_data: Dict, result_msg: str, session_id: str, user_sessions: Dict) -> Tuple[str, str]:
        eligible_schemes = user_data.get("eligible_schemes", [])
        current_scheme = user_data.get("current_requested_scheme", "")
        seen_schemes = user_data.get("seen_schemes", [])
        
        if current_scheme and current_scheme not in seen_schemes:
            seen_schemes.append(current_scheme)
            user_data["seen_schemes"] = seen_schemes
        
        # Filter remaining schemes
        remaining_schemes = [s for s in eligible_schemes if s not in seen_schemes]
        
        if not remaining_schemes:
            # All schemes shown - end session
            del user_sessions[session_id]
            return (result_msg + "\n\n✅ आपकी सभी योजनाओं की जानकारी दे दी गई है। कोई नई योजना पूछने के लिए नई चैट शुरू करें।", "success")
        
        scheme_names = {
            "002": ("1", "सुखद सहारा पेंशन योजना (₹500, कोई अतिरिक्त शर्त नहीं)"),
            "003": ("2", "मुख्यमंत्री पेंशन योजना (₹500, SECC 2011 सूची में नाम आवश्यक)"),
            "005": ("3", "इंदिरा गांधी विधवा पेंशन योजना (₹500, BPL सूची में नाम आवश्यक)")
        }
        
        cont_msg = result_msg + "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        cont_msg += "💡 **अन्य योजनाओं के लिए नंबर बताएं:**\n"
        
        remaining_map = {}
        for scheme in remaining_schemes:
            if scheme in scheme_names:
                num, name = scheme_names[scheme]
                cont_msg += f"{num}. {name}\n"
                remaining_map[num] = scheme
        
        cont_msg += "\nया सीधे लिखें:\n\n📌 दिव्यांग योजनाएं\n📌 विधवा पेंशन\n📌 वृद्धावस्था पेंशन\n📌 परिवार सहायता योजनाएं\n📌 टीजी कार्ड"
        
        user_data["continuation_mode"] = True
        user_data["remaining_options"] = remaining_map
        user_data["step"] = "completed"
        user_sessions[session_id] = user_data
        
        return (cont_msg, "needs_slot")

    @staticmethod
    def show_old_age_menu(user_data: Dict, result_msg: str, session_id: str, user_sessions: Dict) -> Tuple[str, str]:
        """Show menu after showing old age scheme details"""
        
        selected_scheme_id = user_data.get("selected_scheme_id", "")
        seen_schemes = user_data.get("seen_schemes", [])
        eligible_schemes = user_data.get("eligible_schemes", ["003", "004"])
        
        # Extract scheme number from selected_scheme_id
        if "cg_scheme_003" in selected_scheme_id:
            current_scheme = "003"
        elif "cg_scheme_004" in selected_scheme_id:
            current_scheme = "004"
        else:
            current_scheme = None
        
        # Add current scheme to seen list
        if current_scheme and current_scheme not in seen_schemes:
            seen_schemes.append(current_scheme)
            user_data["seen_schemes"] = seen_schemes
        
        # Find remaining schemes
        remaining_schemes = [s for s in eligible_schemes if s not in seen_schemes]
        
        if not remaining_schemes:
            # All schemes shown - end session
            del user_sessions[session_id]
            return (result_msg + "\n\n✅ आपकी सभी योजनाओं की जानकारी दे दी गई है। कोई नई योजना पूछने के लिए नई चैट शुरू करें।", "success")
        
        scheme_names = {
            "003": ("1", "मुख्यमंत्री पेंशन योजना (₹500, SECC 2011 सूची में नाम आवश्यक)"),
            "004": ("2", "इंदिरा गांधी वृद्धावस्था पेंशन योजना (BPL सूची में नाम आवश्यक) - ₹500 प्रति माह")
        }
        
        cont_msg = result_msg + "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        cont_msg += "💡 **अन्य योजना के लिए नंबर बताएं:**\n"
        
        remaining_map = {}
        for scheme in remaining_schemes:
            if scheme in scheme_names:
                num, name = scheme_names[scheme]
                cont_msg += f"{num}. {name}\n"
                remaining_map[num] = scheme
        
        cont_msg += "\nया सीधे लिखें:\n\n📌 दिव्यांग योजनाएं\n📌 विधवा पेंशन\n📌 वृद्धावस्था पेंशन\n📌 परिवार सहायता योजनाएं\n📌 टीजी कार्ड"
        
        user_data["continuation_mode"] = True
        user_data["remaining_options"] = remaining_map
        user_data["step"] = "completed"
        user_sessions[session_id] = user_data
        
        return (cont_msg, "needs_slot")