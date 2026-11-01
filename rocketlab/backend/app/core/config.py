"""RocketLab backend configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RocketLab"
    VERSION: str = "0.1.0"

    # CORS
    BACKEND_CORS_ORIGINS: str = "*"

    # Database
    DATABASE_URL: str = "postgresql+psycopg://rocketlab:rocketlab@localhost:5432/rocketlab"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ADMIN_TOKEN: str = "admin-change-me"
    WORKER_TOKEN: str = "worker-change-me"

    # Demo data
    SEED_DEMO_DATA: bool = "true"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
