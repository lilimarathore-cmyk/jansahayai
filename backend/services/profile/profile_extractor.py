# backend/services/profile/profile_extractor.py
"""Extract user profile information from messages"""

import re
from typing import Dict, Any, Optional


class ProfileExtractor:
    """Extract and normalize user profile data"""
    
    @staticmethod
    def extract_age(text: str) -> Optional[int]:
        text_clean = text.strip()
        
        # Plain number
        if text_clean.isdigit():
            age = int(text_clean)
            if 0 < age < 120:
                return age
        
        patterns = [
            r'(\d{1,2})\s*(?:saal|साल|year|years|वर्ष|sal)',
            r'(?:age|उम्र|aayu|आयु)\s*(?:is|hai|है|:)?\s*(\d{1,2})',
        ]
        for p in patterns:
            m = re.search(p, text.lower())
            if m:
                age = int(m.group(1))
                if 0 < age < 120:
                    return age
        return None
    
    @staticmethod
    def extract_income(text: str) -> Optional[int]:
        patterns = [
            r'(?:income|आय|aay|kamai|कमाई)\s*(?:is|hai|है|:)?\s*(?:rs\.?|₹)?\s*(\d{4,7})',
            r'(?:rs\.?|₹)\s*(\d{4,7})',
            r'(\d{4,7})\s*(?:rupees|रुपये|rs|rupaye|income|kamai)',
        ]
        for p in patterns:
            m = re.search(p, text.lower())
            if m:
                income = int(m.group(1))
                if income > 0:
                    if income < 12000:
                        income *= 12
                    return income
        return None
    
    @staticmethod
    def extract_gender(text: str) -> Optional[str]:
        text_lower = text.lower()
        for kw in ["transgender","kinnar","किन्नर","trans","hijra","हिजड़ा","उभयलिंगी"]:
            if kw in text_lower:
                return "transgender"
        for kw in ["female","महिला","mahila","ladki","लड़की","aurat","औरत","stree","स्त्री","girl","woman"]:
            if kw in text_lower:
                return "female"
        for kw in ["male","पुरुष","purush","ladka","लड़का","aadmi","आदमी","boy","man"]:
            if kw in text_lower:
                return "male"
        return None
    
    @staticmethod
    def extract_disability(text: str) -> Optional[Dict[str, Any]]:
        text_lower = text.lower()
        result = {}
        for kw in ["andhi","अंधी","andha","अंधा","blind","drishti","दृष्टि"]:
            if kw in text_lower:
                result["type"] = "blind"
                break
        for kw in ["bahri","bahra","बहरी","बहरा","deaf","sunai","सुनाई"]:
            if kw in text_lower:
                result["type"] = "deaf"
                break
        for kw in ["langdi","langda","लंगड़ी","लंगड़ा","locomotor","chalne","चलने","apang","अपंग"]:
            if kw in text_lower:
                result["type"] = "locomotor"
                break
        if "type" not in result and any(kw in text_lower for kw in ["divyang","दिव्यांग","disabled","viklang","विकलांग"]):
            result["type"] = "general"
        pct = re.search(r'(\d{1,3})\s*%', text_lower)
        if pct:
            result["percentage"] = int(pct.group(1))
        return result if result else None
    
    @staticmethod
    def extract_education(text: str) -> Optional[Dict[str, Any]]:
        text_lower = text.lower()
        result = {}
        course_map = {"mca":"pg","एमसीए":"pg","mba":"pg","एमबीए":"pg","ma":"pg","एमए":"pg","msc":"pg","ba":"ug","bsc":"ug","bcom":"ug","btech":"ug","बीए":"ug","12th":"12th","10th":"10th"}
        for course, level in course_map.items():
            if course in text_lower:
                result["level"] = level
                result["course"] = course
                break
        yr = re.search(r'(1st|2nd|3rd|first|second|third|pehle|doosre|teesre)\s*(?:year|saal|वर्ष)', text_lower)
        if yr:
            ym = {"1st":1,"first":1,"pehle":1,"2nd":2,"second":2,"doosre":2,"3rd":3,"third":3,"teesre":3}
            result["year"] = ym.get(yr.group(1), 1)
        return result if result else None
    
    @staticmethod
    def extract_student_status(text: str) -> bool:
        return any(kw in text.lower() for kw in ["student","छात्र","vidyarthi","विद्यार्थी","padh","पढ़","study","college","कॉलेज","graduation"])
    
    @staticmethod
    def extract_certificates(text: str) -> Dict[str, bool]:
        text_lower = text.lower()
        result = {}
        if any(kw in text_lower for kw in ["disability certificate","divyang certificate","विकलांग प्रमाण","udid"]):
            result["has_disability_certificate"] = True
        if any(kw in text_lower for kw in ["aadhar","aadhaar","आधार"]):
            result["has_aadhaar"] = True
        return result
    
    @staticmethod
    def extract_bpl_status(text: str) -> Optional[bool]:
        text_lower = text.lower()
        for kw in ["bpl nahi","bpl nhi","no bpl","not bpl"]:
            if kw in text_lower:
                return False
        for kw in ["bpl","बीपीएल","bpl card","बीपीएल कार्ड"]:
            if kw in text_lower:
                return True
        return None
    
    @staticmethod
    def extract_marital_status(text: str) -> Optional[str]:
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["widow","vidhwa","विधवा"]):
            return "widow"
        if any(kw in text_lower for kw in ["married","shadi","शादी","vivahit"]):
            return "married"
        if any(kw in text_lower for kw in ["unmarried","avivahit","अविवाहित","single"]):
            return "unmarried"
        return None
    
    @staticmethod
    def extract_language(text: str) -> str:
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
        total_chars = len(text.strip())
        if total_chars == 0:
            return "hi"
        ratio = hindi_chars / total_chars
        if ratio > 0.3:
            return "hi"
        elif ratio > 0.05:
            return "hinglish"
        return "en"
    
    @classmethod
    def extract_all(cls, message: str, existing_profile: Dict = None) -> Dict[str, Any]:
        profile = existing_profile.copy() if existing_profile else {}
        
        age = cls.extract_age(message)
        if age:
            profile["age"] = age
            print(f"[EXTRACT] Age found: {age}")
        
        income = cls.extract_income(message)
        if income:
            profile["annual_income"] = income
        
        gender = cls.extract_gender(message)
        if gender:
            profile["gender"] = gender
            print(f"[EXTRACT] Gender found: {gender}")
        
        disability = cls.extract_disability(message)
        if disability:
            if "disability" not in profile:
                profile["disability"] = {}
            profile["disability"].update(disability)
        
        education = cls.extract_education(message)
        if education:
            profile["education"] = education
        
        if cls.extract_student_status(message):
            profile["is_student"] = True
            print(f"[EXTRACT] Student: True")
        
        certs = cls.extract_certificates(message)
        if certs:
            if "certificates" not in profile:
                profile["certificates"] = {}
            profile["certificates"].update(certs)
        
        bpl = cls.extract_bpl_status(message)
        if bpl is not None:
            profile["bpl_status"] = bpl
        
        marital = cls.extract_marital_status(message)
        if marital:
            profile["marital_status"] = marital
        
        language = cls.extract_language(message)
        if language:
            profile["language"] = language
        
        return profile


profile_extractor = ProfileExtractor()