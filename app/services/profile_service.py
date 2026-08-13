"""
ProfileService — handles username, refer_id, and avatar updates.

Avatar URL strategy:
  Stored in DB: https://pub-xxx.r2.dev/avatars/{user_id}.webp
  Returned to client: <stored_url>?v=<unix_timestamp>

The query string cache-buster is appended at response time only —
it is never persisted to the database. This ensures:
  - The stored URL always points to the canonical object path.
  - Every upload returns a fresh URL that bypasses browser/CDN cache.
  - No orphaned objects are ever created (one key per user, always overwritten).
"""
import time
from io import BytesIO

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.r2 import BUCKET, r2_client
from app.models.user import User
from app.schemas.profile import (
    ProfileUpdateResponse,
    UpdateReferIdRequest,
    UpdateUsernameRequest,
)
from app.utils.image import (
    process_avatar,
    validate_image_content_type,
    validate_image_size,
)

# R2 object key prefix and content-type for stored avatars
AVATAR_PREFIX = "avatars"
AVATAR_CONTENT_TYPE = "image/webp"

# Cache-Control header sent to R2 on upload.
# "public, max-age=31536000" allows CDN caching; the ?v= buster handles invalidation.
AVATAR_CACHE_CONTROL = "public, max-age=31536000, immutable"


def _avatar_key(user_id: str) -> str:
    """Deterministic R2 object key for a user's avatar."""
    return f"{AVATAR_PREFIX}/{user_id}.webp"


def _avatar_public_url(user_id: str) -> str:
    """Stored (canonical) public URL — no cache-buster."""
    return f"{settings.r2_public_base_url}/{_avatar_key(user_id)}"


def _avatar_versioned_url(user_id: str) -> str:
    """Versioned public URL for client response — appends unix timestamp as ?v=."""
    return f"{_avatar_public_url(user_id)}?v={int(time.time())}"


class ProfileService:

    # ── Username ──────────────────────────────────────────────────────────────

    @staticmethod
    async def update_username(
        db: Session,
        current_user: User,
        data: UpdateUsernameRequest,
    ) -> ProfileUpdateResponse:
        new_username = data.username.strip()

        # No-op if unchanged
        if current_user.username == new_username:
            return ProfileUpdateResponse(
                message="Username is already set to this value.",
                username=current_user.username,
            )

        # Uniqueness check
        existing = db.query(User).filter(User.username == new_username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already taken.",
            )

        current_user.username = new_username
        db.commit()
        db.refresh(current_user)

        return ProfileUpdateResponse(
            message="Username updated successfully.",
            username=current_user.username,
        )

    # ── Refer ID (UID) ────────────────────────────────────────────────────────

    @staticmethod
    async def update_refer_id(
        db: Session,
        current_user: User,
        data: UpdateReferIdRequest,
    ) -> ProfileUpdateResponse:
        new_refer_id = data.refer_id.strip()

        # No-op if unchanged
        if current_user.refer_id == new_refer_id:
            return ProfileUpdateResponse(
                message="Referral ID is already set to this value.",
                refer_id=current_user.refer_id,
            )

        # Uniqueness check
        existing = db.query(User).filter(User.refer_id == new_refer_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This referral ID is already taken.",
            )

        current_user.refer_id = new_refer_id
        db.commit()
        db.refresh(current_user)

        return ProfileUpdateResponse(
            message="Referral ID updated successfully.",
            refer_id=current_user.refer_id,
        )

    # ── Avatar ────────────────────────────────────────────────────────────────

    @staticmethod
    async def upload_avatar(
        db: Session,
        current_user: User,
        file: UploadFile,
    ) -> ProfileUpdateResponse:
        """
        Full avatar upload pipeline:
          1. Validate MIME type
          2. Read & validate file size
          3. Process (crop + resize + encode WebP) in memory
          4. PUT to R2, overwriting avatars/{user_id}.webp
          5. Update DB only if avatar_url changed
          6. Return versioned URL for immediate cache bypass
        """
        # ── 1. MIME validation ────────────────────────────────────────────────
        content_type = file.content_type or ""
        try:
            validate_image_content_type(content_type)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=str(exc),
            )

        # ── 2. Read + size validation ─────────────────────────────────────────
        raw_bytes = await file.read()
        try:
            validate_image_size(raw_bytes)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=str(exc),
            )

        # ── 3. Process image (in-memory, no temp files) ───────────────────────
        try:
            webp_bytes = process_avatar(raw_bytes)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            )

        # ── 4. Upload to R2 ───────────────────────────────────────────────────
        object_key = _avatar_key(current_user.id)
        try:
            r2_client.put_object(
                Bucket=BUCKET,
                Key=object_key,
                Body=BytesIO(webp_bytes),
                ContentType=AVATAR_CONTENT_TYPE,
                ContentLength=len(webp_bytes),
                CacheControl=AVATAR_CACHE_CONTROL,
            )
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Storage upload failed: {exc}",
            )

        # ── 5. Update DB (skip write if URL is identical) ─────────────────────
        canonical_url = _avatar_public_url(current_user.id)
        if current_user.avatar_url != canonical_url:
            current_user.avatar_url = canonical_url
            db.commit()
            db.refresh(current_user)

        # ── 6. Return versioned URL for cache invalidation ────────────────────
        versioned_url = _avatar_versioned_url(current_user.id)
        return ProfileUpdateResponse(
            message="Avatar uploaded successfully.",
            avatar_url=versioned_url,
        )

    @staticmethod
    async def get_avatar_bytes(
        db: Session,
        current_user: User,
    ) -> bytes:
        """Fetch avatar bytes from R2 and return them (proxied to client)."""
        if not current_user.avatar_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No avatar set.",
            )
        
        object_key = _avatar_key(current_user.id)
        try:
            response = r2_client.get_object(Bucket=BUCKET, Key=object_key)
            return response["Body"].read()
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Avatar not found in storage: {exc}",
            )

    # ── Delete Avatar ─────────────────────────────────────────────────────────

    @staticmethod
    async def delete_avatar(
        db: Session,
        current_user: User,
    ) -> ProfileUpdateResponse:
        """Remove the avatar from R2 and clear avatar_url in the database."""
        if not current_user.avatar_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No avatar to delete.",
            )

        object_key = _avatar_key(current_user.id)
        try:
            r2_client.delete_object(Bucket=BUCKET, Key=object_key)
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Storage deletion failed: {exc}",
            )

        current_user.avatar_url = None
        db.commit()

        return ProfileUpdateResponse(message="Avatar removed successfully.")
