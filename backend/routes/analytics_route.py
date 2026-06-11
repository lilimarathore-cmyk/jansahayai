# ============================================
# FILE: backend/routes/analytics_route.py
# ============================================

from fastapi import APIRouter
from backend.database import db, chat_collection, scheme_collection
from datetime import datetime, timedelta
from collections import Counter
import logging

router = APIRouter(prefix="/admin/analytics", tags=["Analytics"])
logger = logging.getLogger(__name__)


def get_chats_list():
    try:
        result = chat_collection.find({})
        if hasattr(result, '__iter__') and not isinstance(result, list):
            return list(result)
        return result if isinstance(result, list) else []
    except Exception as e:
        logger.error(f"Error fetching chats: {e}")
        return []


def get_schemes_list():
    try:
        result = scheme_collection.find({})
        if hasattr(result, '__iter__') and not isinstance(result, list):
            return list(result)
        return result if isinstance(result, list) else []
    except Exception as e:
        logger.error(f"Error fetching schemes: {e}")
        return []


@router.get("/overview")
async def get_overview():
    try:
        chats = get_chats_list()
        total_messages = len(chats)

        session_ids = set()
        for c in chats:
            sid = c.get("session_id")
            if sid and sid not in ["default", "test"]:
                session_ids.add(sid)
        unique_users = len(session_ids) if session_ids else 0
        total_conversations = unique_users if unique_users > 0 else total_messages

        fallback_count = sum(1 for c in chats if c.get("is_fallback") is True)
        fallback_rate = round((fallback_count / total_messages * 100), 1) if total_messages > 0 else 0

        eligible_count = sum(1 for c in chats if c.get("is_eligible") is True)
        success_rate = round((eligible_count / total_messages * 100), 1) if total_messages > 0 else 0

        schemes = get_schemes_list()
        total_schemes = len(schemes)
        active_schemes = sum(1 for s in schemes if s.get("active", True))

        return {
            "total_conversations": total_conversations,
            "unique_users": unique_users,
            "total_messages": total_messages,
            "fallback_rate": fallback_rate,
            "success_rate": success_rate,
            "eligible_count": eligible_count,
            "fallback_count": fallback_count,
            "total_schemes": total_schemes,
            "active_schemes": active_schemes,
        }
    except Exception as e:
        logger.error(f"Overview error: {e}")
        return {
            "total_conversations": 0, "unique_users": 0, "total_messages": 0,
            "fallback_rate": 0, "success_rate": 0, "eligible_count": 0,
            "fallback_count": 0, "total_schemes": 0, "active_schemes": 0,
        }


@router.get("/intents")
async def get_intent_distribution():
    try:
        chats = get_chats_list()
        intent_labels = {
            "ask_documents":   "दस्तावेज़",
            "ask_eligibility": "पात्रता",
            "ask_benefits":    "लाभ/राशि",
            "ask_process":     "आवेदन प्रक्रिया",
            "ask_schemes_list":"योजना सूची",
            "greeting":        "अभिवादन",
            "farewell":        "विदाई",
            "unknown":         "अन्य",
        }
        intent_counts = Counter()
        for c in chats:
            intent = c.get("intent", "unknown") or "unknown"
            intent_counts[intent] += 1

        result = []
        for intent, count in intent_counts.most_common():
            result.append({
                "intent": intent,
                "label": intent_labels.get(intent, intent),
                "count": count,
            })
        return {"data": result, "total": len(chats)}
    except Exception as e:
        logger.error(f"Intent error: {e}")
        return {"data": [], "total": 0}


@router.get("/schemes")
async def get_scheme_popularity():
    try:
        chats = get_chats_list()
        schemes = get_schemes_list()
        scheme_names = {}
        for s in schemes:
            sid = s.get("id") or s.get("scheme_id")
            if sid:
                name = s.get("scheme_name", {})
                if isinstance(name, dict):
                    scheme_names[sid] = name.get("hi", sid)
                else:
                    scheme_names[sid] = str(name)

        scheme_counts = Counter()
        for c in chats:
            sid = c.get("scheme_id")
            if sid:
                scheme_counts[sid] += 1

        result = []
        for sid, count in scheme_counts.most_common(10):
            result.append({
                "scheme_id": sid,
                "scheme_name": scheme_names.get(sid, sid),
                "count": count,
            })
        return {"data": result}
    except Exception as e:
        logger.error(f"Scheme popularity error: {e}")
        return {"data": []}


@router.get("/daily")
async def get_daily_activity():
    try:
        chats = get_chats_list()
        today = datetime.now().date()
        days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
        day_counts = {str(d): 0 for d in days}

        for c in chats:
            ts = c.get("timestamp")
            if ts:
                try:
                    if isinstance(ts, str):
                        ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    chat_date = str(ts.date())
                    if chat_date in day_counts:
                        day_counts[chat_date] += 1
                except Exception:
                    pass

        result = [
            {
                "date": date,
                "label": datetime.strptime(date, "%Y-%m-%d").strftime("%d %b"),
                "count": count,
            }
            for date, count in day_counts.items()
        ]
        return {"data": result}
    except Exception as e:
        logger.error(f"Daily activity error: {e}")
        return {"data": []}


@router.get("/top-queries")
async def get_top_queries():
    try:
        chats = get_chats_list()
        msg_counts = Counter()
        for c in chats:
            msg = c.get("user_message", "").strip()
            if msg and len(msg) > 3:
                msg_counts[msg] += 1

        result = []
        for msg, count in msg_counts.most_common(10):
            result.append({"query": msg, "count": count})
        return {"data": result}
    except Exception as e:
        logger.error(f"Top queries error: {e}")
        return {"data": []}


@router.get("/categories")
async def get_category_distribution():
    try:
        schemes = get_schemes_list()

        category_labels = {
            "divyang_pension":    "दिव्यांग पेंशन",
            "widow_pension":      "विधवा पेंशन",
            "old_age_pension":    "वृद्धावस्था पेंशन",
            "family_assistance":  "परिवार सहायता",
            "scholarship":        "छात्रवृत्ति",
            "assistive_devices":  "सहायक उपकरण",
            "marriage_incentive": "विवाह प्रोत्साहन",
            "civil_services":     "सिविल सेवा",
            "hostel":             "छात्रावास",
            "camp":               "शिविर",
            "rehabilitation":     "पुनर्वास",
            "tg_card":            "टीजी कार्ड",
            "divyang_support":    "दिव्यांग सहायता",
            "divyang_education":  "दिव्यांग शिक्षा",
            "women_pension":      "महिला पेंशन",
            "general_pension":    "सामान्य पेंशन",
            "transgender_support":"ट्रांसजेंडर सहायता",
        }

        cat_counts = Counter()
        for s in schemes:
            cat = s.get("meta", {}).get("category") or s.get("category", "other")
            cat_counts[cat] += 1

        result = []
        for cat, count in cat_counts.most_common():
            result.append({
                "category": cat,
                "label": category_labels.get(cat, cat),
                "count": count,
            })
        return {"data": result}
    except Exception as e:
        logger.error(f"Category distribution error: {e}")
        return {"data": []}
