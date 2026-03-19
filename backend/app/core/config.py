"""Core configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Project metadata
    PROJECT_NAME: str = "Eisenhower Matrix AI Todo"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    DYNAMODB_ENDPOINT_URL: str = ""
    DYNAMODB_TABLE_NAME: str = "se_mini1_todo_list_db"
    AWS_REGION: str = "ap-northeast-2"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # JWT/Security configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS configuration
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]

    # AI service configuration
    AI_BASE_URL: str = "https://air.changwon.ac.kr/simon/v1"
    AI_MODEL: str = "Qwen/Qwen3.5-9B"
    AI_TIMEOUT: int = 10  # seconds
    AI_API_KEY: str = ""


# Global settings instance
settings = Settings()
