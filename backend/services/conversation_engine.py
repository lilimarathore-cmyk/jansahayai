# backend/services/conversation_engine.py
# COMPLETE REWRITE - Smart flow: show schemes first, then eligibility
 
import re
from typing import Tuple, Optional, Dict, Any, List
from backend.utils.text_normalizer import normalize_text, is_greeting
from backend.database import get_scheme, get_all_schemes
from backend.services.response_builder import (
    format_scheme_full_details, extract_localized_text, build_profile_summary
)
from backend.services.session_manager import session_manager
from backend.services.intent_engine import intent_engine
from backend.rag.rag_engine import rag_engine
from backend.services.conversation.eligibility import EligibilityChecker
 
from backend.services.profile import profile_extractor, profile_formatter
from backend.services.handlers import number_handler, followup_handler, direct_scheme_handler, unknown_handler
from backend.services.recommendation import recommendation_scorer, recommendation_formatter
from backend.services.profile_manager import profile_manager
 
from backend.services.conversation.keywords import ConversationKeywords
from backend.services.conversation.extractors import Extractors
from backend.services.conversation.flows.divyang_pension import DivyangPensionFlow
from backend.services.conversation.flows.widow_pension import WidowPensionFlow
from backend.services.conversation.flows.old_age_pension import OldAgePensionFlow
from backend.services.conversation.flows.family_assistance import FamilyAssistanceFlow
from backend.services.conversation.flows.tg_card import TGCardFlow
from backend.services.conversation.responses.scheme_list import SchemeListResponse
from backend.services.conversation.responses.unknown import UnknownResponse
 
 
# ─── Language helpers ─────────────────────────────────────────────────────────
 
def _detect_lang(text: str) -> str:
    """Detect Hindi / Hinglish / English"""
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
    total = len(text.strip())
    if total == 0:
        return "hinglish"
    ratio = hindi_chars / total
    if ratio > 0.3:
        return "hi"
    elif ratio > 0.05:
        return "hinglish"
    return "en"
 
 
def _t(hi: str, hinglish: str, en: str, lang: str) -> str:
    if lang == "hi":
        return hi
    elif lang == "en":
        return en
    return hinglish
 
 
# ─── Scheme list formatter ────────────────────────────────────────────────────
 
def _format_scheme_list(schemes: List[Dict], profile: Dict, lang: str = "hinglish") -> str:
    """Format a numbered list of schemes for the user."""
    if not schemes:
        return _t(
            "आपके प्रोफ़ाइल के अनुसार कोई योजना नहीं मिली।",
            "Aapke profile ke anusar koi yojna nahi mili.",
            "No schemes found matching your profile.",
            lang
        )
 
    # Profile summary header
    lines = [build_profile_summary(profile), ""]
 
    intro = _t(
        "इन जानकारियों के आधार पर ये योजनाएं आपके लिए उपयुक्त हो सकती हैं:",
        "In jankariyon ke aadhar par ye yojnayein aapke liye upyukt ho sakti hain:",
        "Based on your details, these schemes may be suitable for you:",
        lang
    )
    lines.append(intro)
    lines.append("")
 
    for i, s in enumerate(schemes, 1):
        name = extract_localized_text(s.get("scheme_name"), "hi")
        benefit_obj = s.get("content", {}).get("benefits", {})
        benefit = extract_localized_text(benefit_obj.get("text") if isinstance(benefit_obj, dict) else benefit_obj)
        if benefit:
            benefit = benefit[:80] + ("..." if len(benefit) > 80 else "")
            lines.append(f"{i}. **{name}**\n   {benefit}")
        else:
            lines.append(f"{i}. **{name}**")
        lines.append("")
 
    footer = _t(
        "किसी भी योजना की पूरी जानकारी देखने के लिए उसका नंबर या नाम लिखें।\nजैसे: 1, 2, या योजना का नाम",
        "Kisi bhi yojna ki puri jankari dekhne ke liye uska number ya naam likhiye.\nJaise: 1, 2, ya yojna ka naam",
        "Type the number or name of any scheme to see full details.\nExample: 1, 2, or scheme name",
        lang
    )
    lines.append("━" * 30)
    lines.append(footer)
    return "\n".join(lines)
 
 
# ─── Smart scheme filter ──────────────────────────────────────────────────────
 
