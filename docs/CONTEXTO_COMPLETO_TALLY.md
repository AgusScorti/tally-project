# 📋 CONTEXTO COMPLETO DE TALLY

**Documento maestro con toda la información técnica del proyecto**

Usa este archivo para comunicar cambios, migraciones o cualquier decisión técnica.

---

## 📊 RESUMEN EJECUTIVO

```
Nombre:        TALLY
Tipo:          App de tracking de gastos compartidos
Stack:         Python/FastAPI + React/Tailwind + PostgreSQL
Status:        ✅ Producción Ready
Usuarios:      3 usuarios de prueba (juan, maria, carlos)
Datos:         Gastos compartidos, cuotas automáticas, deudas
```

---

## 🏗️ ARQUITECTURA GENERAL

```
┌─────────────────────────────────────────────┐
│          FRONTEND (React/Tailwind)          │
│  http://localhost:3000                      │
│  ├─ Login/Registro                          │
│  ├─ Dashboard (stats + gastos recientes)    │
│  ├─ Expenses (crear/listar gastos)          │
│  ├─ Payments (deudas y pagos)               │
│  ├─ Reports (análisis y gráficos)           │
│  └─ Settings (tarjetas y categorías)        │
└──────────┬──────────────────────────────────┘
           │ HTTP REST API
           │ JWT Authentication
           ↓
┌─────────────────────────────────────────────┐
│       BACKEND (FastAPI/Python)              │
│  http://localhost:8000                      │
│  27 endpoints en 6 routers                  │
│  ├─ /auth (login, register, me)             │
│  ├─ /expenses (CRUD + participantes)        │
│  ├─ /installments (cuotas automáticas)      │
│  ├─ /payments (deudas y saldo)              │
│  ├─ /reports (análisis por período)         │
│  └─ /cards + /categories (CRUD)             │
└──────────┬──────────────────────────────────┘
           │ SQLAlchemy ORM
           ↓
┌─────────────────────────────────────────────┐
│    BASE DE DATOS (PostgreSQL)               │
│  localhost:5432 (o en la nube)              │
│  8 tablas normalizadas                      │
└─────────────────────────────────────────────┘
```

---

## 🗄️ MODELO DE DATOS (8 TABLAS)

### 1. **users**
```sql
- id (PK)
- email (UNIQUE)
- username
- full_name
- hashed_password (bcrypt)
- created_at

3 usuarios de prueba:
- juan@example.com (password123)
- maria@example.com (password123)
- carlos@example.com (password123)
```

### 2. **cards**
```sql
- id (PK)
- user_id (FK → users)
- name (ej: "Visa Personal")
- card_type (visa, mastercard, amex)
- last_four (últimos 4 dígitos)
- created_at
```

### 3. **categories**
```sql
- id (PK)
- user_id (FK → users)
- name (ej: "Comidas", "Transporte")
- color (#22C55E, etc)
- created_at
```

### 4. **expenses** ⭐ PRINCIPAL
```sql
- id (PK)
- card_id (FK → cards)
- category_id (FK → categories)
- date
- concept (descripción)
- total_amount (monto total)
- has_installments (bool)
- num_installments (1-60, o NULL)
- created_at

Ejemplo: "Cena el viernes" 
- total_amount: $300
- participants: Juan ($180), María ($120)
- Si tiene cuotas: 5 cuotas de $60 cada una
```

### 5. **expense_participants** ⭐ CLAVE
```sql
- id (PK)
- expense_id (FK → expenses)
- user_id (FK → users)
- amount (monto que le toca a este usuario)
- percentage (si se divide en porcentaje, ej: 50%)

Relación N:M entre expenses y users
Permite múltiples participantes por gasto
```

### 6. **installments**
```sql
- id (PK)
- expense_id (FK → expenses)
- installment_number (1, 2, 3, ...)
- amount (monto de esta cuota)
- due_date
- paid (bool)
- created_at

Ejemplo: Gasto de $300 en 3 cuotas
- Cuota 1: $100 (generada automáticamente)
- Cuota 2: $100
- Cuota 3: $100
```

### 7. **installment_splits** ⭐ CLAVE
```sql
- id (PK)
- installment_id (FK → installments)
- user_id (FK → users)
- amount (cuánto de esta cuota le toca a este usuario)
- paid (bool)

Ejemplo: Cuota 1 de $100 entre 2 personas
- Juan: $60 (paid=False)
- María: $40 (paid=False)

Permite que cada participante pague su parte de cada cuota
```

### 8. **payments**
```sql
- id (PK)
- from_user_id (FK → users)
- to_user_id (FK → users)
- amount
- description (ej: "Pago por cena")
- payment_date
- confirmed (bool)
- created_at

Registro de pagos realizados para resolver deudas
```

---

## 📊 FLUJOS PRINCIPALES

