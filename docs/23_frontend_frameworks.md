# 23 — Frontend Frameworks (React, Vue) with FastAPI (Complete In-Depth Guide)

> 🎯 **Goal**: Modern frontend framework ko FastAPI backend se connect karo!

---

## 📚 Table of Contents
1. [Framework Kyun?](#framework-kyun)
2. [React Basics](#react-basics)
3. [Vue.js Basics](#vuejs-basics)
4. [API Integration Patterns](#api-integration-patterns)
5. [State Management](#state-management)
6. [Authentication Flow](#authentication-flow)
7. [Full Stack Project Setup](#full-stack-project-setup)
8. [Best Practices](#best-practices)

---

## Framework Kyun?

### Vanilla JS vs Framework

```
Vanilla JavaScript:
─────────────────────────────────────────────────────────
const users = await fetch("/api/users").then(r => r.json());

const container = document.getElementById("users");
container.innerHTML = users.map(u => `
    <div class="user-card">
        <h3>${u.name}</h3>
        <p>${u.email}</p>
        <button onclick="deleteUser(${u.id})">Delete</button>
    </div>
`).join("");

// Now update user...
// Have to manually find and update DOM element
// Easy to create bugs!


With React:
─────────────────────────────────────────────────────────
function UserList() {
    const [users, setUsers] = useState([]);
    
    useEffect(() => {
        fetch("/api/users").then(r => r.json()).then(setUsers);
    }, []);
    
    const deleteUser = (id) => {
        setUsers(users.filter(u => u.id !== id));
    };
    
    return (
        <div>
            {users.map(u => (
                <UserCard key={u.id} user={u} onDelete={deleteUser} />
            ))}
        </div>
    );
}

// Change state → UI updates automatically!
// Component reusable
// Easy to understand and maintain
```

### Framework Comparison

```
React:
─────────────────────────────────────────────────────────
✅ Largest ecosystem
✅ Most job opportunities
✅ Backed by Meta (Facebook)
❌ Steeper learning curve
❌ More boilerplate

Vue.js:
─────────────────────────────────────────────────────────
✅ Easier to learn
✅ Great documentation
✅ Good for small-medium projects
❌ Smaller ecosystem
❌ Fewer job opportunities

Svelte:
─────────────────────────────────────────────────────────
✅ Simplest syntax
✅ No virtual DOM (faster)
✅ Growing rapidly
❌ Smaller community
❌ Fewer resources
```

---

## React Basics

### Create React App

```bash
# Create new React project
npx create-react-app my-frontend
cd my-frontend

# Or with Vite (faster, recommended)
npm create vite@latest my-frontend -- --template react
cd my-frontend
npm install

# Start development server
npm start  # or npm run dev for Vite
```

### Project Structure

```
my-frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── UserList.jsx
│   │   └── UserCard.jsx
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── Login.jsx
│   │   └── Dashboard.jsx
│   ├── services/
│   │   └── api.js          ← API calls
│   ├── context/
│   │   └── AuthContext.jsx ← Global state
│   ├── App.jsx
│   └── main.jsx
├── package.json
└── vite.config.js
```

### Components

```jsx
// src/components/UserCard.jsx

// Functional Component
function UserCard({ user, onDelete }) {
    return (
        <div className="user-card">
            <h3>{user.name}</h3>
            <p>{user.email}</p>
            <button onClick={() => onDelete(user.id)}>
                Delete
            </button>
        </div>
    );
}

export default UserCard;


// With styling
import './UserCard.css';

function UserCard({ user }) {
    const isAdmin = user.role === 'admin';
    
    return (
        <div className={`user-card ${isAdmin ? 'admin' : ''}`}>
            <img src={user.avatar} alt={user.name} />
            <div className="user-info">
                <h3>{user.name}</h3>
                <p>{user.email}</p>
                {isAdmin && <span className="badge">Admin</span>}
            </div>
        </div>
    );
}
```

### State (useState)

```jsx
import { useState } from 'react';

function Counter() {
    // [currentValue, setterFunction] = useState(initialValue)
    const [count, setCount] = useState(0);
    
    return (
        <div>
            <p>Count: {count}</p>
            <button onClick={() => setCount(count + 1)}>+1</button>
            <button onClick={() => setCount(count - 1)}>-1</button>
            <button onClick={() => setCount(0)}>Reset</button>
        </div>
    );
}


// Object state
function UserForm() {
    const [user, setUser] = useState({
        name: '',
        email: '',
    });
    
    const handleChange = (e) => {
        setUser({
            ...user,  // Keep other fields
            [e.target.name]: e.target.value  // Update this field
        });
    };
    
    return (
        <form>
            <input 
                name="name" 
                value={user.name} 
                onChange={handleChange} 
            />
            <input 
                name="email" 
                value={user.email} 
                onChange={handleChange} 
            />
        </form>
    );
}
```

### Effects (useEffect)

```jsx
import { useState, useEffect } from 'react';

function UserList() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    // Runs after component mounts
    useEffect(() => {
        async function fetchUsers() {
            try {
                const response = await fetch('/api/users');
                const data = await response.json();
                setUsers(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        }
        
        fetchUsers();
    }, []);  // Empty array = run once on mount
    
    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error: {error}</p>;
    
    return (
        <ul>
            {users.map(user => (
                <li key={user.id}>{user.name}</li>
            ))}
        </ul>
    );
}


// Effect with dependencies
function UserProfile({ userId }) {
    const [user, setUser] = useState(null);
    
    useEffect(() => {
        fetch(`/api/users/${userId}`)
            .then(r => r.json())
            .then(setUser);
    }, [userId]);  // Re-run when userId changes
    
    return user ? <h1>{user.name}</h1> : <p>Loading...</p>;
}
```

---

## Vue.js Basics

### Create Vue App

```bash
# Create new Vue project
npm create vue@latest my-frontend
cd my-frontend
npm install
npm run dev
```

### Vue Component (SFC - Single File Component)

```vue
<!-- src/components/UserCard.vue -->
<template>
    <div class="user-card" :class="{ admin: isAdmin }">
        <h3>{{ user.name }}</h3>
        <p>{{ user.email }}</p>
        <button @click="$emit('delete', user.id)">Delete</button>
    </div>
</template>

<script setup>
// Props from parent
const props = defineProps({
    user: {
        type: Object,
        required: true
    }
});

// Computed property
const isAdmin = computed(() => props.user.role === 'admin');
</script>

<style scoped>
.user-card {
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 8px;
}
.admin {
    border-color: gold;
}
</style>
```

### Vue State (ref, reactive)

```vue
<!-- src/components/Counter.vue -->
<template>
    <div>
        <p>Count: {{ count }}</p>
        <button @click="count++">+1</button>
        <button @click="count--">-1</button>
        <button @click="count = 0">Reset</button>
    </div>
</template>

<script setup>
import { ref } from 'vue';

// ref for primitive values
const count = ref(0);
</script>


<!-- Object state with reactive -->
<script setup>
import { reactive, ref } from 'vue';

// reactive for objects
const user = reactive({
    name: '',
    email: ''
});

// Or use ref for everything
const users = ref([]);
</script>
```

### Vue Data Fetching

```vue
<template>
    <div>
        <p v-if="loading">Loading...</p>
        <p v-else-if="error">Error: {{ error }}</p>
        <ul v-else>
            <li v-for="user in users" :key="user.id">
                {{ user.name }}
            </li>
        </ul>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const users = ref([]);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
    try {
        const response = await fetch('/api/users');
        users.value = await response.json();
    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
});
</script>
```

---

## API Integration Patterns

### Centralized API Service

```javascript
// src/services/api.js

const API_BASE = 'http://localhost:8000/api';

// Get token from storage
function getAuthHeader() {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

// Wrapper for all API calls
async function apiFetch(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...getAuthHeader(),
            ...options.headers,
        },
    });
    
    // Handle auth errors
    if (response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        throw new Error('Unauthorized');
    }
    
    // Handle other errors
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API Error');
    }
    
    return response.json();
}


// API functions
export const userAPI = {
    getAll: () => apiFetch('/users'),
    getById: (id) => apiFetch(`/users/${id}`),
    create: (data) => apiFetch('/users', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    update: (id, data) => apiFetch(`/users/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }),
    delete: (id) => apiFetch(`/users/${id}`, {
        method: 'DELETE',
    }),
};

export const authAPI = {
    login: async (email, password) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData,
        });
        
        if (!response.ok) throw new Error('Invalid credentials');
        
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        return data;
    },
    
    logout: () => {
        localStorage.removeItem('access_token');
    },
    
    getMe: () => apiFetch('/users/me'),
};
```

### Using in React

```jsx
// src/pages/Users.jsx
import { useState, useEffect } from 'react';
import { userAPI } from '../services/api';

function UsersPage() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        loadUsers();
    }, []);
    
    async function loadUsers() {
        setLoading(true);
        try {
            const data = await userAPI.getAll();
            setUsers(data);
        } catch (error) {
            console.error('Failed to load users:', error);
        } finally {
            setLoading(false);
        }
    }
    
    async function handleDelete(id) {
        if (!confirm('Are you sure?')) return;
        
        try {
            await userAPI.delete(id);
            setUsers(users.filter(u => u.id !== id));
        } catch (error) {
            alert('Failed to delete user');
        }
    }
    
    return (
        <div>
            <h1>Users</h1>
            {loading ? (
                <p>Loading...</p>
            ) : (
                <ul>
                    {users.map(user => (
                        <li key={user.id}>
                            {user.name}
                            <button onClick={() => handleDelete(user.id)}>
                                Delete
                            </button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
```

### React Query (Recommended)

```jsx
// npm install @tanstack/react-query

// src/main.jsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')).render(
    <QueryClientProvider client={queryClient}>
        <App />
    </QueryClientProvider>
);


// src/pages/Users.jsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userAPI } from '../services/api';

function UsersPage() {
    const queryClient = useQueryClient();
    
    // Fetch users
    const { data: users, isLoading, error } = useQuery({
        queryKey: ['users'],
        queryFn: userAPI.getAll,
    });
    
    // Delete mutation
    const deleteMutation = useMutation({
        mutationFn: userAPI.delete,
        onSuccess: () => {
            // Invalidate cache to refetch
            queryClient.invalidateQueries(['users']);
        },
    });
    
    if (isLoading) return <p>Loading...</p>;
    if (error) return <p>Error: {error.message}</p>;
    
    return (
        <ul>
            {users.map(user => (
                <li key={user.id}>
                    {user.name}
                    <button 
                        onClick={() => deleteMutation.mutate(user.id)}
                        disabled={deleteMutation.isLoading}
                    >
                        Delete
                    </button>
                </li>
            ))}
        </ul>
    );
}
```

---

## State Management

### React Context (Built-in)

```jsx
// src/context/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        // Check if logged in on mount
        const token = localStorage.getItem('access_token');
        if (token) {
            authAPI.getMe()
                .then(setUser)
                .catch(() => localStorage.removeItem('access_token'))
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, []);
    
    const login = async (email, password) => {
        await authAPI.login(email, password);
        const userData = await authAPI.getMe();
        setUser(userData);
    };
    
    const logout = () => {
        authAPI.logout();
        setUser(null);
    };
    
    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}

// Custom hook for easy access
export function useAuth() {
    return useContext(AuthContext);
}


// Usage in components
function Navbar() {
    const { user, logout } = useAuth();
    
    return (
        <nav>
            {user ? (
                <>
                    <span>Hello, {user.name}</span>
                    <button onClick={logout}>Logout</button>
                </>
            ) : (
                <a href="/login">Login</a>
            )}
        </nav>
    );
}


// Protected route
function ProtectedRoute({ children }) {
    const { user, loading } = useAuth();
    
    if (loading) return <p>Loading...</p>;
    if (!user) return <Navigate to="/login" />;
    
    return children;
}
```

---

## Authentication Flow

### Login Page

```jsx
// src/pages/Login.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    
    const { login } = useAuth();
    const navigate = useNavigate();
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        
        try {
            await login(email, password);
            navigate('/dashboard');
        } catch (err) {
            setError('Invalid email or password');
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <h1>Login</h1>
            
            {error && <p className="error">{error}</p>}
            
            <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
            />
            
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
            />
            
            <button type="submit" disabled={loading}>
                {loading ? 'Logging in...' : 'Login'}
            </button>
        </form>
    );
}
```

### App Router

```jsx
// src/App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';

// Components
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Navbar />
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route 
                        path="/dashboard" 
                        element={
                            <ProtectedRoute>
                                <Dashboard />
                            </ProtectedRoute>
                        } 
                    />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}
```

---

## Full Stack Project Setup

### Development Setup

```
project/
├── backend/           ← FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   └── routes/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/          ← React/Vue
│   ├── src/
│   ├── package.json
│   └── Dockerfile
│
└── docker-compose.yml
```

### Configure CORS (FastAPI)

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # React dev server
        "http://localhost:5173",     # Vite dev server
        "https://myapp.com",         # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Configure Proxy (Vite)

```javascript
// frontend/vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            // All /api requests go to FastAPI
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
        },
    },
});

