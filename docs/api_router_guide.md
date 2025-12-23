# 📁 APIRouter Complete Guide - Hindi + English

## 📖 Table of Contents
1. [Problem Kya Hai?](#1-problem-kya-hai)
2. [APIRouter Kya Hai?](#2-apirouter-kya-hai)
3. [Folder Structure](#3-folder-structure)
4. [Step by Step Implementation](#4-step-by-step-implementation)
5. [Code Explanation](#5-code-explanation)
6. [Complete Working Example](#6-complete-working-example)
7. [prefix Kya Hai?](#7-prefix-kya-hai)
8. [tags Kya Hai?](#8-tags-kya-hai)
9. [Multiple Routers](#9-multiple-routers)
10. [Best Practices](#10-best-practices)

---

## 1. Problem Kya Hai?

### 🔹 Abhi tak kya kar rahe the?

Sab kuch **EK FILE** mein likh rahe the:

```python
# main.py - EK BADI FILE 😫

from fastapi import FastAPI
app = FastAPI()

# -------- User Routes --------
@app.get("/users")
def get_users():
    return ["user1", "user2"]

@app.post("/users")
def create_user():
    return {"message": "created"}

@app.delete("/users/{id}")
def delete_user(id: int):
    return {"message": "deleted"}

# -------- Product Routes --------
@app.get("/products")
def get_products():
    return ["product1", "product2"]

@app.post("/products")
def create_product():
    return {"message": "created"}

@app.delete("/products/{id}")
def delete_product(id: int):
    return {"message": "deleted"}

# -------- Order Routes --------
@app.get("/orders")
def get_orders():
    return ["order1", "order2"]

@app.post("/orders")
def create_order():
    return {"message": "created"}

# ... aur 50+ routes 😱
```

### 🔹 Problems:

| Problem | Description |
|---------|-------------|
| 📄 File bahut badi | 1000+ lines ho jayegi |
| 🔍 Dhundna mushkil | Kaunsa route kahan hai? |
| 👥 Team work mushkil | 2 log same file edit karein toh conflict |
| 🐛 Bugs fix karna hard | Sab mixed hai |

---

## 2. APIRouter Kya Hai?

### 🔹 Simple Definition

**English:** APIRouter lets you split your routes into multiple files and then connect them to the main app.

**Hindi:** APIRouter se tum apne routes ko alag alag files mein likh sakte ho, phir main app se connect kar sakte ho.

### 🔹 Analogy - Company Departments

```
🏢 Company (FastAPI App)
│
├── 👥 HR Department (users.py)
│   ├── Hire employee
│   ├── Fire employee
│   └── Get employee list
│
├── 📦 Inventory Department (products.py)
│   ├── Add product
│   ├── Remove product
│   └── Get product list
│
└── 🛒 Sales Department (orders.py)
    ├── Create order
    ├── Cancel order
    └── Get order list

Har department ALAG hai, but sab EK company ke under!
```

### 🔹 Code Analogy

```
FastAPI App = Company (Main Boss)
APIRouter   = Department (Sub Boss)
Routes      = Department ke kaam
```

---

## 3. Folder Structure

### 🔹 Before (Single File) ❌

```
📁 project/
└── main.py       # Sab kuch yahan - MESSY!
```

### 🔹 After (Multiple Files) ✅

```
📁 project/
├── main.py              # Main app - sirf routers connect
└── routers/             # Folder for all routers
    ├── __init__.py      # Empty file (Python package)
    ├── users.py         # User related routes
    ├── products.py      # Product related routes
    └── orders.py        # Order related routes
```

### 🔹 Why `__init__.py`?

```python
# __init__.py = Empty file
# Ye Python ko batata hai "ye folder ek package hai"
# Isse hum `from routers import users` kar sakte hain
```

---

## 4. Step by Step Implementation

### 📝 Step 1: Folder Structure Banao

```
📁 router_demo/
├── main.py
└── routers/
    ├── __init__.py      # Empty file
    └── users.py
```

---

### 📝 Step 2: Router File Banao (users.py)

```python
# routers/users.py

from fastapi import APIRouter

# APIRouter banao - ye mini app jaisa hai
router = APIRouter()

# Routes define karo
@router.get("/")
def get_all_users():
    return ["Tarun", "Rahul", "Amit"]

@router.get("/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}

@router.post("/")
def create_user():
    return {"message": "User created!"}
```

**Note:** `@router.get()` use kiya, `@app.get()` nahi!

---

### 📝 Step 3: Main File Banao (main.py)

```python
# main.py

from fastapi import FastAPI
from routers import users  # Router import karo

app = FastAPI()

# Router ko main app se connect karo
app.include_router(
    users.router,      # Konsa router
    prefix="/users",   # URL prefix
    tags=["Users"]     # Swagger docs mein group name
)

# Optional: Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to API!"}
```

---

### 📝 Step 4: Run Karo

```bash
cd router_demo
uvicorn main:app --reload
```

---

### 📝 Step 5: Test Karo

```
GET  http://127.0.0.1:8000/           → {"message": "Welcome to API!"}
GET  http://127.0.0.1:8000/users/     → ["Tarun", "Rahul", "Amit"]
GET  http://127.0.0.1:8000/users/1    → {"user_id": 1, "name": "User 1"}
POST http://127.0.0.1:8000/users/     → {"message": "User created!"}
```

---

## 5. Code Explanation

### 🔹 users.py Explained

```python
from fastapi import APIRouter

# 1️⃣ APIRouter object banao
router = APIRouter()
# Ye FastAPI() jaisa hai, but mini version
# Isko baad mein main app se connect karenge

# 2️⃣ Routes define karo - @router use karo, @app nahi!
@router.get("/")
def get_all_users():
    return ["Tarun", "Rahul", "Amit"]
# Ye route abhi "/users/" banega (prefix ke baad)
```

### 🔹 main.py Explained

```python
from fastapi import FastAPI
from routers import users  # users.py import karo

app = FastAPI()  # Main app

# 3️⃣ Router ko app se connect karo
app.include_router(
    users.router,      # users.py ka router object
    prefix="/users",   # Sab routes ke aage "/users" lagega
    tags=["Users"]     # Swagger docs mein grouping
)
```

### 🔹 Flow Diagram

```
Request: GET /users/

        ↓

main.py dekha: /users/ prefix match hua
        
        ↓
        
users.router ko forward kiya

        ↓

users.py mein dekha: "/" route hai

        ↓

get_all_users() chala

        ↓

Response: ["Tarun", "Rahul", "Amit"]
```

---

## 6. Complete Working Example

### 📁 Folder Structure

```
📁 router_demo/
├── main.py
└── routers/
    ├── __init__.py
    ├── users.py
    └── products.py
```

### 📄 routers/__init__.py

```python
# Empty file - bas Python ko batata hai ye package hai
```

### 📄 routers/users.py

```python
from fastapi import APIRouter

router = APIRouter()

# Fake database
users_db = [
    {"id": 1, "name": "Tarun"},
    {"id": 2, "name": "Rahul"},
    {"id": 3, "name": "Amit"}
]

@router.get("/")
def get_all_users():
    """Get all users"""
    return users_db

@router.get("/{user_id}")
def get_user(user_id: int):
    """Get user by ID"""
    for user in users_db:
        if user["id"] == user_id:
            return user
    return {"error": "User not found"}

@router.post("/")
def create_user(name: str):
    """Create new user"""
    new_user = {"id": len(users_db) + 1, "name": name}
    users_db.append(new_user)
    return new_user
```

### 📄 routers/products.py

```python
from fastapi import APIRouter

router = APIRouter()

# Fake database
products_db = [
    {"id": 1, "name": "Laptop", "price": 50000},
    {"id": 2, "name": "Phone", "price": 20000}
]

@router.get("/")
def get_all_products():
    """Get all products"""
    return products_db

@router.get("/{product_id}")
def get_product(product_id: int):
    """Get product by ID"""
    for product in products_db:
        if product["id"] == product_id:
            return product
    return {"error": "Product not found"}

@router.post("/")
def create_product(name: str, price: int):
    """Create new product"""
    new_product = {"id": len(products_db) + 1, "name": name, "price": price}
    products_db.append(new_product)
    return new_product
```

### 📄 main.py

```python
from fastapi import FastAPI
from routers import users, products

app = FastAPI(
    title="My Shop API",
    description="API with multiple routers"
)

# Connect routers
app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

app.include_router(
    products.router,
    prefix="/products",
    tags=["Products"]
)

@app.get("/")
def root():
    return {"message": "Welcome to My Shop API!"}
```

### 🧪 Test URLs

```
# Root
GET /                    → Welcome message

# Users
GET /users/              → All users
GET /users/1             → User with ID 1
POST /users/?name=John   → Create user

# Products  
GET /products/           → All products
GET /products/1          → Product with ID 1
POST /products/?name=TV&price=30000 → Create product
```

---

## 7. prefix Kya Hai?

### 🔹 Definition

`prefix` = URL ke starting mein kya lagega

### 🔹 Example

```python
# users.py mein
@router.get("/")           # Route: "/"
@router.get("/{user_id}")  # Route: "/{user_id}"

# main.py mein
app.include_router(users.router, prefix="/users")
```

**Result:**
```
"/"           → "/users/"
"/{user_id}"  → "/users/{user_id}"
```

### 🔹 Visual

```
Without prefix:
router.get("/")        → GET /
router.get("/list")    → GET /list

With prefix="/users":
router.get("/")        → GET /users/
router.get("/list")    → GET /users/list
```

### 🔹 Why prefix?

```python
# users.py mein har route pe "/users" likhna padta
@router.get("/users/")           # ❌ Repetitive
@router.get("/users/{id}")       # ❌ Repetitive

# Better: prefix use karo
@router.get("/")                 # ✅ Clean
@router.get("/{id}")             # ✅ Clean
# prefix="/users" automatically lagega
```

---

## 8. tags Kya Hai?

### 🔹 Definition

`tags` = Swagger docs mein routes ko group karta hai

### 🔹 Without tags

```
Swagger UI:
├── GET /users/
├── POST /users/
├── GET /products/
├── POST /products/
├── GET /orders/
└── POST /orders/

Sab mixed! 😫
```

### 🔹 With tags

```
Swagger UI:
├── 👥 Users
│   ├── GET /users/
│   └── POST /users/
│
├── 📦 Products
│   ├── GET /products/
│   └── POST /products/
│
└── 🛒 Orders
    ├── GET /orders/
    └── POST /orders/

Clean & Organized! ✅
```

### 🔹 Code

```python
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(products.router, prefix="/products", tags=["Products"])
```

---

## 9. Multiple Routers

### 🔹 Kitne bhi routers add kar sakte ho

```python
# main.py
from fastapi import FastAPI
from routers import users, products, orders, auth, payments

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
```

### 🔹 Folder Structure

```
📁 project/
├── main.py
└── routers/
    ├── __init__.py
    ├── users.py
    ├── products.py
    ├── orders.py
    ├── auth.py
    └── payments.py
```

---

## 10. Best Practices

### ✅ Do's

```python
# 1. Related routes ek file mein
# users.py mein sirf user routes
# products.py mein sirf product routes

# 2. Meaningful file names
users.py       ✅
products.py    ✅
xyz.py         ❌

# 3. prefix URL friendly rakho
prefix="/users"     ✅
prefix="/Users"     ❌ (lowercase better)
prefix="/user-management"  ✅

# 4. tags descriptive rakho
tags=["Users"]           ✅
tags=["User Management"] ✅
tags=["xyz"]             ❌
```

### ❌ Don'ts

```python
# 1. Ek file mein bahut saare unrelated routes mat likho
# users.py mein products routes mat likho

# 2. Circular imports se bacho
# users.py imports products.py
# products.py imports users.py  ❌ Error!

# 3. router object ka naam change mat karo
router = APIRouter()  ✅
my_router = APIRouter()  # Works but confusing
```

---

## 🎯 Quick Reference

### Syntax Cheat Sheet

```python
# Router file (users.py)
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_all():
    return [...]

@router.post("/")
def create():
    return {...}


# Main file (main.py)
from fastapi import FastAPI
from routers import users

app = FastAPI()
app.include_router(users.router, prefix="/users", tags=["Users"])
```

### Key Points

```
1. APIRouter = Mini FastAPI app
2. @router.get() use karo, @app.get() nahi
3. include_router() se main app se connect karo
4. prefix = URL ke aage kya lagega
5. tags = Swagger docs mein grouping
6. __init__.py = Empty file for Python package
```

---

## 🧠 Memory Trick

```
APIRouter = Department in a Company

Company (FastAPI) has:
├── HR Dept (users.py router)
├── Sales Dept (orders.py router)
└── Inventory Dept (products.py router)

include_router = Department ko company mein add karna
prefix = Department ka address
tags = Department ka signboard
```

---

**Created for FastAPI Learning Journey** 📚
**Date:** 21 December 2024
