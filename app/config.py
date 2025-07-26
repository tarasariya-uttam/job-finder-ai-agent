# Configuration management for the Job Finder AI Agent
# This will handle environment variables, settings, and configuration

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    app_name: str = "Job Finder AI Agent"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database Configuration
    database_url: str = "sqlite:///./job_finder.db"
    
    # AI/ML Configuration
    openai_api_key: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    
    # Job Search Configuration
    max_jobs_per_page: int = 20
    default_search_radius: int = 25  # miles
    
    # Security Configuration
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Environment-specific configurations
def get_settings() -> Settings:
    """Get application settings"""
    return settings 