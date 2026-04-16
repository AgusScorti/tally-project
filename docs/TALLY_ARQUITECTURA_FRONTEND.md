# 🏗️ ARQUITECTURA FRONTEND TALLY

Explicación de cómo está construido el frontend y cómo escalarlo.

---

## 📊 DIAGRAMA DE FLUJO

```
User Browser
     ↓
React Router
     ↓
Pages (5 componentes)
     ├─ LoginPage
     ├─ DashboardPage
     ├─ ExpensesPage
     ├─ PaymentsPage
     ├─ ReportsPage
     └─ SettingsPage
     ↓
Components (Shared)
     ├─ Layout
     └─ (más en el futuro)
     ↓
Zustand Store
     ├─ auth (token, user)
     ├─ expenses (lista)
     └─ payments (deudas)
     ↓
Axios Client
     ↓
FastAPI Backend
     ↓
PostgreSQL
```

---

## 🎯 ESTRUCTURA DE CARPETAS

```
src/
├── api/
│   └── client.js              Instancia de Axios con interceptores
│
├── components/
│   ├── Layout.jsx             Sidebar + navegación
│   └── (agregar más aquí)
│
├── pages/
│   ├── LoginPage.jsx          Sin Layout, solo formulario
│   ├── DashboardPage.jsx      Dashboard principal
│   ├── ExpensesPage.jsx       Crear y listar gastos
│   ├── PaymentsPage.jsx       Gestionar pagos y deudas
│   ├── ReportsPage.jsx        Análisis y reportes
│   └── SettingsPage.jsx       Tarjetas y categorías
│
├── store/
│   └── auth.js                Zustand stores (auth, expenses, payments)
│
├── App.jsx                    Router principal
├── main.jsx                   Entry point
└── index.css                  Tailwind + custom CSS
```

---

## 🔄 FLUJO DE DATOS

### 1. Authentication Flow

```
LoginPage
  ↓
POST /auth/login (email, password)
  ↓
Backend valida + devuelve JWT
  ↓
useAuthStore.login(token, user)
  ↓
Token guardado en localStorage (Zustand persist)
  ↓
Redirect a /dashboard
  ↓
axios client agrega token automáticamente a todos los requests
```

### 2. Crear Gasto Flow

```
ExpensesPage
  ↓
Usuario rellena formulario
  ↓
handleSubmit → POST /expenses
  ↓
Backend crea gasto + participantes + cuotas
  ↓
Frontend: setExpenses([newExpense, ...oldExpenses])
  ↓
UI actualiza automáticamente
```

### 3. Auth Interceptor

```
Cualquier request
  ↓
Axios interceptor.request
  ↓
Agrega: Authorization: Bearer {token}
  ↓
Envía request
  ↓
Si 401: Zustand logout() + redirect /login
```

---

## 🧠 STATE MANAGEMENT (Zustand)

### AuthStore
```javascript
{
  token: string | null,
  user: { id, email, username, ... } | null,
  login: (token, user) => void,
  logout: () => void,
  setUser: (user) => void
}
```

**Persist:** Guardado en localStorage con key "tally-auth"

### ExpensesStore
```javascript
{
  expenses: [],
  loading: false,
  error: null,
  setExpenses: (expenses) => void,
  addExpense: (expense) => void,
  setLoading: (loading) => void
}
```

### PaymentsStore
```javascript
{
  debts: [],
  credits: [],
  balances: {},
  loading: false,
  setDebts: (debts) => void,
  setCredits: (credits) => void,
  ...
}
```

---

## 🎨 COMPONENTES Y PÁGINAS

### LoginPage (Sin Layout)
- Muestra solo formulario
- No tiene sidebar
- Accesible sin autenticación
- Transición a Dashboard después de login

### DashboardPage (Con Layout)
- Header: "Dashboard" + descripción
- Stats: 4 tarjetas (total, expenses, cards, cuotas)
- Dos columnas:
  - Izquierda: Gastos recientes (3 columnas en desktop)
  - Derecha: Deudas (1 columna)
- Animaciones staggered

### ExpensesPage (Con Layout)
- Header con botón "New expense"
- Form desplegable (hidden by default)
  - Card selector
  - Category selector
  - Amount, concept, date
  - Checkbox para cuotas + input
- Lista de gastos
  - Click: expande detalles
  - Muestra cuotas si las tiene

### PaymentsPage (Con Layout)
- Tabs: "You owe" / "Owed to you"
- Botón "Record payment"
- Form: to_user_id, amount, description
- Listas por tab
- Colores: deudas en rojo, créditos en verde

### ReportsPage (Con Layout)
- Selector de mes/año
- 3 stats: total, cards, count
- By Category: tabla + barras de progreso
- By Card: tabla simple
- Actualiza al cambiar fecha

### SettingsPage (Con Layout)
- Tabs: Cards / Categories
- Cada tab tiene botón "Add"
- Grid de items existentes
- Delete button en cada item
- Color picker para categorías

---

## 🔌 CONEXIÓN CON BACKEND

### API Client (src/api/client.js)

