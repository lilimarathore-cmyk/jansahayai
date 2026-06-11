# ============================================
# FILE: backend/database.py
# COMPLETE FIXED VERSION - NO DEBUG, ONLY FIXES
# ============================================

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "divyangbot")
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class LocalCollection:
    def __init__(self, items):
        self._items = items

    def find(self, query=None, projection=None):
        query = query or {}
        return [
            self._apply_projection(item, projection)
            for item in self._items
            if self._matches(item, query)
        ]

    def find_one(self, query=None, projection=None):
        query = query or {}
        for item in self._items:
            if self._matches(item, query):
                return self._apply_projection(item, projection)
        return None

    def insert_one(self, document):
        self._items.append(document)
        return self

    def update_one(self, query, update, upsert=False):
        for item in self._items:
            if self._matches(item, query):
                if "$set" in update:
                    for key, value in update["$set"].items():
                        item[key] = value
                return self
        if upsert:
            new_doc = query.copy()
            if "$set" in update:
                for key, value in update["$set"].items():
                    new_doc[key] = value
            self._items.append(new_doc)
        return self

    def count_documents(self, query=None):
        return len(self._items)

    @staticmethod
    def _get_nested_value(obj: dict, path: str):
        """Get value from nested dict using dot notation"""
        parts = path.split('.')
        current = obj
        for part in parts:
            if not isinstance(current, dict):
                return None
            current = current.get(part)
            if current is None:
                return None
        return current

    @staticmethod
    def _matches(item: dict, query: dict) -> bool:
        """
        Check if item matches query.
        Supports dot notation for nested keys (e.g., 'meta.category')
        """
        for key, value in query.items():
            if '.' in key:
                item_value = LocalCollection._get_nested_value(item, key)
            else:
                item_value = item.get(key)
            
            if item_value != value:
                return False
        return True

    @staticmethod
    def _apply_projection(item, projection):
        if not projection:
            return deepcopy(item)
        result = {}
        for key in projection:
            if key in item:
                result[key] = deepcopy(item[key])
        return result

def _load_local_schemes():
    schemes = []
    if DATA_DIR.exists():
        for path in sorted(DATA_DIR.glob("scheme_*.json")):
            if "zones" not in str(path):
                try:
                    with path.open(encoding="utf-8") as file:
                        schemes.append(json.load(file))
                        print(f"Loaded: {path.name}")
                except Exception as e:
                    print(f"Error loading {path}: {e}")
    else:
        print(f"Data directory not found at: {DATA_DIR}")
    return schemes

def load_zones():
    """Load zones data from zones.json file"""
    zones_file = DATA_DIR / "zones.json"
    if zones_file.exists():
        try:
            with zones_file.open(encoding="utf-8") as file:
                zones_data = json.load(file)
                print(f"Loaded zones from: {zones_file.name}")
                return zones_data
        except Exception as e:
            print(f"Error loading zones.json: {e}")
            return {"city": "बिलासपुर", "zones": []}
    else:
        print(f"Zones file not found at: {zones_file}")
        return {"city": "बिलासपुर", "zones": []}

def _connect_mongo():
    if not MONGO_URL:
        print("[WARN] MONGO_URL not found. Using local JSON scheme data.")
        return None
    try:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        print("[OK] MongoDB Connected Successfully")
        return client[DB_NAME]
    except ServerSelectionTimeoutError:
        print("[WARN] MongoDB unavailable. Using local JSON scheme data.")
        return None
    except Exception as exc:
        print(f"[WARN] MongoDB connection error: {exc}")
        return None

db = _connect_mongo()

if db is not None:
    chat_collection = db["chats"]
    scheme_collection = db["schemes"]
    session_collection = db["sessions"]
    zones_collection = db["zones"]
else:
    chat_collection = LocalCollection([])
    scheme_collection = LocalCollection(_load_local_schemes())
    session_collection = LocalCollection([])
    zones_data = load_zones()
    zones_collection = LocalCollection(zones_data.get("zones", []))

def get_scheme(scheme_id: str) -> Optional[Dict]:
    return scheme_collection.find_one({"id": scheme_id})

def get_schemes_by_category(category: str) -> List[Dict]:
    result = scheme_collection.find({"meta.category": category})
    if 'Cursor' in str(type(result)):
        return list(result)
    return result

def get_all_schemes() -> List[Dict]:
    result = scheme_collection.find({})
    if 'Cursor' in str(type(result)):
        return list(result)
    return result if isinstance(result, list) else list(result)

def get_all_zones() -> List[Dict]:
    if db is not None:
        result = zones_collection.find({})
        if 'Cursor' in str(type(result)):
            return list(result)
        return result
    else:
        return zones_collection.find({})

def get_zone_by_ward(ward_number: int) -> Optional[Dict]:
    zones = get_all_zones()
    for zone in zones:
        wards = zone.get("wards", [])
        if ward_number in wards:
            return zone
    return None

def get_zone_by_area(area_text: str) -> Optional[Dict]:
    if not area_text:
        return None
    
    area_text_lower = area_text.lower().strip()
    zones = get_all_zones()
    
    for zone in zones:
        area_keywords = zone.get("area_keywords", [])
        for keyword in area_keywords:
            if not keyword:
                continue
            keyword_lower = keyword.lower()
            
            if keyword_lower == area_text_lower:
                return zone
            if keyword_lower in area_text_lower:
                return zone
            if len(area_text_lower) > 2 and area_text_lower in keyword_lower:
                return zone
        
        normalized_keywords = zone.get("normalized_keywords", [])
        for keyword in normalized_keywords:
            if not keyword:
                continue
            keyword_lower = keyword.lower()
            
            if keyword_lower == area_text_lower:
                return zone
            if keyword_lower in area_text_lower:
                return zone
            if len(area_text_lower) > 2 and area_text_lower in keyword_lower:
                return zone
    
    return None

def log_chat(log_entry: Dict):
    try:
        chat_collection.insert_one(log_entry)
    except Exception as e:
        print(f"Chat log error: {e}")

def get_session(session_id: str) -> Optional[Dict]:
    result = session_collection.find_one({"session_id": session_id})
    return result

def save_session(session_id: str, session_data: Dict):
    session_collection.update_one(
        {"session_id": session_id},
        {"$set": session_data},
        upsert=True
    )