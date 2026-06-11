# backend/services/recommendation_engine.py
# NEW FILE - Profile-based scheme recommendations

from typing import List, Dict, Any, Tuple
from backend.database import get_all_schemes
from backend.services.conversation.eligibility import EligibilityChecker
from backend.services.response_builder import extract_localized_text


class RecommendationEngine:
    """Recommends schemes based on user profile"""
    
    @staticmethod
    def get_recommendations(profile: Dict[str, Any], limit: int = 5) -> List[Tuple[str, Dict, float]]:
        """Get recommended schemes based on user profile with relevance score"""
        all_schemes = get_all_schemes()
        scored_schemes = []
        
        age = profile.get("age")
        disability_type = profile.get("disability_type", "")
        is_student = profile.get("is_student", False)
        
        for scheme in all_schemes:
            scheme_id = scheme.get("id")
            if not scheme_id or scheme_id == "cg_scheme_008":  # Skip TG Card
                continue
            
            # Calculate relevance score
            score = 0
            
            # Age match
            if age is not None:
                scheme_age_rules = {
                    "cg_scheme_001": (6, 17),
                    "cg_scheme_006": (18, 100),
                    "cg_scheme_002": (18, 39),
                    "cg_scheme_003": (60, 100),
                    "cg_scheme_004": (60, 100),
                    "cg_scheme_005": (18, 60),
                }
                if scheme_id in scheme_age_rules:
                    min_age, max_age = scheme_age_rules[scheme_id]
                    if min_age <= age <= max_age:
                        score += 50
            
            # Disability type match
            if disability_type == "blind":
                if scheme_id in ["cg_scheme_001", "cg_scheme_006", "cg_scheme_010", "cg_scheme_013", "cg_scheme_014", "cg_scheme_015", "cg_scheme_016"]:
                    score += 40
            
            # Student match
            if is_student:
                if scheme_id in ["cg_scheme_010", "cg_scheme_011", "cg_scheme_013"]:
                    score += 30
            
            # Check eligibility
            is_eligible, _ = EligibilityChecker.check_eligibility(scheme_id, **profile)
            if is_eligible:
                score += 100
            
            if score > 0:
                scored_schemes.append((scheme_id, scheme, score))
        
        # Sort by score (highest first)
        scored_schemes.sort(key=lambda x: x[2], reverse=True)
        
        return scored_schemes[:limit]
    
    @staticmethod
    def format_recommendations(schemes: List[Tuple[str, Dict, float]]) -> str:
        """Format recommendations for display"""
        if not schemes:
            return "❌ Aapke profile ke anusar koi scheme eligible nahi mili."
        
        response = "**✅ Aapke profile ke liye recommended schemes:**\n\n"
        for i, (scheme_id, scheme, score) in enumerate(schemes, 1):
            scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
            benefits = extract_localized_text(scheme.get("content", {}).get("benefits", {}).get("text"))
            if not benefits:
                benefits = "Financial assistance provided"
            response += f"{i}. **{scheme_name}**\n   📝 {benefits}\n\n"
        
        response += "---\n💡 **Koi number batayein** - scheme ki puri jankari ke liye."
        return response


recommendation_engine = RecommendationEngine()