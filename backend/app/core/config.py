from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings and configuration"""

    # Database settings
    database_url: str = (
        "postgresql://dataquest_user:your_secure_password_here@"
        "localhost:5432/dataquest_ai"
    )

    # AI/LLM settings
    anthropic_api_key: Optional[str] = None
    langchain_api_key: Optional[str] = None
    langchain_tracing_v2: bool = True
    langchain_project: str = "dataquest-ai"

    # Application settings
    environment: str = "development"
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # File upload settings
    max_file_size_mb: int = 50
    upload_dir: str = "./uploads"

    class Config:
        env_file = "../../.env"  # Look for .env in project root
        case_sensitive = False


# Create global settings instance
settings = Settings()
