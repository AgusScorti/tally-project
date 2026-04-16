"""
Importar todos los modelos para que Alembic los vea
"""
from app.models.user import User
from app.models.card import Card
from app.models.category import Category
from app.models.expense import Expense
from app.models.expense_participant import ExpenseParticipant
from app.models.installment import Installment
from app.models.installment_split import InstallmentSplit
from app.models.payment import Payment

__all__ = [
    "User",
    "Card",
    "Category",
    "Expense",
    "ExpenseParticipant",
    "Installment",
    "InstallmentSplit",
    "Payment",
]
