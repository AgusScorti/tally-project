"""
Modelo Category - Categoría de gasto
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)  # comida, auto, tecnología, etc
    description = Column(String)
    color = Column(String, default="#3B82F6")  # Para UI (hex color)
    icon = Column(String)  # Para UI (emoji o clase de ícono)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="categories")
    expenses = relationship("Expense", back_populates="category")
    
    def __repr__(self):
        return f"<Category {self.name}>"
