# ============================================
# FILE: backend/utils/text_normalizer.py
# COMPLETE FIXED VERSION - Numbers preserved
# ============================================

import re
from typing import Optional

def is_hindi_text(text: str) -> bool:
    """Check if text contains Hindi/Devanagari characters"""
    if not text:
        return False
    # Devanagari Unicode range: \u0900-\u097F
    hindi_pattern = re.compile(r'[\u0900-\u097F]')
    return bool(hindi_pattern.search(text))

def normalize_hindi(text: str) -> str:
    """Normalize Hindi text (preserve Devanagari characters, digits, and %)
    FIXED: Now preserves ASCII digits (0-9), Devanagari digits, and percent sign
    """
    if not text:
        return ""
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text.strip())
    # Keep Devanagari letters, common punctuation, digits (ASCII + Devanagari), percent sign
    # This prevents stripping user-entered numbers like '50' or '50%' which are needed for flows
    text = re.sub(r'[^\u0900-\u097F0-9\u0966-\u096F\s\?\!\.\,\%]', '', text)
    return text.strip()

def normalize_english(text: str) -> str:
    """Normalize English/Hinglish text"""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def normalize_text(text: str) -> str:
    """Main normalize function - detects language and normalizes accordingly"""
    if not text:
        return ""
    
    # Check if text contains Hindi characters
    if is_hindi_text(text):
        return normalize_hindi(text)
    else:
        return normalize_english(text)

def extract_numbers(text: str) -> Optional[int]:
    """Extract first number from text"""
    if not text:
        return None
    match = re.search(r"(\d+)", text)
    if match:
        return int(match.group(1))
    return None

def is_greeting(text: str) -> bool:
    """Check if message is a greeting"""
    if not text:
        return False
    greetings = ["namaste", "नमस्ते", "हैलो", "नमस्कार", "जय श्री राम"]
    text_lower = text.lower()
    for greet in greetings:
        if greet in text_lower:
            return True
    return False