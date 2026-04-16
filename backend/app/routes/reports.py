"""
Routes - Reportes (resúmenes, análisis, estadísticas)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.expense import Expense
from app.models.expense_participant import ExpenseParticipant
from app.models.card import Card
from app.models.category import Category
from app.models.installment import Installment
from app.schemas.reports import CategorySummary, MonthlyReport
from app.security import get_current_active_user

router = APIRouter(prefix="/reports", tags=["reports"])

# ==================== RESUMEN MENSUAL ====================

@router.get("/monthly/{year}/{month}", response_model=MonthlyReport)
def get_monthly_report(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener reporte mensual de gastos
    
    Muestra:
    - Total gastado (mi parte real)
    - Total en tarjetas (monto total registrado)
    - Desglose por categoría
    - Desglose por tarjeta
    """
    
    # Filtrar gastos del mes
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
    
    # Mi gasto real (sum de mis participantes)
    my_expenses_sum = db.query(func.sum(ExpenseParticipant.amount)).filter(
        ExpenseParticipant.user_id == current_user.id,
        ExpenseParticipant.expense.has(
            and_(
                Expense.date >= start_date,
                Expense.date <= end_date,
                Expense.card.has(Card.user_id == current_user.id)
            )
        )
    ).scalar() or Decimal("0")
    
    # Total en tarjetas
    total_in_cards = db.query(func.sum(Expense.total_amount)).join(Card).filter(
        Card.user_id == current_user.id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).scalar() or Decimal("0")
    
    # Por categoría
    from sqlalchemy import and_
    
    category_summaries = db.query(
        Category.id,
        Category.name,
        func.sum(ExpenseParticipant.amount).label("total"),
        func.count(Expense.id).label("count")
    ).join(
        ExpenseParticipant
    ).join(
        Expense
    ).join(
        Card
    ).filter(
        ExpenseParticipant.user_id == current_user.id,
        Expense.date >= start_date,
        Expense.date <= end_date,
        Card.user_id == current_user.id
    ).group_by(
        Category.id, Category.name
    ).all()
    
    by_category = [
        CategorySummary(
            category_id=cat[0],
            category_name=cat[1],
            total=cat[2] or Decimal("0"),
            count=cat[3] or 0
        )
        for cat in category_summaries
    ]
    
    # Por tarjeta
    card_summaries = db.query(
        Card.id,
        Card.name,
        func.sum(Expense.total_amount).label("total"),
        func.count(Expense.id).label("count")
    ).filter(
        Card.user_id == current_user.id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).group_by(
        Card.id, Card.name
    ).all()
    
    by_card = [
        {
            "card_id": card[0],
            "card_name": card[1],
            "total": str(card[2] or Decimal("0")),
            "count": card[3] or 0
        }
        for card in card_summaries
    ]
    
    return MonthlyReport(
        year=year,
        month=month,
        total_spent=my_expenses_sum,
        total_in_cards=total_in_cards,
        by_category=by_category,
        by_card=by_card
    )

# ==================== RESUMEN POR CATEGORÍA ====================

