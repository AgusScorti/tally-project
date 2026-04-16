"""
Schemas Pydantic - Pagos y reportes
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

# ==================== PAYMENT ====================

class PaymentCreate(BaseModel):
    to_user_id: int
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    payment_method: str = Field(default="manual")

class PaymentResponse(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    amount: Decimal
    description: Optional[str] = None
    payment_method: str
    confirmed: bool
    date: datetime
    
    class Config:
        from_attributes = True

# ==================== BALANCE ====================

class BalanceResponse(BaseModel):
    """Balance entre dos usuarios"""
    user_id: int
    other_user_id: int
    balance: Decimal  # Positivo = otra persona me debe, Negativo = yo debo
    
class UserBalance(BaseModel):
    """Balance de un usuario con todos sus deudores/acreedores"""
    user_id: int
    balances: List[BalanceResponse]

# ==================== REPORTS ====================

class CategorySummary(BaseModel):
    """Resumen de gasto por categoría"""
    category_id: int
    category_name: str
    total: Decimal
    count: int

class MonthlyReport(BaseModel):
    """Reporte mensual"""
    year: int
    month: int
    total_spent: Decimal  # Mi gasto real
    total_in_cards: Decimal  # Total en tarjetas
    by_category: List[CategorySummary]
    by_card: List[dict]

class PendingInstallments(BaseModel):
    """Cuotas pendientes"""
    id: int
    expense_id: int
    concept: str
    amount: Decimal
    due_date: datetime
    days_until_due: int
