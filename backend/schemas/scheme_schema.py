#backend/schemas/scheme_schema.py
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class EligibilityRule(BaseModel):
    """Single eligibility rule for a scheme"""
    field: str  # e.g., "age", "disability", "income"
    operator: str  # e.g., ">=", "<=", "==", "!="
    value: Any  # e.g., 18, 40, "हाँ"
    message: str  # Failure message in Hindi


class ConversationStep(BaseModel):
    """Single step in conversation flow"""
    step: int
    question: str  # Question to ask user
    field: str  # Which field to store answer in
    validation: Dict[str, Any]  # Validation rules
    fail_message: str  # Message if validation fails
    next_step_on_pass: str  # Next step number or "final"
    next_step_on_fail: str  # Next step number or "end"


class ConversationFlow(BaseModel):
    """Complete conversation flow for eligibility check"""
    steps: List[ConversationStep]
    final_message: str  # Message when user is eligible
    not_eligible_message: str  # Message when user is not eligible


class SchemeCreate(BaseModel):
    """Schema for creating a new scheme"""
    scheme_id: str = Field(..., pattern=r'^cg_scheme_\d{3}$')  # ✅ Fixed: regex → pattern
    scheme_name: Dict[str, str] = Field(..., description="Hindi and English names")
    category: str = Field(..., description="Scheme category")
    short_answer: str = Field(..., description="Brief description")
    benefits: str = Field(..., description="Benefits details")
    documents: List[str] = Field(..., description="Required documents list")
    apply_steps: List[str] = Field(..., description="Application steps")
    locations: List[str] = Field(..., description="Where to apply")
    pdf_link: str = Field(..., description="PDF download link")
    keywords: List[str] = Field(..., description="Search keywords")
    eligibility_rules: List[EligibilityRule] = Field(default_factory=list)
    conversation_flow: Optional[Dict[str, Any]] = None
    active: bool = True
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        valid_categories = [
            "divyang_pension", "widow_pension", "old_age_pension", 
            "family_assistance", "scholarship", "assistive_devices",
            "marriage_incentive", "civil_services", "hostel", "camp",
            "rehabilitation", "tg_card"
        ]
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")
        return v
    
    @field_validator('eligibility_rules', mode='before')
    @classmethod
    def validate_eligibility_rules(cls, v):
        if v is None:
            return []
        return v


class SchemeUpdate(BaseModel):
    """Schema for updating an existing scheme (all fields optional)"""
    scheme_name: Optional[Dict[str, str]] = None
    category: Optional[str] = None
    short_answer: Optional[str] = None
    benefits: Optional[str] = None
    documents: Optional[List[str]] = None
    apply_steps: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    pdf_link: Optional[str] = None
    keywords: Optional[List[str]] = None
    eligibility_rules: Optional[List[EligibilityRule]] = None
    conversation_flow: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None


class SchemeResponse(BaseModel):
    """Schema for returning scheme data"""
    scheme_id: str
    scheme_name: Dict[str, str]
    category: str
    short_answer: str
    benefits: str
    documents: List[str]
    apply_steps: List[str]
    locations: List[str]
    pdf_link: str
    keywords: List[str]
    eligibility_rules: List[EligibilityRule]
    conversation_flow: Optional[Dict[str, Any]] = None
    active: bool
    created_at: datetime
    updated_at: datetime


class SchemeListResponse(BaseModel):
    """Schema for list of schemes"""
    total: int
    schemes: List[SchemeResponse]