# backend/routes/admin_route.py
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from backend.schemas.scheme_schema import SchemeCreate, SchemeUpdate, SchemeResponse
from backend.services.scheme_manager import scheme_manager
import logging

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)


@router.get("/schemes", response_model=List[Dict[str, Any]])
async def get_all_schemes(active_only: bool = False):
    """
    Get all schemes
    - active_only=True: Only active schemes
    - active_only=False: All schemes (including inactive)
    """
    try:
        schemes = await scheme_manager.get_all_schemes(active_only=active_only)
        return schemes
    except Exception as e:
        logger.error(f"Error in get_all_schemes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching schemes: {str(e)}"
        )


@router.get("/schemes/{scheme_id}", response_model=Dict[str, Any])
async def get_scheme(scheme_id: str):
    """Get a single scheme by ID"""
    try:
        scheme = await scheme_manager.get_scheme_by_id(scheme_id)
        if not scheme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scheme {scheme_id} not found"
            )
        return scheme
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_scheme: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching scheme: {str(e)}"
        )


@router.post("/schemes", status_code=status.HTTP_201_CREATED)
async def create_scheme(scheme_data: SchemeCreate):
    """Create a new scheme"""
    try:
        existing = await scheme_manager.get_scheme_by_id(scheme_data.scheme_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Scheme {scheme_data.scheme_id} already exists"
            )
        
        new_scheme = await scheme_manager.add_scheme(scheme_data)
        return new_scheme
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_scheme: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating scheme: {str(e)}"
        )


@router.put("/schemes/{scheme_id}")
async def update_scheme(scheme_id: str, scheme_data: SchemeUpdate):
    """Update an existing scheme"""
    try:
        existing = await scheme_manager.get_scheme_by_id(scheme_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scheme {scheme_id} not found"
            )
        
        updated_scheme = await scheme_manager.update_scheme(scheme_id, scheme_data)
        return updated_scheme
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_scheme: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating scheme: {str(e)}"
        )


@router.delete("/schemes/{scheme_id}")
async def delete_scheme(scheme_id: str, soft_delete: bool = True):
    """
    Delete a scheme
    - soft_delete=True: Just mark as inactive
    - soft_delete=False: Permanently delete
    """
    try:
        existing = await scheme_manager.get_scheme_by_id(scheme_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scheme {scheme_id} not found"
            )
        
        success = await scheme_manager.delete_scheme(scheme_id, soft_delete=soft_delete)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete scheme {scheme_id}"
            )
        
        return {"message": f"Scheme {scheme_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_scheme: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting scheme: {str(e)}"
        )


@router.get("/stats/overview")
async def get_overview_stats():
    """Get overview statistics for dashboard"""
    try:
        total_schemes = await scheme_manager.get_total_count(active_only=False)
        active_schemes = await scheme_manager.get_total_count(active_only=True)
        
        return {
            "total_schemes": total_schemes,
            "active_schemes": active_schemes,
            "inactive_schemes": total_schemes - active_schemes
        }
    except Exception as e:
        logger.error(f"Error in get_overview_stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stats: {str(e)}"
        )


# ✅ UPDATED: Dynamic categories from database
@router.get("/categories")
async def get_categories():
    """Get all available categories from database schemes"""
    try:
        schemes = await scheme_manager.get_all_schemes(active_only=False)
        unique_categories = list(set([s.get("category") for s in schemes if s.get("category")]))
        
        if unique_categories:
            name_map = {
                "divyang_pension": "दिव्यांग पेंशन",
                "women_pension": "महिला पेंशन",
                "widow_pension": "विधवा पेंशन",
                "general_pension": "सामान्य पेंशन",
                "old_age_pension": "वृद्धावस्था पेंशन",
                "family_assistance": "परिवार सहायता",
                "scholarship": "छात्रवृत्ति",
                "assistive_devices": "सहायक उपकरण",
                "marriage_incentive": "विवाह प्रोत्साहन",
                "civil_services": "सिविल सेवा",
                "hostel": "छात्रावास",
                "camp": "शिविर",
                "rehabilitation": "पुनर्वास",
                "tg_card": "टीजी कार्ड",
                "transgender_support": "ट्रांसजेंडर सहायता",
                "divyang_support": "दिव्यांग सहायता",
                "divyang_education": "दिव्यांग शिक्षा",
                "divyang_empowerment": "दिव्यांग सशक्तिकरण",
                "divyang_education_support": "दिव्यांग शिक्षा सहायता",
                "divyang_equipment_support": "दिव्यांग उपकरण",
                "divyang_rehabilitation_support": "दिव्यांग पुनर्वास",
            }
            categories = [{"id": cat, "name": name_map.get(cat, cat.replace('_', ' ').title())} for cat in unique_categories]
            return sorted(categories, key=lambda x: x["name"])
    except Exception as e:
        logger.error(f"Error fetching categories from DB: {e}")
    
    # Fallback categories
    return [
        {"id": "divyang_pension", "name": "दिव्यांग पेंशन"},
        {"id": "women_pension", "name": "महिला पेंशन"},
        {"id": "widow_pension", "name": "विधवा पेंशन"},
        {"id": "general_pension", "name": "सामान्य पेंशन"},
        {"id": "old_age_pension", "name": "वृद्धावस्था पेंशन"},
        {"id": "family_assistance", "name": "परिवार सहायता"},
        {"id": "scholarship", "name": "छात्रवृत्ति"},
        {"id": "assistive_devices", "name": "सहायक उपकरण"},
        {"id": "marriage_incentive", "name": "विवाह प्रोत्साहन"},
        {"id": "civil_services", "name": "सिविल सेवा"},
        {"id": "hostel", "name": "छात्रावास"},
        {"id": "camp", "name": "शिविर"},
        {"id": "rehabilitation", "name": "पुनर्वास"},
        {"id": "tg_card", "name": "टीजी कार्ड"},
        {"id": "transgender_support", "name": "ट्रांसजेंडर सहायता"},
        {"id": "divyang_support", "name": "दिव्यांग सहायता"},
        {"id": "divyang_education", "name": "दिव्यांग शिक्षा"},
        {"id": "divyang_empowerment", "name": "दिव्यांग सशक्तिकरण"},
        {"id": "divyang_education_support", "name": "दिव्यांग शिक्षा सहायता"},
        {"id": "divyang_equipment_support", "name": "दिव्यांग उपकरण"},
        {"id": "divyang_rehabilitation_support", "name": "दिव्यांग पुनर्वास"},
    ]


@router.get("/debug/schemes-count")
async def debug_schemes_count():
    """Debug endpoint to check schemes count"""
    try:
        total = await scheme_manager.get_total_count(active_only=False)
        return {"total_schemes": total, "message": "Debug endpoint working"}
    except Exception as e:
        return {"error": str(e)}