"""Dependency injection - Supabase Auth based"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.supabase_client import get_supabase_client

security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Validate JWT token with Supabase Auth and return user info.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    
    try:
        client = get_supabase_client()
        
        # Verify token with Supabase Auth
        user_response = client.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        auth_user = user_response.user
        
        # Get role from users table
        profile = client.table("users").select("id, name, email, role").eq(
            "id", str(auth_user.id)
        ).execute()
        
        if profile.data:
            return profile.data[0]
        
        # Fallback if profile not found
        return {
            "id": str(auth_user.id),
            "email": auth_user.email,
            "role": "assignee",
            "name": auth_user.email
        }
    
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_sdr(current_user: dict = Depends(get_current_user)) -> dict:
    """Require SDR or admin role"""
    if current_user.get("role") not in ["admin", "sdr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SDR or Admin access required"
        )
    return current_user
