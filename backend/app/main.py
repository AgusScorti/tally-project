"""
Main.py - Aplicación FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routes import auth, expenses, installments, payments, reports, card_category

# ==================== CREAR TABLAS ====================
# Crear todas las tablas definidas en los modelos
Base.metadata.create_all(bind=engine)

# ==================== LIFESPAN ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("✅ App iniciada")
    yield
    # Shutdown
    print("🛑 App terminada")

# ==================== CREAR APP ====================
app = FastAPI(
    title=settings.APP_NAME,
    description="API para gestionar gastos compartidos",
    version="1.0.0",
    lifespan=lifespan
)

# ==================== CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ROUTES ====================
app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(installments.router)
app.include_router(payments.router)
app.include_router(reports.router)
app.include_router(card_category.cards_router)
app.include_router(card_category.categories_router)

# ==================== HEALTH CHECK ====================
@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "app": settings.APP_NAME}

# ==================== ROOT ====================
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
