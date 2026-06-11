# ============================================
# FILE: backend/services/conversation/flows/old_age_pension.py
# NO CONTINUATION - Direct response only
# ============================================

from typing import Tuple, Optional, Dict
from backend.database import get_scheme
from backend.services.response_builder import format_scheme_full_details, extract_localized_text
from backend.services.conversation.extractors import Extractors
from backend.services.conversation.eligibility import EligibilityChecker
from backend.services.conversation.responses.continuation import ContinuationResponse


class OldAgePensionFlow:
    
    @staticmethod
    def handle(message: str, session_id: str, user_data: Dict, user_sessions: Dict) -> Tuple[Optional[str], Optional[str]]:
        
        # ========== CLEAR ZONE FLAGS AT START ==========
        user_data.pop("awaiting_zone", None)
        user_data.pop("user_zone", None)
        
        # ========== STEP 1: AWAITING AGE ==========
        if user_data["step"] == "awaiting_age":
            age = Extractors.extract_age(message)
            
            if age is None or age < 60:
                return (f"❌ इस योजना के लिए न्यूनतम आयु 60 वर्ष है। कृपया सही आयु बताएं (60+ वर्ष):", "needs_slot")
            
            user_data["age"] = age
            user_data["step"] = "awaiting_scheme_selection"
            user_data["eligible_schemes"] = ["003", "004"]
            user_sessions[session_id] = user_data
            
            return OldAgePensionFlow._show_initial_options(user_data, session_id, user_sessions)
        
        # ========== STEP 2: AWAITING SCHEME SELECTION ==========
        if user_data["step"] == "awaiting_scheme_selection":
            selected = message.strip()
            scheme_option_map = user_data.get("scheme_option_map", {})
            
            if selected in scheme_option_map:
                selected_scheme = scheme_option_map[selected]
                
                if selected_scheme == "003":
                    user_data["step"] = "awaiting_secc"
                    user_data["selected_scheme_id"] = "cg_scheme_003"
                    user_sessions[session_id] = user_data
                    return ("कृपया बताएं, क्या आपका नाम **SECC 2011 सूची** में है? (हाँ/नहीं)", "needs_slot")
                
                elif selected_scheme == "004":
                    user_data["step"] = "awaiting_bpl"
                    user_data["selected_scheme_id"] = "cg_scheme_004"
                    user_sessions[session_id] = user_data
                    return ("कृपया बताएं, क्या आपका नाम **BPL सूची** में है? (हाँ/नहीं)", "needs_slot")
            else:
                available_nums = list(scheme_option_map.keys())
                return (f"कृपया सही नंबर बताएं ({', '.join(available_nums)}):", "needs_slot")
        
        # ========== STEP 3: AWAITING SECC FOR SCHEME 003 ==========
        if user_data["step"] == "awaiting_secc":
            secc_status = Extractors.extract_secc_status(message)
            
            if secc_status:
                age = user_data.get("age")
                is_eligible, reason = EligibilityChecker.check_eligibility(
                    "cg_scheme_003", age=age, secc_status=secc_status)
                
                scheme_name = "मुख्यमंत्री पेंशन योजना - 2018"
                
                if is_eligible:
                    result_msg = f"""✅ **आप {scheme_name} के लिए पात्र हैं!**

📌 **{scheme_name}**

💰 **क्या मिलता है:**
₹500 प्रति माह पेंशन दी जाती है।

✅ **कौन ले सकता है:**
• आवेदक छत्तीसगढ़ का मूल निवासी होना चाहिए
• सामाजिक-आर्थिक जाति जनगणना 2011 की सूची में नाम होना चाहिए
• 60 वर्ष या उससे अधिक आयु के महिला एवं पुरुष पात्र हैं
• 18 वर्ष या उससे अधिक आयु की विधवा / परित्यक्त महिलाएं पात्र हैं

📋 **क्या दस्तावेज चाहिए:**
• सर्वे सूची प्रमाण पत्र
• आधार कार्ड
• बैंक पासबुक की कॉपी
• निवास प्रमाण पत्र
• मोबाइल नंबर
• निर्धारित आवेदन पत्र

📝 **आवेदन कैसे करें:**
1. निर्धारित प्रारूप में आवेदन फॉर्म भरें
2. ग्रामीण क्षेत्र में ग्राम पंचायत में आवेदन जमा करें
3. शहरी क्षेत्र में पार्षद के माध्यम से नगर निगम / नगर पालिका में आवेदन जमा करें

📍 **कहाँ आवेदन करें:**
• ग्राम पंचायत
• जनपद पंचायत
• नगर निगम / नगर पालिका / नगर पंचायत

📥 डाउनलोड फॉर्म"""
                else:
                    result_msg = f"""❌ **आप {scheme_name} के लिए पात्र नहीं हैं.**

**कारण:**
• {reason}

📌 **{scheme_name}**

💰 **क्या मिलता है:**
₹500 प्रति माह पेंशन दी जाती है।

✅ **कौन ले सकता है:**
• आवेदक छत्तीसगढ़ का मूल निवासी होना चाहिए
• सामाजिक-आर्थिक जाति जनगणना 2011 की सूची में नाम होना चाहिए
• 60 वर्ष या उससे अधिक आयु के महिला एवं पुरुष पात्र हैं
• 18 वर्ष या उससे अधिक आयु की विधवा / परित्यक्त महिलाएं पात्र हैं

📋 **क्या दस्तावेज चाहिए:**
• सर्वे सूची प्रमाण पत्र
• आधार कार्ड
• बैंक पासबुक की कॉपी
• निवास प्रमाण पत्र
• मोबाइल नंबर
• निर्धारित आवेदन पत्र

📝 **आवेदन कैसे करें:**
1. निर्धारित प्रारूप में आवेदन फॉर्म भरें
2. ग्रामीण क्षेत्र में ग्राम पंचायत में आवेदन जमा करें
3. शहरी क्षेत्र में पार्षद के माध्यम से नगर निगम / नगर पालिका में आवेदन जमा करें

📍 **कहाँ आवेदन करें:**
• ग्राम पंचायत
• जनपद पंचायत
• नगर निगम / नगर पालिका / नगर पंचायत

📥 डाउनलोड फॉर्म"""
                
                # Clear session and return result (no continuation)
                del user_sessions[session_id]
                return (result_msg, "success")
            else:
                return ("कृपया 'हाँ' या 'नहीं' में बताएं। क्या आपका नाम SECC 2011 सूची में है?", "needs_slot")
        
        # ========== STEP 4: AWAITING BPL FOR SCHEME 004 ==========
        if user_data["step"] == "awaiting_bpl":
            bpl_status = Extractors.extract_bpl_status(message)
            
            if bpl_status:
                age = user_data.get("age")
                is_eligible, reason = EligibilityChecker.check_eligibility(
                    "cg_scheme_004", age=age, bpl_status=bpl_status)
                
                if 60 <= age <= 79:
                    amount_text = "₹500 प्रति माह"
                else:
                    amount_text = "₹650 प्रति माह"
                
                scheme_name = "इंदिरा गांधी राष्ट्रीय वृद्धावस्था पेंशन योजना"
                
                if is_eligible:
                    result_msg = f"""✅ **आप {scheme_name} के लिए पात्र हैं! ({amount_text})**

📌 **{scheme_name}**

💰 **क्या मिलता है:**
60-79 वर्ष के लिए ₹500 और 80 वर्ष या अधिक के लिए ₹650 प्रति माह पेंशन दी जाती है।

✅ **कौन ले सकता है:**
• आवेदक छत्तीसगढ़ का मूल निवासी होना चाहिए
• गरीबी रेखा (BPL) सर्वे सूची में नाम होना चाहिए
• 60 वर्ष या उससे अधिक आयु के वृद्धजन पात्र हैं

📋 **क्या दस्तावेज चाहिए:**
• सर्वे सूची प्रमाण पत्र
• आधार कार्ड
• बैंक पासबुक की कॉपी
• निवास प्रमाण पत्र
• मोबाइल नंबर
• निर्धारित आवेदन पत्र

📝 **आवेदन कैसे करें:**
1. निर्धारित प्रारूप में आवेदन फॉर्म भरें
2. ग्रामीण क्षेत्र में ग्राम पंचायत में आवेदन जमा करें
3. शहरी क्षेत्र में पार्षद के माध्यम से नगर निगम / नगर पालिका में आवेदन जमा करें

📍 **कहाँ आवेदन करें:**
• ग्राम पंचायत
• जनपद पंचायत
• नगर निगम / नगर पालिका / नगर पंचायत

📥 डाउनलोड फॉर्म"""
                else:
                    result_msg = f"""❌ **आप {scheme_name} के लिए पात्र नहीं हैं.**

**कारण:**
• {reason}

📌 **{scheme_name}**

💰 **क्या मिलता है:**
60-79 वर्ष के लिए ₹500 और 80 वर्ष या अधिक के लिए ₹650 प्रति माह पेंशन दी जाती है।

✅ **कौन ले सकता है:**
• आवेदक छत्तीसगढ़ का मूल निवासी होना चाहिए
• गरीबी रेखा (BPL) सर्वे सूची में नाम होना चाहिए
• 60 वर्ष या उससे अधिक आयु के वृद्धजन पात्र हैं

📋 **क्या दस्तावेज चाहिए:**
• सर्वे सूची प्रमाण पत्र
• आधार कार्ड
• बैंक पासबुक की कॉपी
• निवास प्रमाण पत्र
• मोबाइल नंबर
• निर्धारित आवेदन पत्र

📝 **आवेदन कैसे करें:**
1. निर्धारित प्रारूप में आवेदन फॉर्म भरें
2. ग्रामीण क्षेत्र में ग्राम पंचायत में आवेदन जमा करें
3. शहरी क्षेत्र में पार्षद के माध्यम से नगर निगम / नगर पालिका में आवेदन जमा करें

📍 **कहाँ आवेदन करें:**
• ग्राम पंचायत
• जनपद पंचायत
• नगर निगम / नगर पालिका / नगर पंचायत

📥 डाउनलोड फॉर्म"""
                
                # Clear session and return result (no continuation)
                del user_sessions[session_id]
                return (result_msg, "success")
            else:
                return ("कृपया 'हाँ' या 'नहीं' में बताएं। क्या आपका नाम BPL सूची में है?", "needs_slot")
        
        return (None, None)

    @staticmethod
    def _show_initial_options(user_data: Dict, session_id: str, user_sessions: Dict) -> Tuple[str, str]:
        age = user_data.get("age")
        
        if 60 <= age <= 79:
            amount_text = "₹500 प्रति माह"
        else:
            amount_text = "₹650 प्रति माह"
        
        options_msg = f"आपकी आयु {age} वर्ष के लिए निम्नलिखित योजनाएं उपलब्ध हैं:\n\n"
        options_msg += "1. मुख्यमंत्री पेंशन योजना (₹500, SECC 2011 सूची में नाम आवश्यक)\n"
        options_msg += f"2. इंदिरा गांधी वृद्धावस्था पेंशन योजना (BPL सूची में नाम आवश्यक) - {amount_text}\n\n"
        options_msg += "कोई नंबर बताएं (1 या 2):"
        
        scheme_option_map = {"1": "003", "2": "004"}
        user_data["scheme_option_map"] = scheme_option_map
        user_sessions[session_id] = user_data
        return (options_msg, "needs_slot")