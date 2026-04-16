"""
Script para inicializar la base de datos con datos de prueba
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from decimal import Decimal

from app.database import engine, SessionLocal
from app.models import Base
from app.models.user import User
from app.models.card import Card
from app.models.category import Category
from app.models.expense import Expense
from app.models.expense_participant import ExpenseParticipant
from app.models.installment import Installment
from app.models.installment_split import InstallmentSplit
from app.models.payment import Payment
from app.security import get_password_hash


def init_db():
    """Inicializar BD con tablas y datos de prueba"""
    
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas OK")
    
    db = SessionLocal()
    
    try:
        # Verificar si ya hay datos
        if db.query(User).count() > 0:
            print("La BD ya tiene datos. Saltando...")
            return
        
        # ==================== USUARIOS ====================
        print("Creando usuarios...")
        
        user1 = User(
            email="juan@example.com",
            username="juan",
            full_name="Juan Garcia",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        user2 = User(
            email="maria@example.com",
            username="maria",
            full_name="Maria Lopez",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        user3 = User(
            email="carlos@example.com",
            username="carlos",
            full_name="Carlos Rodriguez",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        
        db.add_all([user1, user2, user3])
        db.flush()
        print(f"Usuarios creados: {user1.id}, {user2.id}, {user3.id}")
        
        # ==================== TARJETAS ====================
        print("Creando tarjetas...")
        
        cards = [
            Card(user_id=user1.id, name="Visa Personal", card_type="visa", last_four="4242"),
            Card(user_id=user1.id, name="Mastercard Black", card_type="mastercard", last_four="8888"),
            Card(user_id=user2.id, name="Visa Maria", card_type="visa", last_four="1234"),
            Card(user_id=user3.id, name="Amex Carlos", card_type="amex", last_four="5678"),
        ]
        
        db.add_all(cards)
        db.flush()
        print("Tarjetas creadas OK")
        
        # ==================== CATEGORIAS ====================
        print("Creando categorias...")
        
        categories = [
            Category(user_id=user1.id, name="Comidas", color="#FF6B6B", icon="food"),
            Category(user_id=user1.id, name="Transporte", color="#4ECDC4", icon="car"),
            Category(user_id=user1.id, name="Tecnologia", color="#45B7D1", icon="tech"),
            Category(user_id=user1.id, name="Entretenimiento", color="#96CEB4", icon="fun"),
            Category(user_id=user1.id, name="Servicios", color="#FFEAA7", icon="service"),
            Category(user_id=user2.id, name="Comidas", color="#FF6B6B", icon="food"),
            Category(user_id=user2.id, name="Transporte", color="#4ECDC4", icon="car"),
            Category(user_id=user3.id, name="Comidas", color="#FF6B6B", icon="food"),
        ]
        
        db.add_all(categories)
        db.flush()
        print("Categorias creadas OK")
        
        # ==================== GASTOS ====================
        print("Creando gastos...")
        
        now = datetime.now()
        
        # Gasto 1: Cena entre Juan y Maria
        expense1 = Expense(
            card_id=cards[0].id,
            category_id=categories[0].id,
            date=now - timedelta(days=5),
            concept="Cena restaurante",
            total_amount=Decimal("3000.00"),
            has_installments=False,
            num_installments=1
        )
        db.add(expense1)
        db.flush()
        
        db.add_all([
            ExpenseParticipant(expense_id=expense1.id, user_id=user1.id, amount=Decimal("1800.00"), percentage=Decimal("60")),
            ExpenseParticipant(expense_id=expense1.id, user_id=user2.id, amount=Decimal("1200.00"), percentage=Decimal("40")),
        ])
        
        # Gasto 2: Uber entre los 3
        expense2 = Expense(
            card_id=cards[0].id,
            category_id=categories[1].id,
            date=now - timedelta(days=3),
            concept="Uber al aeropuerto",
            total_amount=Decimal("1500.00"),
            has_installments=False,
            num_installments=1
        )
        db.add(expense2)
        db.flush()
        
        db.add_all([
            ExpenseParticipant(expense_id=expense2.id, user_id=user1.id, amount=Decimal("500.00"), percentage=Decimal("33.33")),
            ExpenseParticipant(expense_id=expense2.id, user_id=user2.id, amount=Decimal("500.00"), percentage=Decimal("33.33")),
            ExpenseParticipant(expense_id=expense2.id, user_id=user3.id, amount=Decimal("500.00"), percentage=Decimal("33.34")),
        ])
        
        # Gasto 3: Netflix con cuotas
        expense3 = Expense(
            card_id=cards[0].id,
            category_id=categories[2].id,
            date=now - timedelta(days=10),
            concept="Laptop compartida",
            total_amount=Decimal("120000.00"),
            has_installments=True,
            num_installments=6
        )
        db.add(expense3)
        db.flush()
        
        db.add_all([
            ExpenseParticipant(expense_id=expense3.id, user_id=user1.id, amount=Decimal("60000.00"), percentage=Decimal("50")),
            ExpenseParticipant(expense_id=expense3.id, user_id=user2.id, amount=Decimal("60000.00"), percentage=Decimal("50")),
        ])
        
        # Crear cuotas para expense3
        installment_amount = Decimal("20000.00")
        for i in range(1, 7):
            due_month = now.month + i
            due_year = now.year
            if due_month > 12:
                due_month -= 12
                due_year += 1
            
            inst = Installment(
                expense_id=expense3.id,
                installment_number=i,
                amount=installment_amount,
                due_date=datetime(due_year, due_month, 1),
                paid=(i == 1)
            )
            db.add(inst)
            db.flush()
            
            db.add_all([
                InstallmentSplit(installment_id=inst.id, user_id=user1.id, amount=Decimal("10000.00"), paid=(i == 1)),
                InstallmentSplit(installment_id=inst.id, user_id=user2.id, amount=Decimal("10000.00"), paid=(i == 1)),
            ])
        
        # Gasto 4: Supermercado
        expense4 = Expense(
            card_id=cards[2].id,
            category_id=categories[5].id,
            date=now - timedelta(days=1),
            concept="Supermercado semana",
            total_amount=Decimal("8500.00"),
            has_installments=False,
            num_installments=1
        )
        db.add(expense4)
        db.flush()
        
        db.add_all([
            ExpenseParticipant(expense_id=expense4.id, user_id=user2.id, amount=Decimal("4250.00"), percentage=Decimal("50")),
            ExpenseParticipant(expense_id=expense4.id, user_id=user1.id, amount=Decimal("4250.00"), percentage=Decimal("50")),
        ])
        
        # ==================== PAGOS ====================
        print("Creando pagos de ejemplo...")
        
        payment1 = Payment(
            from_user_id=user2.id,
            to_user_id=user1.id,
            amount=Decimal("1000.00"),
            description="Pago parcial cena",
            payment_date=now - timedelta(days=2),
            confirmed=True
        )
        db.add(payment1)
        
        db.commit()
        
        print("")
        print("=" * 50)
        print("Base de datos inicializada correctamente!")
        print("=" * 50)
        print("")
        print("Usuarios de prueba:")
        print("  Email: juan@example.com   / Password: password123")
        print("  Email: maria@example.com  / Password: password123")
        print("  Email: carlos@example.com / Password: password123")
        print("")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
