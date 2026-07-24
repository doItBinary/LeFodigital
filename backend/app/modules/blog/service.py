from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Comment, Post, User
from app.dependencies import api_error
from app.modules.blog.schemas import (
    CommentSummary,
    CreateCommentRequest,
    CreatePostRequest,
    PostSummary,
)
from app.modules.gamification.service import recalculate_medals


def _query():
    return select(Post).options(
        selectinload(Post.author),
        selectinload(Post.comments).selectinload(Comment.author),
    )


def to_summary(post: Post) -> PostSummary:
    return PostSummary(
        id=post.id,
        title=post.title,
        content=post.content,
        author_name=post.author.name,
        created_at=post.created_at,
        comments=[
            CommentSummary(
                id=item.id,
                author_name=item.author.name,
                content=item.content,
                created_at=item.created_at,
            )
            for item in sorted(post.comments, key=lambda comment: comment.created_at)
        ],
    )


def list_posts(db: Session) -> list[PostSummary]:
    posts = db.scalars(_query().order_by(Post.created_at.desc())).unique().all()
    return [to_summary(post) for post in posts]


def create_post(db: Session, user: User, data: CreatePostRequest) -> PostSummary:
    post = Post(
        title=data.title.strip(),
        content=data.content.strip(),
        author_id=user.id,
    )
    db.add(post)
    db.flush()
    recalculate_medals(db, user.id)
    db.commit()
    return to_summary(db.scalar(_query().where(Post.id == post.id)))


def add_comment(
    db: Session,
    user: User,
    post_id: UUID,
    data: CreateCommentRequest,
) -> PostSummary:
    post = db.get(Post, post_id)
    if not post:
        raise api_error(status.HTTP_404_NOT_FOUND, "post_not_found", "Publicación no encontrada.")
    db.add(Comment(post_id=post_id, author_id=user.id, content=data.content.strip()))
    db.commit()
    return to_summary(db.scalar(_query().where(Post.id == post_id)))
