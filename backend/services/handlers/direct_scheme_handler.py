# backend/services/handlers/direct_scheme_handler.py
"""Handle direct scheme queries like 'Divyang pension kya hai'"""

from typing import Tuple, Optional, Dict
from backend.services.response_builder import format_scheme_full_details, extract_localized_text
from backend.database import get_scheme


class DirectSchemeHandler:
    """Handle direct scheme name queries"""
    
    # Scheme patterns mapping
    SCHEME_PATTERNS = {
        "pension": ["cg_scheme_001", "cg_scheme_006"],
        "divyang pension": ["cg_scheme_001", "cg_scheme_006"],
        "scholarship": ["cg_scheme_010", "cg_scheme_011", "cg_scheme_013"],
        "widow pension": ["cg_scheme_002"],
        "old age pension": ["cg_scheme_003", "cg_scheme_004"],
    }
    
    @staticmethod
    def handle(message: str, session_id: str, session_data: Dict, save_session_func) -> Tuple[Optional[str], Optional[str]]:
        """Handle direct scheme query"""
        msg_lower = message.lower()
        
        for pattern, scheme_ids in DirectSchemeHandler.SCHEME_PATTERNS.items():
            if pattern in msg_lower:
                scheme = get_scheme(scheme_ids[0])
                if scheme:
                    scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
                    
                    # Update session
                    session_data["current_scheme_id"] = scheme_ids[0]
                    session_data["state"] = "showing_details"
                    save_session_func(session_id, session_data)
                    
                    details = format_scheme_full_details(scheme, show_pdf=True)
                    response = f"**{scheme_name}**\n\n{details}\n\n---\n❓ **Kya aap apni patrata check karna chahenge?**\nApni age batayein."
                    
                    return (response, "success")
        
        return (None, None)


direct_scheme_handler = DirectSchemeHandler()