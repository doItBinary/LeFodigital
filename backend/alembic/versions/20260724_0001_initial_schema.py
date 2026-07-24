"""Create the initial LeFodigital schema.

Revision ID: 20260724_0001
Revises:
Create Date: 2026-07-24
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260724_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=7), nullable=False),
        sa.Column("institution", sa.String(length=160), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("role IN ('teacher', 'student')", name="ck_users_valid_role"),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("uq_users_email_lower", "users", [sa.text("lower(email)")], unique=True)

    op.create_table(
        "refresh_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("replaced_by", sa.Uuid()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_refresh_sessions_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_refresh_sessions"),
    )

    op.create_table(
        "courses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], name="fk_courses_owner_id_users", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_courses"),
    )

    op.create_table(
        "activities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("due_date", sa.Date()),
        sa.Column("status", sa.String(length=9), nullable=False, server_default="draft"),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("points > 0", name="ck_activities_positive_points"),
        sa.CheckConstraint("status IN ('draft', 'published')", name="ck_activities_valid_status"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], name="fk_activities_author_id_users", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], name="fk_activities_course_id_courses", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_activities"),
    )

    op.create_table(
        "activity_completions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("activity_id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("awarded_points", sa.Integer(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("awarded_points > 0", name="ck_activity_completions_positive_awarded_points"),
        sa.ForeignKeyConstraint(["activity_id"], ["activities.id"], name="fk_activity_completions_activity_id_activities", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], name="fk_activity_completions_student_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_activity_completions"),
        sa.UniqueConstraint("activity_id", "student_id", name="uq_completion_activity_student"),
    )

    op.create_table(
        "evidences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("activity_id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("stored_name", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("size_bytes > 0", name="ck_evidences_positive_size"),
        sa.ForeignKeyConstraint(["activity_id"], ["activities.id"], name="fk_evidences_activity_id_activities", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], name="fk_evidences_student_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_evidences"),
        sa.UniqueConstraint("activity_id", "student_id", name="uq_evidence_activity_student"),
        sa.UniqueConstraint("stored_name", name="uq_evidences_stored_name"),
    )

    op.create_table(
        "user_medals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("medal_key", sa.String(length=40), nullable=False),
        sa.Column("awarded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_user_medals_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_user_medals"),
        sa.UniqueConstraint("user_id", "medal_key", name="uq_user_medal"),
    )

    op.create_table(
        "posts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], name="fk_posts_author_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_posts"),
    )

    op.create_table(
        "comments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], name="fk_comments_post_id_posts", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], name="fk_comments_author_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_comments"),
    )

    op.create_table(
        "contact_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("subject", sa.String(length=180), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("sender_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], name="fk_contact_messages_sender_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_contact_messages"),
    )


def downgrade() -> None:
    op.drop_table("contact_messages")
    op.drop_table("comments")
    op.drop_table("posts")
    op.drop_table("user_medals")
    op.drop_table("evidences")
    op.drop_table("activity_completions")
    op.drop_table("activities")
    op.drop_table("courses")
    op.drop_table("refresh_sessions")
    op.drop_index("uq_users_email_lower", table_name="users")
    op.drop_table("users")
