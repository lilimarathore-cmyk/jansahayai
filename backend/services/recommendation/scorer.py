# backend/services/recommendation/scorer.py
"""Score schemes based on user profile"""

from typing import List, Tuple, Dict
from backend.database import get_all_schemes


class RecommendationScorer:
    """Score and rank schemes based on user profile"""
    
    CATEGORY_BASE_SCORES = {
        "pension": 30, "scholarship": 40, "education": 40, "hostel": 35,
        "equipment": 30, "marriage": 20, "tg_card": 50, "family_assistance": 35,
        "camp": 15, "general": 10,
    }
    
    PROFILE_BONUSES = {
        "is_student": {"scholarship": 50, "education": 40, "hostel": 35, "equipment": 25, "pension": 20},
        "has_disability": {"scholarship": 30, "equipment": 40, "pension": 30, "hostel": 25, "marriage": 25, "camp": 20},
        "disability_blind": {"scholarship": 45, "equipment": 50, "education": 40},
        "disability_deaf": {"scholarship": 45, "equipment": 50, "education": 40},
        "disability_locomotor": {"scholarship": 45, "equipment": 60, "pension": 35},
        "bpl": {"pension": 40, "family_assistance": 50, "scholarship": 30, "hostel": 30},
        "low_income": {"pension": 35, "scholarship": 35, "hostel": 30, "family_assistance": 30},
        "has_certificate": {"pension": 30, "scholarship": 25, "equipment": 25},
        "female": {"pension": 20, "scholarship": 25, "marriage": 30},
        "transgender": {"tg_card": 100, "pension": 30, "scholarship": 30},
        "widow": {"pension": 100, "family_assistance": 50},
        "old_age": {"pension": 80},
        "young_student": {"scholarship": 60, "education": 50, "hostel": 40},
    }
    
    @staticmethod
    def _get_profile_attributes(profile: Dict) -> List[str]:
        attrs = []
        if profile.get("is_student"):
            attrs.append("is_student")
        disability = profile.get("disability", {})
        if disability:
            attrs.append("has_disability")
            dtype = disability.get("type", "") if isinstance(disability, dict) else ""
            if dtype == "blind":
                attrs.append("disability_blind")
            elif dtype == "deaf":
                attrs.append("disability_deaf")
            elif dtype == "locomotor":
                attrs.append("disability_locomotor")
        if profile.get("bpl_status"):
            attrs.append("bpl")
        income = profile.get("annual_income", 0)
        if income and income < 100000:
            attrs.append("low_income")
        certs = profile.get("certificates", {})
        if certs.get("has_disability_certificate"):
            attrs.append("has_certificate")
        gender = profile.get("gender", "")
        if gender == "female":
            attrs.append("female")
        elif gender == "transgender":
            attrs.append("transgender")
        if profile.get("marital_status") == "widow":
            attrs.append("widow")
        age = profile.get("age", 0)
        if age and age >= 60:
            attrs.append("old_age")
        elif age and age < 25:
            attrs.append("young_student")
        return attrs
    
    @staticmethod
    def _get_scheme_categories(scheme: Dict) -> List[str]:
        categories = []
        meta = scheme.get("meta", {})
        cat = meta.get("category", "")
        if cat:
            categories.append(cat)
        nlp = scheme.get("nlp", {})
        keywords = nlp.get("keywords", [])
        kw_map = {
            "pension": "pension", "scholarship": "scholarship", "education": "education",
            "hostel": "hostel", "equipment": "equipment", "marriage": "marriage",
            "tg": "tg_card", "transgender": "tg_card", "family": "family_assistance",
            "camp": "camp", "medical": "camp", "wheelchair": "equipment",
            "hearing": "equipment", "cane": "equipment",
        }
        for kw in keywords:
            for key, c in kw_map.items():
                if key in kw.lower() and c not in categories:
                    categories.append(c)
        return categories if categories else ["general"]
    
    @staticmethod
    def score_scheme(scheme: Dict, profile: Dict) -> float:
        score = 0.0
        profile_attrs = RecommendationScorer._get_profile_attributes(profile)
        scheme_cats = RecommendationScorer._get_scheme_categories(scheme)
        for cat in scheme_cats:
            score += RecommendationScorer.CATEGORY_BASE_SCORES.get(cat, 10)
        for attr in profile_attrs:
            bonuses = RecommendationScorer.PROFILE_BONUSES.get(attr, {})
            for cat in scheme_cats:
                score += bonuses.get(cat, 0)
        age = profile.get("age", 0)
        if age:
            nlp = scheme.get("nlp", {})
            age_constraints = nlp.get("age_constraints", {})
            if age_constraints:
                min_age = age_constraints.get("min_age", 0)
                max_age = age_constraints.get("max_age", 200)
                if min_age <= age <= max_age:
                    score += 20
                else:
                    score -= 50
        return max(0, score)
    
    @staticmethod
    def get_scored_schemes(profile: Dict, limit: int = 8) -> List[Tuple[str, Dict, float]]:
        all_schemes = get_all_schemes()
        if not all_schemes:
            return []
        scored = []
        for scheme in all_schemes:
            sid = scheme.get("id", scheme.get("scheme_id", ""))
            s = RecommendationScorer.score_scheme(scheme, profile)
            if s > 0:
                scored.append((sid, scheme, s))
        scored.sort(key=lambda x: x[2], reverse=True)
        return scored[:limit]


recommendation_scorer = RecommendationScorer()