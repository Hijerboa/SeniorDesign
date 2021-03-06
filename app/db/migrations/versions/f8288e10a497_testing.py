"""Testing
Revision ID: f8288e10a497
Revises: 95b81958a9ce
Create Date: 2022-01-08 19:58:29.960039
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
# revision identifiers, used by Alembic
revision = 'f8288e10a497'
down_revision = '95b81958a9ce'
branch_labels = None
depends_on = None
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bills', 'summary',
               existing_type=mysql.LONGTEXT(collation='utf8mb4_unicode_ci'),
               type_=sa.Text(length=16000000),
               existing_nullable=True)
    # ### end Alembic commands ###
def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bills', 'summary',
               existing_type=sa.Text(length=16000000),
               type_=mysql.LONGTEXT(collation='utf8mb4_unicode_ci'),
               existing_nullable=True)
    # ### end Alembic commands ###