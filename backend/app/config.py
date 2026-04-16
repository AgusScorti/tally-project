"""
Configuración centralizada de la aplicación
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://gastos_user:gastos_password@localhost:5432/gastos_db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App
    APP_NAME: str = "Gastos App"
    DEBUG: bool = True
    TIMEZONE: str = "America/Argentina/Buenos_Aires"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