def _filter_schemes_for_profile(profile: Dict) -> List[Dict]:
    """
    Return schemes relevant to the profile.
    Blind users → no widow schemes.
    Children (<18) → no old-age / adult schemes.
    Widow → widow schemes first.
    Transgender → TG Card first.
    """
    all_schemes = get_all_schemes()
    age = profile.get("age")
    disability = profile.get("disability", {})
    dtype = disability.get("type", "") if isinstance(disability, dict) else ""
    gender = profile.get("gender", "")
    marital = profile.get("marital_status", "")
    is_student = profile.get("is_student", False)
 
    WIDOW_IDS    = {"cg_scheme_002", "cg_scheme_005"}
    OLD_AGE_IDS  = {"cg_scheme_003", "cg_scheme_004"}
    TG_ID        = "cg_scheme_008"
    DIVYANG_IDS  = {
        "cg_scheme_001", "cg_scheme_006", "cg_scheme_009",
        "cg_scheme_010", "cg_scheme_011", "cg_scheme_012",
        "cg_scheme_013", "cg_scheme_014", "cg_scheme_015", "cg_scheme_016"
    }
 
    result = []
    for s in all_schemes:
        sid = s.get("id", s.get("scheme_id", ""))
 
        # TG Card — only for transgender
        if sid == TG_ID:
            if gender == "transgender":
                result.insert(0, s)
            continue
 
        # Widow schemes — skip if blind/divyang (unless explicitly widow)
        if sid in WIDOW_IDS:
            if dtype in ("blind", "deaf", "locomotor", "general") and marital != "widow":
                continue
            if marital != "widow" and gender != "female":
                continue
 
        # Old-age schemes — skip if under 60
        if sid in OLD_AGE_IDS:
            if age and age < 55:
                continue
 
        # Age-based divyang filter
        if sid == "cg_scheme_001" and age and age > 17:
            continue
        if sid == "cg_scheme_006" and age and age < 18:
            continue
 
        # Score and keep
        score = recommendation_scorer.score_scheme(s, profile)
        if score > 0:
            result.append(s)
 
    # Sort by score descending
    result.sort(
        key=lambda s: recommendation_scorer.score_scheme(s, profile),
        reverse=True
    )
    return result[:8]
 
 
# ─── Main Engine ──────────────────────────────────────────────────────────────
 