### Flujo 1: Crear Gasto Compartido

```
Usuario crea gasto:
  - Concepto: "Cena"
  - Monto: $300
  - Tarjeta: Visa Personal
  - Categoría: Comidas
  - Participantes: Juan ($180), María ($120)
  - Sin cuotas

Sistema:
  1. Crea registro en expenses ($300)
  2. Crea 2 expense_participants:
     - Juan: $180
     - María: $120
  3. Maria ahora DEBE $180 a Juan

Frontend:
  - Actualiza lista de gastos
  - Muestra en dashboard
```

### Flujo 2: Crear Gasto con Cuotas

```
Usuario crea gasto:
  - Concepto: "Viaje"
  - Monto: $1000
  - Participantes: Juan (50%), María (50%)
  - 5 cuotas mensuales

Sistema:
  1. Crea expense ($1000)
  2. Crea 2 expense_participants (50% cada uno = $500 cada uno)
  3. Crea 5 installments ($200 cada una)
  4. Para CADA cuota, crea installment_splits:
     - Cuota 1: Juan $100, María $100
     - Cuota 2: Juan $100, María $100
     - ... (total 5 cuotas)
  5. María debe $500 total ($100/mes)

Nota: Las cuotas se crean AUTOMÁTICAMENTE
```

### Flujo 3: Ver Deudas

```
Endpoint GET /payments/me/owe

Calcula: ¿Cuánto me deben?
  - Suma todos los expense_participants donde user_id = yo
  - Resta los pagos registrados en payments
  - Resultado: deuda neta con cada persona

Ejemplo:
  - Juan me debe $300 (cena)
  - María me debe $150 (uber)
  - Carlos me debe $0
```

### Flujo 4: Registrar Pago

```
Usuario registra: "Pago $300 a Juan"

Sistema:
  1. Crea registro en payments
  2. Marca como confirmado si ambos aceptan
  3. Deuda se resuelve automáticamente

Cálculo final:
  - Deuda antes: $300
  - Pago registrado: $300
  - Deuda después: $0
```

---

## 🔐 AUTENTICACIÓN Y SEGURIDAD

### JWT (JSON Web Tokens)
```
Login:
  POST /auth/login
  → Backend genera JWT (válido 30 minutos)
  → Frontend guarda en localStorage
  → Incluye en todos los requests: Authorization: Bearer {token}

Logout:
  Frontend borra token de localStorage
  → Redirect a /login
```

### Passwords
```
Storage: Hasheado con bcrypt (no reversible)
Comparación: Flask-bcrypt hash_password() y check_password()
Cambio: No implementado aún
Reset: No implementado aún
```

### Row-Level Security
```
Usuario 1 NO puede:
  - Ver gastos de Usuario 2
  - Modificar categorías de Usuario 2
  - Ver pagos de Usuario 2
  
Implementación:
  - Cada endpoint verifica user_id del token
  - SQLAlchemy filters por user_id
  - No hay "admin" - cada usuario ve solo sus datos
```

---

## 📡 ENDPOINTS (27 TOTAL)

### Auth (3)
```
POST   /auth/register          → Crear cuenta
POST   /auth/login             → Obtener JWT token
GET    /auth/me                → Datos usuario actual
```

### Expenses (5)
```
POST   /expenses               → Crear gasto
GET    /expenses               → Listar mis gastos
GET    /expenses/{id}          → Detalles de gasto
PUT    /expenses/{id}          → Actualizar gasto
DELETE /expenses/{id}          → Eliminar gasto
```

### Installments (5)
```
GET    /installments/pending            → Mis cuotas pendientes
GET    /installments/{id}               → Detalles cuota
GET    /installments/my-splits/pending  → Mis cuotas personales
PUT    /installments/{id}/mark-paid     → Marcar como pagada
GET    /installments/upcoming/by-days   → Próximas cuotas
```

### Payments (7)
```
POST   /payments                        → Registrar pago
GET    /payments/me/owe                 → Lo que debo
GET    /payments/me/owed                → Lo que me deben
GET    /payments/balance/{user_id}      → Balance con usuario X
GET    /payments/balance/all             → Balance con todos
GET    /payments/history                → Historial de pagos
PUT    /payments/{id}/confirm           → Confirmar pago
```

### Reports (4)
```
GET    /reports/monthly/{year}/{month}         → Reporte del mes
GET    /reports/category/{id}                  → Por categoría
GET    /reports/monthly-comparison             → Comparación meses
GET    /reports/statistics                     → Stats globales
```

### Cards (5)
```
POST   /cards                  → Crear tarjeta
GET    /cards                  → Mis tarjetas
GET    /cards/{id}             → Detalles tarjeta
PUT    /cards/{id}             → Actualizar
DELETE /cards/{id}             → Eliminar
```

