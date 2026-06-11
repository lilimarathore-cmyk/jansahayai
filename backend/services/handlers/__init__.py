# backend/services/handlers/__init__.py
from .number_handler import number_handler
from .followup_handler import followup_handler
from .direct_scheme_handler import direct_scheme_handler
from .unknown_handler import unknown_handler

__all__ = ["number_handler", "followup_handler", "direct_scheme_handler", "unknown_handler"]