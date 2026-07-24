from datetime import date, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(StrEnum):
    TEACHER = "teacher"
    STUDENT = "student"


class ActivityStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (Index("uq_users_email_lower", text("lower(email)"), unique=True),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    institution: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    refresh_sessions: Mapped[list["RefreshSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    completions: Mapped[list["ActivityCompletion"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    evidences: Mapped[list["Evidence"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    medals: Mapped[list["UserMedal"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class RefreshSession(Base):
    __tablename__ = "refresh_sessions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replaced_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))

    user: Mapped[User] = relationship(back_populates="refresh_sessions")


class Course(TimestampMixin, Base):
    __tablename__ = "courses"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    owner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    owner: Mapped[User] = relationship()
    activities: Mapped[list["Activity"]] = relationship(back_populates="course")


class Activity(TimestampMixin, Base):
    __tablename__ = "activities"
    __table_args__ = (
        CheckConstraint("points > 0", name="positive_points"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[ActivityStatus] = mapped_column(
        Enum(
            ActivityStatus,
            name="activity_status",
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=ActivityStatus.DRAFT,
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    author_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    course_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("courses.id", ondelete="SET NULL")
    )

    author: Mapped[User] = relationship()
    course: Mapped[Course | None] = relationship(back_populates="activities")
    completions: Mapped[list["ActivityCompletion"]] = relationship(
        back_populates="activity", cascade="all, delete-orphan"
    )
    evidences: Mapped[list["Evidence"]] = relationship(
        back_populates="activity", cascade="all, delete-orphan"
    )


class ActivityCompletion(Base):
    __tablename__ = "activity_completions"
    __table_args__ = (
        UniqueConstraint("activity_id", "student_id", name="uq_completion_activity_student"),
        CheckConstraint("awarded_points > 0", name="positive_awarded_points"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    activity_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    awarded_points: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    activity: Mapped[Activity] = relationship(back_populates="completions")
    student: Mapped[User] = relationship(back_populates="completions")


class Evidence(Base):
    __tablename__ = "evidences"
    __table_args__ = (
        UniqueConstraint("activity_id", "student_id", name="uq_evidence_activity_student"),
        CheckConstraint("size_bytes > 0", name="positive_size"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    activity_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    activity: Mapped[Activity] = relationship(back_populates="evidences")
    student: Mapped[User] = relationship(back_populates="evidences")


class UserMedal(Base):
    __tablename__ = "user_medals"
    __table_args__ = (UniqueConstraint("user_id", "medal_key", name="uq_user_medal"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    medal_key: Mapped[str] = mapped_column(String(40), nullable=False)
    awarded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    user: Mapped[User] = relationship(back_populates="medals")


class Post(TimestampMixin, Base):
    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    author: Mapped[User] = relationship()
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    post_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    post: Mapped[Post] = relationship(back_populates="comments")
    author: Mapped[User] = relationship()


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    subject: Mapped[str] = mapped_column(String(180), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sender_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    sender: Mapped[User] = relationship()
