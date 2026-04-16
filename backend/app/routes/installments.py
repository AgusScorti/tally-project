"""
Routes - Cuotas (Installments)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.installment import Installment
from app.models.installment_split import InstallmentSplit
from app.models.expense import Expense
from app.models.card import Card
from app.schemas.expense import InstallmentResponse
from app.security import get_current_active_user

router = APIRouter(prefix="/installments", tags=["installments"])

# ==================== LISTAR CUOTAS PENDIENTES ====================

@router.get("/pending", response_model=List[InstallmentResponse])
def get_pending_installments(
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener cuotas pendientes del usuario
    (donde es participante de un gasto con cuotas)
    """
    installments = db.query(Installment).join(
        Expense
    ).join(
        Card
    ).filter(
        Installment.is_paid == False,
        Card.user_id == current_user.id
    ).order_by(
        Installment.due_date
    ).offset(skip).limit(limit).all()
    
    return installments

# ==================== LISTAR CUOTAS DE UN GASTO ====================

@router.get("/expense/{expense_id}", response_model=List[InstallmentResponse])
def get_expense_installments(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener todas las cuotas de un gasto"""
    # Verificar que el gasto pertenece al usuario
    expense = db.query(Expense).join(Card).filter(
        Expense.id == expense_id,
        Card.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    installments = db.query(Installment).filter(
        Installment.expense_id == expense_id
    ).order_by(Installment.installment_number).all()
    
    return installments

# ==================== OBTENER DETALLES DE UNA CUOTA ====================

@router.get("/{installment_id}", response_model=dict)
def get_installment_details(
    installment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener detalles de una cuota incluyendo splits
    
    Respuesta:
    ```json
    {
      "id": 1,
      "installment_number": 1,
      "amount": "200.00",
      "due_date": "2024-02-15T00:00:00",
      "is_paid": false,
      "splits": [
        {
          "id": 1,
          "user_id": 1,
          "amount": "120.00",
          "paid": false,
          "user": { "id": 1, "username": "juan" }
        }
      ],
      "expense": { "concept": "Cena", ... }
    }
    ```
    """
    installment = db.query(Installment).join(Expense).join(Card).filter(
        Installment.id == installment_id,
        Card.user_id == current_user.id
    ).first()
    
    if not installment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Installment not found"
        )
    
    splits = db.query(InstallmentSplit).filter(
        InstallmentSplit.installment_id == installment_id
    ).all()
    
    return {
        "id": installment.id,
        "installment_number": installment.installment_number,
        "amount": str(installment.amount),
        "due_date": installment.due_date,
        "is_paid": installment.is_paid,
        "splits": [
            {
                "id": split.id,
                "user_id": split.user_id,
                "amount": str(split.amount),
                "paid": split.paid,
                "paid_date": split.paid_date
            }
            for split in splits
        ]
    }

# ==================== MIS CUOTAS PARA PAGAR ====================

@router.get("/my-splits/pending", response_model=list)
def get_my_pending_splits(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todas mis partes de cuotas pendientes de pagar
    (InstallmentSplit donde soy el usuario y no está pagado)
    """
    my_splits = db.query(InstallmentSplit).filter(
        InstallmentSplit.user_id == current_user.id,
        InstallmentSplit.paid == False
    ).join(Installment).order_by(
        Installment.due_date
    ).all()
    
    result = []
    for split in my_splits:
        installment = split.installment
        expense = installment.expense
        
        result.append({
            "split_id": split.id,
            "installment_id": installment.id,
            "expense_id": expense.id,
            "concept": expense.concept,
            "amount": str(split.amount),
            "due_date": installment.due_date,
            "installment_number": installment.installment_number,
            "total_installments": expense.num_installments
        })
    
    return result

# ==================== MARCAR CUOTA COMO PAGADA ====================

@router.put("/{installment_id}/mark-paid", status_code=status.HTTP_200_OK)
def mark_installment_paid(
    installment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Marcar MI parte de una cuota como pagada
    (Actualiza InstallmentSplit, no la cuota completa)
    """
    # Obtener el split donde soy el usuario
    split = db.query(InstallmentSplit).join(Installment).join(Expense).join(Card).filter(
        InstallmentSplit.installment_id == installment_id,
        InstallmentSplit.user_id == current_user.id,
        Card.user_id == current_user.id
    ).first()
    
    if not split:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Split not found or doesn't belong to you"
        )
    
    # Marcar como pagado
    split.paid = True
    split.paid_date = datetime.utcnow()
    
    # Verificar si TODOS los splits de esta cuota están pagados
    installment = split.installment
    all_splits = db.query(InstallmentSplit).filter(
        InstallmentSplit.installment_id == installment.id
    ).all()
    
    if all(s.paid for s in all_splits):
        installment.is_paid = True
        installment.paid_date = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Split marked as paid",
        "split_id": split.id,
        "installment_paid": installment.is_paid
    }

# ==================== CUOTAS PRÓXIMAS A VENCER ====================

@router.get("/upcoming/by-days", response_model=list)
def get_upcoming_installments(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener cuotas que vencen en los próximos N días
    """
    from datetime import timedelta
    
    now = datetime.utcnow()
    future = now + timedelta(days=days)
    
    splits = db.query(InstallmentSplit).filter(
        InstallmentSplit.user_id == current_user.id,
        InstallmentSplit.paid == False
    ).join(Installment).filter(
        Installment.due_date >= now,
        Installment.due_date <= future
    ).join(Expense).order_by(
        Installment.due_date
    ).all()
    
    result = []
    for split in splits:
        installment = split.installment
        expense = installment.expense
        days_until = (installment.due_date - now).days
        
        result.append({
            "split_id": split.id,
            "installment_id": installment.id,
            "expense_id": expense.id,
            "concept": expense.concept,
            "amount": str(split.amount),
            "due_date": installment.due_date,
            "days_until_due": days_until,
            "installment_number": installment.installment_number
        })
    
    return result
