"""Updates to tasks
Revision ID: 1ef16633796a
Revises: d7a7e9a514a8
Create Date: 2022-02-15 22:39:12.028710
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '1ef16633796a'
down_revision = 'd7a7e9a514a8'
branch_labels = None
depends_on = None
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task_errors', sa.Column('task_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'task_errors', 'tasks', ['task_id'], ['id'])
    # ### end Alembic commands ###
def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'task_errors', type_='foreignkey')
    op.drop_column('task_errors', 'task_id')
    # ### end Alembic commands ###