# backend/services/language_detector.py
# NEW FILE - Language detection for responses

import re
from typing import Literal

Language = Literal["hindi", "english", "hinglish"]


class LanguageDetector:
    """Detects user's language for response consistency"""
    
    def __init__(self):
        self.hindi_pattern = re.compile(r'[\u0900-\u097F]')
        self.hinglish_indicators = [
            "hai", "hain", "hona", "karna", "sakta", "chahta", "raha", "rah",
            "aap", "tum", "mera", "tera", "kya", "kaun", "kahan", "kaise"
        ]
        self.english_indicators = [
            "the", "is", "are", "am", "was", "were", "this", "that", "these", "those"
        ]
    
    def detect(self, text: str) -> Language:
        """Detect language of input text"""
        if not text:
            return "hinglish"
        
        # Check for Hindi/Devanagari characters
        if self.hindi_pattern.search(text):
            return "hindi"
        
        text_lower = text.lower()
        
        # Check for Hinglish indicators
        hinglish_count = sum(1 for word in self.hinglish_indicators if word in text_lower)
        english_count = sum(1 for word in self.english_indicators if word in text_lower)
        
        if hinglish_count >= 2 and english_count < 3:
            return "hinglish"
        
        return "english"
    
    def translate_response(self, response: str, target_lang: Language, original_lang: Language = "hinglish") -> str:
        """Translate response to target language (simplified)"""
        if target_lang == original_lang:
            return response
        
        # Simple word mapping for common phrases
        translations = {
            "age": {"hindi": "आयु", "hinglish": "age", "english": "age"},
            "disability": {"hindi": "दिव्यांगता", "hinglish": "disability", "english": "disability"},
            "income": {"hindi": "आय", "hinglish": "income", "english": "income"},
            "BPL": {"hindi": "बीपीएल", "hinglish": "BPL", "english": "BPL"},
            "student": {"hindi": "छात्र", "hinglish": "student", "english": "student"},
            "eligible": {"hindi": "पात्र", "hinglish": "eligible", "english": "eligible"},
            "not eligible": {"hindi": "पात्र नहीं", "hinglish": "eligible nahi", "english": "not eligible"},
            "documents": {"hindi": "दस्तावेज", "hinglish": "documents", "english": "documents"},
            "apply": {"hindi": "आवेदन करें", "hinglish": "apply karein", "english": "apply"},
        }
        
        # Simplified - return as is for now
        return response


language_detector = LanguageDetector()