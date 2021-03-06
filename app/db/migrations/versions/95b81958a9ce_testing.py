"""Testing
Revision ID: 95b81958a9ce
Revises: e0ccce02653a
Create Date: 2022-01-08 19:55:51.198682
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
# revision identifiers, used by Alembic
revision = '95b81958a9ce'
down_revision = 'e0ccce02653a'
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