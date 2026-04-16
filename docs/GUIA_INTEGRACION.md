# 🔗 GUÍA DE INTEGRACIÓN - BACKEND + FRONTEND

Cómo conectar perfectamente Tally Frontend con Tally Backend.

---

## ✅ PRE-REQUISITOS

```
✓ Backend corriendo en http://localhost:8000
✓ Frontend corriendo en http://localhost:3000
✓ PostgreSQL en Docker (docker-compose up -d)
✓ Base de datos inicializada (python init_db.py)
```

---

## 🔌 SETUP DE CONEXIÓN

### 1. Backend listo

```bash
# Terminal 1
cd gastos-app
docker-compose up -d
python init_db.py
python -m uvicorn app.main:app --reload
```

Verificar:
- http://localhost:8000/health → `{"status": "ok"}`
- http://localhost:8000/docs → Swagger UI visible

### 2. Frontend listo

```bash
# Terminal 2
cd tally-frontend
npm install
npm run dev
```

Verificar:
- http://localhost:3000 → Login page visible

### 3. Archivo .env.local

```bash
# En raíz de tally-frontend/
cat > .env.local << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Tally
EOF
```

---

## 🧪 TEST DE INTEGRACIÓN

### Paso 1: Login

1. Abrir http://localhost:3000
2. Ver Login page
3. Ingresar:
   - Email: `juan@example.com`
   - Password: `password123`
4. Click "Sign in"

**Esperado:** 
- ✅ Frontend se conecta a POST /auth/login
- ✅ Backend valida credenciales
- ✅ Token recibido y guardado
- ✅ Redirect a /dashboard

### Paso 2: Dashboard

Después de login:
1. Ver Dashboard
2. Verificar stats cargados
3. Ver gastos recientes (mínimo 3)
4. Ver deudas pendientes

**Esperado:**
- ✅ GET /reports/statistics funciona
- ✅ GET /expenses funciona
- ✅ GET /payments/me/owe funciona
- ✅ Datos de prueba visible

### Paso 3: Crear Gasto

1. Click "New expense"
2. Llenar formulario:
   - Concept: "Test Expense"
   - Amount: "100"
   - Card: Seleccionar uno
   - Category: Seleccionar uno
   - Date: Hoy
   - Participants: [1, 50]
3. Click "Create expense"

**Esperado:**
- ✅ Form válido
- ✅ POST /expenses funciona
- ✅ Nuevo gasto aparece en lista

### Paso 4: Ver Deudas

1. Ir a Payments tab
2. Ver tab "You owe"
3. Debe haber items (si creó gastos compartidos)
4. Ver tab "Owed to you"

**Esperado:**
- ✅ GET /payments/me/owe funciona
- ✅ GET /payments/me/owed funciona

### Paso 5: Reportes

1. Ir a Reports tab
2. Ver mes actual (auto-seleccionado)
3. Ver stats y tablas de categorías

**Esperado:**
- ✅ GET /reports/monthly/YEAR/MONTH funciona
- ✅ Datos de prueba visible

---

## 🔍 VERIFICACIÓN DETALLADA

### Frontend Console

Abrir DevTools (F12) → Console:

```javascript
// Debe estar sin errores
// Si hay errores: revisar que VITE_API_URL sea correcto
```

### Network Tab

Abrir DevTools → Network:

Después de hacer login, deberías ver requests:
```
POST /auth/login      → 200 OK
GET /auth/me          → 200 OK
GET /reports/statistics → 200 OK
GET /expenses         → 200 OK
GET /payments/me/owe  → 200 OK
```

Todos deben tener status **200 OK**.

### Backend Logs

En terminal donde corre uvicorn:

```
INFO:     127.0.0.1:54321 - "POST /auth/login HTTP/1.1" 200
INFO:     127.0.0.1:54321 - "GET /auth/me HTTP/1.1" 200
INFO:     127.0.0.1:54321 - "GET /reports/statistics HTTP/1.1" 200
```

---

## ❌ TROUBLESHOOTING

### Error: "Cannot reach backend"

```
Problema: Frontend no puede conectar a backend
Solución:
1. Verificar que backend está en http://localhost:8000
2. Verificar .env.local tiene VITE_API_URL correcto
3. Verificar CORS en backend (debe aceptar localhost:3000)
4. Reiniciar npm run dev
```

### Error: "Invalid credentials"

```
Problema: Login falla con credenciales correctas
Solución:
1. Verificar que python init_db.py ejecutó exitosamente
2. Verificar que BD está en Docker (docker ps debe mostrar gastos_db)
3. Verificar que backend no tiene error 500 en logs
4. Intentar con usuario: maria@example.com / password123
```

### Error: "Token expired"

