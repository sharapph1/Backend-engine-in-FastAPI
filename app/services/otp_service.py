from datetime import datetime
import secrets

from sqlalchemy.orm import Session

from app.core.otp_security import hash_otp, verify_otp_hash
from app.models.otp import OTP
from app.models.user import User
from app.services.email_service import EmailService


class OTPService:

    @staticmethod
    def generate_otp() -> str:
        return "".join(str(secrets.randbelow(10)) for _ in range(6))

    @staticmethod
    async def create_otp(
        db: Session,
        user: User,
        purpose: str = "EMAIL_VERIFICATION",
    ) -> str:
        # Delete previous OTPs for this user
        db.query(OTP).filter(OTP.user_id == user.id).delete()

        otp = OTPService.generate_otp()

        otp_record = OTP(
            user_id=user.id,
            otp_hash=hash_otp(otp),
            purpose=purpose,
        )

        db.add(otp_record)
        db.commit()

        await EmailService.send_otp(
            recipient=user.email,
            username=user.username,
            otp=otp,
        )

        return otp

    @staticmethod
    async def verify_otp(
        db: Session,
        user: User,
        entered_otp: str,
    ) -> tuple[bool, str]:
        otp = db.query(OTP).filter(OTP.user_id == user.id).first()

        if otp is None:
            return False, "No active OTP found. Please request a new one."

        if otp.is_used:
            return False, "OTP has already been used."

        now = datetime.utcnow()
        if otp.expires_at < now:
            db.delete(otp)
            db.commit()
            return False, "OTP has expired. Please request a new one."

        if otp.attempts >= 5:
            db.delete(otp)
            db.commit()
            return False, "Maximum verification attempts exceeded. Please request a new OTP."

        if not verify_otp_hash(entered_otp, otp.otp_hash):
            otp.attempts += 1
            db.commit()
            remaining = 5 - otp.attempts
            if remaining <= 0:
                db.delete(otp)
                db.commit()
                return False, "Maximum verification attempts exceeded. Please request a new OTP."
            return False, f"Invalid OTP. {remaining} attempts remaining."

        user.is_verified = True
        db.delete(otp)
        db.commit()

        return True, "Email verified successfully."

    @staticmethod
    async def resend_otp(
        db: Session,
        user: User,
        purpose: str = "EMAIL_VERIFICATION",
    ) -> str:
        if user.is_verified:
            raise ValueError("User email is already verified.")

        return await OTPService.create_otp(db=db, user=user, purpose=purpose)
