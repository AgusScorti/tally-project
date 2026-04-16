# 🚀 DEPLOYMENT A PRODUCCIÓN

Guía completa para desplegar Gastos App en producción.

---

## 📋 Checklist Pre-Producción

### 1. Seguridad

- [ ] Cambiar `SECRET_KEY` en .env (generar aleatoria de 32+ caracteres)
- [ ] Cambiar contraseña de BD PostgreSQL
- [ ] Cambiar `DEBUG=False`
- [ ] Configurar CORS con dominios específicos (no `*`)
- [ ] Usar HTTPS en producción
- [ ] Configurar HSTS headers
- [ ] Rate limiting en endpoints
- [ ] Validar todas las entradas

### 2. Base de Datos

- [ ] Usar PostgreSQL versión estable (15+)
- [ ] Configurar backups diarios
- [ ] Replicación (para alta disponibilidad)
- [ ] Monitoreo de performance
- [ ] Índices optimizados
- [ ] Vacuum y analyze programado

### 3. Rendimiento

- [ ] Redis para caché
- [ ] CDN para assets estáticos
- [ ] Compresión gzip
- [ ] Connection pooling
- [ ] Load balancing (si múltiples instancias)

### 4. Monitoreo & Logging

- [ ] Logs centralizados (ELK, Datadog, etc)
- [ ] Alertas para errores
- [ ] Métricas de performance
- [ ] Health checks
- [ ] Uptime monitoring

---

## 🔧 Opción 1: Desplegar en Heroku (Más Fácil)

### Paso 1: Preparar aplicación

```bash
# Crear Procfile
cat > Procfile << 'EOF'
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
EOF

# Crear runtime.txt
echo "python-3.11.0" > runtime.txt
```

### Paso 2: Crear app en Heroku

```bash
heroku login
heroku create gastos-app
```

### Paso 3: Configurar variables de entorno

```bash
# Generar SECRET_KEY seguro
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Configurar en Heroku
heroku config:set SECRET_KEY="tu-clave-generada"
heroku config:set DEBUG=False
heroku config:set ALGORITHM=HS256
heroku config:set ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Paso 4: Agregar PostgreSQL

```bash
# Heroku agregará DATABASE_URL automáticamente
heroku addons:create heroku-postgresql:standard-0
```

### Paso 5: Deploy

```bash
git push heroku main

# Ver logs
heroku logs --tail

# Ejecutar init_db.py
heroku run python init_db.py
```

### Paso 6: Verificar

```bash
heroku open
# Abrirá https://gastos-app.herokuapp.com
```

---

## 🐳 Opción 2: Desplegar con Docker (Recomendado)

### Paso 1: Crear Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Comando para iniciar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Paso 2: Crear docker-compose para producción

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  web:
    build: .
    container_name: gastos_web
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://gastos_user:${DB_PASSWORD}@db:5432/gastos_db
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    container_name: gastos_db
    environment:
      POSTGRES_USER: gastos_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: gastos_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U gastos_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    container_name: gastos_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
```