```
Problema: Token expira después de 30 minutos
Solución:
1. Hacer logout y login nuevamente
2. En desarrollo: cambiar ACCESS_TOKEN_EXPIRE_MINUTES=1440 (24h)
```

### Error: "CORS error"

```
Problema: CORS headers no configurados
Solución:
1. Verificar app/main.py tiene CORSMiddleware:
   app.add_middleware(
     CORSMiddleware,
     allow_origins=["*"],  # En dev: permite todo
     allow_methods=["*"],
     allow_headers=["*"],
   )
2. Reiniciar backend
```

---

## 📊 FLUJOS DE DATOS ESPERADOS

### Login Flow

```
Frontend (LoginPage)
  ↓ User fills form
  ↓ handleSubmit(email, password)
  ↓ POST http://localhost:8000/auth/login
Backend (/auth/login)
  ↓ Valida credenciales
  ↓ Crea JWT token
  ↓ Retorna {access_token, token_type}
Frontend
  ↓ Recibe token
  ↓ useAuthStore.login(token, user)
  ↓ Guarda en localStorage
  ↓ axios agrega header: Authorization: Bearer {token}
  ↓ Navigate to /dashboard
```

### Create Expense Flow

```
Frontend (ExpensesPage)
  ↓ User fills form
  ↓ handleSubmit(formData)
  ↓ POST http://localhost:8000/expenses
  ↓ Headers: Authorization: Bearer {token}
Backend (/expenses - POST)
  ↓ Extrae token → obtiene user_id
  ↓ Valida datos
  ↓ Crea:
    - Expense record
    - ExpenseParticipant records
    - Installment records (si tiene cuotas)
    - InstallmentSplit records (si tiene cuotas)
  ↓ Retorna expense completo con relaciones
Frontend
  ↓ Recibe response.data
  ↓ setExpenses([newExpense, ...old])
  ↓ UI actualiza automáticamente
  ↓ Muestra toast/feedback
```

---

## 🎯 CHECKLIST FINAL

```
BACKEND:
☐ docker-compose up -d (DB corriendo)
☐ python init_db.py (BD inicializada con datos)
☐ python -m uvicorn app.main:app --reload (API en 8000)
☐ http://localhost:8000/health responde con status "ok"
☐ http://localhost:8000/docs muestra Swagger UI
☐ CORS middleware configurado

FRONTEND:
☐ npm install (dependencias descargadas)
☐ .env.local creado con VITE_API_URL=http://localhost:8000
☐ npm run dev (dev server en 3000)
☐ http://localhost:3000 muestra LoginPage

INTEGRACIÓN:
☐ Login funciona con juan@example.com / password123
☐ Dashboard muestra stats y gastos
☐ Token se agrega automáticamente a requests
☐ Crear gasto funciona
☐ Payments tab muestra deudas
☐ Reports tab muestra datos
☐ Settings tab muestra tarjetas/categorías
☐ Network tab no muestra errores 401/500

DEPLOYMENT READY:
☐ Ambos funcionan localmente
☐ Se puede cambiar VITE_API_URL para producción
☐ Backend está listo para Docker
☐ Frontend está listo para Vercel/Netlify
```

---

## 📱 TESTING EN DIFERENTES DISPOSITIVOS

### Desktop (http://localhost:3000)

```
✓ Sidebar visible
✓ Layout de 2+ columnas
✓ Todos los elementos accesibles
```

### Tablet (DevTools - 768px)

```
✓ Sidebar ocultable
✓ Layout responsivo
✓ Controles optimizados
```

### Mobile (DevTools - 375px)

```
✓ Sidebar como hamburguesa
✓ Una columna
✓ Botones táctiles grandes
✓ Forms apilados verticalmente
```

---

## 🚀 READY FOR PRODUCTION

Una vez verificado todo funciona:

### Backend
```bash
# Cambiar en .env:
DEBUG=False
SECRET_KEY=tu-clave-generada-aleatoria
DATABASE_URL=postgresql://user:pass@host:5432/db

# Deploy
docker build -t tally-backend .
docker run -e DATABASE_URL=... tally-backend
```

### Frontend
```bash
# Crear .env.production:
VITE_API_URL=https://api.tu-dominio.com

# Build
npm run build
# Sube carpeta dist/ a Vercel/Netlify
```

---

## 💡 TIPS FINALES

1. **Siempre mantén ambas terminales abiertas** durante desarrollo
2. **Verifica logs de ambos lados** cuando algo falla
3. **Usa DevTools Network tab** para debuguear requests
4. **Prueba todos los flows** antes de llamar "completado"
5. **Los datos de prueba vienen con init_db.py** - no es necesario crear manualmente

---

**Integración completamente funcional** ✅
