# 🧾 Tally - Gestión de Gastos Compartidos

Sistema completo para trackear gastos compartidos entre personas, con soporte para cuotas automáticas y cálculo de deudas.

## Stack

- **Backend:** Python + FastAPI + PostgreSQL + JWT
- **Frontend:** React + Tailwind CSS + Zustand + Vite

## Estructura

```
tally-project/
├── backend/        ← FastAPI + PostgreSQL
├── frontend/       ← React + Tailwind
└── docs/           ← Documentación
```

## Setup rápido

### Backend
```bash
cd backend
docker-compose up -d          # PostgreSQL
pip install -r requirements.txt
python init_db.py             # Datos de prueba
python -m uvicorn app.main:app --reload
# → http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

## Login de prueba

```
Email:    juan@example.com
Password: password123
```

## Documentación

Ver carpeta `/docs` para guías completas.
