"""
Configuration management for FinanceBot Pro
"""
import os
from typing import Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    app_name: str = "FinanceBot Pro API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8001
    reload: bool = False
    
    # Database Configuration
    mongo_url: str = "mongodb://localhost:27017"
    database_name: str = "financebot_pro"
    
    # AI Model Configuration
    nvidia_api_key: str
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    ai_model: str = "writer/palmyra-fin-70b-32k"
    ai_temperature: float = 0.3
    ai_top_p: float = 0.8
    ai_max_tokens: int = 2048
    
    # Rate Limiting Configuration
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour in seconds
    max_retries: int = 3
    base_delay: float = 2.0
    
    # Portfolio Optimization Configuration
    risk_free_rate: float = 0.02
    default_period: str = "1y"
    max_symbols: int = 20
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security Configuration
    cors_origins: list = ["*"]
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    @validator('nvidia_api_key')
    def validate_nvidia_api_key(cls, v):
        if not v:
            raise ValueError('NVIDIA API key is required')
        return v
    
    @validator('mongo_url')
    def validate_mongo_url(cls, v):
        if not v.startswith(('mongodb://', 'mongodb+srv://')):
            raise ValueError('Invalid MongoDB URL format')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings