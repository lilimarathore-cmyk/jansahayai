# ============================================
# FILE: backend/routes/admin_auth.py
# JWT Authentication for Admin Panel
# This is ADDITIONAL, does NOT remove existing login
# ============================================

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
import os
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])
security = HTTPBearer()

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 8

# Admin credentials (move to env in production)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@jansahay.ai")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123")

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

def create_access_token(email: str) -> str:
    """Create JWT token"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    payload = {
        "sub": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token - for protected routes"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=LoginResponse)
async def admin_login(request: LoginRequest):
    """
    JWT Login - NEW endpoint
    OLD login endpoint (/admin/login) still works unchanged
    """
    if request.email != ADMIN_EMAIL or request.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    token = create_access_token(request.email)
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=JWT_EXPIRY_HOURS * 3600
    )

@router.get("/verify")
async def verify_token_endpoint(email: str = Depends(verify_token)):
    """Verify if token is valid"""
    return {"valid": True, "email": email}