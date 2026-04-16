"""
Routes - Pagos (pagos entre personas, resolución de deudas)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.payment import Payment
from app.models.expense_participant import ExpenseParticipant
from app.models.installment_split import InstallmentSplit
from app.schemas.expense import PaymentCreate, PaymentResponse
from app.schemas.reports import BalanceResponse, UserBalance
from app.security import get_current_active_user

router = APIRouter(prefix="/payments", tags=["payments"])

# ==================== REGISTRAR PAGO ====================

@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Registrar un pago entre usuarios
    
    El usuario actual es quien está pagando (from_user_id)
    
    Ejemplo:
    ```json
    {
      "to_user_id": 2,
      "amount": "150.00",
      "description": "Pago por cena del 15/1",
      "payment_method": "transferencia"
    }
    ```
    """
    # No se puede pagar a uno mismo
    if payment_data.to_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot pay to yourself"
        )
    
    # Verificar que el usuario receptor existe
    to_user = db.query(User).filter(User.id == payment_data.to_user_id).first()
    if not to_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient user not found"
        )
    
    # Crear pago
    db_payment = Payment(
        from_user_id=current_user.id,
        to_user_id=payment_data.to_user_id,
        amount=payment_data.amount,
        description=payment_data.description,
        payment_method=payment_data.payment_method
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    return db_payment

# ==================== OBTENER MIS DEUDAS ====================

@router.get("/me/owe", response_model=list)
def get_my_debts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lo que YO debo (gastos donde participé pero otros pagaron)
    
    Retorna deudas NO pagadas
    """
    debts = []
    
    # Buscar todos los expense_participants donde estoy
    my_participants = db.query(ExpenseParticipant).filter(
        ExpenseParticipant.user_id == current_user.id
    ).all()
    
    for participant in my_participants:
        expense = participant.expense
        
        # Obtener el dueño de la tarjeta (quien pagó)
        card_owner = expense.card.user
        
        if card_owner.id == current_user.id:
            continue  # Yo pagué, no debo
        
        # Verificar si ya pagué esta deuda
        paid = db.query(Payment).filter(
            Payment.from_user_id == current_user.id,
            Payment.to_user_id == card_owner.id,
            Payment.expense_participant_id == participant.id
        ).first()
        
        if paid:
            continue  # Ya está pagado
        
        debts.append({
            "participant_id": participant.id,
            "expense_id": expense.id,
            "from_user_id": current_user.id,
            "to_user_id": card_owner.id,
            "to_user_name": card_owner.full_name or card_owner.username,
            "amount": str(participant.amount),
            "concept": expense.concept,
            "date": expense.date,
            "status": "pending"
        })
    
    return debts

# ==================== OBTENER MIS CRÉDITOS ====================

@router.get("/me/owed", response_model=list)
def get_my_credits(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lo que me DEBEN (yo pagué gastos compartidos)
    
    Retorna créditos NO cobrados
    """
    credits = []
    
    # Buscar todos los gastos donde soy el dueño de la tarjeta
    my_expenses = db.query(ExpenseParticipant).join(
        ExpenseParticipant.expense
    ).filter(
        ExpenseParticipant.expense.has(
            Expense.card.has(Card.user_id == current_user.id)
        )
    ).all()
    
    from app.models.expense import Expense
    from app.models.card import Card
    
    my_expenses = db.query(ExpenseParticipant).filter(
        ExpenseParticipant.expense.has(
            Expense.card.has(Card.user_id == current_user.id)
        )
    ).all()
    
    for participant in my_expenses:
        # Alguien más está en mi gasto
        if participant.user_id == current_user.id:
            continue
        
        # Verificar si ya pagó
        paid = db.query(Payment).filter(
            Payment.from_user_id == participant.user_id,
            Payment.to_user_id == current_user.id,
            Payment.expense_participant_id == participant.id
        ).first()
        
        if paid:
            continue
        
        debtor = db.query(User).filter(User.id == participant.user_id).first()
        expense = participant.expense
        
        credits.append({
            "participant_id": participant.id,
            "expense_id": expense.id,
            "from_user_id": participant.user_id,
            "from_user_name": debtor.full_name or debtor.username,
            "to_user_id": current_user.id,
            "amount": str(participant.amount),
            "concept": expense.concept,
            "date": expense.date,
            "status": "pending"
        })
    
    return credits

# ==================== BALANCE ENTRE DOS USUARIOS ====================

@router.get("/balance/{other_user_id}", response_model=BalanceResponse)
def get_balance_with_user(
    other_user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener balance entre dos usuarios
    
    Positivo = el otro me debe
    Negativo = yo le debo
    
    Ejemplo: balance = 100.00 significa que user_2 me debe $100 a mí
    """
    # Sumar pagos confirmados
    payments_i_made = db.query(Payment).filter(
        Payment.from_user_id == current_user.id,
        Payment.to_user_id == other_user_id,
        Payment.confirmed == True
    ).all()
    
    payments_i_received = db.query(Payment).filter(
        Payment.from_user_id == other_user_id,
        Payment.to_user_id == current_user.id,
        Payment.confirmed == True
    ).all()
    
    balance = Decimal("0")
    balance += sum(p.amount for p in payments_i_received) or Decimal("0")
    balance -= sum(p.amount for p in payments_i_made) or Decimal("0")
    
    return BalanceResponse(
        user_id=current_user.id,
        other_user_id=other_user_id,
        balance=balance
    )

# ==================== MI BALANCE CON TODOS ====================

@router.get("/balance/all", response_model=UserBalance)
def get_all_balances(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener mi balance con todos los usuarios
    
    Retorna diccionario de user_id -> balance pendiente
    """
    # Obtener todos los usuarios con los que tengo transacciones
    other_users = db.query(User).filter(User.id != current_user.id).all()
    
    balances = []
    for other_user in other_users:
        # Calcular balance
        my_debts = db.query(ExpenseParticipant).join(
            ExpenseParticipant.expense
        ).filter(
            ExpenseParticipant.user_id == current_user.id
        ).all()
        
        from app.models.card import Card
        
        my_debts = db.query(ExpenseParticipant).filter(
            ExpenseParticipant.user_id == current_user.id
        ).join(ExpenseParticipant.expense).filter(
            Expense.card.has(Card.user_id == other_user.id)
        ).all()
        
        my_debts_total = sum(p.amount for p in my_debts) if my_debts else Decimal("0")
        
        # Lo que me debe
        their_debts = db.query(ExpenseParticipant).filter(
            ExpenseParticipant.user_id == other_user.id
        ).join(ExpenseParticipant.expense).filter(
            Expense.card.has(Card.user_id == current_user.id)
        ).all()
        
        their_debts_total = sum(p.amount for p in their_debts) if their_debts else Decimal("0")
        
        balance = their_debts_total - my_debts_total
        
        if balance != 0:
            balances.append(BalanceResponse(
                user_id=current_user.id,
                other_user_id=other_user.id,
                balance=balance
            ))
    
    return UserBalance(
        user_id=current_user.id,
        balances=balances
    )

# ==================== CONFIRMAR PAGO ====================

@router.put("/{payment_id}/confirm", status_code=status.HTTP_200_OK)
def confirm_payment(
    payment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Confirmar un pago recibido
    (Solo el receptor puede confirmar)
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.to_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recipient can confirm payment"
        )
    
    if payment.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already confirmed"
        )
    
    payment.confirmed = True
    db.commit()
    
    return {"message": "Payment confirmed", "payment_id": payment.id}

# ==================== HISTORIAL DE PAGOS ====================

@router.get("/history", response_model=List[PaymentResponse])
def get_payment_history(
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener historial de pagos (enviados y recibidos)"""
    payments = db.query(Payment).filter(
        or_(
            Payment.from_user_id == current_user.id,
            Payment.to_user_id == current_user.id
        )
    ).order_by(Payment.date.desc()).offset(skip).limit(limit).all()
    
    return payments
