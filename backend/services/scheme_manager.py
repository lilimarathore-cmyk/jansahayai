# backend/services/scheme_manager.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.schemas.scheme_schema import SchemeCreate, SchemeUpdate
from backend.database import scheme_collection
import logging

logger = logging.getLogger(__name__)


class SchemeManager:
    """Manager class for CRUD operations on schemes"""
    
    def __init__(self):
        self.collection = scheme_collection
    
    async def get_all_schemes(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all schemes from database"""
        try:
            if active_only:
                schemes = self.collection.find({"active": True})
            else:
                schemes = self.collection.find({})
            
            # Convert to list and handle ObjectId + field mapping
            result = []
            for scheme in schemes:
                if "_id" in scheme:
                    scheme["_id"] = str(scheme["_id"])
                
                # Map fields to what frontend expects
                # Frontend expects: scheme_id, scheme_name_hi, scheme_name_en
                if "id" in scheme and "scheme_id" not in scheme:
                    scheme["scheme_id"] = scheme["id"]
                
                if "scheme_name" in scheme and isinstance(scheme["scheme_name"], dict):
                    if "hi" in scheme["scheme_name"] and "scheme_name_hi" not in scheme:
                        scheme["scheme_name_hi"] = scheme["scheme_name"]["hi"]
                    if "en" in scheme["scheme_name"] and "scheme_name_en" not in scheme:
                        scheme["scheme_name_en"] = scheme["scheme_name"]["en"]
                
                # Ensure active field exists
                if "active" not in scheme:
                    scheme["active"] = True
                
                result.append(scheme)
            
            logger.info(f"Retrieved {len(result)} schemes from database")
            return result
            
        except Exception as e:
            logger.error(f"Error getting schemes: {e}")
            return []
    
    async def get_scheme_by_id(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        """Get a single scheme by its ID"""
        try:
            # Try both 'id' and 'scheme_id' fields
            scheme = self.collection.find_one({"id": scheme_id})
            if not scheme:
                scheme = self.collection.find_one({"scheme_id": scheme_id})
            
            if scheme:
                if "_id" in scheme:
                    scheme["_id"] = str(scheme["_id"])
                
                # Map fields
                if "id" in scheme and "scheme_id" not in scheme:
                    scheme["scheme_id"] = scheme["id"]
                
                if "scheme_name" in scheme and isinstance(scheme["scheme_name"], dict):
                    if "hi" in scheme["scheme_name"] and "scheme_name_hi" not in scheme:
                        scheme["scheme_name_hi"] = scheme["scheme_name"]["hi"]
                    if "en" in scheme["scheme_name"] and "scheme_name_en" not in scheme:
                        scheme["scheme_name_en"] = scheme["scheme_name"]["en"]
            
            return scheme
            
        except Exception as e:
            logger.error(f"Error getting scheme {scheme_id}: {e}")
            return None
    
    async def add_scheme(self, scheme_data: SchemeCreate) -> Dict[str, Any]:
        """Add a new scheme to database"""
        try:
            # Check if scheme already exists
            existing = self.collection.find_one({"id": scheme_data.scheme_id})
            if not existing:
                existing = self.collection.find_one({"scheme_id": scheme_data.scheme_id})
            
            if existing:
                raise ValueError(f"Scheme {scheme_data.scheme_id} already exists")
            
            # Prepare document
            scheme_dict = scheme_data.dict()
            scheme_dict["id"] = scheme_data.scheme_id
            scheme_dict["created_at"] = datetime.now()
            scheme_dict["updated_at"] = datetime.now()
            
            # ✅ FIXED: scheme_name already exists as dict {hi, en} from scheme_data.dict()
            # No need to manually create scheme_name object - remove the wrong code
            
            # Insert into database
            self.collection.insert_one(scheme_dict)
            
            logger.info(f"Added new scheme: {scheme_data.scheme_id}")
            return scheme_dict
            
        except Exception as e:
            logger.error(f"Error adding scheme: {e}")
            raise
    
    async def update_scheme(self, scheme_id: str, scheme_data: SchemeUpdate) -> Optional[Dict[str, Any]]:
        """Update an existing scheme"""
        try:
            # Check if scheme exists
            existing = self.collection.find_one({"id": scheme_id})
            if not existing:
                existing = self.collection.find_one({"scheme_id": scheme_id})
            
            if not existing:
                logger.warning(f"Scheme {scheme_id} not found for update")
                return None
            
            # Prepare update data (only provided fields)
            update_data = scheme_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.now()
            
            # Handle scheme_name update
            if "scheme_name_hi" in update_data or "scheme_name_en" in update_data:
                scheme_name = {}
                if "scheme_name_hi" in update_data:
                    scheme_name["hi"] = update_data.pop("scheme_name_hi")
                if "scheme_name_en" in update_data:
                    scheme_name["en"] = update_data.pop("scheme_name_en")
                update_data["scheme_name"] = scheme_name
            
            # Handle scheme_id mapping
            if "scheme_id" in update_data:
                update_data["id"] = update_data.pop("scheme_id")
            
            # Update in database
            self.collection.update_one(
                {"id": scheme_id},
                {"$set": update_data}
            )
            
            # Return updated scheme
            updated = await self.get_scheme_by_id(scheme_id)
            logger.info(f"Updated scheme: {scheme_id}")
            return updated
            
        except Exception as e:
            logger.error(f"Error updating scheme {scheme_id}: {e}")
            raise
    
    async def delete_scheme(self, scheme_id: str, soft_delete: bool = True) -> bool:
        """Delete a scheme"""
        try:
            if soft_delete:
                # Soft delete - just mark as inactive
                self.collection.update_one(
                    {"id": scheme_id},
                    {"$set": {"active": False, "updated_at": datetime.now()}}
                )
                success = True
            else:
                # Hard delete - remove from database
                result = self.collection.delete_one({"id": scheme_id})
                success = result.deleted_count > 0
            
            if success:
                logger.info(f"Deleted scheme: {scheme_id} (soft_delete={soft_delete})")
            else:
                logger.warning(f"Scheme {scheme_id} not found for deletion")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting scheme {scheme_id}: {e}")
            return False
    
    async def get_schemes_by_category(self, category: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get schemes by category"""
        try:
            query = {"category": category}
            if active_only:
                query["active"] = True
            
            schemes = self.collection.find(query)
            
            result = []
            for scheme in schemes:
                if "_id" in scheme:
                    scheme["_id"] = str(scheme["_id"])
                
                # Map fields
                if "id" in scheme and "scheme_id" not in scheme:
                    scheme["scheme_id"] = scheme["id"]
                
                if "scheme_name" in scheme and isinstance(scheme["scheme_name"], dict):
                    if "hi" in scheme["scheme_name"] and "scheme_name_hi" not in scheme:
                        scheme["scheme_name_hi"] = scheme["scheme_name"]["hi"]
                    if "en" in scheme["scheme_name"] and "scheme_name_en" not in scheme:
                        scheme["scheme_name_en"] = scheme["scheme_name"]["en"]
                
                result.append(scheme)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting schemes by category {category}: {e}")
            return []
    
    async def get_total_count(self, active_only: bool = True) -> int:
        """Get total number of schemes"""
        try:
            query = {}
            if active_only:
                query["active"] = True
            
            count = self.collection.count_documents(query)
            return count
            
        except Exception as e:
            logger.error(f"Error counting schemes: {e}")
            return 0


# Singleton instance
scheme_manager = SchemeManager()