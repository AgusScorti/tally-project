# 🏗️ Arquitectura Técnica - Gastos App

Documento detallado sobre el diseño y decisiones de la aplicación.

---

## 📊 Diagrama de Entidades

```
┌─────────────┐
│    User     │
├─────────────┤
│ id (PK)     │
│ email       │
│ username    │
│ password    │
└──────┬──────┘
       │
       ├──(1:N)──→ Card
       ├──(1:N)──→ Category
       ├──(1:N)──→ ExpenseParticipant
       ├──(1:N)──→ Payment (from)
       └──(1:N)──→ Payment (to)

┌─────────────┐
│    Card     │
├─────────────┤
│ id (PK)     │
│ user_id (FK)│
│ name        │
│ card_type   │
└──────┬──────┘
       │
       └──(1:N)──→ Expense

┌──────────────────┐
│    Expense       │
├──────────────────┤
│ id (PK)          │
│ card_id (FK)     │
│ category_id (FK) │
│ date             │
│ concept          │
│ total_amount     │
│ has_installments │
└──────┬───────────┘
       │
       ├──(1:N)──→ ExpenseParticipant
       └──(1:N)──→ Installment

┌────────────────────────┐
│ ExpenseParticipant     │
├────────────────────────┤
│ id (PK)                │
│ expense_id (FK)        │
│ user_id (FK)           │
│ amount (opcional)      │
│ percentage (opcional)  │
└────────────────────────┘

┌─────────────────┐
│  Installment    │
├─────────────────┤
│ id (PK)         │
│ expense_id (FK) │
│ number          │
│ amount          │
│ due_date        │
│ is_paid         │
└────────┬────────┘
         │
         └──(1:N)──→ InstallmentSplit

┌────────────────────┐
│ InstallmentSplit   │
├────────────────────┤
│ id (PK)            │
│ installment_id (FK)│
│ user_id (FK)       │
│ amount             │
│ paid               │
└────────────────────┘

┌──────────────┐
│   Payment    │
├──────────────┤
│ id (PK)      │
│ from_user_id │
│ to_user_id   │
│ amount       │
│ confirmed    │
│ date         │
└──────────────┘
```

---

## 🔑 Decisiones de Diseño Clave

### 1. ¿Por qué ExpenseParticipant está separada?

**Problema:** Un gasto puede involucrar a múltiples personas.

```
Opción 1 (MALA - Acoplada):
Expense: {id, monto, user1, user2, user3, amount1, amount2, amount3}
❌ Rgído, máximo 3 personas, mucho código especial

Opción 2 (BUENA - Normalizada) ✅
Expense: {id, total_amount}
ExpenseParticipant: {id, expense_id, user_id, amount}

Con esto:
- 2 personas: 2 filas
- 5 personas: 5 filas
- Flexible y escalable
```

### 2. ¿Amount vs Percentage?

**Problema:** A veces sé exactamente cuánto, a veces solo sé el %

```
Gasto de $300:

Caso A: Yo = $180, Juan = $120
  → Usar Amount

Caso B: Yo = 60%, Juan = 40%
  → Usar Percentage
  → Sistema calcula: Yo = 180, Juan = 120

Solución: Guardar AMBOS (redundancia controlada)
- Si hay amount, usarlo
- Si hay percentage, calcular amount
```

### 3. ¿Cuotas: ¿Automáticas o Manuales?

**Decisión:** AUTOMÁTICAS (pero permitir edición)

```
Usuario crea gasto con cuotas:
  POST /expenses
    {
      has_installments: true,
      num_installments: 5,
      participants: [{user_id: 1, percentage: 60%}, ...]
    }

Sistema AUTOMÁTICAMENTE:
1. Crea 5 Installment (dividiendo monto equitativamente)
2. Para cada cuota, crea InstallmentSplit
   (aplicando porcentaje a cada usuario)

Resultado:
Cuota 1 ($200): User1=$120 (60%), User2=$80 (40%)
Cuota 2 ($200): User1=$120 (60%), User2=$80 (40%)
...
```

**Ventaja:** El usuario no tiene que calcular, es automático

### 4. ¿Marcar Cuota Pagada: Por Cuota o Por Usuario?

**Decisión:** POR USUARIO (InstallmentSplit.paid)

```
Problema: En una cuota de 3 personas, 1 paga y 2 no

Opción 1 (MALA):
Installment.is_paid = true/false
❌ Si una persona paga, no sé quién pagó

Opción 2 (BUENA) ✅:
Installment.is_paid = true SOLO si TODOS pagaron
InstallmentSplit.paid = true para cada persona

Cuando todos los InstallmentSplit.paid = true
  → Installment.is_paid = true automáticamente
```

