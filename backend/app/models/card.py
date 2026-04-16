"""
Modelo Card - Tarjeta de crédito/débito
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Card(Base):
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)  # ej: "Visa Personal", "Mastercard Trabajo"
    card_type = Column(String)  # visa, mastercard, amex, etc
    last_four = Column(String)  # Últimos 4 dígitos
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="cards")
    expenses = relationship("Expense", back_populates="card", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Card {self.name} ({self.last_four})>"
