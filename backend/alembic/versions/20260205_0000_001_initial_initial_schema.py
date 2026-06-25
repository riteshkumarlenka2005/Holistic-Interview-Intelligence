"""Initial schema with all core tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-05

This migration creates the initial database schema including:
- users: User accounts with role-based access
- otp_tokens: Email verification and password reset tokens
- refresh_tokens: JWT refresh token management
- learning_resources: Educational content
- resource_progress: User progress tracking
- interview_sessions: Interview session management
- interview_analysis: AI analysis results (JSONB)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============= USERS TABLE =============
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='student'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('oauth_provider', sa.String(length=20), nullable=True, server_default='local'),
        sa.Column('oauth_id', sa.String(length=255), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_role', 'users', ['role'], unique=False)
    op.create_index('ix_users_oauth', 'users', ['oauth_provider', 'oauth_id'], unique=False)

    # ============= OTP TOKENS TABLE =============
    op.create_table(
        'otp_tokens',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('code', sa.String(length=6), nullable=False),
        sa.Column('otp_type', sa.String(length=30), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_otp_tokens_user_id', 'otp_tokens', ['user_id'], unique=False)

    # ============= REFRESH TOKENS TABLE =============
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'], unique=False)
    op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'], unique=True)

    # ============= LEARNING RESOURCES TABLE =============
    op.create_table(
        'learning_resources',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('resource_type', sa.String(length=50), nullable=False, server_default='Article'),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('content_body', sa.Text(), nullable=True),
        sa.Column('video_url', sa.String(length=500), nullable=True),
        sa.Column('difficulty_level', sa.String(length=20), nullable=False, server_default='beginner'),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_learning_resources_slug', 'learning_resources', ['slug'], unique=True)
    op.create_index('ix_learning_resources_type', 'learning_resources', ['resource_type'], unique=False)
    op.create_index('ix_learning_resources_difficulty', 'learning_resources', ['difficulty_level'], unique=False)
    op.create_index('ix_learning_resources_published', 'learning_resources', ['is_published'], unique=False)

    # ============= RESOURCE PROGRESS TABLE =============
    op.create_table(
        'resource_progress',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('resource_id', sa.String(length=36), nullable=False),
        sa.Column('progress_percentage', sa.Float(), nullable=False, server_default='0'),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('time_spent_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_position', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resource_id'], ['learning_resources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_resource_progress_user_id', 'resource_progress', ['user_id'], unique=False)
    op.create_index('ix_resource_progress_resource_id', 'resource_progress', ['resource_id'], unique=False)
    op.create_index('ix_resource_progress_user_resource', 'resource_progress', ['user_id', 'resource_id'], unique=True)
    op.create_index('ix_resource_progress_completed', 'resource_progress', ['is_completed'], unique=False)

    # ============= INTERVIEW SESSIONS TABLE =============
    op.create_table(
        'interview_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('session_type', sa.String(length=50), nullable=False, server_default='Mock'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('target_job_role', sa.String(length=255), nullable=True),
        sa.Column('target_company', sa.String(length=255), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('questions', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('responses', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('video_url', sa.String(length=500), nullable=True),
        sa.Column('audio_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_interview_sessions_user_id', 'interview_sessions', ['user_id'], unique=False)
    op.create_index('ix_interview_sessions_user_status', 'interview_sessions', ['user_id', 'status'], unique=False)
    op.create_index('ix_interview_sessions_type', 'interview_sessions', ['session_type'], unique=False)
    op.create_index('ix_interview_sessions_started', 'interview_sessions', ['started_at'], unique=False)

    # ============= INTERVIEW ANALYSIS TABLE =============
    op.create_table(
        'interview_analysis',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('verbal_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('nonverbal_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('multimodal_score', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('analysis_version', sa.String(length=20), nullable=False, server_default='1.0'),
        sa.Column('processing_time_seconds', sa.Integer(), nullable=True),
        sa.Column('explainability', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['interview_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_interview_analysis_session_id', 'interview_analysis', ['session_id'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order of creation (respecting foreign key constraints)
    op.drop_table('interview_analysis')
    op.drop_table('interview_sessions')
    op.drop_table('resource_progress')
    op.drop_table('learning_resources')
    op.drop_table('refresh_tokens')
    op.drop_table('otp_tokens')
    op.drop_table('users')