### Paso 3: Crear nginx.conf

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream web {
        server web:8000;
    }

    # Redirigir HTTP a HTTPS
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    # HTTPS
    server {
        listen 443 ssl http2;
        server_name tu-dominio.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Compression
        gzip on;
        gzip_types text/plain text/css text/json text/javascript application/json;
        gzip_min_length 1000;

        # Rate limiting
        limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

        location / {
            proxy_pass http://web;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://web;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### Paso 4: Deploy

```bash
# Generar certificados SSL (Let's Encrypt)
certbot certonly --standalone -d tu-dominio.com

# Copiar certificados a ./ssl/
cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem ./ssl/cert.pem
cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem ./ssl/key.pem

# Levantar producción
docker-compose -f docker-compose.prod.yml up -d

# Inicializar BD
docker-compose -f docker-compose.prod.yml exec web python init_db.py

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## ☁️ Opción 3: AWS (EC2 + RDS)

### Paso 1: Crear RDS PostgreSQL

```bash
# Via AWS Console o CLI
aws rds create-db-instance \
  --db-instance-identifier gastos-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username gastos_user \
  --master-user-password "tu-password-seguro" \
  --allocated-storage 20 \
  --publicly-accessible false
```

### Paso 2: Crear instancia EC2

```bash
# t2.micro (free tier)
# Ubuntu 22.04 LTS
```

### Paso 3: Instalar en EC2

```bash
# SSH a la instancia
ssh -i clave.pem ubuntu@tu-ip

# Actualizar
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clonar código
git clone https://github.com/tu-usuario/gastos-app.git
cd gastos-app

# Crear .env con RDS endpoint
cat > .env << 'EOF'
DATABASE_URL=postgresql://gastos_user:password@gastos-db.xxxx.rds.amazonaws.com:5432/gastos_db
SECRET_KEY=tu-clave-aleatoria
DEBUG=False
EOF

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔄 Configurar CI/CD con GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      run: pytest tests/ --cov=app

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: success()
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
        heroku_app_name: "gastos-app"
        heroku_email: ${{ secrets.HEROKU_EMAIL }}
```

---

## 📊 Monitoreo en Producción

### Agregar Logging Estructurado

```python
# app/logging_config.py
import logging
import json
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    return logger
```

### Health Checks

```python
# app/main.py
@app.get("/health")
def health():
    """Health check para load balancer"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}, 503
```

### Métricas con Prometheus

```python
# app/middleware.py
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter(
    'gastos_requests_total',
    'Total requests',
    ['method', 'endpoint']
)

request_duration = Histogram(
    'gastos_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    request_count.labels(
        method=request.method,
        endpoint=request.url.path
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response
```

---

## 🔐 Hardening de Seguridad

### 1. Secrets Management

```bash
# Usar AWS Secrets Manager o similar
# Nunca guardar secrets en código

# En producción:
SECRET_KEY=$(aws secretsmanager get-secret-value --secret-id gastos/SECRET_KEY --query SecretString --output text)
```

### 2. SQL Injection Prevention

```python
# ✅ CORRECTO - SQLAlchemy ORM protege
user = db.query(User).filter(User.email == email).first()

# ❌ INCORRECTO - Vulnerable
user = db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### 3. Password Requirements

```python
# app/security.py
def validate_password(password: str):
    if len(password) < 12:
        raise ValueError("Mínimo 12 caracteres")
    if not any(c.isupper() for c in password):
        raise ValueError("Debe contener mayúscula")
    if not any(c.isdigit() for c in password):
        raise ValueError("Debe contener número")
    if not any(c in "!@#$%^&*" for c in password):
        raise ValueError("Debe contener carácter especial")
```

### 4. Rate Limiting

```python
# app/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/auth/login")
@limiter.limit("5/minute")
def login(request: Request, ...):
    # Max 5 intentos por minuto
    pass
```

---

## 📈 Escalabilidad Futura

### 1. Caché con Redis

```python
# app/cache.py
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

def get_user_balance(user_id: int):
    # Intentar obtener del caché
    cached = cache.get(f"balance:{user_id}")
    if cached:
        return json.loads(cached)
    
    # Si no está, calcularlo
    balance = calculate_balance(user_id)
    
    # Guardar en caché por 5 minutos
    cache.setex(f"balance:{user_id}", 300, json.dumps(balance))
    
    return balance
```

### 2. Background Jobs con Celery

```python
# app/tasks.py
from celery import Celery

celery_app = Celery('gastos', broker='redis://localhost:6379')

@celery_app.task
def generate_monthly_report(user_id: int, year: int, month: int):
    """Generar reporte en background"""
    report = get_monthly_report(user_id, year, month)
    send_email(user_id, report)

# En un endpoint:
@app.post("/reports/email-monthly")
def email_monthly_report(user_id: int):
    generate_monthly_report.delay(user_id, year, month)
    return {"message": "Reporte será enviado por email"}
```

### 3. Database Replication

```yaml
# docker-compose para replicación
services:
  postgres-primary:
    image: postgres:15
    environment:
      POSTGRES_REPLICATION_MODE: master
      POSTGRES_REPLICATION_USER: replicator
      POSTGRES_REPLICATION_PASSWORD: password

  postgres-replica:
    image: postgres:15
    environment:
      POSTGRES_REPLICATION_MODE: slave
      POSTGRES_MASTER_SERVICE: postgres-primary
```

---

## 🧪 Testing en Producción

```bash
# Smoke test después de deploy
curl -f https://tu-dominio.com/health
curl -f https://tu-dominio.com/docs
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  https://tu-dominio.com/auth/login
```

---

## 📝 Maintenance

### Backups Diarios

```bash
# Script de backup
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -U gastos_user gastos_db > /backups/gastos_$TIMESTAMP.sql.gz
# Mantener últimos 30 días
find /backups -name "gastos_*.sql.gz" -mtime +30 -delete
```

### Updates

```bash
# Actualizar dependencias
pip list --outdated
pip install -U <package>

# Testear localmente
python -m pytest

# Deploy a staging primero
git commit -m "Update dependencies"
git push origin staging
# Esperar que CI/CD pase
git merge staging main
```

---

## ✅ Checklist Final de Deployment

```
SEGURIDAD:
☐ SECRET_KEY cambiado
☐ DEBUG=False
☐ CORS configurado
☐ SSL/HTTPS activo
☐ Rate limiting habilitado
☐ Passwords validados

BASE DE DATOS:
☐ PostgreSQL 15+
☐ Backups configurados
☐ Health checks pasando
☐ Índices optimizados

MONITOREO:
☐ Logging centralizado
☐ Alertas configuradas
☐ Métricas de performance
☐ Uptime monitoring

PERFORMANCE:
☐ Compression gzip
☐ Connection pooling
☐ Load balancing (si aplica)
☐ CDN para assets

DOCUMENTACIÓN:
☐ Runbook actualizado
☐ Contactos de emergencia
☐ Procedimiento de rollback
```

---

**¡Aplicación lista para producción! 🚀**
