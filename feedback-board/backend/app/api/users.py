from fastapi import APIRouter, Depends
from ..core.dependencies import get_current_user
from ..models.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "uid": current_user['uid'],
        "email": current_user['email'],
        "is_admin": current_user.get('is_admin', False)
    }
