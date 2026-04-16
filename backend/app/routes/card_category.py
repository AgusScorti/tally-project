"""
Routes - Tarjetas y Categorías
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.card import Card
from app.models.category import Category
from app.schemas.expense import CardCreate, CardResponse, CategoryCreate, CategoryResponse
from app.security import get_current_active_user

# ==================== ROUTER CARDS ====================

cards_router = APIRouter(prefix="/cards", tags=["cards"])

@cards_router.post("", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
def create_card(
    card_data: CardCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear una nueva tarjeta"""
    db_card = Card(
        user_id=current_user.id,
        name=card_data.name,
        card_type=card_data.card_type,
        last_four=card_data.last_four
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

@cards_router.get("", response_model=List[CardResponse])
def list_cards(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listar mis tarjetas"""
    cards = db.query(Card).filter(
        Card.user_id == current_user.id,
        Card.is_active == True
    ).all()
    return cards

@cards_router.get("/{card_id}", response_model=CardResponse)
def get_card(
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener detalles de una tarjeta"""
    card = db.query(Card).filter(
        Card.id == card_id,
        Card.user_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    return card

@cards_router.put("/{card_id}", response_model=CardResponse)
def update_card(
    card_id: int,
    card_data: CardCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar una tarjeta"""
    card = db.query(Card).filter(
        Card.id == card_id,
        Card.user_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    card.name = card_data.name
    card.card_type = card_data.card_type
    card.last_four = card_data.last_four
    
    db.commit()
    db.refresh(card)
    return card

@cards_router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Desactivar una tarjeta (soft delete)"""
    card = db.query(Card).filter(
        Card.id == card_id,
        Card.user_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    card.is_active = False
    db.commit()

# ==================== ROUTER CATEGORIES ====================

categories_router = APIRouter(prefix="/categories", tags=["categories"])

@categories_router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear una nueva categoría"""
    db_category = Category(
        user_id=current_user.id,
        name=category_data.name,
        description=category_data.description,
        color=category_data.color,
        icon=category_data.icon
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@categories_router.get("", response_model=List[CategoryResponse])
def list_categories(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listar mis categorías"""
    categories = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.is_active == True
    ).all()
    return categories

@categories_router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener detalles de una categoría"""
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@categories_router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar una categoría"""
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    category.name = category_data.name
    category.description = category_data.description
    category.color = category_data.color
    category.icon = category_data.icon
    
    db.commit()
    db.refresh(category)
    return category

@categories_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Desactivar una categoría (soft delete)"""
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    category.is_active = False
    db.commit()
