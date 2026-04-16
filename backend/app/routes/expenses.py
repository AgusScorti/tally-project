"""
Routes - Gastos (CRUD completo)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.expense import Expense
from app.models.expense_participant import ExpenseParticipant
from app.models.installment import Installment
from app.models.installment_split import InstallmentSplit
from app.models.card import Card
from app.models.category import Category
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.security import get_current_active_user

router = APIRouter(prefix="/expenses", tags=["expenses"])

# ==================== CREAR GASTO ====================

@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo gasto con participantes y cuotas
    
    Validaciones:
    - La tarjeta debe ser del usuario actual
    - La categoría debe ser del usuario actual
    - Al menos un participante
    - Si tiene cuotas, num_installments >= 2
    
    Ejemplo:
    ```json
    {
      "card_id": 1,
      "category_id": 1,
      "date": "2024-01-15T10:30:00",
      "concept": "Cena en restaurante X",
      "total_amount": "300.00",
      "has_installments": false,
      "participants": [
        {
          "user_id": 1,
          "amount": "180.00",
          "description": "Mi parte"
        },
        {
          "user_id": 2,
          "amount": "120.00",
          "description": "Juan"
        }
      ]
    }
    ```
    """
    
    # Verificar que la tarjeta pertenece al usuario actual
    card = db.query(Card).filter(
        Card.id == expense_data.card_id,
        Card.user_id == current_user.id
    ).first()
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found or doesn't belong to you"
        )
    
    # Verificar que la categoría pertenece al usuario actual
    category = db.query(Category).filter(
        Category.id == expense_data.category_id,
        Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or doesn't belong to you"
        )
    
    # Validar participantes
    if not expense_data.participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one participant required"
        )
    
    # Validar montos de participantes suman al total (con tolerancia)
    total_participants = sum(
        p.amount for p in expense_data.participants if p.amount
    ) or sum(
        (expense_data.total_amount * p.percentage / 100) 
        for p in expense_data.participants if p.percentage
    )
    
    if total_participants and abs(float(total_participants) - float(expense_data.total_amount)) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participants amounts don't match total expense"
        )
    
    # Crear gasto
    db_expense = Expense(
        card_id=expense_data.card_id,
        category_id=expense_data.category_id,
        date=expense_data.date,
        concept=expense_data.concept,
        total_amount=expense_data.total_amount,
        notes=expense_data.notes,
        has_installments=expense_data.has_installments,
        num_installments=expense_data.num_installments or 1
    )
    db.add(db_expense)
    db.flush()  # Obtener el ID sin commitear
    
    # Crear participantes
    for participant_data in expense_data.participants:
        # Si tiene porcentaje pero no monto, calcular monto
        amount = participant_data.amount
        if not amount and participant_data.percentage:
            amount = expense_data.total_amount * participant_data.percentage / 100
        
        db_participant = ExpenseParticipant(
            expense_id=db_expense.id,
            user_id=participant_data.user_id,
            amount=amount,
            percentage=participant_data.percentage,
            description=participant_data.description
        )
        db.add(db_participant)
    
    # Crear cuotas si es necesario
    if expense_data.has_installments and expense_data.num_installments:
        installment_amount = expense_data.total_amount / expense_data.num_installments
        
        for i in range(1, expense_data.num_installments + 1):
            # Calcular fecha de pago (próximo mes)
            due_month = expense_data.date.month + i
            due_year = expense_data.date.year
            if due_month > 12:
                due_month -= 12
                due_year += 1
            
            due_date = datetime(
                due_year,
                due_month,
                min(expense_data.date.day, 28)  # Evitar error si es 29-31
            )
            
            db_installment = Installment(
                expense_id=db_expense.id,
                installment_number=i,
                amount=installment_amount,
                due_date=due_date
            )
            db.add(db_installment)
            db.flush()
            
            # Crear splits de cuota para cada participante
            for participant_data in expense_data.participants:
                split_amount = installment_amount
                
                # Si el participante tiene porcentaje, calcular su parte de esta cuota
                if participant_data.percentage:
                    split_amount = installment_amount * participant_data.percentage / 100
                
                db_split = InstallmentSplit(
                    installment_id=db_installment.id,
                    user_id=participant_data.user_id,
                    amount=split_amount
                )
                db.add(db_split)
    
    db.commit()
    db.refresh(db_expense)
    
    return db_expense

# ==================== LISTAR GASTOS ====================

@router.get("", response_model=List[ExpenseResponse])
def list_expenses(
    card_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Listar gastos del usuario con filtros opcionales
    
    Query parameters:
    - card_id: Filtrar por tarjeta
    - category_id: Filtrar por categoría
    - date_from: Desde fecha (ISO format)
    - date_to: Hasta fecha (ISO format)
    - limit: Máximo resultados (default 50)
    - skip: Offset para paginación
    """
    query = db.query(Expense).join(Card).filter(Card.user_id == current_user.id)
    
    if card_id:
        query = query.filter(Expense.card_id == card_id)
    
    if category_id:
        query = query.filter(Expense.category_id == category_id)
    
    if date_from:
        query = query.filter(Expense.date >= date_from)
    
    if date_to:
        query = query.filter(Expense.date <= date_to)
    
    expenses = query.order_by(Expense.date.desc()).offset(skip).limit(limit).all()
    
    return expenses

# ==================== OBTENER GASTO ====================

@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener detalles de un gasto específico"""
    expense = db.query(Expense).join(Card).filter(
        Expense.id == expense_id,
        Card.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    return expense

# ==================== ACTUALIZAR GASTO ====================

@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar gasto (solo concepto, categoría y notas)"""
    expense = db.query(Expense).join(Card).filter(
        Expense.id == expense_id,
        Card.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    # Actualizar campos
    if expense_data.concept:
        expense.concept = expense_data.concept
    
    if expense_data.category_id:
        # Verificar que la categoría es del usuario
        category = db.query(Category).filter(
            Category.id == expense_data.category_id,
            Category.user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        expense.category_id = expense_data.category_id
    
    if expense_data.notes is not None:
        expense.notes = expense_data.notes
    
    db.commit()
    db.refresh(expense)
    
    return expense

# ==================== ELIMINAR GASTO ====================

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar un gasto (y todo lo relacionado)"""
    expense = db.query(Expense).join(Card).filter(
        Expense.id == expense_id,
        Card.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    db.delete(expense)
    db.commit()