// Now in React:
// fetch('/api/users') → goes to http://localhost:8000/api/users
// No CORS issues in development!
```

### Docker Compose for Full Stack

```yaml
# docker-compose.yml
version: "3.8"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
    depends_on:
      - db
    volumes:
      - ./backend:/app
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Production Build

```dockerfile
# frontend/Dockerfile.prod

# Build stage
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

```nginx
# frontend/nginx.conf
server {
    listen 80;
    root /usr/share/nginx/html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Proxy API calls to backend
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }
}
```

---

## Best Practices

### 1. Environment Variables

```javascript
// .env
VITE_API_URL=http://localhost:8000

// Usage in code
const API_URL = import.meta.env.VITE_API_URL;
```

### 2. Error Boundaries (React)

```jsx
class ErrorBoundary extends React.Component {
    state = { hasError: false };
    
    static getDerivedStateFromError(error) {
        return { hasError: true };
    }
    
    render() {
        if (this.state.hasError) {
            return <h1>Something went wrong.</h1>;
        }
        return this.props.children;
    }
}

// Usage
<ErrorBoundary>
    <App />
</ErrorBoundary>
```

### 3. Loading States

```jsx
function DataLoader({ loading, error, children }) {
    if (loading) return <Spinner />;
    if (error) return <ErrorMessage error={error} />;
    return children;
}

// Usage
<DataLoader loading={isLoading} error={error}>
    <UserList users={users} />
</DataLoader>
```

---

## Quick Reference

```jsx
// React Hooks
const [state, setState] = useState(initial);
useEffect(() => { /* side effect */ }, [deps]);

// Vue Composition API
const state = ref(initial);
onMounted(() => { /* side effect */ });

// API Call Pattern
const response = await fetch(url, {
    method: 'POST',
    headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
});
```

---

> **Pro Tip**: "Frontend framework seekhne ka best tarika - apna FastAPI backend ke saath ek chhota sa project banao!" ⚛️
