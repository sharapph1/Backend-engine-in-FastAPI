"""
Image processing utilities for WebX avatar pipeline.

Pipeline:
  raw bytes (any format) → validate → resize/crop → encode as WebP → BytesIO

Why WebP?
- Smaller than JPEG/PNG at equivalent quality
- Supported natively by all modern browsers and Flutter's Image widget
"""
import io
from typing import Tuple

from PIL import Image

# ── Constants ─────────────────────────────────────────────────────────────────
AVATAR_SIZE: Tuple[int, int] = (256, 256)   # Output resolution
AVATAR_QUALITY: int = 85                     # WebP quality (0–100)
MAX_FILE_BYTES: int = 5 * 1024 * 1024        # 5 MB upload limit
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",   # first frame only
    "image/heic",
    "image/heif",
}


def validate_image_content_type(content_type: str) -> None:
    """Raise ValueError if the MIME type is not an accepted image format."""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(
            f"Unsupported file type '{content_type}'. "
            f"Accepted: jpeg, png, webp, gif, heic."
        )


def validate_image_size(data: bytes) -> None:
    """Raise ValueError if the raw bytes exceed MAX_FILE_BYTES."""
    if len(data) > MAX_FILE_BYTES:
        raise ValueError(
            f"File too large ({len(data) // 1024} KB). "
            f"Maximum allowed size is {MAX_FILE_BYTES // (1024 * 1024)} MB."
        )


def process_avatar(raw_bytes: bytes) -> bytes:
    """
    Decode image bytes, center-crop to a square, resize to AVATAR_SIZE,
    and encode as WebP.

    Returns the processed WebP bytes.
    Raises ValueError on corrupt/unreadable image data.
    """
    try:
        img: Image.Image = Image.open(io.BytesIO(raw_bytes))
    except Exception:
        raise ValueError("Cannot read image data. File may be corrupt.")

    # Convert animated GIF / HEIC / CMYK / P-mode images to RGBA for safe processing
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")

    # ── Center-crop to square ────────────────────────────────────────────────
    width, height = img.size
    min_dim = min(width, height)
    left   = (width  - min_dim) // 2
    top    = (height - min_dim) // 2
    right  = left + min_dim
    bottom = top  + min_dim
    img = img.crop((left, top, right, bottom))

    # ── Resize to target resolution ──────────────────────────────────────────
    img = img.resize(AVATAR_SIZE, Image.LANCZOS)

    # ── Flatten transparency for WebP (keep alpha if present) ────────────────
    # WebP supports alpha; no need to composite onto white unless desired.

    # ── Encode to WebP ───────────────────────────────────────────────────────
    output = io.BytesIO()
    img.save(output, format="WEBP", quality=AVATAR_QUALITY, method=6)
    output.seek(0)
    return output.read()
