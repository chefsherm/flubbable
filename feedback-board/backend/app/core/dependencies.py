from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .firebase import verify_token, get_firestore_client
from ..services.user_service import UserService

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify Firebase token and return current user"""
    token = credentials.credentials
    decoded_token = verify_token(token)

    if not decoded_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    db = get_firestore_client()
    user_service = UserService(db)

    # Get or create user in Firestore
    user = user_service.get_or_create_user(
        uid=decoded_token['uid'],
        email=decoded_token.get('email', '')
    )

    return user


async def get_current_admin_user(
    current_user: dict = Depends(get_current_user)
):
    """Verify that current user is an admin"""
    if not current_user.get('is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
