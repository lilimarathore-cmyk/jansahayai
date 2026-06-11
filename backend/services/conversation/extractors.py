# ============================================
# FILE: backend/services/conversation/extractors.py
# COMPLETE FIXED VERSION - Fixed is_no() function for "nhi" recognition
# ============================================

import re
from typing import Optional
from backend.utils.text_normalizer import extract_numbers

class Extractors:
    
    @staticmethod
    def extract_age(text: str) -> Optional[int]:
        numbers = extract_numbers(text)
        if numbers and 1 <= numbers <= 120:
            return numbers
        return None

    @staticmethod
    def extract_disability(text: str) -> Optional[int]:
        text_lower = text.lower()
        match = re.search(r'(\d+)\s*%?\s*(?:percent|प्रतिशत)?', text_lower)
        if match:
            num = int(match.group(1))
            if 0 <= num <= 100:
                return num
        
        numbers = re.findall(r'\b(\d{1,3})\b', text_lower)
        for num_str in numbers:
            num = int(num_str)
            if 1 <= num <= 100:
                disability_context = ["विकलांग", "दिव्यांग", "disability", "disabled", "अपंग"]
                has_context = any(kw in text_lower for kw in disability_context)
                if has_context or (40 <= num <= 100):
                    return num

        disability_map = {
            "अंधा": 100, "अंधी": 100, "blind": 100, "नेत्रहीन": 100, "andha": 100,
            "बहरा": 80, "deaf": 80, "सुन नहीं सकता": 80,
            "गूंगा": 70, "बोल नहीं सकता": 70,
            "लकवा": 80, "paralysis": 80,
            "चल नहीं पाता": 70, "पैर नहीं चलता": 70,
            "हाथ नहीं चलता": 70,
            "बौना": 60, "dwarf": 60,
            "अपंग": 60, "विकलांग": 60, "disabled": 60, "divyang": 60,
        }
        for keyword, percent in disability_map.items():
            if keyword in text_lower:
                return percent
        return None

    @staticmethod
    def extract_income(text: str) -> Optional[int]:
        numbers = extract_numbers(text)
        if numbers:
            if ("लाख" in text or "lakh" in text) and numbers < 100:
                return numbers * 100000
            return numbers
        return None

    @staticmethod
    def extract_education_level(text: str) -> Optional[str]:
        text_clean = text.strip()
        if text_clean == "1":
            return "स्नातक (Graduation)"
        elif text_clean == "2":
            return "परास्नातक (Post Graduation)"
        elif text_clean == "3":
            return "डिप्लोमा (Diploma)"
        elif text_clean == "4":
            return "आईटीआई (ITI)"
        return None

    @staticmethod
    def extract_exam_type(text: str) -> Optional[str]:
        text_clean = text.strip()
        if text_clean == "1":
            return "UPSC"
        elif text_clean == "2":
            return "CGPSC"
        return None

    @staticmethod
    def extract_distance(text: str) -> Optional[int]:
        numbers = extract_numbers(text)
        return numbers if numbers else None

    @staticmethod
    def extract_education_level_hostel(text: str) -> Optional[str]:
        text_clean = text.strip()
        if text_clean == "1":
            return "12वीं उत्तीर्ण (12th Pass)"
        elif text_clean == "2":
            return "महाविद्यालय में अध्ययनरत (College Student)"
        return None

    @staticmethod
    def extract_bpl_status(text: str) -> Optional[str]:
        if Extractors.is_yes(text):
            return "हाँ"
        elif Extractors.is_no(text):
            return "नहीं"
        return None

    @staticmethod
    def extract_secc_status(text: str) -> Optional[str]:
        if Extractors.is_yes(text):
            return "हाँ"
        elif Extractors.is_no(text):
            return "नहीं"
        return None

    @staticmethod
    def extract_widow_category_from_keywords(text: str) -> Optional[str]:
        text_lower = text.lower()
        widow_keywords = ["विधवा", "vidhva", "widow", "बेवा"]
        for kw in widow_keywords:
            if kw in text_lower:
                return "widow"
        abandoned_keywords = ["तलाकशुदा", "परित्यक्ता", "talakshuda", "abandoned"]
        for kw in abandoned_keywords:
            if kw in text_lower:
                return "abandoned"
        return None

    # ========== YES/NO HELPER METHODS ==========
    @staticmethod
    def is_yes(text: str) -> bool:
        """Check if user responded with YES (हाँ, haan, yes, etc.)"""
        if not text:
            return False
        text_lower = text.lower().strip()
        
        # Clean the text
        text_clean = re.sub(r'[^\w]', '', text_lower)
        
        # Exact matches for common "yes" variations
        yes_variations = ["haan", "han", "hn", "ha", "h", "y", "yes", "ok", "हाँ", "हां", "haa", "हाँजी", "haanji", "हांजी", "yeah", "yep", "okay"]
        
        if text_clean in yes_variations:
            return True
        
        # Check if text starts with any variation
        for variation in yes_variations:
            if text_lower.startswith(variation):
                return True
        
        return False

    @staticmethod
    def is_no(text: str) -> bool:
        """Check if user responded with NO (नहीं, nahi, no, etc.)"""
        if not text:
            return False
        text_lower = text.lower().strip()
        
        # Clean the text - remove spaces, punctuation, etc.
        text_clean = re.sub(r'[^\w]', '', text_lower)
        
        # Exact matches for common "no" variations
        no_variations = [
            "nhi", "nahi", "nhin", "no", "ni", "n", "na", "nope",
            "नहीं", "नही", "ना", "न", "nhe", "ne", "nh", "nahii", "nahin"
        ]
        
        # Check exact match on cleaned text
        if text_clean in no_variations:
            return True
        
        # Check if original text starts with any variation (for "nhi ", "nhi.", "nhi\n", etc.)
        for variation in no_variations:
            if text_lower.startswith(variation):
                return True
        
        # Additional check for very short inputs like "n", "no", "na"
        if len(text_clean) <= 2 and text_clean in ["n", "no", "na", "ni", "nh"]:
            return True
        
        return False