class ConversationEngine:
    def __init__(self):
        self.divyang_pension_keywords  = ConversationKeywords.divyang_pension_keywords
        self.widow_pension_keywords    = ConversationKeywords.widow_pension_keywords
        self.old_age_pension_keywords  = ConversationKeywords.old_age_pension_keywords
        self.family_assistance_keywords = ConversationKeywords.family_assistance_keywords
        self.tg_card_keywords          = ConversationKeywords.tg_card_keywords
        self.greeting_patterns         = ConversationKeywords.greeting_patterns
 
        self.user_sessions  = {}
        self.use_llm        = True
 
    # ── Session helpers ───────────────────────────────────────────────────────
 
    def _save_session(self, session_id: str):
        if session_id in self.user_sessions:
            session_manager.save_session(session_id, self.user_sessions[session_id].copy())
 
    def _get_session(self, session_id: str) -> Dict:
        if session_id not in self.user_sessions:
            saved = session_manager.get_session(session_id)
            self.user_sessions[session_id] = saved if saved else {}
        return self.user_sessions[session_id]
 
    def _clear_session(self, session_id: str):
        if session_id in self.user_sessions:
            del self.user_sessions[session_id]
        number_handler.last_shown_schemes = []
 
    # ── Greeting ──────────────────────────────────────────────────────────────
 
    def _handle_greeting(self, session_id: str) -> Tuple[str, str]:
        self._clear_session(session_id)
        msg = (
            "🙏 Namaste! Main JanSahayAI hoon.\n\n"
            "Main Chhattisgarh government schemes ke baare mein jankari deta hoon.\n\n"
            "Main in topics par madad kar sakta hoon:\n"
            "- Divyang Schemes (Pension, Scholarship, Devices)\n"
            "- Pension Schemes (Widow, Old Age)\n"
            "- Scholarship & Hostel\n"
            "- TG Card\n"
            "- Family Assistance\n\n"
            "Aap seedha apni jankari de sakte hain:\n"
            "- \"Mai 22 saal ki andhi student hoon, mere liye yojnayein batao\"\n"
            "- \"Divyang pension kya hai?\"\n"
            "- \"TG Card ke liye kya chahiye?\"\n\n"
            "Apna sawaal likhiye, main madad karunga. 😊"
        )
        return msg, "success"
 
    # ── Core: extract info + show schemes ────────────────────────────────────
 
    def _has_personal_info(self, message: str) -> bool:
        """Does this message contain personal profile info?"""
        msg = message.lower()
        indicators = [
            # disability
            "andhi","andha","blind","divyang","viklang","disabled","bahra","bahri",
            "deaf","langda","langdi","अंधी","अंधा","दिव्यांग","विकलांग","अपंग",
            # age
            r'\d{1,2}\s*(?:saal|साल|year|वर्ष)',
            # student
            "student","padh","पढ़","college","mca","btech","ba ","bsc",
            # gender / marital
            "widow","vidhwa","विधवा","transgender","kinnar","किन्नर",
            # income / BPL
            r'\d{4,7}\s*(?:rs|₹|rupees|रुपये)', "bpl","income","आय",
            # "mere liye" type
            "mere liye","मेरे लिए","mujhe","मुझे","kaun si","कौन सी",
            "batao","बताओ","chahiye","चाहिए",
        ]
        for ind in indicators:
            if isinstance(ind, str):
                if ind in msg:
                    return True
            else:
                if re.search(ind, msg):
                    return True
        return False
 
    def _handle_smart_profile_flow(
        self, message: str, session_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Main smart handler:
        1. Extract entities from message (and existing session profile).
        2. If enough info → show filtered scheme list.
        3. If missing critical info → ask ONE natural question.
        4. Always update session.
        """
        if not self._has_personal_info(message):
            return None, None
 
        session_data = self._get_session(session_id)
        lang = _detect_lang(message)
 
        # Merge new info into existing profile
        profile = session_data.get("profile", {})
        profile = profile_extractor.extract_all(message, profile)
        profile["language"] = lang
        session_data["profile"] = profile
        session_data["state"] = "collecting_profile"
        self._save_session(session_id)
 
        print(f"[PROFILE] Extracted: {profile}")
 
        # ── Try to show schemes ───────────────────────────────────────────────
        schemes = _filter_schemes_for_profile(profile)
 
        if schemes:
            # We have enough info to show schemes
            number_handler.set_schemes(schemes)
            session_data["last_schemes"] = [
                s.get("id", s.get("scheme_id", "")) for s in schemes
            ]
            session_data["state"] = "showing_recommendations"
            self._save_session(session_id)
            return _format_scheme_list(schemes, profile, lang), "success"
 
        # ── Ask for one missing field ─────────────────────────────────────────
        question = self._ask_missing_field(profile, lang)
        return question, "needs_slot"
 
    def _ask_missing_field(self, profile: Dict, lang: str) -> str:
        """Ask the single most important missing field naturally."""
        if "age" not in profile:
            return _t(
                "आपकी उम्र क्या है?",
                "Aapki age kitni hai?",
                "How old are you?",
                lang
            )
        if "disability" not in profile and "gender" not in profile and "marital_status" not in profile:
            return _t(
                "क्या आप दिव्यांग हैं? या आप किस श्रेणी के लिए योजना देखना चाहते हैं?",
                "Kya aap divyang hain? Ya aap kis category ke liye yojna dekhna chahte hain?\n(Divyang / Widow / Old Age / Family Assistance)",
                "Are you divyang? Or which category of scheme are you looking for?\n(Divyang / Widow / Old Age / Family Assistance)",
                lang
            )
        # Fallback — generic
        return _t(
            "कृपया अपनी जानकारी दें ताकि मैं उपयुक्त योजनाएं बता सकूं।",
            "Kripya thodi aur jankari dein taaki main upyukt yojnayein bata sakoon.",
            "Please share a bit more about yourself so I can suggest suitable schemes.",
            lang
        )
 
    # ── Number / name selection ───────────────────────────────────────────────
 
    def _handle_number_or_name_selection(
        self, message: str, session_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        session_data = self._get_session(session_id)
        state = session_data.get("state", "")
        lang = _detect_lang(message)
 
        if state not in ("showing_recommendations", "showing_details"):
            return None, None
 
        # Use stored schemes list
        stored_ids = session_data.get("last_schemes", [])
        if stored_ids and not number_handler.last_shown_schemes:
            schemes = [get_scheme(sid) for sid in stored_ids if get_scheme(sid)]
            number_handler.set_schemes(schemes)
 
        resp, status = number_handler.handle(
            message, session_id, session_data, lambda sid: get_scheme(sid)
        )
        if resp:
            session_data["state"] = "showing_details"
            # Try to track which scheme was selected
            num = number_handler._extract_number(message)
            if num and number_handler.last_shown_schemes:
                idx = num - 1
                if 0 <= idx < len(number_handler.last_shown_schemes):
                    s = number_handler.last_shown_schemes[idx]
                    session_data["active_scheme"] = s.get("id", s.get("scheme_id", ""))
            self._save_session(session_id)
            return resp, status
 
        return None, None
 
    # ── Follow-up (documents / process / where etc.) ─────────────────────────
 
    def _handle_followup_query(
        self, message: str, session_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        if session_id not in self.user_sessions:
            return None, None
        session_data = self.user_sessions[session_id]
        state = session_data.get("state", "")
        active_scheme = session_data.get("active_scheme")
 
        if state == "showing_details" and active_scheme:
            ft = followup_handler._detect_followup_type(message)
            if ft:
                resp = followup_handler._get_scheme_detail_for_followup(
                    active_scheme, ft, message
                )
                if resp:
                    return resp, "success"
 
        def fmt(schemes): return recommendation_formatter.format(schemes)
        resp, status = followup_handler.handle(message, session_data, fmt)
        if resp:
            self._save_session(session_id)
            return resp, status
 
        return None, None
 
    # ── TG Card ───────────────────────────────────────────────────────────────
 
    def _handle_tg_card(
        self, message: str, session_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        if not TGCardFlow.is_tg_card_query(message, self.tg_card_keywords):
            return None, None
        self._clear_session(session_id)
        scheme = get_scheme("cg_scheme_008")
        if not scheme:
            return TGCardFlow.get_tg_card_details(), "success"
        session = self._get_session(session_id)
        session.update({
            "active_scheme": "cg_scheme_008",
            "state": "showing_details"
        })
        self._save_session(session_id)
        return format_scheme_full_details(scheme, show_pdf=True), "success"
 
    # ── Direct scheme query (e.g. "divyang pension kya hai") ─────────────────
 
    def _handle_direct_scheme_query(
        self, message: str, session_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        session = self._get_session(session_id)
        resp, status = direct_scheme_handler.handle(
            message, session_id, session,
            lambda sid, data: self._save_session(sid)
        )
        return resp, status
 
    # ── Active pension/scheme flows ───────────────────────────────────────────
 
    def _handle_active_flows(
        self, message: str, session_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        if session_id not in self.user_sessions:
            return None, None
        user_data = self.user_sessions[session_id]
        scheme_type = user_data.get("scheme")
 
        flows = {
            "unified_widow_pension":    WidowPensionFlow,
            "unified_old_age_pension":  OldAgePensionFlow,
            "family_assistance":        FamilyAssistanceFlow,
        }
        if scheme_type in flows:
            resp, status = flows[scheme_type].handle(
                message, session_id, user_data, self.user_sessions
            )
            if resp:
                self._save_session(session_id)
            return (resp, status) if resp else (None, None)
 
        if user_data.get("pension_flow_active"):
            resp, status = DivyangPensionFlow.handle(
                message, session_id, user_data, self.user_sessions
            )
            if resp:
                self._save_session(session_id)
            return (resp, status) if resp else (None, None)
 
        return None, None
 
    # ── Unknown ───────────────────────────────────────────────────────────────
 
    def _handle_unknown(self, message: str) -> Tuple[str, str]:
        if unknown_handler.is_off_topic(message):
            return unknown_handler.get_response(message), "unknown"
        return UnknownResponse.handle_unknown_query(message), "unknown"
 
    # ── Profile continuation (user answering a question we asked) ─────────────
 
    def _handle_profile_continuation(
        self, message: str, session_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """User is answering a previous profile question (e.g. we asked age, they reply '22')."""
        session_data = self._get_session(session_id)
        state = session_data.get("state", "")
        profile = session_data.get("profile", {})
        lang = profile.get("language", "hinglish")
 
        if state != "collecting_profile":
            return None, None
 
        # Try to extract any info from the reply
        updated = profile_extractor.extract_all(message, profile)
        if updated == profile:
            # Nothing new extracted
            return None, None
 
        session_data["profile"] = updated
        profile = updated
        self._save_session(session_id)
 
        schemes = _filter_schemes_for_profile(profile)
        if schemes:
            number_handler.set_schemes(schemes)
            session_data["last_schemes"] = [
                s.get("id", s.get("scheme_id", "")) for s in schemes
            ]
            session_data["state"] = "showing_recommendations"
            self._save_session(session_id)
            return _format_scheme_list(schemes, profile, lang), "success"
 
        # Still not enough — ask next missing field
        question = self._ask_missing_field(profile, lang)
        return question, "needs_slot"
 
    # ═════════════════════════════════════════════════════════════════════════
    # MAIN PROCESS METHOD
    # ═════════════════════════════════════════════════════════════════════════
 
    def process(self, message: str, session_id: str) -> Tuple[str, str]:
        msg_lower = message.lower().strip()
        normalized = normalize_text(message)
 
        # ── 1. GREETING ───────────────────────────────────────────────────────
        greetings = [
            "hi","hello","namaste","नमस्ते","hey","हैलो","नमस्कार",
            "hii","heylo","hy","namaskar"
        ]
        if any(g == msg_lower for g in greetings) or is_greeting(normalized):
            return self._handle_greeting(session_id)
 
        # Load session
        session_data = self._get_session(session_id)
 
        # ── 2. ACTIVE PENSION / SCHEME FLOWS (highest priority mid-conversation)
        resp, status = self._handle_active_flows(message, session_id)
        if resp:
            return resp, status
 
        # ── 3. FOLLOW-UP ON SHOWN SCHEME (documents, process, etc.)
        resp, status = self._handle_followup_query(message, session_id)
        if resp:
            return resp, status
 
        # ── 4. NUMBER / NAME SELECTION from recommendation list
        resp, status = self._handle_number_or_name_selection(message, session_id)
        if resp:
            return resp, status
 
        # ── 5. TG CARD
        resp, status = self._handle_tg_card(message, session_id)
        if resp:
            return resp, status
 
        # ── 6. FAMILY DEATH / DIRECT SCHEME KEYWORDS
        for kw in ["मुखिया की मृत्यु", "मुखिया का निधन", "मुखिया की death"]:
            if kw in msg_lower:
                scheme = get_scheme("cg_scheme_007")
                if scheme:
                    session_data.update({"active_scheme": "cg_scheme_007", "state": "showing_details"})
                    self._save_session(session_id)
                    return format_scheme_full_details(scheme, show_pdf=False), "success"
 
        # ── 7. PROFILE CONTINUATION (user answering our question)
        resp, status = self._handle_profile_continuation(message, session_id)
        if resp:
            return resp, status
 
        # ── 8. SMART PROFILE FLOW (new personal info in message)
        resp, status = self._handle_smart_profile_flow(message, session_id)
        if resp:
            return resp, status
 
        # ── 9. DIRECT SCHEME QUERY ("divyang pension kya hai" etc.)
        resp, status = self._handle_direct_scheme_query(message, session_id)
        if resp:
            return resp, status
 
        # ── 10. WIDOW / OLD AGE / FAMILY KEYWORD SHORTCUTS
        if any(kw in msg_lower for kw in self.widow_pension_keywords):
            self._clear_session(session_id)
            self.user_sessions[session_id] = {
                "scheme": "unified_widow_pension",
                "step": "awaiting_age",
                "pension_flow_active": True
            }
            self._save_session(session_id)
            lang = _detect_lang(message)
            return _t(
                "विधवा पेंशन योजना के लिए आपकी उम्र क्या है?",
                "Widow Pension Yojna ke liye aapki age kitni hai?",
                "What is your age for Widow Pension Scheme?",
                lang
            ), "needs_slot"
 
        if any(kw in msg_lower for kw in self.old_age_pension_keywords):
            self._clear_session(session_id)
            self.user_sessions[session_id] = {
                "scheme": "unified_old_age_pension",
                "step": "awaiting_age",
                "pension_flow_active": True
            }
            self._save_session(session_id)
            lang = _detect_lang(message)
            return _t(
                "वृद्धावस्था पेंशन के लिए आपकी उम्र क्या है? (60+ वर्ष)",
                "Old Age Pension ke liye aapki age kitni hai? (60+ years)",
                "What is your age for Old Age Pension? (60+ years)",
                lang
            ), "needs_slot"
 
        if any(kw in msg_lower for kw in self.family_assistance_keywords):
            self._clear_session(session_id)
            self.user_sessions[session_id] = {
                "scheme": "family_assistance",
                "step": "awaiting_bpl",
                "pension_flow_active": True
            }
            self._save_session(session_id)
            lang = _detect_lang(message)
            return _t(
                "परिवार सहायता योजना के लिए — क्या परिवार का नाम BPL सूची में है? (हाँ/नहीं)",
                "Family Assistance ke liye — kya family ka naam BPL list mein hai? (Haan/Nahi)",
                "For Family Assistance — is the family in the BPL list? (Yes/No)",
                lang
            ), "needs_slot"
 
        # ── 11. UNKNOWN
        return self._handle_unknown(message)
 
 
# ─── Singleton ────────────────────────────────────────────────────────────────
conversation_engine = ConversationEngine()
 
from backend.services.conversation.responses.scheme_list import set_conversation_engine
set_conversation_engine(conversation_engine)
 
print("[INFO] ConversationEngine initialized - Multi-scheme + Number selection fixed")