from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str

    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    BREVO_SMTP_HOST: str = "smtp-relay.brevo.com"
    BREVO_SMTP_PORT: int = 587
    BREVO_SMTP_USERNAME: str
    BREVO_SMTP_PASSWORD: str
    BREVO_FROM_EMAIL: str

    # Cloudflare R2 (S3-compatible object storage)
    R2_ACCOUNT_ID: str
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str = "webx-assets"
    # Optional: custom domain or pub-xxx.r2.dev URL.
    # Falls back to https://<bucket>.r2.dev if not set.
    R2_PUBLIC_URL: Optional[str] = None

    @property
    def r2_endpoint_url(self) -> str:
        return f"https://{self.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

    @property
    def r2_public_base_url(self) -> str:
        if self.R2_PUBLIC_URL:
            return self.R2_PUBLIC_URL.rstrip("/")
        # Default R2 public URL pattern when bucket public access is enabled
        return f"https://pub-{self.R2_ACCOUNT_ID}.r2.dev"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()