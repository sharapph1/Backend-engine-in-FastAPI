from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import (
    MessageResponse,
    RefreshTokenRequest,
    ResendOTP,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    VerifyOTP,
)
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserRegister,
    db: Session = Depends(get_db),
):
    return await AuthService.register_user(db=db, data=data)


@router.post(
    "/verify-otp",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_otp(
    data: VerifyOTP,
    db: Session = Depends(get_db),
):
    message = await AuthService.verify_user_otp(db=db, data=data)
    return MessageResponse(message=message)


@router.post(
    "/resend-otp",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def resend_otp(
    data: ResendOTP,
    db: Session = Depends(get_db),
):
    message = await AuthService.resend_user_otp(db=db, data=data)
    return MessageResponse(message=message)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    data: UserLogin,
    db: Session = Depends(get_db),
):
    return await AuthService.login_user(db=db, data=data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    return await AuthService.refresh_tokens(db=db, data=data)


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def logout(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = await AuthService.logout_user(
        db=db, data=data, current_user=current_user
    )
    return MessageResponse(message=message)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
