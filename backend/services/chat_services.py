# ============================================
# FILE: backend/services/chat_services.py
# ============================================

from backend.services.conversation_engine import conversation_engine

def chat(user_query: str, session_id: str = "default"):
    """
    Main chat handler
    Returns: (response, status)
    """
    try:
        if not user_query or len(user_query.strip()) == 0:
            return "कृपया अपना प्रश्न लिखें।", "error"
        
        response, status = conversation_engine.process(user_query.strip(), session_id)
        
        if not response or len(response.strip()) == 0:
            return "इस जानकारी के बारे में डेटा उपलब्ध नहीं है।", "unknown"
        
        # Check if this is a zone response or needs PDF button
        # The PDF button logic is handled in chat_route.py
        
        return response, status
    
    except Exception as e:
        print(f"CHAT SERVICE ERROR: {e}")
        return "कुछ तकनीकी समस्या हो गई है। कृपया फिर से प्रयास करें।", "error"