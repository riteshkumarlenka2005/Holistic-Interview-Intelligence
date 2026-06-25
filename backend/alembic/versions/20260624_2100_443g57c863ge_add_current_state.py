"""add current_state

Revision ID: 443g57c863ge
Revises: 332f46b752fd
Create Date: 2026-06-24 21:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '443g57c863ge'
down_revision: Union[str, None] = '332f46b752fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add current_state column to interview_sessions
    op.add_column('interview_sessions', sa.Column('current_state', sa.String(length=20), server_default='waiting', nullable=False))


def downgrade() -> None:
    # Remove current_state column from interview_sessions
    op.drop_column('interview_sessions', 'current_state')
