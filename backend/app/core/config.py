from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Database settings
    postgres_user: str = "dataquest_user"
    postgres_password: str = "dataquest_password"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "dataquest_ai"
    
    # Computed database URL
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
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
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()