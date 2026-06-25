"""phase 2 schema

Revision ID: 554h68d974hf
Revises: 443g57c863ge
Create Date: 2026-06-24 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '554h68d974hf'
down_revision: Union[str, None] = '443g57c863ge'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create interview_templates table
    op.create_table('interview_templates',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('target_job_role', sa.String(length=255), nullable=True),
        sa.Column('technical_weight', sa.Integer(), server_default='70', nullable=False),
        sa.Column('communication_weight', sa.Integer(), server_default='20', nullable=False),
        sa.Column('speech_weight', sa.Integer(), server_default='10', nullable=False),
        sa.Column('confidence_weight', sa.Integer(), server_default='0', nullable=False),
        sa.Column('base_difficulty', sa.String(length=50), server_default='intermediate', nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 2. Add difficulty_modifier to interview_sessions
    op.add_column('interview_sessions', sa.Column('difficulty_modifier', sa.Integer(), server_default='0', nullable=False))
    
    # 3. Add per-answer scores to responses
    op.add_column('responses', sa.Column('technical_score', sa.Float(), nullable=True))
    op.add_column('responses', sa.Column('communication_score', sa.Float(), nullable=True))
    op.add_column('responses', sa.Column('speech_metrics', sa.JSON(), nullable=True))
    op.add_column('responses', sa.Column('feedback', sa.Text(), nullable=True))

def downgrade() -> None:
    op.drop_column('responses', 'feedback')
    op.drop_column('responses', 'speech_metrics')
    op.drop_column('responses', 'communication_score')
    op.drop_column('responses', 'technical_score')
    op.drop_column('interview_sessions', 'difficulty_modifier')
    op.drop_table('interview_templates')
