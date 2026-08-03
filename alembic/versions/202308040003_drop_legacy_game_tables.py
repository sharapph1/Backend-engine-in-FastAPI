"""Drop legacy game tables after data migration"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "202308040003_drop_legacy_game_tables"

down_revision = "202308040002_migrate_game_counts"
branch_labels = None
depends_on = None

def upgrade():
    # Drop legacy tables if they exist
    op.drop_table('game_likes')
    op.drop_table('game_pins')
    op.drop_table('game_plays')

def downgrade():
    # Recreate tables (basic schema) – useful only for local testing
    op.create_table(
        'game_likes',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('game_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_table(
        'game_pins',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('game_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_table(
        'game_plays',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('game_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
