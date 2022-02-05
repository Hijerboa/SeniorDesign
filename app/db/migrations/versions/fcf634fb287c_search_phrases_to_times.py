"""Search phrases to times
Revision ID: fcf634fb287c
Revises: 49a19a0bb80a
Create Date: 2022-02-05 03:45:33.215079
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'fcf634fb287c'
down_revision = '49a19a0bb80a'
branch_labels = None
depends_on = None
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('key_rate_limit',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('last_query', sa.DateTime(), nullable=False),
    sa.Column('type', sa.Enum('archive', 'non_archive', name='twitter_api_token_type'), nullable=False),
    sa.Column('tweets_pulled', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('search_phrase_date',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('search_phrase_id', sa.Integer(), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['search_phrase_id'], ['search_phrases.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('search_phrase_date')
    op.drop_table('key_rate_limit')
    # ### end Alembic commands ###