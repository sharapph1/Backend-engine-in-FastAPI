import secrets
import string
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.session import Session as UserSession
from app.models.user import User
from app.schemas.auth import (
    RefreshTokenRequest,
    ResendOTP,
    TokenResponse,
    UserLogin,
    UserRegister,
    VerifyOTP,
)
from app.services.otp_service import OTPService


class AuthService:

def _gen_refer_id() -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(8))


class AuthService:
    @staticmethod
    async def register_user(
        db: Session,
        data: UserRegister,
    ) -> User:
        existing_user = db.query(User).filter(
            or_(
                User.email == data.email,
                User.username == data.username,
            )
        ).first()

        if existing_user:
            if existing_user.email == data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email is already registered.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already taken.",
            )

        hashed_pwd = hash_password(data.password)

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hashed_pwd,
            is_verified=False,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        if not user.refer_id:
            from app.services.referral_service import ReferralService as _RS
            user.refer_id = _RS.generate_refer_id()
            db.commit()
            db.refresh(user)

        # Auto-claim referral if code was provided
        if data.referral_code and data.referral_code.strip():
            try:
                from app.schemas.referral import ReferralClaimRequest as _RCR
                from app.services.referral_service import ReferralService as _RS
                await _RS.claim_referral(
                    db=db,
                    user=user,
                    data=_RCR(referral_code=data.referral_code.strip()),
                )
            except Exception:
                pass  # Never fail registration because of a bad referral code

        await OTPService.create_otp(db=db, user=user)

        return user

    @staticmethod
    async def verify_user_otp(
        db: Session,
        data: VerifyOTP,
    ) -> TokenResponse:
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        # If already verified, just issue tokens directly
        if not user.is_verified:
            success, message = await OTPService.verify_otp(
                db=db,
                user=user,
                entered_otp=data.otp,
            )

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=message,
                )

        # Issue tokens after successful verification
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        session_record = UserSession(
            user_id=user.id,
            refresh_token_hash=hash_password(refresh_token),
        )
        db.add(session_record)
        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    @staticmethod
    async def resend_user_otp(
        db: Session,
        data: ResendOTP,
    ) -> str:
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        try:
            await OTPService.resend_otp(db=db, user=user)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        return "OTP sent successfully."

    @staticmethod
    async def login_user(
        db: Session,
        data: UserLogin,
    ) -> TokenResponse:
        user = db.query(User).filter(
            or_(
                User.email == data.email_or_username,
                User.username == data.email_or_username,
            )
        ).first()

        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email is not verified. Please verify your OTP first.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled.",
            )

        user.last_login = datetime.utcnow()

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        session_record = UserSession(
            user_id=user.id,
            refresh_token_hash=hash_password(refresh_token),
        )

        db.add(session_record)
        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    @staticmethod
    async def refresh_tokens(
        db: Session,
        data: RefreshTokenRequest,
    ) -> TokenResponse:
        try:
            payload = decode_token(data.refresh_token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type.",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload.",
            )

        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User inactive or missing.",
            )

        active_sessions = db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_revoked == False,
            UserSession.expires_at > datetime.utcnow(),
        ).all()

        matching_session = None
        for sess in active_sessions:
            if verify_password(data.refresh_token, sess.refresh_token_hash):
                matching_session = sess
                break

        if not matching_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session revoked or invalid.",
            )

        new_access_token = create_access_token(subject=user.id)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=data.refresh_token,
            token_type="bearer",
        )

    @staticmethod
    async def logout_user(
        db: Session,
        data: RefreshTokenRequest,
        current_user: User,
    ) -> str:
        active_sessions = db.query(UserSession).filter(
            UserSession.user_id == current_user.id,
            UserSession.is_revoked == False,
        ).all()

        revoked_count = 0
        for sess in active_sessions:
            if verify_password(data.refresh_token, sess.refresh_token_hash):
                sess.is_revoked = True
                revoked_count += 1

        db.commit()

        if revoked_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Active session not found or already logged out.",
            )

        return "Successfully logged out."