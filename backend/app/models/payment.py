"""
Modelo Payment - Pago de deudas entre personas
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, String, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Quien debe
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)    # Quien recibe
    
    # Se puede vincar a un expense_participant o installment_split específico
    expense_participant_id = Column(Integer, ForeignKey("expense_participants.id"), nullable=True)
    installment_split_id = Column(Integer, ForeignKey("installment_splits.id"), nullable=True)
    
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String)  # Ej: "Transferencia por cena del 15/1"
    payment_method = Column(String, default="manual")  # manual, transferencia, efectivo, etc
    
    confirmed = Column(Boolean, default=False, index=True)  # Si el receptor confirmó
    date = Column(DateTime, default=datetime.utcnow, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    from_user = relationship("User", back_populates="payments_sent", foreign_keys=[from_user_id])
    to_user = relationship("User", back_populates="payments_received", foreign_keys=[to_user_id])
    
    def __repr__(self):
        return f"<Payment ${self.amount} from user_{self.from_user_id} to user_{self.to_user_id}>"
