from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routes import auth, expenses, installments, payments, reports, card_category

import app.models.user
import app.models.card
import app.models.category
import app.models.expense
import app.models.expense_participant
import app.models.installment
import app.models.installment_split
import app.models.payment

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App iniciada")
    yield
    print("App terminada")

app = FastAPI(
    title=settings.APP_NAME,
    description="API para gestionar gastos compartidos",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(installments.router)
app.include_router(payments.router)
app.include_router(reports.router)
app.include_router(card_category.cards_router)
app.include_router(card_category.categories_router)

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}

@app.get("/")
def root():
    return {"app": settings.APP_NAME, "version": "1.0.0", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