### Categories (5)
```
POST   /categories             → Crear categoría
GET    /categories             → Mis categorías
GET    /categories/{id}        → Detalles
PUT    /categories/{id}        → Actualizar
DELETE /categories/{id}        → Eliminar
```

---

## 🎨 FRONTEND (6 PÁGINAS)

### LoginPage
- Email + Password
- Alternador Sign in / Sign up
- Datos guardados en Zustand (localStorage)

### DashboardPage
- Stats: Total gastado, cantidad de gastos, tarjetas, cuotas
- Lista de gastos recientes
- Deudas pendientes
- Diseño 2 columnas en desktop

### ExpensesPage
- Formulario para crear gasto (desplegable)
- Soporta múltiples participantes
- Checkbox para cuotas (especificar cantidad)
- Lista de todos los gastos
- Filtrable por tarjeta/categoría (futuro)

### PaymentsPage
- Tabs: "You owe" / "Owed to you"
- Botón "Record payment"
- Formulario: to_user_id, amount, description
- Listas por usuario

### ReportsPage
- Selector mes/año
- Stats del período
- Tabla de gastos por categoría con barras
- Tabla de gastos por tarjeta
- Comparativa de meses

### SettingsPage
- Tabs: Cards / Categories
- CRUD para tarjetas (crear, eliminar)
- CRUD para categorías (crear con color picker)
- Gestión visual e intuitiva

---

## 🗺️ ÁRBOL DE CARPETAS

```
BACKEND:
gastos-app/
├── app/
│   ├── __init__.py
│   ├── main.py                 ← FastAPI app
│   ├── config.py               ← Settings
│   ├── database.py             ← SQLAlchemy setup
│   ├── security.py             ← JWT + bcrypt
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── card.py
│   │   ├── category.py
│   │   ├── expense.py
│   │   ├── expense_participant.py
│   │   ├── installment.py
│   │   ├── installment_split.py
│   │   └── payment.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── expense.py
│   │   └── reports.py
│   │
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       ├── expenses.py
│       ├── installments.py
│       ├── payments.py
│       ├── reports.py
│       └── card_category.py
│
├── init_db.py                  ← Setup inicial
├── test_api.py                 ← Testing
├── requirements.txt            ← Dependencias
├── .env                        ← Config local
├── docker-compose.yml          ← PostgreSQL en Docker
└── Dockerfile                  ← Para producción

FRONTEND:
tally-frontend/
├── src/
│   ├── pages/
│   │   ├── LoginPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── ExpensesPage.jsx
│   │   ├── PaymentsPage.jsx
│   │   ├── ReportsPage.jsx
│   │   └── SettingsPage.jsx
│   │
│   ├── components/
│   │   └── Layout.jsx
│   │
│   ├── store/
│   │   └── auth.js             ← Zustand stores
│   │
│   ├── api/
│   │   └── client.js           ← Axios client
│   │
│   ├── App.jsx                 ← Router
│   ├── main.jsx                ← Entry point
│   └── index.css               ← Tailwind
│
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── .env.local
```

---

## 🚀 STACK TECNOLÓGICO

### Backend
- **Framework:** FastAPI 0.104.1
- **Web Server:** Uvicorn 0.24.0
- **ORM:** SQLAlchemy 2.0.23
- **DB Driver:** psycopg2-binary (PostgreSQL)
- **Auth:** JWT + passlib + bcrypt
- **Validation:** Pydantic 2.5.0
- **Migration:** Alembic 1.12.1

### Frontend
- **Framework:** React 18
- **Routing:** React Router v6
- **Styling:** Tailwind CSS 3.3
- **Build:** Vite 5.0
- **State:** Zustand 4.4
- **Animation:** Framer Motion 10.16
- **HTTP:** Axios 1.6
- **Dates:** date-fns 2.30

### Database
- **Type:** PostgreSQL 15 (relational)
- **Container:** Docker
- **Normalization:** 3NF (8 tables)
- **Migrations:** Alembic ready

### DevOps
- **Containerization:** Docker
- **Reverse Proxy:** Nginx
- **SSL:** Let's Encrypt ready
- **CI/CD:** GitHub Actions ready

---

## 📈 USUARIOS Y DATOS DE PRUEBA

### Usuarios creados por init_db.py

```
1. Juan
   - Email: juan@example.com
   - Password: password123
   - Role: Regular user
   - Created: Al ejecutar init_db.py

2. María
   - Email: maria@example.com
   - Password: password123
   - Role: Regular user
   - Created: Al ejecutar init_db.py

3. Carlos
   - Email: carlos@example.com
   - Password: password123
   - Role: Regular user
   - Created: Al ejecutar init_db.py
```

### Datos iniciales

