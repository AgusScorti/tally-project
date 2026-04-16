"""
Modelo ExpenseParticipant - División de un gasto entre personas
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, String
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from app.database import Base

class ExpenseParticipant(Base):
    __tablename__ = "expense_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Se puede usar AMOUNT O PERCENTAGE, pero guardamos ambas para flexibilidad
    amount = Column(Numeric(12, 2), nullable=True)  # Monto específico (ej: $50)
    percentage = Column(Numeric(5, 2), nullable=True)  # Porcentaje (ej: 30.5%)
    
    description = Column(String)  # Ej: "Bebida de Juan"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    expense = relationship("Expense", back_populates="participants")
    user = relationship("User", back_populates="expense_participants")
    
    def __repr__(self):
        if self.amount:
            return f"<Participant user_id={self.user_id} amount=${self.amount}>"
        else:
            return f"<Participant user_id={self.user_id} {self.percentage}%>"
