"""
Modelo Installment - Cuota de un gasto (si tiene multiple pagos)
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from app.database import Base

class Installment(Base):
    __tablename__ = "installments"
    
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False, index=True)
    
    installment_number = Column(Integer, nullable=False)  # 1, 2, 3...
    amount = Column(Numeric(12, 2), nullable=False)  # Monto de esta cuota
    due_date = Column(DateTime, nullable=False, index=True)
    
    is_paid = Column(Boolean, default=False, index=True)  # Cuota completa pagada
    paid_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    expense = relationship("Expense", back_populates="installments")
    splits = relationship("InstallmentSplit", back_populates="installment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Installment #{self.installment_number} ${self.amount}>"
