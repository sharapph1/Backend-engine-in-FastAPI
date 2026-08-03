from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.game import Game
from app.models.user import User
from app.schemas.game import GameActionResponse, GameCreate, GameResponse


class GameService:

    @staticmethod
    async def create_game(db: Session, data: GameCreate) -> GameResponse:
        existing = db.query(Game).filter(Game.url == data.url).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Game URL already registered.",
            )

        game = Game(
            title=data.title,
            url=data.url,
            thumbnail_url=data.thumbnail_url,
            is_latest=data.is_latest,
            is_active=True,
        )
        db.add(game)
        db.commit()
        db.refresh(game)

        return GameResponse(
            id=game.id,
            title=game.title,
            url=game.url,
            thumbnail_url=game.thumbnail_url,
            is_latest=game.is_latest,
            likes_count=game.likes_count,
            plays_count=game.plays_count,
            is_liked=False,
            added_at=game.added_at,
        )

    @staticmethod
    async def get_games(db: Session, user: User | None = None) -> list[GameResponse]:
        games = db.query(Game).filter(Game.is_active == True).all()

        results = []
        for g in games:
            results.append(
                GameResponse(
                    id=g.id,
                    title=g.title,
                    url=g.url,
                    thumbnail_url=g.thumbnail_url,
                    is_latest=g.is_latest,
                    likes_count=g.likes_count,
                    plays_count=g.plays_count,
                    is_liked=False,  # no per-user like tracking in denormalized model
                    added_at=g.added_at,
                )
            )

        return results

    @staticmethod
    async def get_game_by_id(db: Session, game_id: str, user: User | None = None) -> GameResponse:
        g = db.query(Game).filter(Game.id == game_id, Game.is_active == True).first()
        if not g:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game not found.",
            )

        return GameResponse(
            id=g.id,
            title=g.title,
            url=g.url,
            thumbnail_url=g.thumbnail_url,
            is_latest=g.is_latest,
            likes_count=g.likes_count,
            plays_count=g.plays_count,
            is_liked=False,
            added_at=g.added_at,
        )

    @staticmethod
    async def like_game(db: Session, game_id: str) -> GameActionResponse:
        """Atomically increment likes_count."""
        game = db.query(Game).filter(Game.id == game_id, Game.is_active == True).first()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found.")

        db.execute(
            text("UPDATE games SET likes_count = likes_count + 1 WHERE id = :gid"),
            {"gid": game_id},
        )
        db.commit()
        return GameActionResponse(message="Liked game.", active=True)

    @staticmethod
    async def record_gameplay(db: Session, game_id: str) -> GameActionResponse:
        """Atomically increment plays_count."""
        game = db.query(Game).filter(Game.id == game_id, Game.is_active == True).first()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found.")

        db.execute(
            text("UPDATE games SET plays_count = plays_count + 1 WHERE id = :gid"),
            {"gid": game_id},
        )
        db.commit()
        return GameActionResponse(message="Gameplay recorded.", active=True)
