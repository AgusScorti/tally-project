"""
Modelo InstallmentSplit - Cómo se divide UNA cuota entre personas
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from app.database import Base

class InstallmentSplit(Base):
    __tablename__ = "installment_splits"
    
    id = Column(Integer, primary_key=True, index=True)
    installment_id = Column(Integer, ForeignKey("installments.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    amount = Column(Numeric(12, 2), nullable=False)  # Cuánto de ESTA cuota le toca a este user
    paid = Column(Boolean, default=False, index=True)  # Si esta persona ya pagó su parte
    paid_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    installment = relationship("Installment", back_populates="splits")
    user = relationship("User")
    
    def __repr__(self):
        return f"<Split user_id={self.user_id} ${self.amount}>"