### 5. Sistema de Pagos (Deudas)

**Decisión:** Registrar pagos explícitos, no inferir

```
Opción 1 (INFERIR DEUDAS AUTOMÁTICAMENTE):
❌ Complejo, ambiguo, fácil equivocarse

Opción 2 (PAGOS EXPLÍCITOS) ✅:
Payment table registra:
  from_user: quien paga
  to_user: quien recibe
  amount: cuánto
  confirmed: aceptado por receptor

Query de balance:
  balance = (payments yo recibí) - (payments que envié)
```

### 6. Autorización: ¿Quién puede ver/editar qué?

**Reglas Implementadas:**

```
Usuario solo puede ver:
- SUS tarjetas
- SUS gastos registrados
- SUS categorías
- Gastos donde PARTICIPA
- Pagos donde PARTICIPA

No hay "admin", cada usuario es su propio admin
```

---

## 🔄 Flujos Principales

### Flujo 1: Crear Gasto Compartido

```
Usuario A (Juan) paga $300 en Visa
Participan: Juan 60%, María 40%

1. POST /expenses
   {
     card_id: 1 (Visa de Juan),
     category_id: 5,
     concept: "Cena",
     total_amount: 300,
     participants: [
       {user_id: 1, percentage: 60},  // Juan
       {user_id: 2, percentage: 40}   // María
     ]
   }

2. Sistema crea:
   - Expense: id=42, total=300
   - ExpenseParticipant: (42, 1, amount=180)
   - ExpenseParticipant: (42, 2, amount=120)

3. DEUDA AUTOMÁTICA (inferida):
   María le debe a Juan: $120
   
4. Cuando María paga:
   POST /payments
   {
     to_user_id: 1 (Juan),
     amount: 120,
     description: "Pago por cena"
   }
   
   → Se crea Payment: (from=2, to=1, amount=120)
   → Balance se actualiza: María no le debe nada
```

### Flujo 2: Gasto con Cuotas

```
Usuario A paga Laptop de $1000 en 5 cuotas
Participan: Usuario A (40%), Usuario B (60%)

1. POST /expenses
   {
     total_amount: 1000,
     has_installments: true,
     num_installments: 5,
     participants: [
       {user_id: 1, percentage: 40},
       {user_id: 2, percentage: 60}
     ]
   }

2. Sistema crea:
   Expense: id=42, total=1000
   
   Installment #1: $200, due_date=FEB
   InstallmentSplit: (inst=N, user=1, amount=80)
   InstallmentSplit: (inst=N, user=2, amount=120)
   
   Installment #2: $200, due_date=MAR
   InstallmentSplit: (inst=N+1, user=1, amount=80)
   InstallmentSplit: (inst=N+1, user=2, amount=120)
   
   ... (igual para 5 cuotas)

3. Consulta: "¿Cuáles son mis cuotas pendientes?"
   GET /installments/my-splits/pending
   
   → Devuelve todos mis InstallmentSplit donde paid=false
   → Total a pagar: $500 (en todas mis cuotas)

4. Cuando Usuario B paga cuota 1:
   PUT /installments/{split_id}/mark-paid
   
   → InstallmentSplit.paid = true
   → Sistema verifica si TODOS los splits de esta cuota están pagados
   → Si sí: Installment.is_paid = true
```

### Flujo 3: Ver Deudas

```
Consulta 1: "¿A quién le debo dinero?"
GET /payments/me/owe

Logic:
  FOR EACH ExpenseParticipant WHERE user_id = YO:
    gasto = ExpenseParticipant.expense
    dueno_tarjeta = gasto.card.user
    
    IF dueno_tarjeta != YO:
      # Yo le debo al dueño
      deuda = ExpenseParticipant.amount
      
      # Verificar si ya pagué
      pago_existe = Payment WHERE from=YO, to=dueno, expense_participant_id=X
      
      IF NOT pago_existe:
        # Aún debo
        yield deuda

Resultado:
[
  {deuda a María: $120, por cena},
  {deuda a Carlos: $80, por viaje}
]

Consulta 2: "¿Quién me debe dinero?"
GET /payments/me/owed

Logic:
  FOR EACH ExpenseParticipant WHERE expense.card.user = YO:
    IF ExpenseParticipant.user_id != YO:
      # Otro usuario debe
      credito = ExpenseParticipant.amount
      
      IF NOT payment_exists:
        yield credito

Resultado:
[
  {Juan me debe: $150, por cena},
  {María me debe: $200, por viaje}
]
```

---

## 🔒 Seguridad

### Autenticación: JWT Token

