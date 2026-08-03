"""add game count columns to games table"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "202308040001_add_game_count_columns"
# Use the most recent existing revision as down_revision
# Adjust if the actual latest revision ID differs
 down_revision = "95e709d0d272"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('games', sa.Column('thumbnail_url', sa.String(), nullable=True))
    op.add_column('games', sa.Column('is_latest', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('games', sa.Column('likes_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('games', sa.Column('plays_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('games', sa.Column('added_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))

def downgrade():
    op.drop_column('games', 'added_at')
    op.drop_column('games', 'plays_count')
    op.drop_column('games', 'likes_count')
    op.drop_column('games', 'is_latest')
    op.drop_column('games', 'thumbnail_url')
