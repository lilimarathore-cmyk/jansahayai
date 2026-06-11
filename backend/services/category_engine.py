# ============================================
# FILE: backend/services/category_engine.py
# FIX 4: Add Hindi name mapping for better category detection
# CHANGE: ADDED new hindi_to_category mapping (no existing code removed)
# ============================================

from typing import Optional, List

class CategoryEngine:
    def __init__(self):
        self.category_patterns = {
            "दिव्यांग": [
                "divyang", "विकलांग", "दिव्यांग", "disability", "disabled", 
                "विकलांगता", "अपंग", "handicap", "physically challenged",
                "blind", "अंधा", "अंधी", "नेत्रहीन", "blindness",
                "deaf", "बहरा", "मूक", "बधिर", "hearing impaired",
                "speech", "वाक्", "लकवा", "paralysis", "wheelchair",
                "orthopedic", "मानसिक", "mental", "intellectual",
                "autism", "आटिज्म", "multiple disability", "बहुविकलांग",
                "drishtiheen", "netrahin", "andha", "andhi"
            ],
            "विधवा": [
                "widow", "विधवा", "विध्वा", "बेवा", "विधवा पेंशन", 
                "widow pension", "पति की मृत्यु", "vidhva", "vidhava",
                "vidhwa", "vidhva pension", "vidhava pension"
            ],
            "वृद्धावस्था": [
                "old age", "वृद्ध", "बुजुर्ग", "बुद्धा", "senior citizen",
                "वृद्धावस्था", "बूढ़े", "aged", "elderly", "vriddha",
                "budhapa", "old age pension", "bujurg"
            ],
            "छात्रवृत्ति": [
                "scholarship", "छात्रवृत्ति", "education", "शिक्षा", 
                "student", "विद्यार्थी", "पढ़ाई", "school", "college",
                "chhatravritti", "scholarship for", "fees"
            ],
            "पुनर्वास / शिविर": [
                "rehab", "पुनर्वास", "शिविर", "camp", "equipment", "सामान",
                "सहायता", "help", "support", "train", "प्रशिक्षण",
                "punarvas", "shivir", "upkaran"
            ],
            "उभयलिंगी / ट्रांसजेंडर": [
                "tg card", "tg card kaise banega", "transgender card", "ट्रांसजेंडर कार्ड",
                "टीजी कार्ड", "उभयलिंगी", "तृतीय लिंग", "third gender", "किन्नर",
                "हिजड़ा", "transgender scheme", "tg registration", "tg id",
                "kinnar", "hijra", "transgender"
            ]
        }
        
        self.category_mapping = {
            "दिव्यांग": ["divyang_pension", "divyang_equipment", "divyang_support", "divyang_education"],
            "विधवा": ["widow_pension", "women_pension"],
            "वृद्धावस्था": ["old_age_pension"],
            "छात्रवृत्ति": ["divyang_education"],
            "पुनर्वास / शिविर": ["divyang_rehab", "divyang_camp"],
            "उभयलिंगी / ट्रांसजेंडर": ["transgender_support"]
        }
        
        # High priority keywords for disability
        self.disability_keywords = {
            "blind": "दिव्यांग", "अंधा": "दिव्यांग", "अंधी": "दिव्यांग", "नेत्रहीन": "दिव्यांग",
            "deaf": "दिव्यांग", "बहरा": "दिव्यांग", "लकवा": "दिव्यांग", "paralysis": "दिव्यांग",
            "wheelchair": "दिव्यांग", "व्हीलचेयर": "दिव्यांग", "मानसिक": "दिव्यांग",
            "बोलना": "दिव्यांग", "चलना": "दिव्यांग", "सुनना": "दिव्यांग", "देखना": "दिव्यांग"
        }
        
        # ✅ NEW FIX 4: Hindi to category mapping for better detection
        # Ye sirf additional mappings hain, old system pehle jaisa kaam karega
        self.hindi_to_category = {
            "दिव्यांग": "दिव्यांग",
            "विकलांग": "दिव्यांग",
            "विधवा": "विधवा",
            "तलाकशुदा": "विधवा",
            "परित्यक्ता": "विधवा",
            "बुजुर्ग": "वृद्धावस्था",
            "वृद्ध": "वृद्धावस्था",
            "वृद्धावस्था": "वृद्धावस्था",
            "छात्रवृत्ति": "छात्रवृत्ति",
            "परिवार सहायता": "पुनर्वास / शिविर",
            "मृत्यु सहायता": "पुनर्वास / शिविर",
            "टीजी कार्ड": "उभयलिंगी / ट्रांसजेंडर",
            "tg card": "उभयलिंगी / ट्रांसजेंडर",
            "किन्नर": "उभयलिंगी / ट्रांसजेंडर",
            "हिजड़ा": "उभयलिंगी / ट्रांसजेंडर",
        }
    
    def detect_top_level_group(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        
        # First check disability keywords (highest priority)
        for keyword, category in self.disability_keywords.items():
            if keyword in text_lower:
                return category
        
        # Then check regular patterns
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return category
        
        # ✅ NEW FIX 4: Fallback to Hindi name mapping
        for hindi_word, category in self.hindi_to_category.items():
            if hindi_word in text_lower or hindi_word in text:
                return category
        
        return None
    
    def detect_category_switch(self, text: str) -> Optional[str]:
        return self.detect_top_level_group(text)
    
    def get_menu(self) -> List[str]:
        return list(self.category_patterns.keys())
    
    def get_menu_response(self) -> str:
        response = """नमस्ते! 👋

मैं आपकी सरकारी योजनाओं के बारे में जानकारी दे सकता हूँ।

कृपया बताएं:

• दिव्यांग - विकलांगजन योजनाएं
• विधवा - विधवा पेंशन और महिला योजनाएं
• वृद्धावस्था - बुजुर्ग पेंशन योजना
• छात्रवृत्ति - शिक्षा छात्रवृत्ति योजनाएं
• पुनर्वास / शिविर - पुनर्वास और शिविर योजनाएं
• उभयलिंगी / ट्रांसजेंडर - TG Card योजना

या सीधे कोई सवाल पूछें।"""
        return response
    
    def get_categories_for_group(self, group: str) -> List[str]:
        return self.category_mapping.get(group, [])

category_engine = CategoryEngine()