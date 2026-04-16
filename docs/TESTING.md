# 🧪 Testing Guide

Guía completa para testing de la aplicación Gastos App.

---

## 📋 Estructura de Tests

```
tests/
├── __init__.py
├── conftest.py              # Fixtures compartidas
├── test_auth.py             # Tests de autenticación
├── test_expenses.py         # Tests de gastos
├── test_installments.py     # Tests de cuotas
├── test_payments.py         # Tests de pagos
└── test_reports.py          # Tests de reportes
```

---

## ⚙️ Setup de Testing

### 1. Crear conftest.py

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.security import hash_password

# Base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture
def db_engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Crear usuario de prueba"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_token(client, test_user):
    """Obtener token JWT de prueba"""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    return response.json()["access_token"]

@pytest.fixture
def auth_header(test_token):
    """Header de autenticación"""
    return {"Authorization": f"Bearer {test_token}"}
```

### 2. Instalar pytest

```bash
pip install pytest pytest-cov pytest-asyncio
```

---

## ✅ Tests de Autenticación

```python
# tests/test_auth.py
import pytest
from fastapi import status

def test_register_success(client):
    """Registro exitoso"""
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "securepass123"
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data

def test_register_duplicate_email(client, test_user):
    """No permitir emails duplicados"""
    response = client.post("/auth/register", json={
        "email": "test@example.com",  # Ya existe
        "username": "newuser",
        "password": "securepass123"
    })
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_success(client, test_user):
    """Login exitoso"""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Credenciales inválidas"""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, auth_header):
    """Obtener usuario actual"""
    response = client.get("/auth/me", headers=auth_header)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"

def test_invalid_token(client):
    """Token inválido"""
    response = client.get("/auth/me", headers={
        "Authorization": "Bearer invalid_token"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_missing_token(client):
    """Sin token"""
    response = client.get("/auth/me")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
```

---

## 💰 Tests de Gastos

```python
# tests/test_expenses.py
import pytest
from datetime import datetime
from decimal import Decimal

def test_create_expense_simple(client, auth_header, db_session, test_user):
    """Crear gasto simple"""
    # Crear tarjeta
    card = create_test_card(db_session, test_user.id)
    category = create_test_category(db_session, test_user.id)
    
    response = client.post("/expenses", 
        headers=auth_header,
        json={
            "card_id": card.id,
            "category_id": category.id,
            "date": datetime.now().isoformat(),
            "concept": "Cena",
            "total_amount": "300.00",
            "has_installments": False,
            "participants": [
                {"user_id": test_user.id, "amount": "300.00"}
            ]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["concept"] == "Cena"
    assert data["total_amount"] == "300.00"

def test_create_expense_with_installments(client, auth_header, db_session, test_user):
    """Crear gasto con cuotas"""
    card = create_test_card(db_session, test_user.id)
    category = create_test_category(db_session, test_user.id)
    
    response = client.post("/expenses",
        headers=auth_header,
        json={
            "card_id": card.id,
            "category_id": category.id,
            "date": datetime.now().isoformat(),
            "concept": "Viaje",
            "total_amount": "1000.00",
            "has_installments": True,
            "num_installments": 5,
            "participants": [
                {"user_id": test_user.id, "percentage": "100.00"}
            ]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["has_installments"] == True
    assert len(data["installments"]) == 5
    
    # Verificar que cada cuota es 1000/5 = 200
    for inst in data["installments"]:
        assert inst["amount"] == "200.00"

def test_list_expenses(client, auth_header, db_session, test_user):
    """Listar gastos"""
    # Crear algunos gastos
    for i in range(3):
        create_test_expense(db_session, test_user.id)
    
    response = client.get("/expenses", headers=auth_header)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

def test_cannot_access_others_expenses(client, auth_header, db_session, test_user, another_user):
    """No puede ver gastos de otros"""
    # Crear gasto para otro usuario
    expense = create_test_expense(db_session, another_user.id)
    
    response = client.get(f"/expenses/{expense.id}", headers=auth_header)
    
    assert response.status_code == 404
```

---

## 💳 Tests de Cuotas

```python
# tests/test_installments.py
def test_get_pending_installments(client, auth_header, db_session, test_user):
    """Obtener cuotas pendientes"""
    # Crear gasto con cuotas
    expense = create_test_expense_with_installments(
        db_session, test_user.id, num_installments=3
    )
    
    response = client.get("/installments/pending", headers=auth_header)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

def test_mark_installment_paid(client, auth_header, db_session, test_user):
    """Marcar cuota como pagada"""
    expense = create_test_expense_with_installments(
        db_session, test_user.id, num_installments=1
    )
    installment = expense.installments[0]
    split = installment.splits[0]
    
    response = client.put(
        f"/installments/{installment.id}/mark-paid",
        headers=auth_header
    )
    
    assert response.status_code == 200
    
    # Verificar que está marcado como pagado
    db_session.refresh(split)
    assert split.paid == True
```

---

## 🔄 Tests de Pagos

```python
# tests/test_payments.py
def test_get_my_debts(client, auth_header, db_session, test_user):
    """Ver lo que debo"""
    other_user = create_test_user(db_session, "other@example.com")
    
    # Crear gasto donde otro usuario pagó
    card = create_test_card(db_session, other_user.id)
    category = create_test_category(db_session, other_user.id)
    
    expense = create_test_expense(
        db_session,
        other_user.id,
        card.id,
        category.id,
        participants=[
            {"user_id": test_user.id, "amount": "100.00"},
            {"user_id": other_user.id, "amount": "100.00"}
        ]
    )
    
    response = client.get("/payments/me/owe", headers=auth_header)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(d["amount"] == "100.00" for d in data)

def test_register_payment(client, auth_header, db_session, test_user):
    """Registrar pago"""
    other_user = create_test_user(db_session, "other@example.com")
    
    response = client.post("/payments",
        headers=auth_header,
        json={
            "to_user_id": other_user.id,
            "amount": "50.00",
            "description": "Pago por cena"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == "50.00"
```

---

## 📊 Tests de Reportes

```python
# tests/test_reports.py
def test_get_monthly_report(client, auth_header, db_session, test_user):
    """Obtener reporte mensual"""
    # Crear algunos gastos
    create_test_expense(db_session, test_user.id)
    
    response = client.get(
        "/reports/monthly/2024/1",
        headers=auth_header
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2024
    assert data["month"] == 1
    assert "total_spent" in data
    assert "by_category" in data

def test_get_statistics(client, auth_header, db_session, test_user):
    """Obtener estadísticas"""
    response = client.get("/reports/statistics", headers=auth_header)
    
    assert response.status_code == 200
    data = response.json()
    assert "total_all_time" in data
    assert "total_expenses" in data
    assert "total_cards" in data
```

---

## 🚀 Ejecutar Tests

### Todos los tests
```bash
pytest
```

### Con cobertura
```bash
pytest --cov=app tests/
```

### Un archivo específico
```bash
pytest tests/test_auth.py
```

### Una función específica
```bash
pytest tests/test_auth.py::test_login_success
```

### Con output detallado
```bash
pytest -v
```

### Modo watch (re-ejecutar al cambiar código)
```bash
pytest-watch
```

---

## 📈 Coverage Target

```
app/
├── models/          → 90%+
├── schemas/         → 85%+
├── routes/          → 85%+
├── security.py      → 95%+
└── database.py      → 80%+

Target global: 85%+
```

Ver reporte HTML:
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

---

## 🔍 Helpers para Tests

```python
# tests/helpers.py
def create_test_user(db_session, email="test@example.com"):
    from app.models.user import User
    from app.security import hash_password
    
    user = User(
        email=email,
        username=email.split("@")[0],
        hashed_password=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def create_test_card(db_session, user_id):
    from app.models.card import Card
    
    card = Card(
        user_id=user_id,
        name="Test Card",
        card_type="visa",
        last_four="4242"
    )
    db_session.add(card)
    db_session.commit()
    db_session.refresh(card)
    return card

def create_test_category(db_session, user_id):
    from app.models.category import Category
    
    category = Category(
        user_id=user_id,
        name="Test Category",
        color="#FF0000"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category

def create_test_expense(db_session, user_id, card_id=None, category_id=None, participants=None):
    from app.models.expense import Expense
    from app.models.expense_participant import ExpenseParticipant
    from datetime import datetime
    from decimal import Decimal
    
    if not card_id:
        card = create_test_card(db_session, user_id)
        card_id = card.id
    
    if not category_id:
        category = create_test_category(db_session, user_id)
        category_id = category.id
    
    expense = Expense(
        card_id=card_id,
        category_id=category_id,
        date=datetime.now(),
        concept="Test Expense",
        total_amount=Decimal("100.00")
    )
    db_session.add(expense)
    db_session.flush()
    
    if participants:
        for p in participants:
            participant = ExpenseParticipant(
                expense_id=expense.id,
                user_id=p["user_id"],
                amount=Decimal(p.get("amount", "50.00"))
            )
            db_session.add(participant)
    
    db_session.commit()
    db_session.refresh(expense)
    return expense
```

---

## ✅ Checklist de Testing

```
Antes de commit:
☐ pytest pasa 100%
☐ Coverage >= 85%
☐ No hay warnings
☐ Code es legible

Antes de release:
☐ Tests en staging pasan
☐ Load tests ejecutados
☐ Security tests pasan
☐ Integración con BD real OK
```

---

**¡Aplicación con tests robusto!** ✅