```
1. Login:
   POST /auth/login
   {email, password}
   
   → Verificar contraseña (bcrypt)
   → Generar JWT: {sub: user_id, exp: now + 30min}
   → Token firmado con SECRET_KEY

2. Request protegido:
   GET /expenses
   Header: Authorization: Bearer {token}
   
   → Verificar firma del token
   → Extraer user_id
   → Asegurarse que solo ve SUS datos
```

### Autorización: Row-Level Security

```
Ejemplo: GET /expenses/{id}

def get_expense(..., current_user):
    expense = db.query(Expense).filter(
        Expense.id == id,
        Expense.card.user_id == current_user.id  # ← IMPORTANTE
    ).first()
    
    if not expense:
        raise 404
    
    return expense

✅ Solo ve sus propios gastos
✅ No puede ver gastos de otros
```

---

## 📈 Performance

### Optimizaciones Implementadas

1. **Índices en BD:**
```sql
INDEX: expenses(card_id)
INDEX: expenses(date)
INDEX: expense_participants(user_id)
INDEX: installments(is_paid)
INDEX: payments(from_user_id, to_user_id)
```

2. **Pool de Conexiones:**
```python
pool_size=20
max_overflow=40
pool_pre_ping=True  # Verifica conexiones
```

3. **Paginación:**
```python
# GET /expenses?limit=50&skip=0
# Nunca traer todas las filas de una
```

4. **Relaciones Lazy:**
```python
# No cargar RelationShips innecesarias
relationship("Installment", lazy="select")
```

---

## 🚀 Escalabilidad Futura

### Si crece a 10,000 usuarios:

1. **Caché (Redis):**
   - Cache balances por usuario
   - Cache reportes mensuales
   
2. **Particionamiento de BD:**
   - Particionar expenses por user_id
   - Particionar payments por fecha
   
3. **Asincronía:**
   - Usar Celery para cálculos pesados
   - Background jobs para reportes PDF
   
4. **CQRS Pattern:**
   - Separar lecturas de escrituras
   - Base de datos de lectura (analytics)

---

## 📝 Convenciones de Código

### Nombres de Variables

```python
# Usuarios/IDs
user: User  # El modelo
user_id: int  # Solo el ID
current_user: User  # Usuario autenticado

# Gastos
expense: Expense  # El modelo
expense_data: ExpenseCreate  # Schema Pydantic
db_expense: Expense  # Después de BD

# Dinero
amount: Decimal  # Siempre Decimal, nunca float
total_amount: Decimal
balance: Decimal
```

### Estructura de Endpoints

```python
# POST (crear)
@router.post("/expenses", response_model=ExpenseResponse, status_code=201)
def create_expense(data: ExpenseCreate, current_user: User = Depends(...)):
    """Crear nuevo gasto"""

# GET (listar)
@router.get("/expenses", response_model=List[ExpenseResponse])
def list_expenses(current_user: User = Depends(...)):
    """Listar gastos del usuario"""

# GET (obtener)
@router.get("/expenses/{id}", response_model=ExpenseResponse)
def get_expense(id: int, current_user: User = Depends(...)):
    """Obtener gasto específico"""

# PUT (actualizar)
@router.put("/expenses/{id}", response_model=ExpenseResponse)
def update_expense(id: int, data: ExpenseUpdate, current_user: User = Depends(...)):
    """Actualizar gasto"""

# DELETE (eliminar)
@router.delete("/expenses/{id}", status_code=204)
def delete_expense(id: int, current_user: User = Depends(...)):
    """Eliminar gasto"""
```

---

## 🧪 Testing Strategy

```python
# tests/test_expenses.py
def test_create_expense():
    """Crear gasto con participantes"""

def test_expense_list_filters():
    """Filtrar gastos por fecha, categoría, etc"""

def test_cannot_see_others_expenses():
    """Usuario no puede ver gastos de otros"""

def test_installments_split_correctly():
    """Cuotas se dividen correctamente por porcentaje"""

def test_balance_calculation():
    """Balance correcto entre usuarios"""
```

---

## 📚 Stack Justificado

| Tech | Razón |
|------|-------|
| **FastAPI** | Rápido, moderno, perfecto para CRUD |
| **SQLAlchemy** | ORM flexible, soporta raw SQL si necesitas |
| **PostgreSQL** | Robusto, ACID, soporta transacciones |
| **JWT** | Stateless, escalable, seguro |
| **Pydantic** | Validación automática, serialización JSON |
| **Alembic** | Migrations versionadas |
| **Pytest** | Testing framework estándar |

---

**Fin de la Arquitectura Técnica** ✅
