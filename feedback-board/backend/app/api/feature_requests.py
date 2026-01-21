from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..core.dependencies import get_current_user, get_current_admin_user
from ..core.firebase import get_firestore_client
from ..models.schemas import FeatureRequestCreate, FeatureRequestResponse
from ..services.feature_request_service import FeatureRequestService
from ..services.vote_service import VoteService

router = APIRouter(prefix="/feature-requests", tags=["feature-requests"])


@router.get("", response_model=List[FeatureRequestResponse])
async def get_all_feature_requests():
    """Get all feature requests (public endpoint)"""
    db = get_firestore_client()
    service = FeatureRequestService(db)
    return service.get_all()


@router.get("/{request_id}", response_model=FeatureRequestResponse)
async def get_feature_request(request_id: str):
    """Get a specific feature request (public endpoint)"""
    db = get_firestore_client()
    service = FeatureRequestService(db)
    request = service.get_by_id(request_id)

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature request not found"
        )

    return request


@router.post("", response_model=FeatureRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_feature_request(
    data: FeatureRequestCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new feature request"""
    db = get_firestore_client()
    service = FeatureRequestService(db)

    return service.create(
        title=data.title,
        description=data.description,
        author_id=current_user['uid'],
        author_email=current_user['email']
    )


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature_request(
    request_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """Delete a feature request (admin only)"""
    db = get_firestore_client()
    service = FeatureRequestService(db)

    # Check if request exists
    request = service.get_by_id(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature request not found"
        )

    service.delete(request_id)
    return None


@router.post("/{request_id}/vote", response_model=FeatureRequestResponse)
async def vote_for_request(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Vote for a feature request"""
    db = get_firestore_client()
    request_service = FeatureRequestService(db)
    vote_service = VoteService(db)

    # Check if request exists
    request = request_service.get_by_id(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature request not found"
        )

    # Check if user already voted
    if vote_service.has_user_voted(current_user['uid'], request_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already voted for this request"
        )

    # Create vote
    vote_service.create_vote(current_user['uid'], request_id)

    # Increment vote count
    return request_service.increment_votes(request_id)


@router.delete("/{request_id}/vote", response_model=FeatureRequestResponse)
async def unvote_for_request(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove vote from a feature request"""
    db = get_firestore_client()
    request_service = FeatureRequestService(db)
    vote_service = VoteService(db)

    # Check if request exists
    request = request_service.get_by_id(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature request not found"
        )

    # Check if user has voted
    if not vote_service.has_user_voted(current_user['uid'], request_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not voted for this request"
        )

    # Delete vote
    vote_service.delete_vote(current_user['uid'], request_id)

    # Decrement vote count
    return request_service.decrement_votes(request_id)
