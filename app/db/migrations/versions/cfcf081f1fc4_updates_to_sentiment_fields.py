"""Updates to sentiment fields
Revision ID: cfcf081f1fc4
Revises: c693afa7a2e8
Create Date: 2022-03-28 14:50:06.373323
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
# revision identifiers, used by Alembic
revision = 'cfcf081f1fc4'
down_revision = 'c693afa7a2e8'
branch_labels = None
depends_on = None
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bills', 'sentiment',
               existing_type=mysql.FLOAT(),
               type_=sa.JSON(),
               existing_nullable=True)
    op.add_column('tweets', sa.Column('sentiment_confidence', sa.Float(), nullable=True))
    # ### end Alembic commands ###
def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tweets', 'sentiment_confidence')
    op.alter_column('bills', 'sentiment',
               existing_type=sa.JSON(),
               type_=mysql.FLOAT(),
               existing_nullable=True)
    # ### end Alembic commands ###