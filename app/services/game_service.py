from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.game import Game
from app.models.gamelike import GameLike
from app.models.gamepin import GamePin
from app.models.gameplay import GamePlay
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
            is_active=True,
        )
        db.add(game)
        db.commit()
        db.refresh(game)

        return GameResponse(
            id=game.id,
            title=game.title,
            url=game.url,
            likes_count=0,
            pins_count=0,
            plays_count=0,
            is_liked=False,
            is_pinned=False,
            created_at=game.created_at,
        )

    @staticmethod
    async def get_games(db: Session, user: User | None = None) -> list[GameResponse]:
        games = db.query(Game).filter(Game.is_active == True).all()

        results = []
        for g in games:
            likes_count = db.query(GameLike).filter(GameLike.game_id == g.id).count()
            pins_count = db.query(GamePin).filter(GamePin.game_id == g.id).count()
            plays_count = db.query(GamePlay).filter(GamePlay.game_id == g.id).count()

            is_liked = False
            is_pinned = False
            if user:
                is_liked = db.query(GameLike).filter(
                    GameLike.game_id == g.id, GameLike.user_id == user.id
                ).first() is not None
                is_pinned = db.query(GamePin).filter(
                    GamePin.game_id == g.id, GamePin.user_id == user.id
                ).first() is not None

            results.append(
                GameResponse(
                    id=g.id,
                    title=g.title,
                    url=g.url,
                    likes_count=likes_count,
                    pins_count=pins_count,
                    plays_count=plays_count,
                    is_liked=is_liked,
                    is_pinned=is_pinned,
                    created_at=g.created_at,
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

        likes_count = db.query(GameLike).filter(GameLike.game_id == g.id).count()
        pins_count = db.query(GamePin).filter(GamePin.game_id == g.id).count()
        plays_count = db.query(GamePlay).filter(GamePlay.game_id == g.id).count()

        is_liked = False
        is_pinned = False
        if user:
            is_liked = db.query(GameLike).filter(
                GameLike.game_id == g.id, GameLike.user_id == user.id
            ).first() is not None
            is_pinned = db.query(GamePin).filter(
                GamePin.game_id == g.id, GamePin.user_id == user.id
            ).first() is not None

        return GameResponse(
            id=g.id,
            title=g.title,
            url=g.url,
            likes_count=likes_count,
            pins_count=pins_count,
            plays_count=plays_count,
            is_liked=is_liked,
            is_pinned=is_pinned,
            created_at=g.created_at,
        )

    @staticmethod
    async def toggle_like_game(db: Session, game_id: str, user: User) -> GameActionResponse:
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found.")

        existing = db.query(GameLike).filter(
            GameLike.game_id == game_id, GameLike.user_id == user.id
        ).first()

        if existing:
            db.delete(existing)
            db.commit()
            return GameActionResponse(message="Unliked game.", active=False)

        new_like = GameLike(game_id=game_id, user_id=user.id)
        db.add(new_like)
        db.commit()
        return GameActionResponse(message="Liked game.", active=True)

    @staticmethod
    async def toggle_pin_game(db: Session, game_id: str, user: User) -> GameActionResponse:
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found.")

        existing = db.query(GamePin).filter(
            GamePin.game_id == game_id, GamePin.user_id == user.id
        ).first()

        if existing:
            db.delete(existing)
            db.commit()
            return GameActionResponse(message="Unpinned game.", active=False)

        new_pin = GamePin(game_id=game_id, user_id=user.id)
        db.add(new_pin)
        db.commit()
        return GameActionResponse(message="Pinned game.", active=True)

    @staticmethod
    async def record_gameplay(db: Session, game_id: str, user: User) -> GameActionResponse:
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found.")

        gameplay = GamePlay(game_id=game_id, user_id=user.id)
        db.add(gameplay)
        db.commit()

        return GameActionResponse(message="Gameplay recorded.", active=True)
