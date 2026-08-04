"""
Cloudflare R2 client — S3-compatible object storage.

Uses boto3 with the R2 endpoint. A single client instance is created at
module import time and reused across all requests (thread-safe per boto3 docs).
"""
import boto3
from botocore.client import Config

from app.core.config import settings

# boto3 S3 client pointed at Cloudflare R2
r2_client = boto3.client(
    "s3",
    endpoint_url=settings.r2_endpoint_url,
    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    config=Config(
        signature_version="s3v4",
        # R2 does not use region-based routing; us-east-1 is the conventional value
        region_name="auto",
    ),
)

BUCKET = settings.R2_BUCKET_NAME
