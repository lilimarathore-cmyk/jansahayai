# backend/services/conversation/flows/tg_card.py
# TG CARD - Special case: PDF allowed without eligibility check

from typing import Tuple, Optional
from backend.database import get_scheme
from backend.services.response_builder import format_scheme_full_details

class TGCardFlow:
    
    @staticmethod
    def get_tg_card_details() -> str:
        """Return TG Card scheme details with PDF link (special case)"""
        scheme = get_scheme("cg_scheme_008")
        
        office_details = """

कार्यालय की जानकारी

कार्यालय: संयुक्त संचालक, समाज कल्याण विभाग
पता: जिला समाज कल्याण कार्यालय, बिलासपुर (छ.ग.)

जोन कमिश्नर (संयुक्त संचालक):
अपर कलेक्टर/संयुक्त संचालक समाज कल्याण
फोन: 07752-220127, 07752-423500 (जिला कार्यालय)

कार्यपालन अभियंता:
नगर निगम बिलासपुर के तहत समाज कल्याण प्रकोष्ठ

कार्यालय समय

दिन: सोमवार से शुक्रवार
समय: सुबह 10:30 बजे से शाम 5:00 बजे तक
लंच टाइम: दोपहर 1:00 से 2:00 बजे तक
अवकाश: शनिवार-रविवार

नोट: कृपया जाने से पहले फोन करके समय अवश्य पूछ लें।

"""
        
        if scheme:
            # TG Card is special case - show PDF even without eligibility check
            base_response = format_scheme_full_details(scheme, show_pdf=True)
            return base_response + office_details
        
        # Fallback if scheme not found - with PDF link
        return """
उभयलिंगी व्यक्तियों को टी.जी. कार्ड जारी करना

क्या मिलता है

इस योजना के तहत टी.जी. कार्ड जारी किया जाता है।

कौन ले सकता है

- आवेदक छत्तीसगढ़ का मूल निवासी होना चाहिए

आवश्यक दस्तावेज

- आधार कार्ड
- निवास प्रमाण पत्र
- 8वीं / 10वीं प्रमाण पत्र
- शपथ पत्र
- 02 पासपोर्ट साइज फोटो

आवेदन कैसे करें

1. निर्धारित प्रारूप में आवेदन पत्र भरें
2. आवश्यक दस्तावेजों के साथ आवेदन जमा करें

**डाउनलोड फॉर्म**

/forms/cg_scheme_008.pdf
""" + office_details

    @staticmethod
    def is_tg_card_query(message: str, tg_card_keywords: list) -> bool:
        """Check if user is asking about TG Card"""
        message_lower = message.lower()
        all_keywords = tg_card_keywords + [
            "sixer", "सिक्सर", "hijra", "हिजड़ा", "kinnar", "किन्नर",
            "उभयलिंगी", "transgender", "ट्रांसजेंडर"
        ]
        return any(kw in message_lower for kw in all_keywords)