@router.get("/category/{category_id}", response_model=dict)
def get_category_summary(
    category_id: int,
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener resumen detallado de una categoría
    """
    # Verificar que la categoría es del usuario
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Construir query
    query = db.query(
        Expense.id,
        Expense.concept,
        Expense.date,
        ExpenseParticipant.amount,
        Card.name.label("card_name")
    ).join(
        Card
    ).join(
        ExpenseParticipant
    ).filter(
        Expense.category_id == category_id,
        ExpenseParticipant.user_id == current_user.id,
        Card.user_id == current_user.id
    )
    
    if date_from:
        query = query.filter(Expense.date >= date_from)
    if date_to:
        query = query.filter(Expense.date <= date_to)
    
    expenses = query.order_by(Expense.date.desc()).all()
    
    total = sum(e[3] for e in expenses) if expenses else Decimal("0")
    
    return {
        "category_id": category_id,
        "category_name": category.name,
        "total": str(total),
        "count": len(expenses),
        "expenses": [
            {
                "expense_id": e[0],
                "concept": e[1],
                "date": e[2],
                "my_amount": str(e[3]),
                "card": e[4]
            }
            for e in expenses
        ]
    }

# ==================== COMPARATIVA MENSUAL ====================

@router.get("/monthly-comparison", response_model=list)
def get_monthly_comparison(
    months: int = Query(6, ge=1, le=24),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Comparativa de gasto mes a mes (últimos N meses)
    """
    today = datetime.now()
    result = []
    
    for i in range(months):
        month_date = today - timedelta(days=30 * i)
        year = month_date.year
        month = month_date.month
        
        # Calcular rango del mes
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # Mi gasto del mes
        monthly_total = db.query(func.sum(ExpenseParticipant.amount)).filter(
            ExpenseParticipant.user_id == current_user.id,
            ExpenseParticipant.expense.has(
                and_(
                    Expense.date >= start_date,
                    Expense.date <= end_date,
                    Expense.card.has(Card.user_id == current_user.id)
                )
            )
        ).scalar() or Decimal("0")
        
        result.append({
            "year": year,
            "month": month,
            "month_name": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"][month - 1],
            "total": str(monthly_total)
        })
    
    return list(reversed(result))

# ==================== TOP GASTOS ====================

@router.get("/top-expenses", response_model=list)
def get_top_expenses(
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener los gastos más grandes (mi parte)"""
    expenses = db.query(
        Expense.id,
        Expense.concept,
        Expense.date,
        Category.name,
        ExpenseParticipant.amount
    ).join(
        Card
    ).join(
        Category
    ).join(
        ExpenseParticipant
    ).filter(
        ExpenseParticipant.user_id == current_user.id,
        Card.user_id == current_user.id
    ).order_by(
        ExpenseParticipant.amount.desc()
    ).limit(limit).all()
    
    return [
        {
            "expense_id": e[0],
            "concept": e[1],
            "date": e[2],
            "category": e[3],
            "amount": str(e[4])
        }
        for e in expenses
    ]

# ==================== ESTADÍSTICAS GENERALES ====================

@router.get("/statistics", response_model=dict)
def get_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Estadísticas generales del usuario
    """
    # Total gastado (todos los tiempos)
    total_all_time = db.query(func.sum(ExpenseParticipant.amount)).filter(
        ExpenseParticipant.user_id == current_user.id
    ).scalar() or Decimal("0")
    
    # Cantidad de gastos
    total_expenses = db.query(func.count(Expense.id)).join(Card).filter(
        Card.user_id == current_user.id
    ).scalar() or 0
    
    # Cantidad de tarjetas
    total_cards = db.query(func.count(Card.id)).filter(
        Card.user_id == current_user.id
    ).scalar() or 0
    
    # Cantidad de categorías
    total_categories = db.query(func.count(Category.id)).filter(
        Category.user_id == current_user.id
    ).scalar() or 0
    
    # Cuotas pendientes
    pending_installments = db.query(func.count(Installment.id)).filter(
        Installment.is_paid == False
    ).scalar() or 0
    
    # Promedio de gasto por categoría
    avg_by_category = db.query(
        Category.name,
        func.avg(ExpenseParticipant.amount).label("avg_amount")
    ).join(
        ExpenseParticipant
    ).join(
        Expense
    ).join(
        Card
    ).filter(
        ExpenseParticipant.user_id == current_user.id,
        Card.user_id == current_user.id
    ).group_by(Category.id, Category.name).all()
    
    return {
        "total_all_time": str(total_all_time),
        "total_expenses": total_expenses,
        "total_cards": total_cards,
        "total_categories": total_categories,
        "pending_installments": pending_installments,
        "avg_by_category": [
            {"category": cat[0], "average": str(cat[1] or Decimal("0"))}
            for cat in avg_by_category
        ]
    }
