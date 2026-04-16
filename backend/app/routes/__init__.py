"""
Routes - Importar todos los routers
"""
from app.routes import auth, expenses, installments, payments, reports, card_category

__all__ = [
    "auth",
    "expenses",
    "installments",
    "payments",
    "reports",
    "card_category",
]
