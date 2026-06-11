# ============================================
# FILE: backend/schemas/chat_schema.py
# ============================================

from pydantic import BaseModel
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    status: str
    response: str
    session_id: str
    scheme_id: Optional[str] = None
    is_eligible: Optional[bool] = False

class SessionData(BaseModel):
    session_id: str
    user_zone: Optional[Dict] = None
    user_ward: Optional[int] = None
    last_active_scheme_id: Optional[str] = None
    scheme: Optional[str] = None
    scheme_id: Optional[str] = None
    step: Optional[str] = None
    age: Optional[int] = None
    disability: Optional[int] = None
    income: Optional[int] = None
    bpl_status: Optional[str] = None
    secc_status: Optional[str] = None
    pension_flow_active: Optional[bool] = False
    continuation_mode: Optional[bool] = False
    remaining_options: Optional[Dict] = None