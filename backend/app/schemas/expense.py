"""
Schemas Pydantic - Gastos, tarjetas y categorías
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

# ==================== CATEGORY ====================

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: str = Field(default="#3B82F6")
    icon: Optional[str] = None

class CategoryResponse(CategoryCreate):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== CARD ====================

class CardCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    card_type: Optional[str] = None  # visa, mastercard, amex
    last_four: Optional[str] = Field(None, max_length=4)

class CardResponse(CardCreate):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== EXPENSE PARTICIPANT ====================

class ExpenseParticipantCreate(BaseModel):
    user_id: int
    amount: Optional[Decimal] = None
    percentage: Optional[Decimal] = None
    description: Optional[str] = None
    
    # Validación: debe tener amount O percentage
    def __init__(self, **data):
        super().__init__(**data)
        if not self.amount and not self.percentage:
            raise ValueError("Debe proporcionar 'amount' o 'percentage'")

class ExpenseParticipantResponse(ExpenseParticipantCreate):
    id: int
    expense_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== INSTALLMENT ====================

class InstallmentResponse(BaseModel):
    id: int
    installment_number: int
    amount: Decimal
    due_date: datetime
    is_paid: bool
    paid_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ==================== EXPENSE ====================

class ExpenseCreate(BaseModel):
    card_id: int
    category_id: int
    date: datetime
    concept: str = Field(..., min_length=1, max_length=255)
    total_amount: Decimal = Field(..., gt=0)
    notes: Optional[str] = None
    has_installments: bool = False
    num_installments: Optional[int] = Field(None, ge=2, le=60)
    participants: List[ExpenseParticipantCreate]

class ExpenseUpdate(BaseModel):
    concept: Optional[str] = None
    category_id: Optional[int] = None
    notes: Optional[str] = None

class ExpenseResponse(BaseModel):
    id: int
    card_id: int
    category_id: int
    date: datetime
    concept: str
    total_amount: Decimal
    notes: Optional[str] = None
    has_installments: bool
    num_installments: int
    participants: List[ExpenseParticipantResponse]
    installments: List[InstallmentResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True
