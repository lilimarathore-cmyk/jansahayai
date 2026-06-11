# ============================================
# FILE: backend/routes/chat_route.py
# COMPLETE FIXED VERSION - TG Card PDF button working
# ============================================

from fastapi import APIRouter
from backend.database import log_chat
from datetime import datetime
from backend.schemas.chat_schema import ChatRequest, ChatResponse
from backend.services.chat_services import chat

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_api(request: ChatRequest):
    reply, status = chat(request.message, request.session_id)
    
    scheme_id = None
    is_eligible = False
    
    # ========== STEP 1: CHECK ELIGIBILITY ==========
    eligible_patterns = [
        "पात्र हैं",
        "पात्र है",
        "eligible",
        "आप पात्र हैं",
        "✅ **आप",
        "पात्र हैं!**",
        "**आप पात्र हैं**",
        "पात्र हैं!",
        "आप इस योजना के लिए पात्र हैं"
    ]
    
    if any(pattern in reply for pattern in eligible_patterns):
        is_eligible = True
        
        # ========== STEP 2: DETECT SCHEME FROM REPLY ==========
        
        # Sukhad Sahara (Widow Pension)
        if "✅ **आप सुखद सहारा पेंशन योजना के लिए पात्र हैं!**" in reply or \
           "सुखद सहारा पेंशन योजना" in reply or \
           "Sukhad Sahara" in reply:
            scheme_id = "cg_scheme_002"
        
        # Indira Gandhi Widow
        elif "✅ **आप इंदिरा गांधी राष्ट्रीय विधवा पेंशन योजना के लिए पात्र हैं!**" in reply or \
             "इंदिरा गांधी विधवा पेंशन योजना" in reply or \
             "Indira Gandhi Widow" in reply:
            scheme_id = "cg_scheme_005"
        
        # Indira Gandhi Old Age
        elif "✅ **आप इंदिरा गांधी राष्ट्रीय वृद्धावस्था पेंशन योजना के लिए पात्र हैं! (₹500 प्रति माह)**" in reply or \
             "इंदिरा गांधी राष्ट्रीय वृद्धावस्था पेंशन योजना" in reply or \
             "Indira Gandhi Old Age" in reply:
            scheme_id = "cg_scheme_004"
        
        # Mukhyamantri Pension
        elif "✅ **आप मुख्यमंत्री पेंशन योजना - 2018 के लिए पात्र हैं!**" in reply or \
             "मुख्यमंत्री पेंशन योजना" in reply or \
             "Mukhyamantri Pension" in reply:
            scheme_id = "cg_scheme_003"
        
        # Indira Gandhi Divyang
        elif "इंदिरा गांधी राष्ट्रीय दिव्यांग पेंशन योजना" in reply or \
             "Indira Gandhi Divyang" in reply:
            scheme_id = "cg_scheme_006"
        
        # Social Security Divyang
        elif "सामाजिक सुरक्षा दिव्यांग पेंशन योजना" in reply or \
             "Social Security Divyang" in reply:
            scheme_id = "cg_scheme_001"
        
        # Family Assistance
        elif "राष्ट्रीय परिवार सहायता योजना" in reply or \
             "Family Assistance" in reply or \
             "National Family Benefit" in reply or \
             "आप राष्ट्रीय परिवार सहायता योजना के लिए पात्र हैं!" in reply:
            scheme_id = "cg_scheme_007"
        
        # Scholarship
        elif "दिव्यांगजन छात्रवृत्ति योजना" in reply or \
             "Divyang Scholarship" in reply or \
             "scholarship" in reply.lower():
            scheme_id = "cg_scheme_010"
        
        # Higher Education
        elif "दिव्यांग उच्च शिक्षा प्रोत्साहन योजना" in reply or \
             "Higher Education" in reply:
            scheme_id = "cg_scheme_011"
        
        # Civil Services
        elif "दिव्यांगजन सिविल सेवा प्रोत्साहन योजना" in reply or \
             "Civil Services" in reply:
            scheme_id = "cg_scheme_012"
        
        # Marriage
        elif "दिव्यांगजन विवाह प्रोत्साहन योजना" in reply or \
             "Marriage Incentive" in reply:
            scheme_id = "cg_scheme_009"
        
        # Hostel
        elif "दिव्यांगजन विद्यार्थियों के लिये छात्रावास योजना" in reply or \
             "Hostel" in reply:
            scheme_id = "cg_scheme_013"
        
        # Camp
        elif "दिव्यांगजन हेतु शिविरों का आयोजन" in reply or \
             "Camp" in reply:
            scheme_id = "cg_scheme_014"
        
        # Assistive Devices
        elif "कृत्रिम अंग / सहायक उपकरण प्रदाय योजना" in reply or \
             "Assistive Devices" in reply or \
             "Wheelchair" in reply:
            scheme_id = "cg_scheme_015"
        
        # Rehabilitation
        elif "राष्ट्रीय दिव्यांगजन पुनर्वास कार्यक्रम" in reply or \
             "Rehabilitation" in reply:
            scheme_id = "cg_scheme_016"
    
    # ========== STEP 3: SPECIAL CASE - TG CARD (Always eligible) ==========
    # Check for TG Card in reply with multiple patterns
    tg_card_patterns = [
        "उभयलिंगी व्यक्तियों को टी.जी. कार्ड जारी करना",
        "उभयलिंगी व्यक्तियों",
        "टी.जी. कार्ड",
        "TG Card",
        "tg card",
        "transgender card",
        "ट्रांसजेंडर",
        "ट्रांसजेंडर कार्ड"
    ]
    
    reply_lower = reply.lower()
    if any(pattern.lower() in reply_lower for pattern in tg_card_patterns):
        scheme_id = "cg_scheme_008"
        is_eligible = True
    
    # ========== STEP 4: FALLBACK TO SESSION ==========
    if not scheme_id and is_eligible:
        try:
            from backend.services.conversation_engine import conversation_engine
            if request.session_id in conversation_engine.user_sessions:
                session_data = conversation_engine.user_sessions[request.session_id]
                scheme_id = session_data.get("last_active_scheme_id")
                if not scheme_id:
                    current = session_data.get("current_requested_scheme")
                    if current:
                        scheme_id = f"cg_scheme_{current}"
                if not scheme_id:
                    selected = session_data.get("selected_scheme_id")
                    if selected:
                        scheme_id = selected
        except:
            pass
    
    # ========== STEP 5: CONTINUATION MENU DETECTION ==========
    continuation_patterns = [
        "अन्य योजनाओं के लिए नंबर बताएं",
        "अन्य योजना के लिए नंबर बताएं",
        "कोई नंबर बताएं",
        "अन्य योजना के लिए नंबर",
        "💡 **अन्य योजना के लिए नंबर बताएं:**"
    ]
    is_continuation_only = any(pattern in reply for pattern in continuation_patterns)
    is_eligible_text = any(pattern in reply for pattern in ["पात्र हैं", "पात्र है", "eligible"])
    
    if is_continuation_only and not is_eligible_text:
        scheme_id = None
        is_eligible = False

    # ========== LOGGING ==========
    try:
        intent = "unknown"
        msg = request.message.lower()
        
        if any(w in msg for w in ["दस्तावेज़", "document", "कागज"]):
            intent = "ask_documents"
        elif any(w in msg for w in ["पात्र", "eligible", "योग्य"]):
            intent = "ask_eligibility"
        elif any(w in msg for w in ["पैसा", "राशि", "कितना", "₹", "benefit"]):
            intent = "ask_benefits"
        elif any(w in msg for w in ["आवेदन", "apply", "form", "कैसे करें"]):
            intent = "ask_process"
        elif any(w in msg for w in ["नमस्ते", "hello", "हैलो", "hi"]):
            intent = "greeting"
        elif any(w in msg for w in ["धन्यवाद", "bye", "शुक्रिया"]):
            intent = "farewell"
        elif any(w in msg for w in ["सभी योजना", "list", "सूची"]):
            intent = "ask_schemes_list"

        is_fallback = any(p in reply for p in [
            "समझ नहीं आया", "जानकारी उपलब्ध नहीं",
            "कृपया दोबारा", "तकनीकी समस्या"
        ])

        log_chat({
            "session_id": request.session_id,
            "user_message": request.message,
            "bot_reply": reply,
            "intent": intent,
            "scheme_id": scheme_id,
            "is_eligible": is_eligible,
            "is_fallback": is_fallback,
            "status": status,
            "timestamp": datetime.now(),
        })
    except Exception as log_err:
        print(f"Logging error: {log_err}")
        
    # ========== STEP 6: RETURN RESPONSE ==========
    return ChatResponse(
        status=status,
        response=reply,
        session_id=request.session_id,
        scheme_id=scheme_id if is_eligible else None,
        is_eligible=is_eligible
    )