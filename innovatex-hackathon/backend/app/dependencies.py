import jwt
from dataclasses import dataclass
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

security_scheme = HTTPBearer(auto_error=False)


@dataclass
class UserPayload:
    """Decoded Supabase JWT user payload."""
    user_id: str
    email: str
    role: str


def verify_supabase_jwt(token: str) -> UserPayload:
    """Verify a Supabase-issued JWT and return user payload."""
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={
                "verify_aud": True,
                "verify_exp": True,
                "require": ["sub", "exp", "iat"],
            },
            audience="authenticated",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )

    return UserPayload(
        user_id=payload.get("sub", ""),
        email=payload.get("email", ""),
        role=payload.get("role", "authenticated"),
    )


async def get_current_user_required(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> UserPayload:
    """FastAPI dependency - requires valid JWT. Returns 401 if missing or invalid."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return verify_supabase_jwt(credentials.credentials)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[UserPayload]:
    """FastAPI dependency - returns user if valid token, None if missing or invalid."""
    if credentials is None:
        return None
    try:
        return verify_supabase_jwt(credentials.credentials)
    except HTTPException:
        return None
