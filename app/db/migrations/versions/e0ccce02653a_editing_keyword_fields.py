"""Editing keyword fields
Revision ID: e0ccce02653a
Revises: 0ef19d940745
Create Date: 2022-01-08 04:09:43.938718
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
# revision identifiers, used by Alembic
revision = 'e0ccce02653a'
down_revision = '0ef19d940745'
branch_labels = None
depends_on = None
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bill_to_keyword')
    op.add_column('bill_key_words', sa.Column('bill', sa.String(length=16), nullable=True))
    op.create_foreign_key(None, 'bill_key_words', 'bills', ['bill'], ['bill_id'])
    op.drop_column('bill_key_words', 'value')
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
    op.add_column('bill_key_words', sa.Column('value', mysql.FLOAT(), nullable=False))
    op.drop_constraint(None, 'bill_key_words', type_='foreignkey')
    op.drop_column('bill_key_words', 'bill')
    op.create_table('bill_to_keyword',
    sa.Column('bill_id', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=16), nullable=True),
    sa.Column('keyword', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['bill_id'], ['bills.bill_id'], name='bill_to_keyword_ibfk_1'),
    sa.ForeignKeyConstraint(['keyword'], ['bill_key_words.id'], name='bill_to_keyword_ibfk_2'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###