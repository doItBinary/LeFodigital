from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.blog.schemas import (
    CreateCommentRequest,
    CreatePostRequest,
    PostSummary,
)
from app.modules.blog.service import add_comment, create_post, list_posts


router = APIRouter(prefix="/posts", tags=["Blog"])


@router.get("", response_model=list[PostSummary])
def get_posts(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PostSummary]:
    return list_posts(db)


@router.post("", response_model=PostSummary, status_code=status.HTTP_201_CREATED)
def post(
    data: CreatePostRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PostSummary:
    return create_post(db, user, data)


@router.post("/{post_id}/comments", response_model=PostSummary, status_code=status.HTTP_201_CREATED)
def comment(
    post_id: UUID,
    data: CreateCommentRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PostSummary:
    return add_comment(db, user, post_id, data)
