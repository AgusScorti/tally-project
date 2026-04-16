# 🚀 SETUP DESDE CERO - PASO A PASO

**Guía para cuando NO tienes NADA descargado aún**

---

## 📋 PREREQUISITOS

Antes de empezar, verifica que tengas:

```
✓ Python 3.9+ instalado
✓ Node.js + npm instalado
✓ Docker instalado
✓ Git instalado (opcional pero recomendado)
✓ Un editor de código (VS Code, PyCharm, etc)
```

### Verificar que tienes todo:

```bash
python --version         # Debe ser 3.9+
node --version           # Debe ser 14+
npm --version            # Debe estar instalado
docker --version         # Debe estar instalado
git --version            # Opcional
```

---

## ⬇️ PASO 1: DESCARGAR TODOS LOS ARCHIVOS

### Opción A: Descargar como ZIP (MÁS FÁCIL)

```
1. Busca el BOTÓN ⬇️ en la esquina superior derecha de esta interfaz
2. Hazi click → "Download all"
3. Se descargará: tally-proyecto.zip (o similar)
4. Guárdalo en tu computadora (Descargas, Desktop, etc)
5. Extrae el ZIP
6. ¡Ya tienes todos los archivos!
```

### Opción B: Descargar manualmente

```
1. Ve a /mnt/user-data/outputs/ en la interfaz
2. Busca estos archivos PRIMERO:
   - 00_BIENVENIDA_FINAL.txt
   - README_PROYECTO_COMPLETO.md
   - gastos-app-QUICKSTART.md
   - CONTEXTO_COMPLETO_TALLY.md
3. Descargalos
4. Luego descarga TODOS los demás
```

---

## 📁 PASO 2: CREAR ESTRUCTURA DE CARPETAS

### Después de descargar, crea esto en tu computadora:

```bash
# Abre terminal/cmd en donde quieras el proyecto

# Crear carpeta principal
mkdir tally-proyecto
cd tally-proyecto

# Crear subcarpetas para backend y frontend
mkdir gastos-app
mkdir tally-frontend
```

**Resultado:**
```
tally-proyecto/
├── gastos-app/        ← Backend (aún vacío)
├── tally-frontend/    ← Frontend (aún vacío)
└── (archivos .md que descargaste)
```

---

## 🔧 PASO 3: COPIAR ARCHIVOS DEL BACKEND

Los archivos backend descargados tienen prefijo **`gastos-app-`** o son archivos **.py**

### 3.1: Copiar archivos de documentación

```bash
# Ya están en tally-proyecto/
# Simplemente déjalos ahí:
- gastos-app-README.md
- gastos-app-QUICKSTART.md
- gastos-app-ARQUITECTURA.md
- gastos-app-DEPLOYMENT.md
- gastos-app-TESTING.md
- gastos-app-requirements.txt
```

### 3.2: Copiar archivos Python al backend

Dentro de `gastos-app/`:

```bash
cd gastos-app

# Crear estructura de carpetas
mkdir app
mkdir app/models
mkdir app/schemas
mkdir app/routes

# Copiar archivos principales a app/
# De los descargados, busca archivos .py y cópialos a:
app/
├── __init__.py                    (crear vacío)
├── main.py                        (de descargas)
├── config.py                      (de descargas)
├── database.py                    (de descargas)
├── security.py                    (de descargas)
│
├── models/
│   ├── __init__.py                (crear vacío)
│   ├── user.py                    (de descargas)
│   ├── card.py                    (de descargas)
│   ├── category.py                (de descargas)
│   ├── expense.py                 (de descargas)
│   ├── expense_participant.py     (de descargas)
│   ├── installment.py             (de descargas)
│   ├── installment_split.py       (de descargas)
│   └── payment.py                 (de descargas)
│
├── schemas/
│   ├── __init__.py                (crear vacío)
│   ├── auth.py                    (de descargas)
│   ├── expense.py                 (de descargas)
│   └── reports.py                 (de descargas)
│
└── routes/
    ├── __init__.py                (crear vacío)
    ├── auth.py                    (de descargas)
    ├── expenses.py                (de descargas)
    ├── installments.py            (de descargas)
    ├── payments.py                (de descargas)
    ├── reports.py                 (de descargas)
    └── card_category.py           (de descargas)

# Copiar scripts y config a raíz de gastos-app/
├── init_db.py                     (de descargas)
├── test_api.py                    (de descargas)
├── requirements.txt               (de descargas)
├── .env                           (crear desde .env.example)
├── docker-compose.yml             (de descargas)
├── Dockerfile                     (de descargas)
└── .gitignore                     (de descargas)
```

### 3.3: Crear archivos vacíos faltantes

```bash
# En gastos-app/app/
touch __init__.py

# En gastos-app/app/models/
touch __init__.py

# En gastos-app/app/schemas/
touch __init__.py

# En gastos-app/app/routes/
touch __init__.py
```

