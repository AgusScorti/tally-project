"""
Modelo User - Usuario del sistema
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    cards = relationship("Card", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    expense_participants = relationship("ExpenseParticipant", back_populates="user", foreign_keys="ExpenseParticipant.user_id")
    payments_sent = relationship("Payment", back_populates="from_user", foreign_keys="Payment.from_user_id")
    payments_received = relationship("Payment", back_populates="to_user", foreign_keys="Payment.to_user_id")
    
    def __repr__(self):
        return f"<User {self.email}>"
