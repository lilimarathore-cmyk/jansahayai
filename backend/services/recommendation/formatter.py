# backend/services/recommendation/formatter.py
"""Format recommendations for display"""

from typing import List, Dict, Tuple
from backend.services.response_builder import extract_localized_text


class RecommendationFormatter:
    """Format scheme recommendations with numbers"""
    
    @staticmethod
    def format(schemes: List[Tuple[str, Dict, int]]) -> str:
        """Format recommendations with numbers"""
        if not schemes:
            return "❌ Aapke profile ke anusar koi yojna eligible nahi mili."
        
        response = "**✅ Aapke liye upyukt yojnayein:**\n\n"
        
        for i, (_, scheme, _) in enumerate(schemes, 1):
            name = extract_localized_text(scheme.get("scheme_name"), "hi")
            benefits = extract_localized_text(scheme.get("content", {}).get("benefits", {}).get("text"))
            if not benefits:
                benefits = "Aarthik sahayta pradaan ki jaati hai"
            
            response += f"{i}. **{name}**\n   📝 {benefits}\n\n"
        
        response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        response += "💡 **Kisi bhi yojna ki puri jankari ke liye number likhiye:** 1, 2, 3..."
        
        return response


recommendation_formatter = RecommendationFormatter()