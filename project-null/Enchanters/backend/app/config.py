from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "KisaanSeva"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me"
    FERNET_KEY: str = "change-me"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str = "postgresql+asyncpg://kisaanseva:kisaanseva@localhost:5432/kisaanseva"

    REDIS_URL: str = "redis://localhost:6379/0"

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    JWT_SECRET_KEY: str = "change-me-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "kisaanseva"
    S3_REGION: str = "ap-south-1"

    INDIA_POST_API_URL: str = "https://api.postalpincode.in/pincode"
    DATA_GOV_API_KEY: str = ""
    DATA_GOV_API_URL: str = "https://api.data.gov.in/resource"
    PMFBY_API_URL: str = "https://pmfby.gov.in/api"
    LGD_API_URL: str = "https://lgdirectory.gov.in/api"

    SMS_PROVIDER: str = "msg91"
    MSG91_AUTH_KEY: str = ""
    MSG91_SENDER_ID: str = "KSSEVA"
    MSG91_TEMPLATE_ID: str = ""

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@kisaanseva.in"

    CORS_ORIGINS: str = "http://localhost:3000,http://app.kisaanseva.in,http://service.kisaanseva.in"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
