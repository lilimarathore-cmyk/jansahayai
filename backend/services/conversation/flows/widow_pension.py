# ============================================
# FILE: backend/services/conversation/flows/widow_pension.py
# FINAL FIXED VERSION - Age-based filtering as per JSON rules
# ============================================

from typing import Tuple, Optional, Dict
from backend.database import get_scheme
from backend.services.response_builder import format_scheme_full_details, extract_localized_text
from backend.services.conversation.extractors import Extractors
from backend.services.conversation.eligibility import EligibilityChecker
from backend.services.conversation.responses.continuation import ContinuationResponse


class WidowPensionFlow:
    
    @staticmethod
    def handle(message: str, session_id: str, user_data: Dict, user_sessions: Dict) -> Tuple[Optional[str], Optional[str]]:
        
        # ========== CLEAR ZONE FLAGS AT START ==========
        user_data.pop("awaiting_zone", None)
        user_data.pop("user_zone", None)
        
        # ========== CHECK IF IN CONTINUATION MODE ==========
        if user_data.get("continuation_mode", False):
            remaining_options = user_data.get("remaining_options", {})
            selected = message.strip()
            
            if selected in remaining_options:
                selected_scheme = remaining_options[selected]
                user_data["current_requested_scheme"] = selected_scheme
                user_data["step"] = "awaiting_additional_info"
                user_data["continuation_mode"] = False
                user_sessions[session_id] = user_data
                
                if selected_scheme == "002":
                    is_eligible, reason = EligibilityChecker.check_eligibility(
                        "cg_scheme_002", age=user_data.get("age"), widow_category=user_data.get("widow_category"))
                    scheme = get_scheme("cg_scheme_002")
                    if scheme:
                        full_details = format_scheme_full_details(scheme)
                        scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
                        result_msg = f"✅ **आप {scheme_name} के लिए पात्र हैं!**\n\n{full_details}" if is_eligible else f"❌ **आप {scheme_name} के लिए पात्र नहीं हैं।**\n\n**कारण:**\n{reason}\n\n{full_details}"
                        user_data["last_active_scheme_id"] = "cg_scheme_002"
                        return ContinuationResponse.show_widow_menu(user_data, result_msg, session_id, user_sessions)
                    return ("योजना की जानकारी उपलब्ध नहीं है।", "error")
                
                elif selected_scheme == "003":
                    return ("कृपया बताएं, क्या आपका नाम **SECC 2011 सूची** में है? (हाँ/नहीं)", "needs_slot")
                
                elif selected_scheme == "005":
                    return ("कृपया बताएं, क्या आपका नाम **BPL सूची** में है? (हाँ/नहीं)", "needs_slot")
            else:
                del user_sessions[session_id]
                return (None, None)
        
        # ========== STEP 1: AWAITING AGE ==========
        if user_data["step"] == "awaiting_age":
            age = Extractors.extract_age(message)
            
            # Age validation: minimum 18 required
            if age is None or age < 18:
                return ("❌ आयु मान्य नहीं है। कृपया 18 वर्ष या उससे अधिक आयु बताएं:", "needs_slot")
            
            # Valid age received
            user_data["age"] = age
            user_data["step"] = "awaiting_scheme_selection"
            user_sessions[session_id] = user_data
            
            category = user_data.get("widow_category", "widow")
            eligible_schemes = []
            
            # ========== AGE-BASED SCHEME FILTERING AS PER JSON RULES ==========
            if category == "widow":
                # Widow (विधवा) - as per JSON rules
                if 18 <= age <= 39:
                    eligible_schemes = ["002", "003", "005"]
                elif 40 <= age <= 60:
                    eligible_schemes = ["003", "005"]
                elif age > 60:
                    eligible_schemes = ["003"]
            else:
                # Abandoned (तलाकशुदा / परित्यक्ता) - as per JSON rules
                if 18 <= age <= 60:
                    eligible_schemes = ["002", "003", "005"]
                elif age > 60:
                    eligible_schemes = ["002", "003"]
            
            user_data["eligible_schemes"] = eligible_schemes
            user_data["seen_schemes"] = []
            
            if not eligible_schemes:
                user_data["step"] = "completed"
                if category == "widow":
                    result_msg = f"❌ **आप किसी भी योजना के लिए पात्र नहीं हैं।**\n\n**कारण:** विधवा के लिए आयु {age} वर्ष है। कृपया 18-39 वर्ष के बीच आयु होने पर पुनः प्रयास करें।"
                else:
                    result_msg = f"❌ **आप किसी भी योजना के लिए पात्र नहीं हैं।**\n\n**कारण:** आयु {age} वर्ष है। कृपया 18+ वर्ष होने पर पुनः प्रयास करें।"
                del user_sessions[session_id]
                return (result_msg, "success")
            
            return WidowPensionFlow._show_initial_options(user_data, session_id, user_sessions)
        
        # ========== STEP 2: AWAITING SCHEME SELECTION ==========
        if user_data["step"] == "awaiting_scheme_selection":
            selected = message.strip()
            scheme_option_map = user_data.get("scheme_option_map", {})
            
            if selected in scheme_option_map:
                selected_scheme = scheme_option_map[selected]
                user_data["current_requested_scheme"] = selected_scheme
                user_data["step"] = "awaiting_additional_info"
                user_sessions[session_id] = user_data
                
                if selected_scheme == "002":
                    is_eligible, reason = EligibilityChecker.check_eligibility(
                        "cg_scheme_002", age=user_data.get("age"), widow_category=user_data.get("widow_category"))
                    scheme = get_scheme("cg_scheme_002")
                    if scheme:
                        full_details = format_scheme_full_details(scheme)
                        scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
                        result_msg = f"✅ **आप {scheme_name} के लिए पात्र हैं!**\n\n{full_details}" if is_eligible else f"❌ **आप {scheme_name} के लिए पात्र नहीं हैं।**\n\n**कारण:**\n{reason}\n\n{full_details}"
                        if selected_scheme not in user_data.get("seen_schemes", []):
                            user_data["seen_schemes"] = user_data.get("seen_schemes", []) + [selected_scheme]
                        user_data["last_active_scheme_id"] = "cg_scheme_002"
                        return ContinuationResponse.show_widow_menu(user_data, result_msg, session_id, user_sessions)
                    return ("योजना की जानकारी उपलब्ध नहीं है।", "error")
                
                elif selected_scheme == "003":
                    return ("कृपया बताएं, क्या आपका नाम **SECC 2011 सूची** में है? (हाँ/नहीं)", "needs_slot")
                
                elif selected_scheme == "005":
                    return ("कृपया बताएं, क्या आपका नाम **BPL सूची** में है? (हाँ/नहीं)", "needs_slot")
            else:
                available_nums = list(scheme_option_map.keys())
                return (f"कृपया सही नंबर बताएं ({', '.join(available_nums)}):", "needs_slot")
        
        # ========== STEP 3: AWAITING ADDITIONAL INFO ==========
        if user_data["step"] == "awaiting_additional_info":
            selected_scheme_id = user_data.get("current_requested_scheme", "")
            
            if selected_scheme_id == "003":
                secc_status = Extractors.extract_secc_status(message)
                if secc_status:
                    is_eligible, reason = EligibilityChecker.check_eligibility(
                        "cg_scheme_003", 
                        age=user_data.get("age"), 
                        secc_status=secc_status,
                        widow_category=user_data.get("widow_category"))
                    scheme = get_scheme("cg_scheme_003")
                    if scheme:
                        full_details = format_scheme_full_details(scheme)
                        scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
                        result_msg = f"✅ **आप {scheme_name} के लिए पात्र हैं!**\n\n{full_details}" if is_eligible else f"❌ **आप {scheme_name} के लिए पात्र नहीं हैं।**\n\n**कारण:**\n{reason}\n\n{full_details}"
                        if "003" not in user_data.get("seen_schemes", []):
                            user_data["seen_schemes"] = user_data.get("seen_schemes", []) + ["003"]
                        user_data["last_active_scheme_id"] = "cg_scheme_003"
                        return ContinuationResponse.show_widow_menu(user_data, result_msg, session_id, user_sessions)
                    return ("योजना की जानकारी उपलब्ध नहीं है।", "error")
                else:
                    return ("कृपया 'हाँ' या 'नहीं' में बताएं। क्या आपका नाम SECC 2011 सूची में है?", "needs_slot")
            
            elif selected_scheme_id == "005":
                bpl_status = Extractors.extract_bpl_status(message)
                if bpl_status:
                    is_eligible, reason = EligibilityChecker.check_eligibility(
                        "cg_scheme_005", 
                        age=user_data.get("age"), 
                        bpl_status=bpl_status,
                        widow_category=user_data.get("widow_category"))
                    scheme = get_scheme("cg_scheme_005")
                    if scheme:
                        full_details = format_scheme_full_details(scheme)
                        scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
                        result_msg = f"✅ **आप {scheme_name} के लिए पात्र हैं!**\n\n{full_details}" if is_eligible else f"❌ **आप {scheme_name} के लिए पात्र नहीं हैं।**\n\n**कारण:**\n{reason}\n\n{full_details}"
                        if "005" not in user_data.get("seen_schemes", []):
                            user_data["seen_schemes"] = user_data.get("seen_schemes", []) + ["005"]
                        user_data["last_active_scheme_id"] = "cg_scheme_005"
                        return ContinuationResponse.show_widow_menu(user_data, result_msg, session_id, user_sessions)
                    return ("योजना की जानकारी उपलब्ध नहीं है।", "error")
                else:
                    return ("कृपया 'हाँ' या 'नहीं' में बताएं। क्या आपका नाम BPL सूची में है?", "needs_slot")
        
        return (None, None)

    @staticmethod
    def _show_initial_options(user_data: Dict, session_id: str, user_sessions: Dict) -> Tuple[str, str]:
        eligible_schemes = user_data.get("eligible_schemes", [])
        age = user_data.get("age")
        
        options_msg = f"आपकी आयु {age} वर्ष के लिए निम्नलिखित योजनाएं उपलब्ध हैं:\n\n"
        option_num = 1
        scheme_option_map = {}
        
        scheme_names = {
            "002": "सुखद सहारा पेंशन योजना (₹500, कोई अतिरिक्त शर्त नहीं)",
            "003": "मुख्यमंत्री पेंशन योजना (₹500, SECC 2011 सूची में नाम आवश्यक)",
            "005": "इंदिरा गांधी विधवा पेंशन योजना (₹500, BPL सूची में नाम आवश्यक)"
        }
        
        for scheme in eligible_schemes:
            options_msg += f"{option_num}. {scheme_names.get(scheme, 'योजना')}\n"
            scheme_option_map[str(option_num)] = scheme
            option_num += 1
        
        options_msg += f"\nकोई नंबर बताएं (1-{option_num-1}):"
        user_data["scheme_option_map"] = scheme_option_map
        user_data["seen_schemes"] = []
        user_sessions[session_id] = user_data
        return (options_msg, "needs_slot")