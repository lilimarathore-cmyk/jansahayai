#backend/utils/feature_flags.py
# Feature Flags Configuration
# In future, these can be moved to database or .env file

class FeatureFlags:
    """
    Feature flags to enable/disable features without code changes.
    Set to False initially, change to True when feature is ready.
    """
    
    # Dynamic Schemes (Phase 3)
    # When False: Uses hardcoded schemes from data/scheme_001.json
    # When True: Fetches schemes from MongoDB 'dynamic_schemes' collection
    USE_DYNAMIC_SCHEMES = False
    
    # Analytics (Phase 4)
    # When False: No analytics logging
    # When True: Logs user interactions to MongoDB 'analytics_logs' collection
    USE_ANALYTICS = False
    
    # PDF Download (Feature 1 - Already working)
    ENABLE_PDF_DOWNLOAD = True
    
    # Voice Assistant (Enhancements - Feature 4)
    ENHANCE_VOICE_ASSISTANT = False
    
    # Admin Panel Access
    ADMIN_ACCESS_ENABLED = True
    
    # Complaint System (Feature 5)
    COMPLAINT_SYSTEM_ENABLED = False


# Singleton instance
feature_flags = FeatureFlags()