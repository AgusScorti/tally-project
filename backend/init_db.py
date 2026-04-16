import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from decimal import Decimal

from app.database import engine, SessionLocal, Base
from app.models.user import User
from app.models.card import Card
from app.models.category import Category
from app.models.expense import Expense
from app.models.expense_participant import ExpenseParticipant
from app.models.installment import Installment
from app.models.installment_split import InstallmentSplit
from app.models.payment import Payment
from app.security import get_password_hash

# Importar todos los modelos para que Base los registre
import app.models.user
import app.models.card
import app.models.category
import app.models.expense
import app.models.expense_participant
import app.models.installment
import app.models.installment_split
import app.models.payment


def init_db():
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas OK")

    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("La BD ya tiene datos. Saltando...")
            return

        # USUARIOS
        print("Creando usuarios...")
        user1 = User(email="juan@example.com",   username="juan",   full_name="Juan Garcia",       hashed_password=get_password_hash("password123"), is_active=True)
        user2 = User(email="maria@example.com",  username="maria",  full_name="Maria Lopez",        hashed_password=get_password_hash("password123"), is_active=True)
        user3 = User(email="carlos@example.com", username="carlos", full_name="Carlos Rodriguez",   hashed_password=get_password_hash("password123"), is_active=True)
        db.add_all([user1, user2, user3])
        db.flush()
        print(f"  Usuarios: {user1.id}, {user2.id}, {user3.id}")

        # TARJETAS
        print("Creando tarjetas...")
        cards = [
            Card(user_id=user1.id, name="Visa Personal",     card_type="visa",       last_four="4242"),
            Card(user_id=user1.id, name="Mastercard Black",  card_type="mastercard", last_four="8888"),
            Card(user_id=user2.id, name="Visa Maria",        card_type="visa",       last_four="1234"),
            Card(user_id=user3.id, name="Amex Carlos",       card_type="amex",       last_four="5678"),
        ]
        db.add_all(cards)
        db.flush()

        # CATEGORIAS
        print("Creando categorias...")
        categories = [
            Category(user_id=user1.id, name="Comidas",          color="#FF6B6B"),
            Category(user_id=user1.id, name="Transporte",        color="#4ECDC4"),
            Category(user_id=user1.id, name="Tecnologia",        color="#45B7D1"),
            Category(user_id=user1.id, name="Entretenimiento",   color="#96CEB4"),
            Category(user_id=user2.id, name="Comidas",           color="#FF6B6B"),
            Category(user_id=user2.id, name="Transporte",        color="#4ECDC4"),
            Category(user_id=user3.id, name="Comidas",           color="#FF6B6B"),
        ]
        db.add_all(categories)
        db.flush()

        now = datetime.now()

        # GASTO 1: Cena Juan y Maria (sin cuotas)
        print("Creando gastos...")
        e1 = Expense(card_id=cards[0].id, category_id=categories[0].id,
                     date=now - timedelta(days=5), concept="Cena restaurante",
                     total_amount=Decimal("3000.00"), has_installments=False, num_installments=1)
        db.add(e1); db.flush()
        db.add_all([
            ExpenseParticipant(expense_id=e1.id, user_id=user1.id, amount=Decimal("1800.00"), percentage=Decimal("60")),
            ExpenseParticipant(expense_id=e1.id, user_id=user2.id, amount=Decimal("1200.00"), percentage=Decimal("40")),
        ])

        # GASTO 2: Uber entre 3
        e2 = Expense(card_id=cards[0].id, category_id=categories[1].id,
                     date=now - timedelta(days=3), concept="Uber aeropuerto",
                     total_amount=Decimal("1500.00"), has_installments=False, num_installments=1)
        db.add(e2); db.flush()
        db.add_all([
            ExpenseParticipant(expense_id=e2.id, user_id=user1.id, amount=Decimal("500.00"),  percentage=Decimal("33.33")),
            ExpenseParticipant(expense_id=e2.id, user_id=user2.id, amount=Decimal("500.00"),  percentage=Decimal("33.33")),
            ExpenseParticipant(expense_id=e2.id, user_id=user3.id, amount=Decimal("500.00"),  percentage=Decimal("33.34")),
        ])

        # GASTO 3: Laptop con 6 cuotas
        e3 = Expense(card_id=cards[0].id, category_id=categories[2].id,
                     date=now - timedelta(days=10), concept="Laptop compartida",
                     total_amount=Decimal("120000.00"), has_installments=True, num_installments=6)
        db.add(e3); db.flush()
        db.add_all([
            ExpenseParticipant(expense_id=e3.id, user_id=user1.id, amount=Decimal("60000.00"), percentage=Decimal("50")),
            ExpenseParticipant(expense_id=e3.id, user_id=user2.id, amount=Decimal("60000.00"), percentage=Decimal("50")),
        ])

        inst_amount = Decimal("20000.00")
        for i in range(1, 7):
            due_month = now.month + i
            due_year = now.year
            if due_month > 12:
                due_month -= 12
                due_year += 1
            inst = Installment(
                expense_id=e3.id,
                installment_number=i,
                amount=inst_amount,
                due_date=datetime(due_year, due_month, 1),
                is_paid=(i == 1)
            )
            db.add(inst); db.flush()
            db.add_all([
                InstallmentSplit(installment_id=inst.id, user_id=user1.id, amount=Decimal("10000.00"), paid=(i == 1)),
                InstallmentSplit(installment_id=inst.id, user_id=user2.id, amount=Decimal("10000.00"), paid=(i == 1)),
            ])

        # GASTO 4: Supermercado
        e4 = Expense(card_id=cards[2].id, category_id=categories[4].id,
                     date=now - timedelta(days=1), concept="Supermercado",
                     total_amount=Decimal("8500.00"), has_installments=False, num_installments=1)
        db.add(e4); db.flush()
        db.add_all([
            ExpenseParticipant(expense_id=e4.id, user_id=user2.id, amount=Decimal("4250.00"), percentage=Decimal("50")),
            ExpenseParticipant(expense_id=e4.id, user_id=user1.id, amount=Decimal("4250.00"), percentage=Decimal("50")),
        ])

        # PAGO
        print("Creando pagos...")
        db.add(Payment(
            from_user_id=user2.id,
            to_user_id=user1.id,
            amount=Decimal("1000.00"),
            description="Pago parcial cena",
            date=now - timedelta(days=2),
            confirmed=True
        ))

        db.commit()

        print("")
        print("=" * 50)
        print("Base de datos inicializada correctamente!")
        print("=" * 50)
        print("Usuarios de prueba:")
        print("  juan@example.com   / password123")
        print("  maria@example.com  / password123")
        print("  carlos@example.com / password123")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
