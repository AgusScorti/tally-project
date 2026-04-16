# 🎨 TALLY FRONTEND - GUÍA DE SETUP

Frontend moderno, minimalista y responsive para Tally.

---

## 📋 Stack Tecnológico

```
Frontend Framework: React 18
Styling: Tailwind CSS
State Management: Zustand
Animations: Framer Motion
Routing: React Router v6
HTTP Client: Axios
Build Tool: Vite
```

---

## 🚀 Setup Inicial

### 1. Crear proyecto

```bash
npm create vite@latest tally-frontend -- --template react
cd tally-frontend
npm install
```

### 2. Instalar dependencias

```bash
npm install react-router-dom axios zustand framer-motion date-fns
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 3. Copiar archivos

Copia todos los archivos `.jsx`, `.css`, `.js` desde esta entrega a sus ubicaciones correctas:

```
src/
├── App.jsx
├── main.jsx
├── index.css
├── api/
│   └── client.js
├── store/
│   └── auth.js (y otros stores)
├── components/
│   └── Layout.jsx
└── pages/
    ├── LoginPage.jsx
    ├── DashboardPage.jsx
    ├── ExpensesPage.jsx
    ├── PaymentsPage.jsx
    ├── ReportsPage.jsx
    └── SettingsPage.jsx
```

### 4. Configurar variables de entorno

Crea `.env.local`:

```
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Tally
```

### 5. Iniciar desarrollo

```bash
npm run dev
```

La app estará en `http://localhost:3000`

---

## 🎯 Estructura del Proyecto

```
tally-frontend/
├── src/
│   ├── api/                  # Cliente HTTP
│   ├── components/           # Componentes reutilizables
│   ├── pages/               # Páginas completas
│   ├── store/               # Zustand stores
│   ├── App.jsx              # Router principal
│   ├── main.jsx             # Entry point
│   └── index.css            # Tailwind + custom
│
├── public/                   # Assets estáticos
├── index.html               # HTML base
├── package.json
├── vite.config.js          # Config Vite
├── tailwind.config.js      # Paleta Tally
└── postcss.config.js       # PostCSS
```

---

## 🎨 Paleta de Colores Tally

Los colores están configurados en `tailwind.config.js`:

```
Verde Principal:     #22C55E (tally-500)
Verde Profundo:      #16A34A (tally-600)
Texto:               #1F2937 (tally-text)
Fondo Claro:         #F9FAFB (tally-light)
Acento:              #38BDF8 (tally-accent)
```

Uso en JSX:

```jsx
<div className="bg-tally-500 text-white">
  Verde de Tally
</div>

<button className="bg-tally-text hover:bg-tally-600">
  Button
</button>
```

---

## 📱 Responsive Design

La aplicación es completamente responsive:

**Breakpoints:**
- `sm`: 640px
- `md`: 768px (donde se muestra sidebar)
- `lg`: 1024px
- `xl`: 1280px

Ejemplo:

```jsx
<div className="hidden md:flex">
  Sidebar (solo visible en desktop)
</div>

<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
  Responsive grid
</div>
```

---

## 🔌 Conexión con Backend

El backend corre en `http://localhost:8000`

En desarrollo, Vite redirige las requests:

```javascript
// Automático - no necesitas cambiar nada
const response = await api.get('/expenses')
// Se conecta a http://localhost:8000/expenses
```

En producción, actualiza `VITE_API_URL` en `.env.production`:

```
VITE_API_URL=https://tu-dominio.com/api
```

---

## 📄 Páginas Implementadas

### 1. LoginPage
- Formulario limpio de login/registro
- Sin iconos innecesarios
- Transiciones suaves

### 2. DashboardPage
- Stats principales
- Gastos recientes
- Deudas pendientes
- Diseño de dos columnas

### 3. ExpensesPage
- Listar gastos
- Crear nuevo gasto (con form desplegable)
- Soporte para cuotas
- Participantes múltiples

### 4. PaymentsPage (por implementar)
- Deudas personales
- Créditos
- Balance con otros usuarios
- Registrar pagos

### 5. ReportsPage (por implementar)
- Reporte mensual
- Gastos por categoría
- Análisis temporal

