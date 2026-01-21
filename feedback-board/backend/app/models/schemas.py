from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    uid: str
    email: str
    is_admin: bool = False


class FeatureRequestCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)


class FeatureRequestResponse(BaseModel):
    id: str
    title: str
    description: str
    author_id: str
    author_email: str
    votes: int = 0
    created_at: str
    updated_at: str


class VoteResponse(BaseModel):
    id: str
    user_id: str
    request_id: str
    created_at: str


class ErrorResponse(BaseModel):
    detail: str
