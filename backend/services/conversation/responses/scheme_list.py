# ============================================
# FILE: backend/services/conversation/responses/scheme_list.py
# COMPLETE FIXED VERSION - Maintains correct order
# ============================================

from backend.database import get_all_schemes
from backend.services.response_builder import extract_localized_text

_conversation_engine = None

def set_conversation_engine(engine):
    global _conversation_engine
    _conversation_engine = engine
    print(f"[DEBUG] set_conversation_engine called, engine={engine is not None}")

class SchemeListResponse:
    
    @staticmethod
    def get_divyang_schemes_brief_response() -> str:
        global _conversation_engine
        
        print("[DEBUG] get_divyang_schemes_brief_response called")
        
        # ✅ FIX: Define schemes in EXACT display order (1 to 10)
        # This order is FIXED and will NEVER change
        scheme_order = [
            ("cg_scheme_001", "सामाजिक सुरक्षा दिव्यांग पेंशन योजना", "दिव्यांग व्यक्तियों को ₹500 प्रति माह पेंशन"),
            ("cg_scheme_006", "इंदिरा गांधी राष्ट्रीय दिव्यांग पेंशन योजना", "दिव्यांग व्यक्तियों को ₹500 प्रति माह पेंशन"),
            ("cg_scheme_009", "दिव्यांगजन विवाह प्रोत्साहन योजना", "दिव्यांग दंपत्ति को विवाह के बाद प्रोत्साहन राशि"),
            ("cg_scheme_010", "दिव्यांगजन छात्रवृत्ति योजना", "दिव्यांग विद्यार्थियों को पढ़ाई के लिए आर्थिक सहायता"),
            ("cg_scheme_011", "दिव्यांग उच्च शिक्षा प्रोत्साहन योजना", "दिव्यांग विद्यार्थियों को उच्च शिक्षा के लिए आर्थिक सहायता"),
            ("cg_scheme_012", "दिव्यांगजन सिविल सेवा प्रोत्साहन योजना", "सिविल सेवा परीक्षा पास करने वाले दिव्यांगों को प्रोत्साहन राशि"),
            ("cg_scheme_013", "दिव्यांगजन विद्यार्थियों के लिये छात्रावास योजना", "दूर रहने वाले दिव्यांग छात्रों को छात्रावास सुविधा"),
            ("cg_scheme_014", "दिव्यांगजन हेतु शिविरों का आयोजन", "प्रमाण पत्र, उपकरण और परामर्श"),
            ("cg_scheme_015", "कृत्रिम अंग / सहायक उपकरण प्रदाय योजना", "₹6000 तक के सहायक उपकरण निःशुल्क"),
            ("cg_scheme_016", "राष्ट्रीय दिव्यांगजन पुनर्वास कार्यक्रम", "मार्गदर्शन, प्रमाण पत्र एवं योजनाओं से जोड़ना")
        ]
        
        # Build schemes array in EXACT order (not database order!)
        divyang_schemes = []
        
        try:
            result = get_all_schemes()
            if 'Cursor' in str(type(result)):
                all_schemes = list(result)
            elif isinstance(result, list):
                all_schemes = result
            else:
                all_schemes = []
            
            # ✅ CRITICAL: Loop through scheme_order to maintain correct order
            for scheme_id, name, desc in scheme_order:
                found = False
                for scheme in all_schemes:
                    if scheme.get("id", "") == scheme_id:
                        divyang_schemes.append(scheme)
                        found = True
                        print(f"[DEBUG] Added {scheme_id} at position {len(divyang_schemes)}")
                        break
                if not found:
                    # Use fallback if not in database
                    divyang_schemes.append({
                        "id": scheme_id,
                        "scheme_name": {"hi": name},
                        "desc": desc
                    })
                    print(f"[DEBUG] Added fallback {scheme_id} at position {len(divyang_schemes)}")
                    
        except Exception as e:
            print(f"[ERROR] Failed to load schemes: {e}")
            # Use fallback in correct order
            for scheme_id, name, desc in scheme_order:
                divyang_schemes.append({
                    "id": scheme_id,
                    "scheme_name": {"hi": name},
                    "desc": desc
                })
        
        # ✅ DEBUG: Print final order
        print("[DEBUG] ===== FINAL last_shown_schemes ORDER =====")
        for idx, s in enumerate(divyang_schemes, 1):
            print(f"  Number {idx} → {s.get('id')}")
        print("[DEBUG] ==========================================")
        
        # Store in conversation engine for number selection
        if _conversation_engine is not None:
            _conversation_engine.last_shown_schemes = divyang_schemes
            print(f"[DEBUG] ✅ Stored {len(divyang_schemes)} schemes")
        else:
            print("[ERROR] ❌ _conversation_engine is None!")
        
        # Build response (use scheme_order for display)
        response = "**📌 दिव्यांग योजनाएं**\n\n"
        for i, (scheme_id, name, desc) in enumerate(scheme_order, 1):
            response += f"{i}. **{name}**\n"
            response += f"   📝 {desc}\n\n"
        
        response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        response += "💡 कोई **नंबर** बताएं - उस योजना की पूरी जानकारी मिलेगी।\n"
        response += "जैसे: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10\n\n"
        response += "📌 टीजी कार्ड के लिए 'टीजी कार्ड' लिखें。"
        
        return response
    
    @staticmethod
    def _get_fallback_divyang_response() -> str:
        return """**📌 दिव्यांग योजनाएं**

1. **सामाजिक सुरक्षा दिव्यांग पेंशन योजना**
2. **इंदिरा गांधी राष्ट्रीय दिव्यांग पेंशन योजना**
3. **दिव्यांगजन विवाह प्रोत्साहन योजना**
4. **दिव्यांगजन छात्रवृत्ति योजना**
5. **दिव्यांग उच्च शिक्षा प्रोत्साहन योजना**
6. **दिव्यांगजन सिविल सेवा प्रोत्साहन योजना**
7. **दिव्यांगजन विद्यार्थियों के लिये छात्रावास योजना**
8. **दिव्यांगजन हेतु शिविरों का आयोजन**
9. **कृत्रिम अंग / सहायक उपकरण प्रदाय योजना**
10. **राष्ट्रीय दिव्यांगजन पुनर्वास कार्यक्रम**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 कोई **नंबर** बताएं - उस योजना की पूरी जानकारी मिलेगी।
जैसे: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

📌 टीजी कार्ड के लिए 'टीजी कार्ड' लिखें。"""
    
    @staticmethod
    def get_family_assistance_schemes_brief_response() -> str:
        """Get family assistance schemes list"""
        try:
            result = get_all_schemes()
            if 'Cursor' in str(type(result)):
                all_schemes = list(result)
            else:
                all_schemes = result if result else []
        except Exception:
            return SchemeListResponse._get_fallback_family_response()
        
        if not all_schemes:
            return SchemeListResponse._get_fallback_family_response()
        
        family_schemes = []
        for scheme in all_schemes:
            scheme_id = scheme.get("id", "")
            if scheme_id == "cg_scheme_007":
                family_schemes.append(scheme)
        
        if not family_schemes:
            return SchemeListResponse._get_fallback_family_response()
        
        response = "**📌 परिवार सहायता योजनाएं**\n\n"
        for i, scheme in enumerate(family_schemes, 1):
            scheme_name_data = scheme.get("scheme_name", {})
            if isinstance(scheme_name_data, dict):
                name = scheme_name_data.get("hi", "योजना")
            else:
                name = str(scheme_name_data)
            
            response += f"{i}. **{name}**\n\n"
        
        response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        response += "💡 कोई **नंबर** बताएं - उस योजना की पूरी जानकारी मिलेगी。"
        return response
    
    @staticmethod
    def _get_fallback_family_response() -> str:
        return """**📌 परिवार सहायता योजनाएं**

1. **राष्ट्रीय परिवार सहायता योजना**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 कोई **नंबर** बताएं - उस योजना की पूरी जानकारी मिलेगी。"""