"""
Modelo Expense - Gasto registrado en tarjeta
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Numeric, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from app.database import Base

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    concept = Column(String, nullable=False)  # ej: "Cena en restaurante X"
    total_amount = Column(Numeric(12, 2), nullable=False)  # Lo que aparece en tarjeta
    notes = Column(Text)
    
    # Cuotas
    has_installments = Column(Boolean, default=False)
    num_installments = Column(Integer, default=1)  # Si tiene cuotas
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    card = relationship("Card", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")
    participants = relationship("ExpenseParticipant", back_populates="expense", cascade="all, delete-orphan")
    installments = relationship("Installment", back_populates="expense", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Expense {self.concept} ${self.total_amount}>"
