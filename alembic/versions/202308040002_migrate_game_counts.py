"""migrate existing like/play counts into games table"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "202308040002_migrate_game_counts"
down_revision = "202308040001_add_game_count_columns"
branch_labels = None
depends_on = None

def upgrade():
    # Update likes_count from GameLike table
    op.execute(
        """
        UPDATE games SET likes_count = sub.cnt
        FROM (
            SELECT game_id, COUNT(*) AS cnt FROM game_likes GROUP BY game_id
        ) AS sub
        WHERE games.id = sub.game_id;
        """
    )
    # Update plays_count from GamePlay table
    op.execute(
        """
        UPDATE games SET plays_count = sub.cnt
        FROM (
            SELECT game_id, COUNT(*) AS cnt FROM game_plays GROUP BY game_id
        ) AS sub
        WHERE games.id = sub.game_id;
        """
    )
    # Optionally set added_at to earliest created_at from related tables if needed
    op.execute(
        """
        UPDATE games SET added_at = sub.min_created
        FROM (
            SELECT game_id, MIN(created_at) AS min_created FROM (
                SELECT game_id, created_at FROM game_likes
                UNION ALL
                SELECT game_id, created_at FROM game_plays
                UNION ALL
                SELECT game_id, created_at FROM game_pins
            ) AS all_events
            GROUP BY game_id
        ) AS sub
        WHERE games.id = sub.game_id;
        """
    )

def downgrade():
    # No automatic revert; set counts to 0
    op.execute("UPDATE games SET likes_count = 0, plays_count = 0")
