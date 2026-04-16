"""
Schemas - Importar todos los schemas
"""
from app.schemas.auth import UserBase, UserCreate, UserUpdate, UserResponse, Token, LoginRequest, TokenData
from app.schemas.expense import (
    CardCreate, CardResponse,
    CategoryCreate, CategoryResponse,
    ExpenseParticipantCreate, ExpenseParticipantResponse,
    InstallmentResponse,
    ExpenseCreate, ExpenseUpdate, ExpenseResponse,
    PaymentCreate, PaymentResponse
)
from app.schemas.reports import (
    BalanceResponse, UserBalance,
    CategorySummary, MonthlyReport,
    PendingInstallments
)

__all__ = [
    # Auth
    "UserBase", "UserCreate", "UserUpdate", "UserResponse",
    "Token", "LoginRequest", "TokenData",
    
    # Cards & Categories
    "CardCreate", "CardResponse",
    "CategoryCreate", "CategoryResponse",
    
    # Expenses
    "ExpenseParticipantCreate", "ExpenseParticipantResponse",
    "InstallmentResponse",
    "ExpenseCreate", "ExpenseUpdate", "ExpenseResponse",
    
    # Payments
    "PaymentCreate", "PaymentResponse",
    
    # Reports
    "BalanceResponse", "UserBalance",
    "CategorySummary", "MonthlyReport",
    "PendingInstallments",
]
