"""removing task
Revision ID: a4b8e9bcac89
Revises: fcf634fb287c
Create Date: 2022-02-15 21:57:49.779989
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
# revision identifiers, used by Alembic
revision = 'a4b8e9bcac89'
down_revision = 'fcf634fb287c'
branch_labels = None
depends_on = None
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tasks')
    # ### end Alembic commands ###
def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tasks',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('task_id', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=64), nullable=False),
    sa.Column('status', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=16), nullable=True),
    sa.Column('message', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=512), nullable=True),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('task_type', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=64), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='tasks_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###