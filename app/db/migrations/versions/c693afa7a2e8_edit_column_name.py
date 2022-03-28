"""Edit column name
Revision ID: c693afa7a2e8
Revises: eb8c090680d0
Create Date: 2022-03-26 12:26:19.934138
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'c693afa7a2e8'
down_revision = 'eb8c090680d0'
branch_labels = None
depends_on = None
def upgrade() -> None:
    op.alter_column('tweets', 'seniment', nullable=True, new_column_name='sentiment', existing_type=sa.Float)
def downgrade() -> None:
    op.alter_column('tweets', 'sentiment', nullable=True, new_column_name='seniment', existing_type=sa.Float)