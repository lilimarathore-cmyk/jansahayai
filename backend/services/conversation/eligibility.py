# backend/services/conversation/eligibility.py
# COMPLETE FIXED - Age-based and disability-type filtering

from typing import Tuple, Optional, Dict, Any, List
from backend.database import get_all_schemes
from backend.services.response_builder import extract_localized_text


class EligibilityChecker:
    
    @staticmethod
    def check_eligibility(scheme_id: str, **kwargs) -> Tuple[bool, str]:
        """Check eligibility for a single scheme"""
        reasons = []
        
        age = kwargs.get("age")
        disability = kwargs.get("disability", kwargs.get("disability_percentage"))
        disability_type = kwargs.get("disability_type", "")
        income = kwargs.get("income")
        bpl_status = kwargs.get("bpl_status")
        is_student = kwargs.get("is_student", False)
        
        # ========== SCHEME 001: Divyang Pension (6-17 years) ==========
        if scheme_id == "cg_scheme_001":
            if age is not None:
                if age < 6:
                    reasons.append(f"Age {age} years hai. Minimum 6 years chahiye.")
                elif age > 17:
                    reasons.append(f"Age {age} years hai. Ye scheme 6-17 years ke bachchon ke liye hai.")
            if disability is not None and disability < 40:
                reasons.append(f"Disability {disability}% hai. Minimum 40% chahiye.")
            if not disability_type:
                reasons.append("Divyang certificate required.")
        
        # ========== SCHEME 002: Widow Pension (18-39 years) ==========
        elif scheme_id == "cg_scheme_002":
            # Blind users are NOT eligible
            if disability_type == "blind":
                reasons.append("यह योजना विधवा महिलाओं के लिए है, दिव्यांगजन के लिए नहीं।")
            elif age is not None:
                if age < 18:
                    reasons.append(f"Age {age} years hai. Minimum 18 years chahiye.")
                elif age > 39:
                    reasons.append(f"Age {age} years hai. Maximum 39 years hai.")
            else:
                reasons.append("Age information missing.")
        
        # ========== SCHEME 003: Mukhyamantri Pension ==========
        elif scheme_id == "cg_scheme_003":
            if age is not None and age < 60:
                reasons.append(f"Age {age} years hai. Minimum 60 years chahiye.")
            if kwargs.get("secc_status") != "हाँ":
                reasons.append("SECC 2011 list me naam hona chahiye.")
        
        # ========== SCHEME 004: Indira Gandhi Old Age ==========
        elif scheme_id == "cg_scheme_004":
            if age is not None and age < 60:
                reasons.append(f"Age {age} years hai. Minimum 60 years chahiye.")
            if bpl_status != "yes":
                reasons.append("BPL list me naam hona chahiye.")
        
        # ========== SCHEME 005: Indira Gandhi Widow ==========
        elif scheme_id == "cg_scheme_005":
            if disability_type == "blind":
                reasons.append("यह योजना विधवा महिलाओं के लिए है, दिव्यांगजन के लिए नहीं।")
            elif age is not None:
                if age < 18:
                    reasons.append(f"Age {age} years hai. Minimum 18 years chahiye.")
                elif age > 60:
                    reasons.append(f"Age {age} years hai. Maximum 60 years hai.")
            if bpl_status != "yes":
                reasons.append("BPL list me naam hona chahiye.")
        
        # ========== SCHEME 006: Indira Gandhi Divyang (18+) ==========
        elif scheme_id == "cg_scheme_006":
            if age is not None and age < 18:
                reasons.append(f"Age {age} years hai. 18+ years chahiye.")
            if disability is not None and disability < 40:
                reasons.append(f"Disability {disability}% hai. Minimum 40% chahiye.")
            if income is not None and income > 200000:
                reasons.append(f"Annual income ₹{income:,} hai. ₹2,00,000 se kam honi chahiye.")
        
        # ========== SCHEME 007: Family Assistance ==========
        elif scheme_id == "cg_scheme_007":
            if age is not None:
                if age < 18:
                    reasons.append(f"Deceased age {age} years hai. 18+ chahiye.")
                elif age > 60:
                    reasons.append(f"Deceased age {age} years hai. Maximum 60 years hai.")
            if bpl_status != "yes":
                reasons.append("BPL list me naam hona chahiye.")
        
        # ========== SCHEME 008: TG Card ==========
        elif scheme_id == "cg_scheme_008":
            pass  # Always eligible
        
        # ========== SCHEME 009: Marriage Incentive ==========
        elif scheme_id == "cg_scheme_009":
            male_age = kwargs.get("male_age")
            female_age = kwargs.get("female_age")
            if male_age is not None and (male_age < 21 or male_age > 45):
                reasons.append(f"Male age {male_age} years hai. 21-45 chahiye.")
            if female_age is not None and (female_age < 18 or female_age > 45):
                reasons.append(f"Female age {female_age} years hai. 18-45 chahiye.")
            if disability is not None and disability < 40:
                reasons.append(f"Disability {disability}% hai. Minimum 40% chahiye.")
        
        # ========== SCHEME 010: Scholarship ==========
        elif scheme_id == "cg_scheme_010":
            class_grade = kwargs.get("class_grade")
            if disability is not None and disability < 40:
                reasons.append(f"Disability {disability}% hai. Minimum 40% chahiye.")
            if class_grade is not None and (class_grade < 1 or class_grade > 12):
                reasons.append(f"Class {class_grade} hai. Class 1-12 ke liye hai.")
            if not is_student:
                reasons.append("Regular student hona chahiye.")
        
        # ========== SCHEME 011: Higher Education ==========
        elif scheme_id == "cg_scheme_011":
            if age is not None and age < 18:
                reasons.append(f"Age {age} years hai. 18+ chahiye.")
            if disability is not None and disability < 40:
                reasons.append(f"Disability {disability}% hai. Minimum 40% chahiye.")
        
        # ========== SCHEME 012: Civil Services ==========
        elif scheme_id == "cg_scheme_012":
            if disability is not None and disability < 40:
                reasons.append(f"Disability {disability}% hai. Minimum 40% chahiye.")
        
        # ========== SCHEME 013: Hostel ==========
        elif scheme_id == "cg_scheme_013":
            distance = kwargs.get("distance")
            if disability is not None and disability < 40:
                reasons.append(f"Disability {disability}% hai. Minimum 40% chahiye.")
            if distance is not None and distance <= 20:
                reasons.append(f"Distance {distance} km hai. 20 km se zyada chahiye.")
        
        # ========== SCHEME 014: Camp ==========
        elif scheme_id == "cg_scheme_014":
            if disability is not None and disability < 40:
                reasons.append(f"Disability {disability}% hai. Minimum 40% chahiye.")
        
        # ========== SCHEME 015: Assistive Devices ==========
        elif scheme_id == "cg_scheme_015":
            if disability is not None and disability < 40:
                reasons.append(f"Disability {disability}% hai. Minimum 40% chahiye.")
            if income is not None and income >= 6500:
                reasons.append(f"Monthly income ₹{income} hai. ₹6500 se kam honi chahiye.")
        
        # ========== SCHEME 016: Rehabilitation ==========
        elif scheme_id == "cg_scheme_016":
            if disability is not None and disability < 40:
                reasons.append(f"Disability {disability}% hai. Minimum 40% chahiye.")
        
        if reasons:
            return False, "\n".join(reasons)
        return True, "Eligible"
    
    @staticmethod
    def get_all_eligible_schemes(user_entities: Dict[str, Any]) -> List[Tuple[str, Dict, str]]:
        """Get all schemes user is eligible for with smart filtering"""
        all_schemes = get_all_schemes()
        eligible_schemes = []
        seen_ids = set()
        
        age = user_entities.get("age")
        disability_type = user_entities.get("disability_type", "")
        is_blind = disability_type == "blind"
        
        # Define scheme categories
        divyang_schemes = ["cg_scheme_001", "cg_scheme_006", "cg_scheme_009", "cg_scheme_010", 
                           "cg_scheme_011", "cg_scheme_012", "cg_scheme_013", "cg_scheme_014", 
                           "cg_scheme_015", "cg_scheme_016"]
        widow_schemes = ["cg_scheme_002", "cg_scheme_005"]
        old_age_schemes = ["cg_scheme_003", "cg_scheme_004"]
        
        for scheme in all_schemes:
            scheme_id = scheme.get("id")
            if not scheme_id or scheme_id in seen_ids:
                continue
            seen_ids.add(scheme_id)
            
            # Skip TG Card in list
            if scheme_id == "cg_scheme_008":
                continue
            
            # For blind users, skip widow schemes
            if is_blind and scheme_id in widow_schemes:
                print(f"[FILTER] Skipping widow scheme {scheme_id} for blind user")
                continue
            
            # For children (under 18), skip adult schemes
            if age is not None and age < 18:
                if scheme_id in old_age_schemes:
                    continue
                if scheme_id == "cg_scheme_006" and age < 18:
                    continue
            
            is_eligible, reason = EligibilityChecker.check_eligibility(scheme_id, **user_entities)
            if is_eligible:
                eligible_schemes.append((scheme_id, scheme, reason))
        
        print(f"[ELIGIBLE] Found {len(eligible_schemes)} schemes")
        return eligible_schemes


eligibility_checker = EligibilityChecker()