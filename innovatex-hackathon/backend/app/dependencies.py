import jwt
from dataclasses import dataclass
from typing import Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
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


def _get_jwks_public_key(token_kid: str = "") -> str:
    """
    Build the ES256 public key from the Supabase JWKS.
    
    If SUPABASE_JWKS_URL is set, fetches the JWKS dynamically.
    Otherwise falls back to HS256 with SUPABASE_JWT_SECRET.
    """
    if settings.SUPABASE_JWKS_URL:
        import httpx
        import json as _json
        try:
            response = httpx.get(settings.SUPABASE_JWKS_URL, timeout=10)
            response.raise_for_status()
            jwks = response.json()
            # Find key matching the token's kid, fall back to first key
            key_data = None
            for key in jwks["keys"]:
                if token_kid and key.get("kid") == token_kid:
                    key_data = key
                    break
            if key_data is None:
                key_data = jwks["keys"][0]
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch JWKS: {exc}",
            )
        return _build_ec_public_key(key_data)
    elif settings.SUPABASE_JWT_SECRET:
        # HS256 fallback — return None to signal HS256 mode
        return None
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No JWKS URL or JWT secret configured",
        )


def _build_ec_public_key(jwk: dict) -> str:
    """Convert an EC JWK to a PEM-encoded public key string."""
    import base64

    x_int = int.from_bytes(
        base64.urlsafe_b64decode(jwk["x"] + "=="), "big"
    )
    y_int = int.from_bytes(
        base64.urlsafe_b64decode(jwk["y"] + "=="), "big"
    )

    public_key = ec.EllipticCurvePublicNumbers(
        x_int, y_int, ec.SECP256R1()
    ).public_key(default_backend())

    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")


def verify_supabase_jwt(token: str) -> UserPayload:
    """Verify a Supabase-issued JWT and return user payload.

    Supports both ES256 (JWKS) and HS256 (shared secret) depending on config.
    """
    try:
        # Try JWKS (ES256) first
        if settings.SUPABASE_JWKS_URL:
            # Extract kid from token header before decoding
            import json as _json
            import base64
            header_part = token.split(".")[0]
            header_part += "=" * (4 - len(header_part) % 4)
            try:
                header = _json.loads(base64.urlsafe_b64decode(header_part).decode())
            except Exception:
                header = {}
            kid = header.get("kid", "")

            public_key = _get_jwks_public_key(kid)
            algorithms = ["ES256"]
            secret_or_key = public_key
        elif settings.SUPABASE_JWT_SECRET:
            algorithms = ["HS256"]
            secret_or_key = settings.SUPABASE_JWT_SECRET
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="JWT verification not configured",
            )

        payload = jwt.decode(
            token,
            secret_or_key,
            algorithms=algorithms,
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
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed token",
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