```
Tarjetas por usuario: 1-2 cada uno
Categorías: Comidas, Transporte, Entretenimiento
Gastos: ~10 gastos compartidos de ejemplo
Cuotas: Algunos con 3-5 cuotas
Deudas: Estado inicial con múltiples deudas
```

---

## 🔄 MIGRACIONES A LA NUBE

### Si quisieras migrar PostgreSQL a la nube:

#### Opción 1: AWS RDS
```
1. Crear RDS instance (PostgreSQL 15)
2. Obtener endpoint: gastos-db.xxxxx.rds.amazonaws.com
3. Cambiar DATABASE_URL en .env:
   DATABASE_URL=postgresql://user:password@gastos-db.xxxxx.rds.amazonaws.com:5432/gastos_db
4. Ejecutar alembic upgrade head (si hay migrations)
5. Backend apunta a RDS automáticamente
```

#### Opción 2: DigitalOcean Managed Database
```
1. Crear managed database PostgreSQL
2. Obtener connection string
3. Cambiar DATABASE_URL
4. Mismo proceso que arriba
```

#### Opción 3: Heroku PostgreSQL
```
1. Heroku crea automáticamente BD con DATABASE_URL
2. No necesitas hacer nada - funciona directo
3. git push heroku main → Automático
```

### Lo que NO cambia:
- Código backend (usa SQLAlchemy ORM)
- Código frontend
- Estructura de tablas
- Endpoints

### Lo que SÍ necesita cambio:
- `DATABASE_URL` en .env
- Credenciales (user/password)
- Posiblemente SSL si lo requiere la nube

---

## 🎯 CARACTERÍSTICAS PRINCIPALES

### ✅ Implementado
- Autenticación JWT
- Gastos compartidos con múltiples participantes
- Cuotas automáticas (1-60 cuotas)
- Cálculo automático de deudas
- Sistema de pagos
- Reportes por período
- CRUD de tarjetas
- CRUD de categorías
- Diseño responsive
- Testing suite

### ⏳ TODO (Futuro)
- Notificaciones por email
- Cambio de contraseña
- Reset de contraseña
- Búsqueda de gastos
- Filtros avanzados
- Gráficos más complejos
- Exportar a Excel/PDF
- Modo oscuro
- Internacionalización

---

## 💾 BACKUP Y DATOS

### Información crítica a preservar
```
✓ Base de datos completa (PostgreSQL)
✓ Código frontend (Git)
✓ Código backend (Git)
✓ .env con variables sensibles (NO en Git)
✓ SECRET_KEY (cambiar en producción)
```

### Cómo hacer backup
```
# Backup de BD local
pg_dump -U gastos_user -h localhost gastos_db > backup.sql

# Restore de BD
psql -U gastos_user -h localhost gastos_db < backup.sql

# En RDS
pg_dump postgresql://user:pass@rds-endpoint:5432/db > backup.sql
```

---

## 🔍 CÓMO LEER ESTE DOCUMENTO

**Si necesitas:**

1. **Cambiar algo de BD** → Ver "MODELO DE DATOS"
2. **Agregar endpoint** → Ver "ENDPOINTS" + "FLUJOS"
3. **Migrar a nube** → Ver "MIGRACIONES A LA NUBE"
4. **Entender deudas** → Ver "Flujo 3: Ver Deudas"
5. **Escalabilidad** → Ver "STACK TECNOLÓGICO"
6. **Pasar contexto a dev** → Envía este archivo

---

## ✉️ CONTEXTO PARA COMUNICACIÓN

**Siempre que hables con otro dev, menciona:**

```
"Tengo una app Tally con:
- Backend FastAPI (27 endpoints, 8 modelos)
- Frontend React (6 páginas)
- BD PostgreSQL (relacional, 3NF)
- Stack: Python/FastAPI + React/Tailwind
- JWT auth + bcrypt
- Cuotas automáticas
- Cálculo de deudas
- 40 archivos documentados"
```

---

## 📞 REFERENCIAS PARA CAMBIOS

### Para migración de BD
- Ver sección "MIGRACIONES A LA NUBE"
- SQLAlchemy docs: https://docs.sqlalchemy.org
- Alembic docs: https://alembic.sqlalchemy.org

### Para agregar features
- Modelos: Ver "MODELO DE DATOS"
- Endpoints: Copiar patrón en app/routes/
- Frontend: Copiar patrón de DashboardPage.jsx

### Para scaling
- Database: RDS, DigitalOcean, Heroku
- Backend: Docker, Kubernetes
- Frontend: Vercel, Netlify, Cloudflare
- Cache: Redis para balance calculations

---

**Este documento es tu referencia única y completa para entender TODO sobre Tally.**

**Comparte este archivo cuando hables con otros devs, arquitectos o cuando migres a otro proveedor.**

**Creado:** [HOY]
**Stack:** Python/FastAPI + React/Tailwind + PostgreSQL
**Status:** ✅ Producción Ready
