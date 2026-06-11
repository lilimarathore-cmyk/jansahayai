# backend/services/handlers/unknown_handler.py
"""Handle unknown/off-topic queries"""


class UnknownHandler:
    """Handle queries outside bot's scope"""
    
    OFF_TOPIC_KEYWORDS = ["bitcoin", "crypto", "cricket", "movie", "song", "weather", "news", "stock"]
    
    @staticmethod
    def is_off_topic(message: str) -> bool:
        msg_lower = message.lower()
        return any(kw in msg_lower for kw in UnknownHandler.OFF_TOPIC_KEYWORDS)
    
    @staticmethod
    def get_response(message: str = None) -> str:
        """Get polite unknown response"""
        return """🙏 Kshama karein, main sirf **Chhattisgarh government schemes** aur **beneficiary services** se sambandhit jankari de sakta hoon.

Main in topics par madad kar sakta hoon:

• 🧑‍🦯 Divyang Schemes - Pension, scholarship, assistance
• 👵 Pension Schemes - Widow, old age, disability  
• 📚 Scholarship Schemes - Educational financial aid
• 💳 TG Card - Ration and benefits card
• 👨‍👩‍👧‍👦 Family Assistance - Death/family support schemes

Kripya inme se kisi vishay par prashn poochhiye."""


unknown_handler = UnknownHandler()