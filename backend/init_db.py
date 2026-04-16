#!/usr/bin/env python
"""
Script para inicializar la base de datos
Crea todas las tablas y datos de prueba
"""
import sys
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from decimal import Decimal

# Importar modelos y config
from app.config import settings
from app.database import Base, SessionLocal
from app.models.user import User
from app.models.card import Card
from app.models.category import Category
from app.models.expense import Expense
from app.models.expense_participant import ExpenseParticipant
from app.models.installment import Installment
from app.models.installment_split import InstallmentSplit
from app.security import hash_password

def init_db():
    """Inicializar BD"""
    print("🗄️  Creando tablas...")
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas")

def seed_db():
    """Agregar datos de prueba"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existen datos
        if db.query(User).count() > 0:
            print("⚠️  BD ya contiene datos, saltando seed")
            return
        
        print("🌱 Agregando datos de prueba...")
        
        # ==================== CREAR USUARIOS ====================
        user1 = User(
            email="juan@example.com",
            username="juan",
            full_name="Juan García",
            hashed_password=hash_password("password123")
        )
        
        user2 = User(
            email="maria@example.com",
            username="maria",
            full_name="María López",
            hashed_password=hash_password("password123")
        )
        
        user3 = User(
            email="carlos@example.com",
            username="carlos",
            full_name="Carlos Rodríguez",
            hashed_password=hash_password("password123")
        )
        
        db.add_all([user1, user2, user3])
        db.flush()  # Obtener IDs
        
        print(f"✅ Usuarios creados: {user1.username}, {user2.username}, {user3.username}")
        
        # ==================== CREAR TARJETAS ====================
        card1 = Card(
            user_id=user1.id,
            name="Visa Personal",
            card_type="visa",
            last_four="4242"
        )
        
        card2 = Card(
            user_id=user1.id,
            name="Mastercard Trabajo",
            card_type="mastercard",
            last_four="5555"
        )
        
        db.add_all([card1, card2])
        db.flush()
        
        print(f"✅ Tarjetas creadas")
        
        # ==================== CREAR CATEGORÍAS ====================
        categories = [
            Category(user_id=user1.id, name="Comida", color="#FF6B6B", icon="🍔"),
            Category(user_id=user1.id, name="Transporte", color="#4ECDC4", icon="🚗"),
            Category(user_id=user1.id, name="Tecnología", color="#45B7D1", icon="💻"),
            Category(user_id=user1.id, name="Entretenimiento", color="#96CEB4", icon="🎮"),
            Category(user_id=user1.id, name="Otros", color="#CCCCCC", icon="📌"),
        ]
        
        db.add_all(categories)
        db.flush()
        
        print(f"✅ Categorías creadas")
        
        # ==================== CREAR GASTO SIMPLE ====================
        expense1 = Expense(
            card_id=card1.id,
            category_id=categories[0].id,  # Comida
            date=datetime.now() - timedelta(days=5),
            concept="Cena en restaurante La Piazza",
            total_amount=Decimal("300.00"),
            has_installments=False,
            num_installments=1
        )
        
        db.add(expense1)
        db.flush()
        
        # Participantes del gasto
        participant1 = ExpenseParticipant(
            expense_id=expense1.id,
            user_id=user1.id,
            amount=Decimal("180.00"),
            description="Mi parte"
        )
        
        participant2 = ExpenseParticipant(
            expense_id=expense1.id,
            user_id=user2.id,
            amount=Decimal("120.00"),
            description="Maria"
        )
        
        db.add_all([participant1, participant2])
        
        print(f"✅ Gasto simple creado: {expense1.concept}")
        
        # ==================== CREAR GASTO CON CUOTAS ====================
        expense2 = Expense(
            card_id=card1.id,
            category_id=categories[2].id,  # Tecnología
            date=datetime.now() - timedelta(days=10),
            concept="Laptop para Juan (en 5 cuotas)",
            total_amount=Decimal("1000.00"),
            has_installments=True,
            num_installments=5
        )
        
        db.add(expense2)
        db.flush()
        
        # Participantes (porcentaje)
        participant3 = ExpenseParticipant(
            expense_id=expense2.id,
            user_id=user1.id,
            percentage=Decimal("40.00")
        )
        
        participant4 = ExpenseParticipant(
            expense_id=expense2.id,
            user_id=user2.id,
            percentage=Decimal("60.00")
        )
        
        db.add_all([participant3, participant4])
        db.flush()
        
        # Crear cuotas
        for i in range(1, 6):
            due_month = datetime.now().month + i
            due_year = datetime.now().year
            if due_month > 12:
                due_month -= 12
                due_year += 1
            
            installment = Installment(
                expense_id=expense2.id,
                installment_number=i,
                amount=Decimal("200.00"),
                due_date=datetime(due_year, due_month, 1)
            )
            
            db.add(installment)
            db.flush()
            
            # Splits (aplicar porcentaje a cada cuota)
            split1 = InstallmentSplit(
                installment_id=installment.id,
                user_id=user1.id,
                amount=Decimal("80.00")  # 40% de 200
            )
            
            split2 = InstallmentSplit(
                installment_id=installment.id,
                user_id=user2.id,
                amount=Decimal("120.00")  # 60% de 200
            )
            
            db.add_all([split1, split2])
        
        print(f"✅ Gasto con cuotas creado: {expense2.concept}")
        
        # ==================== CREAR MÁS GASTOS ====================
        more_expenses = [
            Expense(
                card_id=card1.id,
                category_id=categories[0].id,
                date=datetime.now() - timedelta(days=2),
                concept="Café con amigos",
                total_amount=Decimal("85.50")
            ),
            Expense(
                card_id=card1.id,
                category_id=categories[1].id,
                date=datetime.now() - timedelta(days=1),
                concept="Uber al trabajo",
                total_amount=Decimal("45.00")
            ),
            Expense(
                card_id=card2.id,
                category_id=categories[3].id,
                date=datetime.now(),
                concept="Cine y palomitas",
                total_amount=Decimal("120.00")
            ),
        ]
        
        db.add_all(more_expenses)
        db.flush()
        
        # Participantes para los otros gastos
        for expense in more_expenses:
            p1 = ExpenseParticipant(
                expense_id=expense.id,
                user_id=user1.id,
                amount=expense.total_amount * Decimal("0.5")
            )
            p2 = ExpenseParticipant(
                expense_id=expense.id,
                user_id=user3.id,
                amount=expense.total_amount * Decimal("0.5")
            )
            db.add_all([p1, p2])
        
        print(f"✅ Gastos adicionales creados")
        
        # Commit
        db.commit()
        print("\n✅ BD inicializada correctamente\n")
        print("📌 Usuarios creados:")
        print(f"  - juan@example.com / password123")
        print(f"  - maria@example.com / password123")
        print(f"  - carlos@example.com / password123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    seed_db()
