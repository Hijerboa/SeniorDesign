"""Adding table for key phrases
Revision ID: b09fc1873142
Revises: 49c969dc1d47
Create Date: 2021-11-12 17:07:44.206778
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
# revision identifiers, used by Alembic
revision = 'b09fc1873142'
down_revision = '49c969dc1d47'
branch_labels = None
depends_on = None
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bill_key_words',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('bill', sa.String(length=16), nullable=True),
    sa.Column('training_model', sa.String(length=16), nullable=True),
    sa.Column('phrase', sa.String(length=128), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['bill'], ['bills.bill_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_constraint('tasks_ibfk_1', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'launched_by')
    # ### end Alembic commands ###
def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('launched_by', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('tasks_ibfk_1', 'tasks', 'users', ['launched_by'], ['id'])
    op.drop_table('bill_key_words')
    # ### end Alembic commands ###