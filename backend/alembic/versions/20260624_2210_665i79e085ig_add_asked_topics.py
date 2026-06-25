"""add asked_topics for topic memory

Revision ID: 665i79e085ig
Revises: 554h68d974hf
Create Date: 2026-06-24 22:10:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '665i79e085ig'
down_revision: Union[str, None] = '554h68d974hf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('interview_sessions',
        sa.Column('asked_topics', sa.JSON(), server_default='[]', nullable=False)
    )


def downgrade() -> None:
    op.drop_column('interview_sessions', 'asked_topics')
