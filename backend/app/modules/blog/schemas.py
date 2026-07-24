from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.core.schemas import ApiModel


class CreatePostRequest(ApiModel):
    title: str = Field(min_length=2, max_length=180)
    content: str = Field(min_length=2, max_length=10_000)


class CreateCommentRequest(ApiModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentSummary(ApiModel):
    id: UUID
    author_name: str
    content: str
    created_at: datetime


class PostSummary(ApiModel):
    id: UUID
    title: str
    content: str
    author_name: str
    created_at: datetime
    comments: list[CommentSummary]
