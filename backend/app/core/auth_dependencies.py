import httpx
from fastapi import Header, HTTPException, Depends
from typing import Optional, Dict
from app.core.config import settings

async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict:
    """
    Verifies the JWT token by calling Supabase Auth API.
    Usage:
        @router.get("/me")
        async def me(user: dict = Depends(get_current_user)):
            return user
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Bearer token")

    token = authorization.split(" ", 1)[1]

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.SUPABASE_ANON_KEY,
                },
                timeout=10.0,
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user_data = response.json()
            # Backward compatibility for existing code
            user_data["user_id"] = user_data.get("id")
            user_data["role"] = user_data.get("app_metadata", {}).get("role", "user")
            
            return user_data
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Authentication service unavailable")

async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Checks if the user is active (Supabase user object usually means they are active).
    """
    return current_user

async def require_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Check for admin role in Supabase user metadata.
    """
    # Supabase roles are usually in user_metadata or app_metadata
    role = current_user.get("app_metadata", {}).get("role", "user")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[dict]:
    """
    Get user if authenticated, else None.
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
