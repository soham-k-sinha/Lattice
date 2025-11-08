"""Application settings and configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App Configuration
    APP_NAME: str = "Lattice Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "production"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/lattice_db"

    # JWT Authentication
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Feature Flags
    FEATURE_KNOT: bool = False
    FEATURE_AI: bool = False
    FEATURE_SNOWFLAKE: bool = False
    FEATURE_X: bool = False

    # Knot API
    KNOT_ENVIRONMENT: str = "production"  # or "production"
    KNOT_API_URL: str = "https://production.knotapi.com"
    KNOT_CLIENT_ID: str = ""
    KNOT_CLIENT_SECRET: str = ""

    # AI Providers
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Snowflake
    SNOWFLAKE_ACCOUNT: str = ""
    SNOWFLAKE_USER: str = ""
    SNOWFLAKE_PASSWORD: str = ""
    SNOWFLAKE_DATABASE: str = ""
    SNOWFLAKE_SCHEMA: str = ""
    SNOWFLAKE_WAREHOUSE: str = ""

    # X API
    X_API_KEY: str = ""
    X_API_SECRET: str = ""
    X_BEARER_TOKEN: str = ""

    # Logging
    LOG_LEVEL: str = "DEBUG"


# Global settings instance
settings = Settings()

