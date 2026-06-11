# ============================================
# FILE: backend/main.py
# FIX 5: Register admin routes
# CHANGE: ADDED admin_router (no existing code removed)
# ============================================

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.chat_route import router as chat_router
from backend.routes.admin_route import router as admin_router
from backend.routes.analytics_route import router as analytics_router


load_dotenv()

app = FastAPI(title="DivyangBot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(analytics_router)

@app.get("/")
def root():
    return {"status": "success", "message": "DivyangBot Backend Running"}

@app.get("/health")
def health():
    return {"status": "ok"}