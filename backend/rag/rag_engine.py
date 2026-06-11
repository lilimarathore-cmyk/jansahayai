# backend/rag/rag_engine.py
# COMPLETE REWRITE - Hybrid Search with Intent-Aware Retrieval

from typing import List, Dict, Optional, Tuple, Any
from backend.database import get_all_schemes, get_scheme
from backend.utils.text_normalizer import normalize_text
import re


class RAGEngine:
    def __init__(self):
        # Cache for frequent queries
        self._cache = {}
        self._cache_size = 100
        
        # Field weights for scoring
        self.field_weights = {
            "scheme_id_exact": 100,      # Exact scheme ID match
            "scheme_name_exact": 80,      # Exact scheme name match
            "scheme_id_partial": 60,      # Partial scheme ID
            "scheme_name_partial": 50,    # Partial scheme name match
            "category_match": 40,         # Category match
            "keyword_match": 30,          # Keyword match from NLP
            "benefits_match": 20,         # Benefits text match
            "content_match": 15,          # Any content match
            "short_answer_match": 10      # Short answer match
        }
        
        # Intent to field mapping (which field to prioritize)
        self.intent_field_map = {
            "ask_documents": "content.documents",
            "ask_eligibility": "content.eligibility.rules",
            "ask_benefits": "content.benefits.text",
            "ask_process": "content.application.steps",
            "ask_location": "content.application.locations",
            "ask_amount": "content.benefits.text",
            "general": "content.short_answer"
        }
        
        # Stop words to ignore in search
        self.stop_words = {"है", "के", "में", "को", "से", "की", "का", "हो", "और", "भी", "यह", "वह", "for", "the", "a", "an", "is", "are", "to", "of", "and"}
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for search (remove stop words, extra spaces)"""
        if not text:
            return ""
        text = text.lower()
        # Remove stop words
        words = text.split()
        words = [w for w in words if w not in self.stop_words]
        return " ".join(words)
    
    def _search_in_field(self, text: str, search_term: str) -> bool:
        """Check if search term exists in text"""
        if not text or not search_term:
            return False
        normalized_text = self._normalize_text(text)
        normalized_term = self._normalize_text(search_term)
        return normalized_term in normalized_text
    
    def _calculate_relevance_score(self, scheme: Dict, query: str, intent: str = "general") -> float:
        """
        Calculate relevance score for a scheme based on query and intent.
        Higher score = more relevant.
        """
        score = 0.0
        query_lower = query.lower()
        query_normalized = self._normalize_text(query)
        
        scheme_id = scheme.get("id", scheme.get("scheme_id", ""))
        
        # ========== 1. EXACT SCHEME ID MATCH (Highest Priority) ==========
        if scheme_id and query_lower == scheme_id.lower():
            score += self.field_weights["scheme_id_exact"]
            return score
        
        # Partial scheme ID match
        if scheme_id and scheme_id.lower() in query_lower:
            score += self.field_weights["scheme_id_partial"]
        
        # ========== 2. SCHEME NAME MATCH ==========
        scheme_name_obj = scheme.get("scheme_name", {})
        if isinstance(scheme_name_obj, dict):
            name_hi = scheme_name_obj.get("hi", "")
            name_en = scheme_name_obj.get("en", "")
        else:
            name_hi = str(scheme_name_obj)
            name_en = str(scheme_name_obj)
        
        # Exact name match (Hindi)
        if name_hi and query_lower == name_hi.lower():
            score += self.field_weights["scheme_name_exact"]
        elif name_hi and query_normalized in self._normalize_text(name_hi):
            score += self.field_weights["scheme_name_partial"]
        
        # Exact name match (English)
        if name_en and query_lower == name_en.lower():
            score += self.field_weights["scheme_name_exact"]
        elif name_en and query_normalized in self._normalize_text(name_en):
            score += self.field_weights["scheme_name_partial"]
        
        # ========== 3. CATEGORY MATCH ==========
        category = scheme.get("meta", {}).get("category", "")
        if category and query_normalized in self._normalize_text(category):
            score += self.field_weights["category_match"]
        
        # ========== 4. NLP KEYWORDS MATCH ==========
        nlp = scheme.get("nlp", {})
        keywords = nlp.get("keywords", [])
        scheme_keywords = nlp.get("scheme_identity_keywords", [])
        all_keywords = keywords + scheme_keywords
        
        for keyword in all_keywords:
            if keyword and keyword.lower() in query_lower:
                score += self.field_weights["keyword_match"]
                break  # One keyword match is enough for this bonus
        
        # ========== 5. CONTENT FIELD MATCH (Intent-Aware) ==========
        content = scheme.get("content", {})
        
        # Check intent-specific field first
        if intent in self.intent_field_map:
            target_field = self.intent_field_map[intent]
            field_parts = target_field.split(".")
            field_value = content
            for part in field_parts:
                if isinstance(field_value, dict):
                    field_value = field_value.get(part, {})
                else:
                    break
            
            # Extract text from field
            field_text = self._extract_text_from_field(field_value)
            if self._search_in_field(field_text, query):
                score += self.field_weights["content_match"] + 10  # Bonus for intent match
        
        # ========== 6. BENEFITS TEXT MATCH ==========
        benefits = content.get("benefits", {})
        benefits_text = self._extract_text_from_field(benefits)
        if self._search_in_field(benefits_text, query):
            score += self.field_weights["benefits_match"]
        
        # ========== 7. SHORT ANSWER MATCH ==========
        short_answer = content.get("short_answer", {})
        short_text = self._extract_text_from_field(short_answer)
        if self._search_in_field(short_text, query):
            score += self.field_weights["short_answer_match"]
        
        # ========== 8. GENERAL CONTENT MATCH ==========
        content_str = str(content).lower()
        if query_lower in content_str:
            score += self.field_weights["content_match"]
        
        return score
    
    def _extract_text_from_field(self, field: Any) -> str:
        """Extract text from nested field structure"""
        if field is None:
            return ""
        
        if isinstance(field, str):
            return field
        
        if isinstance(field, dict):
            # Try Hindi first, then English, then any text field
            if "hi" in field and field["hi"]:
                return field["hi"]
            if "en" in field and field["en"]:
                return field["en"]
            if "text" in field and field["text"]:
                return self._extract_text_from_field(field["text"])
            # Return first string value found
            for value in field.values():
                if isinstance(value, str):
                    return value
        
        if isinstance(field, list):
            texts = []
            for item in field[:3]:  # Limit to first 3 items
                text = self._extract_text_from_field(item)
                if text:
                    texts.append(text)
            return " ".join(texts)
        
        return str(field)
    
    def search_schemes(
        self, 
        query: str, 
        intent: str = "general",
        limit: int = 5,
        min_score: int = 10
    ) -> List[Dict]:
        """
        Search schemes by relevance score.
        
        Args:
            query: User query
            intent: Detected intent
            limit: Max number of results
            min_score: Minimum score to include
        
        Returns:
            List of schemes with '_rag_score' added
        """
        # Check cache first
        cache_key = f"{query}_{intent}"
        if cache_key in self._cache:
            return self._cache[cache_key][:limit]
        
        all_schemes = get_all_schemes()
        if not all_schemes:
            return []
        
        scored_results = []
        for scheme in all_schemes:
            score = self._calculate_relevance_score(scheme, query, intent)
            if score >= min_score:
                scheme_copy = scheme.copy()
                scheme_copy["_rag_score"] = score
                scored_results.append(scheme_copy)
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x["_rag_score"], reverse=True)
        
        # Cache results (limit cache size)
        self._cache[cache_key] = scored_results
        if len(self._cache) > self._cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        return scored_results[:limit]
    
    def get_best_scheme(
        self, 
        query: str, 
        intent: str = "general",
        min_score: int = 20
    ) -> Optional[Dict]:
        """
        Get the single best matching scheme.
        
        Returns:
            Scheme dict or None if no good match found
        """
        results = self.search_schemes(query, intent, limit=1, min_score=min_score)
        if results:
            return results[0]
        return None
    
    def get_scheme_by_id(self, scheme_id: str) -> Optional[Dict]:
        """Get scheme by exact ID (with fallback to get_scheme)"""
        # First try RAG scoring
        results = self.search_schemes(scheme_id, "ask_specific_scheme", limit=1, min_score=50)
        if results and results[0].get("id", results[0].get("scheme_id")) == scheme_id:
            return results[0]
        
        # Fallback to database get_scheme
        return get_scheme(scheme_id)
    
    def get_schemes_by_category(self, category: str) -> List[Dict]:
        """Get all schemes in a category"""
        all_schemes = get_all_schemes()
        result = []
        
        for scheme in all_schemes:
            scheme_category = scheme.get("meta", {}).get("category", "")
            if scheme_category == category:
                result.append(scheme)
        
        return result
    
    def search_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict]:
        """Simple keyword search (fast, no scoring)"""
        keyword_lower = keyword.lower()
        all_schemes = get_all_schemes()
        results = []
        
        for scheme in all_schemes:
            scheme_name = scheme.get("scheme_name", {})
            if isinstance(scheme_name, dict):
                name_text = scheme_name.get("hi", "") + " " + scheme_name.get("en", "")
            else:
                name_text = str(scheme_name)
            
            if keyword_lower in name_text.lower():
                results.append(scheme)
                if len(results) >= limit:
                    break
        
        return results
    
    def format_search_results(self, results: List[Dict]) -> str:
        """Format search results for display"""
        if not results:
            return "❌ कोई योजना नहीं मिली।"
        
        response = "🔍 **खोज परिणाम:**\n\n"
        for i, scheme in enumerate(results, 1):
            scheme_name_obj = scheme.get("scheme_name", {})
            if isinstance(scheme_name_obj, dict):
                name = scheme_name_obj.get("hi", "योजना")
            else:
                name = str(scheme_name_obj)
            
            score = scheme.get("_rag_score", 0)
            response += f"{i}. **{name}**"
            
            # Show relevance indicator
            if score > 80:
                response += " 🎯 (बिल्कुल सही)"
            elif score > 50:
                response += " ✅ (संबंधित)"
            
            response += "\n\n"
        
        response += "💡 किसी योजना की पूरी जानकारी के लिए उसका **नंबर** या **Scheme ID** लिखें।"
        return response
    
    def clear_cache(self):
        """Clear the search cache"""
        self._cache.clear()
        print("[RAG] Cache cleared")


# ========== SINGLETON INSTANCE ==========
rag_engine = RAGEngine()