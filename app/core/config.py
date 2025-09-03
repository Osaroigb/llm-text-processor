import logging
from enum import Enum
from typing import Optional
from functools import lru_cache
from colorlog import ColoredFormatter
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, ValidationInfo, field_validator


class Environment(str, Enum):
    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'
    TESTING = 'testing'


class CoreSettings(BaseSettings):
    """Core application settings."""
    PROJECT_NAME: str = 'LLM Text Processor'
    PROJECT_VERSION: str = '0.1.0'
    PROJECT_DESCRIPTION: str = 'API for processing text using LLM-based analysis and PostgreSQL storage.'
    DEBUG: bool = False
    LOG_LEVEL: str = 'INFO'
    ENVIRONMENT: Environment = Environment.DEVELOPMENT


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    POSTGRES_USER: str = Field(default='postgres')
    POSTGRES_PASSWORD: str = Field(default='password123')
    POSTGRES_HOST: str = Field(default='localhost')
    POSTGRES_PORT: str = Field(default='5432')
    POSTGRES_DB: str = Field(default='llm_processor')
    DATABASE_URL: PostgresDsn | None = None
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    @field_validator('DATABASE_URL', mode='before')
    def assemble_db_url(cls, v: str | None, info: ValidationInfo) -> str | None:
        if v is not None:
            return v
            
        data = info.data
        user = data.get('POSTGRES_USER')
        password = data.get('POSTGRES_PASSWORD')
        host = data.get('POSTGRES_HOST', 'localhost')
        port = data.get('POSTGRES_PORT', '5432')
        db = data.get('POSTGRES_DB')

        if user and password and host and port and db:
            return f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}'
        return v


class AppSettings(BaseSettings):
    """Application server settings."""
    APP_HOST: str = Field(default='0.0.0.0')
    APP_PORT: int = Field(default=8000)
    APP_RELOAD: bool = Field(default=False)


class OpenAISettings(BaseSettings):
    """OpenAI API configuration."""
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = Field(default='gpt-3.5-turbo')
    OPENAI_MAX_TOKENS: int = Field(default=1000)
    OPENAI_TEMPERATURE: float = Field(default=0.7)


class LoggingSettings(BaseSettings):
    """Logging configuration."""
    LOG_FORMAT: str = Field(default='%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_DATE_FORMAT: str = Field(default='%Y-%m-%d %H:%M:%S')
    LOG_COLORS: dict = Field(default={
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red",
    })


class Settings(
    CoreSettings,
    DatabaseSettings,
    AppSettings,
    OpenAISettings,
    LoggingSettings,
):
    """Main settings class that combines all configuration sections."""
    
    model_config = {
        'env_file': '.env',
        'env_file_encoding': 'utf-8',
        'extra': 'ignore',
        'case_sensitive': False
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def setup_logging(settings: Settings) -> None:
    """Setup logging configuration for the entire application."""
    # Create formatter
    formatter = ColoredFormatter(
        settings.LOG_FORMAT,
        datefmt=settings.LOG_DATE_FORMAT,
        log_colors=settings.LOG_COLORS,
        secondary_log_colors={},  # Ensure secondary colors are empty
    )
    
    # Create handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        handlers=[handler],
        force=True  # Override any existing configuration
    )    

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the configured formatting."""
    return logging.getLogger(name)
