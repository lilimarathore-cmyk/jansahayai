# backend/services/analytics_engine.py
from datetime import datetime
from typing import Dict, Optional
from backend.database import log_chat
from backend.utils.text_normalizer import normalize_text

class AnalyticsEngine:
    def log_query(
        self,
        session_id: str,
        raw_query: str,
        normalized_query: str,
        top_level_group: Optional[str],
        detected_category: Optional[str],
        selected_scheme_id: Optional[str],
        detected_intent: str,
        resolution_status: str,
        llm_used: bool = False
    ):
        log_entry = {
            "session_id": session_id,
            "raw_query": raw_query,
            "normalized_query": normalized_query,
            "top_level_group": top_level_group,
            "detected_category": detected_category,
            "selected_scheme_id": selected_scheme_id,
            "detected_intent": detected_intent,
            "resolution_status": resolution_status,
            "llm_used": llm_used,
            "timestamp": datetime.now().isoformat()
        }
        log_chat(log_entry)
    
    def log_unknown(self, session_id: str, query: str):
        self.log_query(
            session_id=session_id,
            raw_query=query,
            normalized_query=normalize_text(query),
            top_level_group=None,
            detected_category=None,
            selected_scheme_id=None,
            detected_intent="unknown",
            resolution_status="unknown",
            llm_used=False
        )

analytics_engine = AnalyticsEngine()