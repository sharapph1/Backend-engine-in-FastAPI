from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.game import GameActionResponse, GameCreate, GameResponse
from app.services.game_service import GameService

router = APIRouter(
    prefix="/games",
    tags=["Games"],
)


@router.post(
    "",
    response_model=GameResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_game(
    data: GameCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # admin-only in future; auth required for now
):
    return await GameService.create_game(db=db, data=data)


@router.get(
    "",
    response_model=list[GameResponse],
    status_code=status.HTTP_200_OK,
)
async def list_games(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),  # public endpoint
):
    return await GameService.get_games(db=db, user=current_user)


@router.get(
    "/{game_id}",
    response_model=GameResponse,
    status_code=status.HTTP_200_OK,
)
async def get_game(
    game_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),  # public endpoint
):
    return await GameService.get_game_by_id(db=db, game_id=game_id, user=current_user)


@router.post(
    "/{game_id}/like",
    response_model=GameActionResponse,
    status_code=status.HTTP_200_OK,
)
async def like_game(
    game_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # must be logged in to like
):
    return await GameService.like_game(db=db, game_id=game_id)


@router.post(
    "/{game_id}/play",
    response_model=GameActionResponse,
    status_code=status.HTTP_200_OK,
)
async def record_play(
    game_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),  # record plays even for guests
):
    return await GameService.record_gameplay(db=db, game_id=game_id)
