from fastapi import APIRouter, Depends
from typing import List
from ..core.dependencies import get_current_user
from ..core.firebase import get_firestore_client
from ..models.schemas import VoteResponse
from ..services.vote_service import VoteService

router = APIRouter(prefix="/votes", tags=["votes"])


@router.get("/me", response_model=List[VoteResponse])
async def get_my_votes(current_user: dict = Depends(get_current_user)):
    """Get all votes by the current user"""
    db = get_firestore_client()
    service = VoteService(db)
    return service.get_user_votes(current_user['uid'])
