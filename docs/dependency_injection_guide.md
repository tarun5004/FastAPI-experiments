# 🔌 Dependency Injection Complete Guide - Hindi + English

## 📖 Table of Contents
1. [Kya hai Dependency Injection?](#1-kya-hai-dependency-injection)
2. [Kyun use karte hain?](#2-kyun-use-karte-hain)
3. [Basic Syntax](#3-basic-syntax)
4. [Step by Step Flow](#4-step-by-step-flow)
5. [Real World Examples](#5-real-world-examples)
6. [Multiple Dependencies](#6-multiple-dependencies)
7. [Nested Dependencies](#7-nested-dependencies)
8. [Dependencies with Parameters](#8-dependencies-with-parameters)
9. [Common Use Cases](#9-common-use-cases)
10. [Best Practices](#10-best-practices)

---

## 1. Kya hai Dependency Injection?

### 🔹 Simple Definition

**English:** A way to provide (inject) common functionality to multiple endpoints automatically.

**Hindi:** Ek tarika jisse common code automatically har endpoint mein inject ho jaye.

### 🔹 Ek Line Mein

```
Depends() = "Ye function pehle chala, result mujhe de"
```

### 🔹 Real Life Analogy

```
🏢 Office Entry System:

Without DI (Dependency Injection):
   Room 1 jaana → Guard check → ID dikhao → Sign karo → Entry
   Room 2 jaana → Guard check → ID dikhao → Sign karo → Entry
   Room 3 jaana → Guard check → ID dikhao → Sign karo → Entry
   (Har baar same process! 😫)

With DI:
   Reception pe ek baar → Access Card mila ✅
   Room 1 → Card tap → Entry!
   Room 2 → Card tap → Entry!
   Room 3 → Card tap → Entry!
   (Automatic hai! 🎉)
```

---

## 2. Kyun use karte hain?

### 🔹 Problem: Code Duplication

```python
# ❌ Without Dependency Injection - Same code 3 baar!

@app.get("/orders")
def get_orders():
    # Check if user is logged in
    token = get_token_from_header()
    if not token:
        raise HTTPException(401, "Not logged in")
    user = decode_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    # Ab actual kaam karo
    return {"orders": [...]}

@app.get("/profile")
def get_profile():
    # Check if user is logged in (SAME CODE!)
    token = get_token_from_header()
    if not token:
        raise HTTPException(401, "Not logged in")
    user = decode_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    # Ab actual kaam karo
    return {"profile": {...}}

@app.get("/cart")
def get_cart():
    # Check if user is logged in (SAME CODE AGAIN!)
    token = get_token_from_header()
    if not token:
        raise HTTPException(401, "Not logged in")
    user = decode_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    # Ab actual kaam karo
    return {"cart": [...]}
```

**Problems:**
- Same code 3 baar likha 😫
- Agar change karna hai toh 3 jagah karna padega
- Galti hone ka chance zyada

---

### 🔹 Solution: Dependency Injection

```python
# ✅ With Dependency Injection - Ek baar likho, har jagah use karo!

from fastapi import Depends

# Step 1: Common logic ek function mein
def get_current_user():
    token = get_token_from_header()
    if not token:
        raise HTTPException(401, "Not logged in")
    user = decode_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    return user

# Step 2: Depends() se automatic inject
@app.get("/orders")
def get_orders(user = Depends(get_current_user)):
    return {"user": user, "orders": [...]}

@app.get("/profile")
def get_profile(user = Depends(get_current_user)):
    return {"user": user, "profile": {...}}

@app.get("/cart")
def get_cart(user = Depends(get_current_user)):
    return {"user": user, "cart": [...]}
```

**Benefits:**
- Code ek baar likha ✅
- Change ek jagah karo, sab jagah apply ✅
- Clean aur readable code ✅

---

## 3. Basic Syntax

### 🔹 Step 1: Dependency Function Banao

```python
def my_dependency():
    # Kuch logic
    return some_value
```

### 🔹 Step 2: Depends() se Use Karo

```python
from fastapi import Depends

@app.get("/endpoint")
def my_endpoint(result = Depends(my_dependency)):
    #            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #            FastAPI automatically my_dependency() call karega
    #            Jo return hoga, wo "result" mein aayega
    return {"data": result}
```

### 🔹 Complete Example

```python
from fastapi import FastAPI, Depends

app = FastAPI()

# Dependency function
def get_database():
    return {"status": "connected", "db": "MySQL"}

# Endpoint using dependency
@app.get("/users")
def get_users(db = Depends(get_database)):
    # db = {"status": "connected", "db": "MySQL"}
    return {"database": db, "users": ["user1", "user2"]}
```

**Output:**
```json
{
    "database": {"status": "connected", "db": "MySQL"},
    "users": ["user1", "user2"]
}
```

---

## 4. Step by Step Flow

### 🔹 Visual Flow

```
Request: GET /users
         │
         ▼
┌─────────────────────────────────┐
│ FastAPI dekha:                  │
│ Depends(get_database) hai       │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Pehle get_database() call kiya  │
│ Return: {"status": "connected"} │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Result ko "db" mein inject kiya │
│ db = {"status": "connected"}    │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Ab get_users() function chala   │
│ with db already available       │
└─────────────────────────────────┘
         │
         ▼
Response: {"database": {...}, "users": [...]}
```

### 🔹 Code Flow

```python
# Step 1: Request aaya
# GET /users

# Step 2: FastAPI ne parameter dekha
def get_users(db = Depends(get_database)):
#             ^^^^^^^^^^^^^^^^^^^^^^^^^^
#             "Isko pehle solve karna hai"

# Step 3: get_database() call hua
def get_database():
    return {"status": "connected"}  # Ye return hua

# Step 4: Return value "db" mein gaya
# db = {"status": "connected"}

# Step 5: Ab actual function chala
def get_users(db = {"status": "connected"}):  # Already filled!
    return {"database": db}

# Step 6: Response bheja
```

---

## 5. Real World Examples

### 🔹 Example 1: User Authentication

```python
from fastapi import FastAPI, Depends, HTTPException, Header

app = FastAPI()

# Dependency: Get current logged-in user
def get_current_user(authorization: str = Header(None)):
    """
    Ye function har request pe automatically chalega
    Header se token lega aur user return karega
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Token missing")
    
    # Token validate karo (simplified)
    if authorization == "Bearer admin123":
        return {"user_id": 1, "username": "admin", "role": "admin"}
    elif authorization == "Bearer user456":
        return {"user_id": 2, "username": "tarun", "role": "user"}
    else:
        raise HTTPException(status_code=401, detail="Invalid token")

# Protected endpoints - Sirf logged in users access kar sakte hain
@app.get("/my-orders")
def get_my_orders(user = Depends(get_current_user)):
    return {
        "user": user,
        "orders": ["Order 1", "Order 2"]
    }

@app.get("/my-profile")
def get_my_profile(user = Depends(get_current_user)):
    return {
        "user": user,
        "profile": {"email": f"{user['username']}@gmail.com"}
    }
```

**Testing:**
```
# Without token
GET /my-orders → 401 "Token missing"

# With valid token
GET /my-orders
Header: Authorization: Bearer admin123
→ {"user": {"user_id": 1, ...}, "orders": [...]}
```

---

### 🔹 Example 2: Database Connection

```python
from fastapi import FastAPI, Depends

app = FastAPI()

# Fake database class
class Database:
    def __init__(self):
        self.connected = True
    
    def query(self, sql):
        return [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    
    def close(self):
        self.connected = False

# Dependency: Database connection
def get_db():
    """
    Har request ke liye:
    1. Database connection banao
    2. Use karo
    3. Connection close karo
    """
    db = Database()
    print("Database connected!")
    try:
        yield db  # Ye db endpoint ko milega
    finally:
        db.close()
        print("Database closed!")

# Endpoints using database
@app.get("/products")
def get_products(db = Depends(get_db)):
    products = db.query("SELECT * FROM products")
    return {"products": products}

@app.get("/categories")
def get_categories(db = Depends(get_db)):
    categories = db.query("SELECT * FROM categories")
    return {"categories": categories}
```

**Note:** `yield` use kiya - ye cleanup ke liye hai (connection close)

---

### 🔹 Example 3: Pagination

```python
from fastapi import FastAPI, Depends, Query

app = FastAPI()

# Dependency: Common pagination parameters
def get_pagination(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    """
    Har list endpoint mein pagination chahiye
    Ye dependency automatically page aur limit handle karega
    """
    skip = (page - 1) * limit
    return {"skip": skip, "limit": limit, "page": page}

# Sample data
all_users = [f"User {i}" for i in range(1, 101)]  # 100 users
all_products = [f"Product {i}" for i in range(1, 51)]  # 50 products

@app.get("/users")
def get_users(pagination = Depends(get_pagination)):
    start = pagination["skip"]
    end = start + pagination["limit"]
    users = all_users[start:end]
    return {
        "page": pagination["page"],
        "limit": pagination["limit"],
        "users": users
    }

@app.get("/products")
def get_products(pagination = Depends(get_pagination)):
    start = pagination["skip"]
    end = start + pagination["limit"]
    products = all_products[start:end]
    return {
        "page": pagination["page"],
        "limit": pagination["limit"],
        "products": products
    }
```

**Testing:**
```
GET /users?page=1&limit=5
→ {"page": 1, "limit": 5, "users": ["User 1", ..., "User 5"]}

GET /users?page=2&limit=5
→ {"page": 2, "limit": 5, "users": ["User 6", ..., "User 10"]}
```

---

## 6. Multiple Dependencies

### 🔹 Ek Endpoint mein Multiple Dependencies

```python
from fastapi import FastAPI, Depends

app = FastAPI()

def get_db():
    return {"db": "MySQL"}

def get_current_user():
    return {"user_id": 1, "name": "Tarun"}

def get_settings():
    return {"theme": "dark", "language": "en"}

# Multiple dependencies in one endpoint
@app.get("/dashboard")
def get_dashboard(
    db = Depends(get_db),
    user = Depends(get_current_user),
    settings = Depends(get_settings)
):
    return {
        "database": db,
        "user": user,
        "settings": settings
    }
```

**Output:**
```json
{
    "database": {"db": "MySQL"},
    "user": {"user_id": 1, "name": "Tarun"},
    "settings": {"theme": "dark", "language": "en"}
}
```

---

## 7. Nested Dependencies

### 🔹 Dependency ke andar Dependency

```python
from fastapi import FastAPI, Depends

app = FastAPI()

# Level 1: Database connection
def get_db():
    return {"connection": "MySQL"}

# Level 2: Depends on get_db
def get_user_repository(db = Depends(get_db)):
    return {"db": db, "repository": "UserRepository"}

# Level 3: Depends on get_user_repository
def get_current_user(repo = Depends(get_user_repository)):
    # Repo use karke user fetch karo
    return {"user": "Tarun", "fetched_from": repo}

# Endpoint
@app.get("/profile")
def get_profile(user = Depends(get_current_user)):
    return user
```

**Flow:**
```
get_profile needs → get_current_user
                           ↓
         get_current_user needs → get_user_repository
                                         ↓
                   get_user_repository needs → get_db
                                                  ↓
                                         get_db runs first!
                                                  ↓
                             Then get_user_repository
                                                  ↓
                                   Then get_current_user
                                                  ↓
                                     Finally get_profile
```

**Output:**
```json
{
    "user": "Tarun",
    "fetched_from": {
        "db": {"connection": "MySQL"},
        "repository": "UserRepository"
    }
}
```

---

## 8. Dependencies with Parameters

### 🔹 Dependency jo parameters le

```python
from fastapi import FastAPI, Depends, Query

app = FastAPI()

# Dependency with query parameters
def common_parameters(
    search: str = Query(None, description="Search term"),
    sort_by: str = Query("id", description="Sort field"),
    order: str = Query("asc", description="Sort order")
):
    return {
        "search": search,
        "sort_by": sort_by,
        "order": order
    }

@app.get("/items")
def get_items(params = Depends(common_parameters)):
    return {"params": params, "items": ["item1", "item2"]}

@app.get("/users")
def get_users(params = Depends(common_parameters)):
    return {"params": params, "users": ["user1", "user2"]}
```

**Testing:**
```
GET /items?search=phone&sort_by=price&order=desc
→ {
    "params": {"search": "phone", "sort_by": "price", "order": "desc"},
    "items": [...]
  }
```

---

### 🔹 Class-based Dependency

```python
from fastapi import FastAPI, Depends

app = FastAPI()

class Pagination:
    def __init__(self, page: int = 1, limit: int = 10):
        self.page = page
        self.limit = limit
        self.skip = (page - 1) * limit

@app.get("/items")
def get_items(pagination: Pagination = Depends()):
    return {
        "page": pagination.page,
        "limit": pagination.limit,
        "skip": pagination.skip
    }
```

---

## 9. Common Use Cases

### 🔹 Use Case Table

| Use Case | Dependency Function | Purpose |
|----------|-------------------|---------|
| Authentication | `get_current_user()` | Token verify, user info |
| Database | `get_db()` | DB connection manage |
| Pagination | `get_pagination()` | Page, limit handle |
| Permissions | `require_admin()` | Role check |
| Rate Limiting | `check_rate_limit()` | API call limit |
| Logging | `log_request()` | Request log |
| Validation | `validate_api_key()` | API key check |

---

### 🔹 Authentication + Authorization Example

```python
from fastapi import FastAPI, Depends, HTTPException

app = FastAPI()

# Dependency 1: Get current user
def get_current_user():
    # Simplified - normally token se user fetch hota
    return {"id": 1, "name": "Tarun", "role": "user"}

# Dependency 2: Check if admin (depends on get_current_user)
def require_admin(user = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only!")
    return user

# Public endpoint - Any logged in user
@app.get("/products")
def get_products(user = Depends(get_current_user)):
    return {"user": user, "products": [...]}

# Admin only endpoint
@app.get("/admin/users")
def get_all_users(admin = Depends(require_admin)):
    return {"admin": admin, "all_users": [...]}
```

---

## 10. Best Practices

### ✅ Do's (Karo)

```python
# 1. Dependency functions ko alag file mein rakho
# dependencies.py
def get_db():
    ...
def get_current_user():
    ...

# main.py
from dependencies import get_db, get_current_user

# 2. yield use karo cleanup ke liye
def get_db():
    db = connect()
    try:
        yield db
    finally:
        db.close()

# 3. Type hints use karo
def get_current_user() -> dict:
    return {"id": 1}

# 4. HTTPException raise karo invalid cases mein
def get_current_user(token: str = Header()):
    if not token:
        raise HTTPException(401, "Token required")
```

### ❌ Don'ts (Mat karo)

```python
# 1. Heavy computation mat karo dependency mein
def bad_dependency():
    time.sleep(10)  # ❌ Block ho jayega
    return data

# 2. Global state mat use karo
current_user = None  # ❌ Wrong!
def get_user():
    global current_user
    return current_user

# 3. Dependency mein response mat bhejo
def bad_dependency():
    return Response(...)  # ❌ Confusing
```

---

## 🎯 Quick Reference

### Syntax Cheat Sheet

```python
# Basic dependency
def my_dep():
    return value

@app.get("/")
def endpoint(result = Depends(my_dep)):
    return result

# Multiple dependencies
@app.get("/")
def endpoint(
    a = Depends(dep1),
    b = Depends(dep2)
):
    return {"a": a, "b": b}

# Nested dependency
def dep1():
    return "A"

def dep2(a = Depends(dep1)):
    return f"{a} + B"

# Class dependency
class MyDep:
    def __init__(self, param: int = 1):
        self.param = param

@app.get("/")
def endpoint(dep: MyDep = Depends()):
    return dep.param

# Dependency with yield (cleanup)
def get_db():
    db = connect()
    try:
        yield db
    finally:
        db.close()
```

---

## 🧠 Memory Trick

```
Depends = "Depend karta hoon is function pe"
         = "Ye function pehle chale, mujhe result de"
         = "Waiter jo pehle order le aur phir serve kare"

Without Depends → Khud kitchen jao, khud lao
With Depends    → Waiter laake dega automatically
```

---

## 📝 Summary

```
1. Depends() = Automatic function injection
2. Reusable code = Ek baar likho, har jagah use karo
3. Common uses = Auth, DB, Pagination, Validation
4. Multiple Depends = Ek endpoint mein kayi dependencies
5. Nested Depends = Dependency ke andar dependency
6. yield = Cleanup ke liye (DB close, etc.)
```

---

**Created for FastAPI Learning Journey** 📚
**Date:** 20 December 2024
