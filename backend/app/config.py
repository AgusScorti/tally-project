from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://gastos_user:gastos_password@localhost:5432/gastos_db"
    SECRET_KEY: str = "clave-secreta-tally-2024-cambiar-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    APP_NAME: str = "Tally"
    DEBUG: bool = True
    TIMEZONE: str = "UTC"

    model_config = {"env_file": None}  # No leer .env por ahora

settings = Settings()