### 3.4: Crear .env desde template

```bash
# En gastos-app/
# Si descargaste gastos-app-.env.example, cópialo como .env

cp gastos-app-.env.example .env

# O créalo manualmente con este contenido:
cat > .env << 'EOF'
DATABASE_URL=postgresql://gastos_user:gastos_password@localhost:5432/gastos_db
SECRET_KEY=tu-clave-secreta-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=Gastos App
DEBUG=True
TIMEZONE=America/Argentina/Buenos_Aires
EOF
```

---

## 🎨 PASO 4: COPIAR ARCHIVOS DEL FRONTEND

Los archivos frontend tienen prefijo **`tally-`**

### 4.1: Copiar archivos de configuración

```bash
cd ../tally-frontend

# Copiar archivos a raíz:
- tally-package.json     → Renombrar a package.json
- tally-index.html       → Renombrar a index.html
- tally-vite.config.js   → Renombrar a vite.config.js
- tally-tailwind.config.js → Renombrar a tailwind.config.js
- tally-postcss.config.js → Renombrar a postcss.config.js
- tally-.env.example     → Copiar como .env.local
- tally-.gitignore       → Copiar como .gitignore
```

### 4.2: Crear estructura de carpetas

```bash
# En tally-frontend/
mkdir -p src/pages
mkdir -p src/components
mkdir -p src/store
mkdir -p src/api
```

### 4.3: Copiar archivos de código

```
src/
├── pages/
│   ├── LoginPage.jsx                  (de descargas)
│   ├── DashboardPage.jsx              (de descargas)
│   ├── ExpensesPage.jsx               (de descargas)
│   ├── PaymentsPage.jsx               (de descargas)
│   ├── ReportsPage.jsx                (de descargas)
│   └── SettingsPage.jsx               (de descargas)
│
├── components/
│   └── Layout.jsx                     (de descargas)
│
├── store/
│   └── auth.js                        (de descargas: tally-src-store.js)
│
├── api/
│   └── client.js                      (de descargas: tally-src-api-client.js)
│
├── App.jsx                            (de descargas: tally-src-App.jsx)
├── main.jsx                           (de descargas: tally-src-main.jsx)
└── index.css                          (de descargas: tally-src-index.css)
```

### 4.4: Crear .env.local

```bash
# En tally-frontend/
cat > .env.local << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Tally
EOF
```

---

## ✅ ESTRUCTURA FINAL ESPERADA

```
tally-proyecto/
│
├── gastos-app/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── card.py
│   │   │   ├── category.py
│   │   │   ├── expense.py
│   │   │   ├── expense_participant.py
│   │   │   ├── installment.py
│   │   │   ├── installment_split.py
│   │   │   └── payment.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── expense.py
│   │   │   └── reports.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── expenses.py
│   │       ├── installments.py
│   │       ├── payments.py
│   │       ├── reports.py
│   │       └── card_category.py
│   ├── init_db.py
│   ├── test_api.py
│   ├── requirements.txt
│   ├── .env
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── .gitignore
│
├── tally-frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── ExpensesPage.jsx
│   │   │   ├── PaymentsPage.jsx
│   │   │   ├── ReportsPage.jsx
│   │   │   └── SettingsPage.jsx
│   │   ├── components/
│   │   │   └── Layout.jsx
│   │   ├── store/
│   │   │   └── auth.js
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .env.local
│   └── .gitignore
│
└── Documentación/
    ├── 00_BIENVENIDA_FINAL.txt
    ├── README_PROYECTO_COMPLETO.md
    ├── CONTEXTO_COMPLETO_TALLY.md
    ├── gastos-app-QUICKSTART.md
    ├── TALLY_FRONTEND_GUIDE.md
    └── ... (6 docs más)
```

---

## 🎯 AHORA SÍ: EJECUTAR LA APP

### Terminal 1 - Backend

```bash
cd tally-proyecto/gastos-app

# 1. Levantar PostgreSQL en Docker
docker-compose up -d

# 2. Verificar que PostgreSQL está corriendo
docker ps
# Deberías ver: gastos_db (estado: Up)

# 3. Instalar dependencias Python
pip install -r requirements.txt

# 4. Inicializar base de datos
python init_db.py
# Deberías ver: ✅ BD inicializada correctamente

# 5. Levantar servidor FastAPI
python -m uvicorn app.main:app --reload
# Deberías ver: 
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

✅ **Backend corriendo en http://localhost:8000**

### Terminal 2 - Frontend

```bash
cd tally-proyecto/tally-frontend

# 1. Instalar dependencias Node
npm install

# 2. Levantar dev server Vite
npm run dev
# Deberías ver:
# VITE v5.0.0 ready in 234 ms
# ➜  Local: http://localhost:5173/
```

✅ **Frontend corriendo en http://localhost:5173**

### Terminal 3 - Navegador

```bash
# Abre navegador y ve a:
http://localhost:5173

# Deberías ver: Login page
# Ingresa:
Email: juan@example.com
Password: password123

# Click "Sign in"
# ¡Deberías ver el Dashboard!
```

✅ **¡APP FUNCIONANDO!**

---

## 🔍 VERIFICACIÓN

### Backend funcionando:
```bash
# En terminal 1, deberías ver:
INFO:     127.0.0.1:54321 - "GET /health HTTP/1.1" 200

# O visita: http://localhost:8000/docs
# Deberías ver: Swagger UI con todos los endpoints
```

### Frontend funcionando:
```bash
# En terminal 2, deberías ver:
✓ 42 modules transformed
ready in 234 ms

# O visita: http://localhost:5173
# Deberías ver: Login page de Tally
```

### BD funcionando:
```bash
# En terminal 1 del bash:
docker ps
# Deberías ver: gastos_db en estado Up

docker logs gastos_db
# Deberías ver: Database system is ready to accept connections
```

---

## ⚠️ PROBLEMAS COMUNES

### "No encuentro la carpeta gastos-app"

```
Solución:
1. ¿Descargaste los archivos? (ZIP)
2. ¿Extrajiste el ZIP?
3. ¿Creaste la carpeta gastos-app?
4. ¿Copiaste los archivos .py en app/?

Si NO:
- Descarga primero el ZIP
- Extrae en tu computadora
- Créate la estructura de carpetas
```

### "Module not found: fastapi"

```
Solución:
1. Asegúrate que estás en carpeta gastos-app/
2. Ejecuta: pip install -r requirements.txt
3. Espera a que termine
4. Verifica: pip list | grep fastapi
```

### "Port 8000 already in use"

```
Solución 1: Cambiar puerto
python -m uvicorn app.main:app --port 8001

Solución 2: Matar proceso anterior
# En Windows:
netstat -ano | findstr :8000
taskkill /PID {PID} /F

# En Mac/Linux:
lsof -i :8000
kill -9 {PID}
```

### "Docker not found"

```
Solución:
1. Instala Docker desde: https://www.docker.com/products/docker-desktop
2. Reinicia tu computadora
3. Verifica: docker --version
```

---

## 📝 CHECKLIST FINAL

Antes de decir "¡LISTO!", verifica:

```
DESCARGAS:
☐ Descargué el ZIP desde la interfaz
☐ Extrajé el ZIP en mi computadora
☐ Veo carpeta: tally-proyecto/

BACKEND:
☐ Creé carpeta: gastos-app/app/models/
☐ Creé carpeta: gastos-app/app/schemas/
☐ Creé carpeta: gastos-app/app/routes/
☐ Copié todos los archivos .py
☐ Creé archivo .env en gastos-app/
☐ docker-compose up -d (PostgreSQL corriendo)
☐ pip install -r requirements.txt (dependencias)
☐ python init_db.py (BD inicializada)
☐ python -m uvicorn app.main:app --reload (servidor corriendo)
☐ http://localhost:8000/docs muestra Swagger UI

FRONTEND:
☐ Creé carpeta: tally-frontend/src/pages/
☐ Creé carpeta: tally-frontend/src/components/
☐ Creé carpeta: tally-frontend/src/store/
☐ Creé carpeta: tally-frontend/src/api/
☐ Copié todos los archivos .jsx y .js
☐ Creé archivo .env.local en tally-frontend/
☐ Copié package.json correctamente
☐ npm install (dependencias)
☐ npm run dev (dev server corriendo)
☐ http://localhost:5173 muestra Login page

INTEGRACIÓN:
☐ Frontend conecta a backend (login funciona)
☐ juan@example.com / password123 funciona
☐ Dashboard muestra datos
☐ Crear gasto funciona
☐ Ver deudas funciona

¡LISTO! ✅
```

---

## 🎉 ¡COMPLETADO!

Si llegaste acá y verificaste todo:

```
✅ Backend corriendo en http://localhost:8000
✅ Frontend corriendo en http://localhost:5173
✅ BD PostgreSQL en Docker
✅ Datos de prueba cargados
✅ Login funciona
✅ Dashboard visible
✅ Integración completa

¡TU APP TALLY FUNCIONA! 🚀
```

---

## 📞 SI ALGO NO FUNCIONA

Mira en este orden:

1. **SETUP_DESDE_CERO.md** (este archivo) → PROBLEMAS COMUNES
2. **gastos-app-QUICKSTART.md** → Para backend específicamente
3. **TALLY_FRONTEND_GUIDE.md** → Para frontend específicamente
4. **CONTEXTO_COMPLETO_TALLY.md** → Para entender arquitectura
5. **Terminal logs** → Mira qué dice el error exacto

---

**¡Ya puedes ejecutar tu app desde cero!** 🎊

Descarga → Organiza → Ejecuta → ¡Funciona!
