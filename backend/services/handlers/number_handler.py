# backend/services/handlers/number_handler.py
"""Handle number-based scheme selection"""
 
from typing import Tuple, Optional, Dict, List
 
 
class NumberHandler:
    NUMBER_WORDS = {
        "1":1,"१":1,"first":1,"pehla":1,"पहला":1,"1st":1,"ek":1,"एक":1,
        "2":2,"२":2,"second":2,"doosra":2,"दूसरा":2,"2nd":2,"do":2,"दो":2,
        "3":3,"३":3,"third":3,"teesra":3,"तीसरा":3,"3rd":3,"teen":3,"तीन":3,
        "4":4,"४":4,"fourth":4,"chauttha":4,"चौथा":4,"4th":4,"char":4,"चार":4,
        "5":5,"५":5,"fifth":5,"paanchwa":5,"पाँचवा":5,"5th":5,"paanch":5,"पाँच":5,
        "6":6,"६":6,"sixth":6,"chhatha":6,"छठा":6,"6th":6,
        "7":7,"७":7,"seventh":7,"saatwa":7,"सातवाँ":7,"7th":7,
        "8":8,"८":8,"eighth":8,"aathwa":8,"आठवाँ":8,"8th":8,
    }
 
    def __init__(self):
        self.last_shown_schemes: List[Dict] = []
 
    def set_schemes(self, schemes: List[Dict]):
        self.last_shown_schemes = schemes
 
    def _extract_number(self, message: str) -> Optional[int]:
        msg = message.lower().strip()
        # Exact word match
        for word, num in self.NUMBER_WORDS.items():
            if msg == word:
                return num
        # Pure digit
        if msg.isdigit():
            n = int(msg)
            if 1 <= n <= 10:
                return n
        return None
 
    def _find_scheme_by_name(self, name: str, schemes: List[Dict]) -> Optional[Dict]:
        from backend.services.response_builder import extract_localized_text
        name_lower = name.lower()
        for scheme in schemes:
            scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
            if name_lower in scheme_name.lower():
                return scheme
            sid = scheme.get("id", scheme.get("scheme_id", ""))
            if name_lower in sid.lower():
                return scheme
        return None
 
    def handle(
        self,
        message: str,
        session_id: str,
        session_data: Dict,
        get_scheme_func
    ) -> Tuple[Optional[str], Optional[str]]:
        from backend.services.response_builder import format_scheme_full_details
 
        msg_lower = message.lower().strip()
 
        # Number selection
        num = self._extract_number(message)
        if num and self.last_shown_schemes and 1 <= num <= len(self.last_shown_schemes):
            scheme = self.last_shown_schemes[num - 1]
            sid = scheme.get("id", scheme.get("scheme_id", ""))
            if sid:
                full_scheme = get_scheme_func(sid)
                if full_scheme:
                    # Update active scheme in session
                    session_data["active_scheme"] = sid
                    session_data["state"] = "showing_details"
                    return format_scheme_full_details(full_scheme, show_pdf=False), "success"
 
        # Name-based selection (only if message is reasonably long)
        if self.last_shown_schemes and len(msg_lower) > 3:
            scheme = self._find_scheme_by_name(msg_lower, self.last_shown_schemes)
            if scheme:
                sid = scheme.get("id", scheme.get("scheme_id", ""))
                if sid:
                    full_scheme = get_scheme_func(sid)
                    if full_scheme:
                        session_data["active_scheme"] = sid
                        session_data["state"] = "showing_details"
                        return format_scheme_full_details(full_scheme, show_pdf=False), "success"
 
        return None, None
 
 
number_handler = NumberHandler()