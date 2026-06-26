from fastapi import APIRouter, Depends
from app.dependencies import get_current_user_required, UserPayload

router = APIRouter()


@router.get("/me")
async def get_me(user: UserPayload = Depends(get_current_user_required)):
    """Get current authenticated user info."""
    return {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
    }


@router.get("/verify")
async def verify_token(user: UserPayload = Depends(get_current_user_required)):
    """Verify that the provided JWT token is valid."""
    return {
        "valid": True,
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role,
        },
    }