### 6. SettingsPage (por implementar)
- Gestión de tarjetas
- Categorías personalizadas
- Perfil de usuario

---

## 🎬 Animaciones

Se usan Framer Motion para transiciones suaves:

```jsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  Contenido animado
</motion.div>
```

**Características:**
- Fade-in al cargar páginas
- Hover effects en botones
- Stagger animations en listas
- Smooth transitions entre estados

---

## 🧹 Estilo y Convenciones

### Sin iconos "de IA"
```jsx
// ❌ NO HAGAS ESTO:
<button>
  <ArrowRight /> Crear gasto
</button>

// ✅ HACES ESTO:
<button>
  Create expense
</button>
```

### Botones minimalistas
```jsx
// Verde para acciones primarias
<button className="bg-tally-500">Crear</button>

// Gris para acciones secundarias
<button className="bg-tally-border">Cancelar</button>
```

### Espaciado consistente
```jsx
// Siempre usar escala de Tailwind
p-4, p-6, p-8 (padding)
gap-3, gap-4, gap-6 (espaciado entre items)
```

---

## 🚀 Build para Producción

```bash
npm run build
```

Genera carpeta `dist/` lista para servir.

```bash
npm run preview
```

Previsualiza la versión optimizada localmente.

---

## 🔍 Debugging

### Ver requests al backend
```javascript
// En src/api/client.js
client.interceptors.request.use((config) => {
  console.log('Request:', config.url, config.data);
  return config;
});
```

### Zustand DevTools
```bash
npm install zustand-devtools
```

```javascript
import { devtools } from 'zustand/middleware';

export const useAuthStore = create(
  devtools((set) => ({...}))
);
```

---

## 📦 Deployment

### En Vercel
```bash
npm install -g vercel
vercel
```

### En Netlify
```bash
npm run build
# Deja que Netlify lea dist/
```

### En tu servidor
```bash
npm run build
# Sirve la carpeta dist/ con tu servidor web (Nginx, Apache, etc)
```

---

## 🎨 Personalización

### Cambiar colores
Edita `tailwind.config.js` en la sección `tally`:

```javascript
colors: {
  tally: {
    500: '#22C55E', // Cambiar aquí
    600: '#16A34A',
    // ...
  }
}
```

### Cambiar tipografía
```javascript
fontFamily: {
  sans: ['Tu Font', 'sans-serif'],
  display: ['Otra Font', 'sans-serif'],
}
```

### Agregar más páginas
```javascript
// 1. Crear archivo en src/pages/
// 2. Agregar route en src/App.jsx
// 3. Agregar nav item en src/components/Layout.jsx
```

---

## 🧪 Testing (Opcional)

Instala Vitest:

```bash
npm install -D vitest @testing-library/react
```

Crea archivos `.test.jsx` junto a los componentes.

---

## 📝 Notas de Desarrollo

- El layout usa sidebar en desktop, menu hamburguesa en mobile
- Todos los inputs usan la clase `.input-base` de Tailwind
- Las animaciones son suaves (200-300ms)
- El tema respeta la paleta: nunca mezclar colores
- Los botones NO llevan iconos, solo texto
- Los hover states son sutiles (cambio de color/fondo)

---

## ✅ Checklist de Setup

```
Frontend:
☐ npm install
☐ Copiar todos los archivos .jsx, .js, .css
☐ Configurar .env.local
☐ npm run dev funciona
☐ Login/Dashboard accesibles

Backend:
☐ python -m uvicorn app.main:app --reload
☐ http://localhost:8000/docs accesible
☐ CORS configurado

Testing:
☐ Login con credenciales de prueba
☐ Ver dashboard
☐ Crear gasto
☐ Listar gastos
```

---

## 🎉 ¡Listo!

Tu frontend Tally está listo para desarrollar. 

**Próximos pasos:**
1. Implementar páginas restantes (PaymentsPage, ReportsPage, etc)
2. Agregar validaciones de formularios
3. Mejorar manejo de errores
4. Agregar notificaciones (toast)
5. Polir UI con animaciones

---

**Creado con ❤️ - Minimalista, moderno, sin "AI slop"**