```javascript
// Configuración
const client = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' }
})

// Request interceptor: agrega token JWT
client.interceptors.request.use((config) => {
  const { token } = useAuthStore.getState()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: maneja 401
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

### Uso en Componentes

```javascript
// Automático: token se agrega a todos los requests
const response = await api.get('/expenses')
const response = await api.post('/expenses', data)
const response = await api.delete(`/expenses/${id}`)
```

---

## 🎨 TAILWIND CONFIGURATION

### Color System

```javascript
// tailwind.config.js
colors: {
  tally: {
    50: '#f0fdf4',
    100: '#dcfce7',
    // ...
    500: '#22C55E',    // Verde principal
    600: '#16A34A',    // Verde profundo
    text: '#1F2937',   // Texto oscuro
    light: '#F9FAFB',  // Fondo claro
    border: '#E5E7EB', // Bordes
    hover: '#F3F4F6',  // Hover states
    accent: '#38BDF8'  // Azul acento
  }
}
```

### Component Classes

```javascript
// Reutilizable en toda la app
<input className="input-base" />      // px-4 py-2.5 border rounded-xl focus:ring-2
<button className="btn-primary" />    // bg-tally-500 hover:bg-tally-600
<button className="btn-secondary" />  // bg-tally-border hover:bg-tally-hover
<div className="card-base" />         // bg-white rounded-xl border
<label className="text-label" />      // text-sm font-medium mb-2
```

---

## 🎬 ANIMACIONES (Framer Motion)

### Page Load Animation

```javascript
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.3 }}
>
  Content
</motion.div>
```

### Stagger Animation

```javascript
const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0 }
}

<motion.div variants={containerVariants} initial="hidden" animate="show">
  {items.map((item) => (
    <motion.div key={item.id} variants={itemVariants}>
      {item}
    </motion.div>
  ))}
</motion.div>
```

---

## 📱 RESPONSIVE BREAKPOINTS

```
sm: 640px   (Mobile)
md: 768px   (Tablet) ← Punto clave: sidebar visible
lg: 1024px  (Desktop)
xl: 1280px  (Large)
```

### Ejemplos

```jsx
// Sidebar: hidden en mobile, visible en md+
<aside className="hidden md:flex">

// Grid: 1 columna mobile, 2+ en desktop
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

// Padding: distinto según pantalla
<div className="px-4 md:px-8">
```

---

## 🚀 SCALING DEL PROYECTO

### Agregar Nueva Página

1. Crear archivo en `src/pages/MiPaginaPage.jsx`
2. Agregar route en `src/App.jsx`:
   ```jsx
   <Route path="/mi-pagina" element={<MiPaginaPage />} />
   ```
3. Agregar nav item en `src/components/Layout.jsx`:
   ```jsx
   { path: '/mi-pagina', label: 'Mi Página', icon: 'icon' }
   ```

### Agregar Nuevo Componente Reutilizable

1. Crear en `src/components/MiComponente.jsx`
2. Importar donde necesites
3. Ejemplo:
   ```jsx
   import MiComponente from '../components/MiComponente'
   
   <MiComponente prop="valor" />
   ```

### Agregar Nuevo Store

1. Crear en `src/store/miStore.js`
2. Usar en componentes:
   ```jsx
   import { useMiStore } from '../store/miStore'
   const { data, setData } = useMiStore()
   ```

### Agregar Nuevas Clases Tailwind

Editar `src/index.css`:
```css
@layer components {
  .mi-clase {
    @apply px-4 py-2 bg-tally-500 text-white rounded-xl;
  }
}
```

---

## 🔍 DEBUGGING

### Console Logs
```javascript
// Ver state de Zustand
console.log(useAuthStore.getState())

// Ver requests
client.interceptors.request.use((config) => {
  console.log('Request:', config.url, config.data)
  return config
})
```

### React DevTools
```bash
npm install -D @react-devtools/shell
```

### Tailwind IntelliSense (VS Code)
```json
{
  "extensions": {
    "recommendations": [
      "bradlc.vscode-tailwindcss"
    ]
  }
}
```

---

## 📊 PERFORMANCE

### Code Splitting (automático con Vite)
```javascript
// vite.config.js
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        vendor: ['react', 'react-dom'],
        ui: ['framer-motion']
      }
    }
  }
}
```

### Lazy Loading Pages
```javascript
// Futuro: si necesitas
const DashboardPage = lazy(() => import('./pages/DashboardPage'))

<Suspense fallback={<Loading />}>
  <DashboardPage />
</Suspense>
```

---

## 🧪 TESTING

### Vitest Setup
```bash
npm install -D vitest @testing-library/react
```

### Ejemplo de test
```javascript
// src/pages/LoginPage.test.jsx
import { render, screen } from '@testing-library/react'
import LoginPage from './LoginPage'

test('renders login form', () => {
  render(<LoginPage />)
  expect(screen.getByPlaceholderText('Email')).toBeInTheDocument()
})
```

---

## 📦 BUILD Y DEPLOY

### Local Build
```bash
npm run build
# Genera carpeta dist/
```

### Preview
```bash
npm run preview
# Previsualiza localmente en puerto 4173
```

### Deploy a Vercel
```bash
vercel
# Automático: sube dist/ y configura
```

### Deploy a Netlify
```bash
npm run build
# Sube carpeta dist/ a Netlify
```

---

## 🎯 MEJORAS FUTURAS

1. **Componentes más pequeños**
   - Extraer CardList de ExpensesPage
   - Extraer DebtItem de PaymentsPage

2. **Error Handling**
   - Agregar ErrorBoundary
   - Toast notifications para errores

3. **Forms más robustos**
   - Validación con react-hook-form
   - Mensajes de error inline

4. **Testing**
   - Unit tests para componentes
   - Integration tests para flows

5. **Performance**
   - Memoization donde sea necesario
   - Virtual scrolling para listas grandes

6. **Internacionalización**
   - i18next para múltiples idiomas

---

**Arquitectura limpia, escalable y mantenible** ✅
