# backend/services/intent_engine.py
"""Intent detection + Entity extraction + Language detection"""

import re
from typing import Dict, Any, Optional


class IntentEngine:
    """Detect intent, extract entities, and identify language"""
    
    INTENT_PATTERNS = {
        "profile_scheme_query": [
            r"(mere|मेरे|mujhe|मुझे|meri|मेरी).*(liye|लिए|ke liye|के लिए)",
            r"(kaun|कौन).*(scheme|yojna|योजना|schemes|yojnayein|योजनाएं)",
            r"(batao|बताओ|batayein|बताएं|suggest|suggest karo)",
        ],
        "scheme_info": [
            r"(kya hai|क्या है|batao|बताओ|jankari|जानकारी|details|detail)",
            r"(ke baare mein|के बारे में|ke bare me)",
        ],
        "eligibility_check": [
            r"(eligible|पात्र|patra|yogya|योग्य)",
            r"(can i|kya main|क्या मैं|apply kar|apply kr)",
            r"(milega|मिलेगा|mil sakti|मिल सकती)",
        ],
        "followup_documents": [
            r"(document|दस्तावेज|dastavej|doc|docs)",
            r"(kya.*lagega|kya.*chahiye|क्या.*लगेगा|क्या.*चाहिए)",
        ],
        "followup_where": [
            r"(kahan|कहाँ|where|kaha|office|कार्यालय)",
            r"(apply kahan|आवेदन कहाँ|submit kahan)",
            r"(address|पता|pata|location|jagah|जगह)",
        ],
        "followup_how": [
            r"(kaise|कैसे|how|process|प्रक्रिया|prakriya)",
            r"(apply|आवेदन|aavedan|form|फॉर्म|register)",
        ],
        "followup_benefits": [
            r"(kya milta|क्या मिलता|benefit|labh|लाभ|fayda|फायदा)",
        ],
        "greeting": [
            r"^(hi|hello|hey|namaste|नमस्ते|नमस्कार|hii|heylo|hy)$",
        ],
        "negative": [r"^(nahi|नहीं|no|nhi|not|bas|enough)$"],
        "affirmative": [r"^(haan|हाँ|हां|yes|ji|ha|ok|okay|thik|ठीक)$"],
        "number_selection": [
            r"^\d+$",
            r"^(first|second|third|fourth|fifth|pehla|doosra|teesra|chautha|paanchwa)$",
        ],
    }
    
    ENTITY_PATTERNS = {
        "age": [
            r'(\d{1,2})\s*(?:saal|साल|year|years|वर्ष|sal)',
            r'(?:age|उम्र|aayu|आयु)\s*(?:is|hai|है|:)?\s*(\d{1,2})',
        ],
        "income": [
            r'(?:income|आय|aay|kamai|कमाई|salary|तनख्वाह)\s*(?:is|hai|है|:)?\s*(?:rs\.?|₹)?\s*(\d{4,7})',
            r'(?:rs\.?|₹)\s*(\d{4,7})',
            r'(\d{4,7})\s*(?:rupees|रुपये|rs|rupaye|income|kamai)',
        ],
        "disability_type": [
            r'(andhi|अंधी|andha|अंधा|blind|drishti|दृष्टि)',
            r'(bahra|बहरा|deaf|sunai|सुनाई)',
            r'(langda|लंगड़ा|locomotor|chalne|चलने)',
            r'(divyang|दिव्यांग|disabled|viklang|विकलांग)',
        ],
        "disability_percentage": [
            r'(\d{1,3})\s*%\s*(?:disability|divyang|viklang|विकलांगता)',
        ],
        "gender": [
            r'\b(female|महिला|mahila|ladki|लड़की|aurat|औरत|stree|स्त्री)\b',
            r'\b(male|पुरुष|purush|ladka|लड़का|aadmi|आदमी)\b',
            r'\b(transgender|kinnar|किन्नर|trans|hijra|हिजड़ा|ubhaylingi|उभयलिंगी)\b',
        ],
        "education": [
            r'(?:padh|पढ़|study|student|छात्र|vidyarthi|विद्यार्थी).*?(?:raha|रहा|rahi|रही|hu|हूँ|ho|हो)',
            r'(ba|बीए|bsc|बीएससी|bcom|बीकॉम|ma|एमए|msc|mca|एमसीए|mba|एमबीए|btech|बीटेक|mtech|phd|पीएचडी|diploma|डिप्लोमा)',
            r'(1st|2nd|3rd|4th|first|second|third|fourth|pehle|doosre|teesre|chauthe)\s*(?:year|saal|वर्ष|semester|sem)',
        ],
        "bpl_status": [r'(bpl|बीपीएल|below poverty|bpl card|बीपीएल कार्ड)'],
        "marital_status": [
            r'(widow|vidhwa|विधवा)',
            r'(married|shadi|शादी|vivahit|विवाहित)',
            r'(unmarried|avivahit|अविवाहित|single)',
            r'(divorced|talak|तलाक|parityakta|परित्यक्ता)',
        ],
        "certificate": [
            r'(certificate|प्रमाण पत्र|praman patra)',
            r'(disability certificate|divyang certificate|विकलांग प्रमाण)',
        ],
    }
    
    HINDI_KEYWORDS = [
        "है", "हूँ", "हो", "क्या", "कौन", "कहाँ", "कैसे",
        "मेरा", "मेरी", "मेरे", "आपका", "योजना", "जानकारी",
        "पेंशन", "दिव्यांग", "विधवा", "छात्रवृत्ति", "आवेदन",
        "दस्तावेज", "पात्रता", "लाभ", "में", "को", "से", "के",
    ]
    
    @classmethod
    def detect_intent(cls, message: str) -> str:
        msg_lower = message.lower().strip()
        scores = {}
        for intent, patterns in cls.INTENT_PATTERNS.items():
            score = sum(1 for p in patterns if re.search(p, msg_lower))
            if score > 0:
                scores[intent] = score
        return max(scores, key=scores.get) if scores else "unknown"
    
    @classmethod
    def extract_entities(cls, message: str) -> Dict[str, Any]:
        entities = {}
        msg_lower = message.lower()
        
        for p in cls.ENTITY_PATTERNS["age"]:
            m = re.search(p, msg_lower)
            if m:
                age = int(m.group(1))
                if 0 < age < 120:
                    entities["age"] = age
                    break
        
        for p in cls.ENTITY_PATTERNS["income"]:
            m = re.search(p, msg_lower)
            if m:
                income = int(m.group(1))
                if income > 0:
                    if income < 12000:
                        income *= 12
                    entities["annual_income"] = income
                    break
        
        for p in cls.ENTITY_PATTERNS["disability_type"]:
            m = re.search(p, msg_lower)
            if m:
                t = m.group(1).lower()
                if any(w in t for w in ["andhi","andha","blind","drishti","दृष्टि"]):
                    entities["disability_type"] = "blind"
                elif any(w in t for w in ["bahra","deaf","sunai","सुनाई"]):
                    entities["disability_type"] = "deaf"
                elif any(w in t for w in ["langda","locomotor","chalne","चलने"]):
                    entities["disability_type"] = "locomotor"
                else:
                    entities["disability_type"] = "general"
                break
        
        for p in cls.ENTITY_PATTERNS["disability_percentage"]:
            m = re.search(p, msg_lower)
            if m:
                entities["disability_percentage"] = int(m.group(1))
                break
        
        for p in cls.ENTITY_PATTERNS["gender"]:
            m = re.search(p, msg_lower)
            if m:
                t = m.group(1).lower()
                if any(w in t for w in ["transgender","kinnar","किन्नर","trans","hijra","उभयलिंगी"]):
                    entities["gender"] = "transgender"
                elif any(w in t for w in ["female","महिला","mahila","ladki","aurat","stree"]):
                    entities["gender"] = "female"
                else:
                    entities["gender"] = "male"
                break
        
        for p in cls.ENTITY_PATTERNS["education"]:
            m = re.search(p, msg_lower)
            if m:
                full = m.group(0).lower()
                if any(c in full for c in ["mca","एमसीए","mba","एमबीए","mtech","एमटेक","ma","msc"]):
                    entities["education_level"] = "pg"
                elif any(c in full for c in ["ba","bsc","bcom","btech","बीए"]):
                    entities["education_level"] = "ug"
                elif any(c in full for c in ["diploma","डिप्लोमा"]):
                    entities["education_level"] = "diploma"
                entities["is_student"] = True
                yr = re.search(r'(1st|2nd|3rd|4th|first|second|third|fourth|pehle|doosre|teesre|chauthe)\s*(?:year|saal|वर्ष)', full)
                if yr:
                    ym = {"1st":1,"first":1,"pehle":1,"2nd":2,"second":2,"doosre":2,"3rd":3,"third":3,"teesre":3,"4th":4,"fourth":4,"chauthe":4}
                    entities["education_year"] = ym.get(yr.group(1), 1)
                break
        
        if any(w in msg_lower for w in ["student","छात्र","vidyarthi","विद्यार्थी","padh","पढ़","study"]):
            entities["is_student"] = True
        
        for p in cls.ENTITY_PATTERNS["bpl_status"]:
            if re.search(p, msg_lower):
                entities["bpl_status"] = True
                break
        
        for p in cls.ENTITY_PATTERNS["marital_status"]:
            m = re.search(p, msg_lower)
            if m:
                t = m.group(1).lower()
                if any(w in t for w in ["widow","vidhwa","विधवा"]):
                    entities["marital_status"] = "widow"
                elif any(w in t for w in ["divorced","talak","parityakta"]):
                    entities["marital_status"] = "divorced"
                elif any(w in t for w in ["married","shadi","विवाहित"]):
                    entities["marital_status"] = "married"
                else:
                    entities["marital_status"] = "unmarried"
                break
        
        for p in cls.ENTITY_PATTERNS["certificate"]:
            m = re.search(p, msg_lower)
            if m:
                if "disability" in m.group(0).lower() or "divyang" in m.group(0).lower() or "विकलांग" in m.group(0):
                    entities["has_disability_certificate"] = True
                elif "income" in m.group(0).lower() or "आय" in m.group(0):
                    entities["has_income_certificate"] = True
                elif "domicile" in m.group(0).lower() or "nivas" in m.group(0).lower():
                    entities["has_domicile"] = True
        
        return entities
    
    @classmethod
    def detect_language(cls, message: str) -> str:
        msg_lower = message.lower()
        hindi_count = sum(1 for w in cls.HINDI_KEYWORDS if w in msg_lower)
        english_count = len(re.findall(r'\b[a-z]+\b', msg_lower))
        if hindi_count > english_count:
            return "hi"
        elif english_count > hindi_count * 2:
            return "en"
        return "hinglish"
    
    @classmethod
    def process(cls, message: str) -> Dict[str, Any]:
        return {
            "intent": cls.detect_intent(message),
            "entities": cls.extract_entities(message),
            "language": cls.detect_language(message),
        }


intent_engine = IntentEngine()