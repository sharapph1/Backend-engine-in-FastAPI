from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.profile import (
    ProfileUpdateResponse,
    UpdateReferIdRequest,
    UpdateUsernameRequest,
)
from app.services.profile_service import ProfileService

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


@router.patch(
    "/username",
    response_model=ProfileUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update username",
    description=(
        "Update the authenticated user's username. "
        "Must be 3–30 characters, alphanumeric and underscores only. "
        "Returns 409 if already taken."
    ),
)
async def update_username(
    data: UpdateUsernameRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProfileService.update_username(
        db=db, current_user=current_user, data=data
    )


@router.patch(
    "/refer-id",
    response_model=ProfileUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update referral UID",
    description=(
        "Update the authenticated user's unique referral ID. "
        "Must be 4–20 characters, alphanumeric and underscores only. "
        "Returns 409 if already taken."
    ),
)
async def update_refer_id(
    data: UpdateReferIdRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProfileService.update_refer_id(
        db=db, current_user=current_user, data=data
    )


@router.post(
    "/avatar",
    response_model=ProfileUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload or replace avatar",
    description=(
        "Upload a new avatar image (jpeg/png/webp/gif/heic, max 5 MB). "
        "The image is center-cropped, resized to 256×256, encoded as WebP, "
        "and stored at avatars/{user_id}.webp in R2 (overwriting any existing file). "
        "Returns a versioned URL to bypass browser/CDN cache."
    ),
)
async def upload_avatar(
    file: UploadFile = File(..., description="Image file to upload as avatar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProfileService.upload_avatar(
        db=db, current_user=current_user, file=file
    )


@router.delete(
    "/avatar",
    response_model=ProfileUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete avatar",
    description="Permanently remove the user's avatar from storage and clear it from the profile.",
)
async def delete_avatar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProfileService.delete_avatar(db=db, current_user=current_user)
