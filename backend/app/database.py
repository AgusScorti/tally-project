"""
Configuración de SQLAlchemy y conexión a base de datos
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings

# Engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=20,
    max_overflow=40
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para modelos
Base = declarative_base()

# Dependency para FastAPI
def get_db() -> Session:
    """
    Dependency injection para obtener sesión de BD
    Uso en endpoints: def mi_endpoint(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
