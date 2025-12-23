# 📘 SQLAlchemy Complete Documentation (Hindi/English Mix)

---

## 🎯 Yeh Documentation Kiske Liye Hai?
- Beginners jo SQLAlchemy seekhna chahte hain
- Developers jo FastAPI + Database integration seekhna chahte hain
- Jo log Python ORM concepts samajhna chahte hain

---

# 📚 PART 1: SQLAlchemy Basics

---

## 1.1 SQLAlchemy Kya Hai?

**Definition:**
SQLAlchemy ek Python library hai jo databases ke saath kaam karne ke liye use hoti hai.

**Simple Analogy:**
- Bina SQLAlchemy: Tum directly SQL language mein baat karte ho database se
- SQLAlchemy ke saath: Tum Python objects se baat karte ho, SQLAlchemy SQL mein translate kar deta hai

```
┌─────────────────┐
│   Python Code   │
│   (Classes)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   SQLAlchemy    │  ← Translator
│   (ORM)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Database      │
│   (SQL)         │
└─────────────────┘
```

---

## 1.2 ORM Kya Hai?

**Full Form:** Object Relational Mapper

**Simple Explanation:**
- Object = Python class/object
- Relational = Database table (rows & columns)
- Mapper = Dono ko connect karta hai

**Example:**
```python
# Python Class (Object)
class User:
    id = 1
    name = "Tarun"
    email = "tarun@gmail.com"

# Database Table (Relational)
# users table:
# | id | name  | email           |
# |----|-------|-----------------|
# | 1  | Tarun | tarun@gmail.com |
```

ORM automatically Python class ko database table mein convert karta hai!

---

## 1.3 SQLAlchemy Core vs ORM

| Feature | Core | ORM |
|---------|------|-----|
| Approach | SQL-like syntax | Python classes |
| Control | Zyada control | Kam control, zyada convenience |
| Speed | Thoda faster | Thoda slower (but negligible) |
| Use Case | Complex queries, reporting | CRUD APIs, web apps |
| Learning | SQL knowledge zaruri | Python knowledge enough |

**Rule of Thumb:**
- Beginners → ORM use karo
- FastAPI APIs → ORM use karo
- Complex analytics/reporting → Core use karo

---

# 📚 PART 2: Installation & Setup

---

## 2.1 Installation

```bash
pip install sqlalchemy
```

**FastAPI ke saath:**
```bash
pip install sqlalchemy fastapi uvicorn
```

**Async support ke liye:**
```bash
pip install sqlalchemy[asyncio] asyncpg  # PostgreSQL
pip install sqlalchemy[asyncio] aiosqlite  # SQLite async
```

---

## 2.2 Database URL Formats

| Database | URL Format |
|----------|------------|
| SQLite | `sqlite:///./database.db` |
| PostgreSQL | `postgresql://user:password@localhost:5432/dbname` |
| MySQL | `mysql+pymysql://user:password@localhost/dbname` |
| PostgreSQL Async | `postgresql+asyncpg://user:password@localhost:5432/dbname` |

**SQLite Special:**
- `sqlite:///./test.db` → Current folder mein test.db file
- `sqlite:///:memory:` → RAM mein temporary DB (testing ke liye)

---

# 📚 PART 3: Core Components (Deep Dive)

---

## 3.1 Engine — Database ka Gateway

**Kya karta hai?**
- Database se connection establish karta hai
- Connection pool manage karta hai
- SQL queries execute karta hai

**Code:**
```python
from sqlalchemy import create_engine

# SQLite example
engine = create_engine("sqlite:///./app.db")

# PostgreSQL example
engine = create_engine("postgresql://user:pass@localhost/mydb")

# With options
engine = create_engine(
    "sqlite:///./app.db",
    echo=True,  # SQL queries print karo (debugging)
    connect_args={"check_same_thread": False}  # SQLite specific
)
```

**Analogy:**
Engine = Hotel ka main gate  
Sab guests (queries) isi gate se enter/exit karte hain

---

## 3.2 Session — Database se Baat karne ka Tarika

**Kya karta hai?**
- Database operations handle karta hai
- Transactions manage karta hai (commit/rollback)
- Objects track karta hai

**Code:**
```python
from sqlalchemy.orm import sessionmaker

# Session factory banao
SessionLocal = sessionmaker(
    autocommit=False,   # Manual commit karna padega
    autoflush=False,    # Manual flush karna padega
    bind=engine         # Kis engine se connect karna hai
)

# Session use karo
session = SessionLocal()
```

**Analogy:**
Session = Waiter  
- Order leta hai (add)
- Kitchen ko bhejta hai (commit)
- Galti ho toh cancel karta hai (rollback)

---

## 3.3 Base — Models ka Parent

**Kya karta hai?**
- Sab models (tables) isse inherit karte hain
- SQLAlchemy ko batata hai ki kaunse classes tables hain

**Code:**
```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Sab models Base se inherit karenge
class User(Base):
    __tablename__ = "users"
    # ...

class Product(Base):
    __tablename__ = "products"
    # ...
```

**Analogy:**
Base = Blueprint template  
Sab buildings (tables) isi template se banti hain

---

## 3.4 Complete Setup File (database.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Database URL
DATABASE_URL = "sqlite:///./app.db"

# 2. Engine create karo
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite only
)

# 3. Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 4. Base class
Base = declarative_base()

# 5. Dependency function (FastAPI ke liye)
def get_db():
    """
    Har request ke liye:
    1. Naya session banao
    2. Use karo
    3. Finally close karo
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

# 📚 PART 4: Models (Tables) — Deep Dive

---

## 4.1 Basic Model Structure

```python
from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users"  # Table ka naam
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
```

---

## 4.2 Column Types — Complete List

| Python/SQLAlchemy | Database | Use Case |
|-------------------|----------|----------|
| `Integer` | INT | IDs, counts |
| `String(50)` | VARCHAR(50) | Short text |
| `Text` | TEXT | Long text |
| `Boolean` | BOOLEAN | True/False |
| `Float` | FLOAT | Decimal numbers |
| `DateTime` | DATETIME | Date + time |
| `Date` | DATE | Only date |
| `Time` | TIME | Only time |
| `Enum` | ENUM | Fixed choices |
| `JSON` | JSON | JSON data |

**Import:**
```python
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, 
    Float, DateTime, Date, Time, Enum, JSON
)
```

---

## 4.3 Column Options — Complete List

| Option | Meaning | Example |
|--------|---------|---------|
| `primary_key=True` | Primary key (unique ID) | `id = Column(Integer, primary_key=True)` |
| `unique=True` | Value unique hona chahiye | `email = Column(String, unique=True)` |
| `index=True` | Fast search ke liye index | `email = Column(String, index=True)` |
| `nullable=False` | NULL allowed nahi | `name = Column(String, nullable=False)` |
| `default=value` | Default value | `is_active = Column(Boolean, default=True)` |
| `server_default` | DB level default | `Column(DateTime, server_default=func.now())` |

---

## 4.4 Complete Model Examples

### User Model
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

### Product Model
```python
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    category = Column(String(100), index=True)
```

### Order Model
```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="orders")
```

---

## 4.5 OOP Methods in Models

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    
    # Instance Method
    def greet(self):
        """Object ka data use karta hai"""
        return f"Hello, {self.name}!"
    
    def deactivate(self):
        """User ko deactivate karo"""
        self.is_active = False
    
    # Static Method
    @staticmethod
    def table_info():
        """Class/object dono se call ho sakta hai"""
        return "This is the users table"
    
    # Class Method
    @classmethod
    def create_admin(cls, name, email):
        """Naya admin user banao"""
        return cls(name=name, email=email, is_admin=True)
    
    # String representation
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"
```

**Usage:**
```python
# Instance method
user = User(name="Tarun", email="t@gmail.com")
print(user.greet())  # Hello, Tarun!

# Static method
print(User.table_info())  # This is the users table

# Class method
admin = User.create_admin("Admin", "admin@gmail.com")
```

---

# 📚 PART 5: CRUD Operations — Complete Guide

---

## 5.1 CREATE — Naya Record Banana

### Basic Create
```python
# 1. Object banao
new_user = User(name="Tarun", email="tarun@gmail.com")

# 2. Session mein add karo
db.add(new_user)

# 3. Database mein save karo
db.commit()

# 4. Generated values load karo (like id)
db.refresh(new_user)

print(new_user.id)  # Ab id available hai
```

### Bulk Create (Multiple Records)
```python
users = [
    User(name="User1", email="u1@gmail.com"),
    User(name="User2", email="u2@gmail.com"),
    User(name="User3", email="u3@gmail.com"),
]

db.add_all(users)
db.commit()
```

### Create with Error Handling
```python
from sqlalchemy.exc import IntegrityError

try:
    new_user = User(name="Tarun", email="existing@gmail.com")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
except IntegrityError:
    db.rollback()
    print("Email already exists!")
```

---

## 5.2 READ — Records Padhna

### Get All Records
```python
users = db.query(User).all()
# Returns: List of User objects
```

### Get One Record by ID
```python
# Method 1: filter + first
user = db.query(User).filter(User.id == 5).first()

# Method 2: get (older API)
user = db.query(User).get(5)
```

### Filter Records
```python
# Single condition
active_users = db.query(User).filter(User.is_active == True).all()

# Multiple conditions (AND)
users = db.query(User).filter(
    User.is_active == True,
    User.name == "Tarun"
).all()

# OR condition
from sqlalchemy import or_
users = db.query(User).filter(
    or_(User.name == "Tarun", User.name == "Rahul")
).all()
```

### Search (LIKE Query)
```python
# Contains (case-sensitive)
users = db.query(User).filter(User.name.like("%tarun%")).all()

# Contains (case-insensitive) - PostgreSQL
users = db.query(User).filter(User.name.ilike("%tarun%")).all()

# Starts with
users = db.query(User).filter(User.name.like("Tar%")).all()

# Ends with
users = db.query(User).filter(User.name.like("%run")).all()
```

### Pagination
```python
# Skip first 10, get next 10
users = db.query(User).offset(10).limit(10).all()

# Page-based pagination
def get_users_page(db, page: int = 1, per_page: int = 10):
    skip = (page - 1) * per_page
    return db.query(User).offset(skip).limit(per_page).all()
```

### Ordering
```python
# Ascending
users = db.query(User).order_by(User.name).all()

# Descending
users = db.query(User).order_by(User.name.desc()).all()

# Multiple columns
users = db.query(User).order_by(User.is_active.desc(), User.name).all()
```

### Count
```python
total = db.query(User).count()
active_count = db.query(User).filter(User.is_active == True).count()
```

### Select Specific Columns
```python
# Only names and emails
results = db.query(User.name, User.email).all()
# Returns: List of tuples [(name, email), ...]
```

---

## 5.3 UPDATE — Record Update Karna

### Update Single Record
```python
# 1. Record dhundo
user = db.query(User).filter(User.id == 5).first()

# 2. Value change karo
user.name = "New Name"
user.email = "newemail@gmail.com"

# 3. Save karo
db.commit()

# 4. (Optional) Refresh karo
db.refresh(user)
```

### Bulk Update
```python
# Sab inactive users ko active karo
db.query(User).filter(User.is_active == False).update(
    {"is_active": True}
)
db.commit()
```

### Update with Dictionary
```python
user = db.query(User).filter(User.id == 5).first()
update_data = {"name": "New Name", "email": "new@gmail.com"}

for key, value in update_data.items():
    setattr(user, key, value)

db.commit()
```

---

## 5.4 DELETE — Record Delete Karna

### Hard Delete (Permanent)
```python
# 1. Record dhundo
user = db.query(User).filter(User.id == 5).first()

# 2. Delete karo
db.delete(user)

# 3. Save karo
db.commit()
```

### Soft Delete (Recommended)
```python
# is_active = False set karo, delete mat karo
user = db.query(User).filter(User.id == 5).first()
user.is_active = False
db.commit()

# Ab queries mein sirf active users fetch karo
active_users = db.query(User).filter(User.is_active == True).all()
```

### Bulk Delete
```python
# Sab inactive users delete karo
db.query(User).filter(User.is_active == False).delete()
db.commit()
```

---

# 📚 PART 6: Relationships — Tables Ko Connect Karna

---

## 6.1 One-to-Many Relationship

**Example:** Ek User ke multiple Posts ho sakte hain

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    # Relationship: User -> Posts
    posts = relationship("Post", back_populates="owner")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationship: Post -> User
    owner = relationship("User", back_populates="posts")
```

**Usage:**
```python
# User ke posts access karo
user = db.query(User).first()
print(user.posts)  # List of Post objects

# Post ka owner access karo
post = db.query(Post).first()
print(post.owner.name)  # User name
```

---

## 6.2 Many-to-Many Relationship

**Example:** Users aur Roles (Ek user multiple roles, ek role multiple users)

```python
from sqlalchemy import Table

# Association table
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id"))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    roles = relationship("Role", secondary=user_roles, back_populates="users")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    users = relationship("User", secondary=user_roles, back_populates="roles")
```

---

# 📚 PART 7: FastAPI Integration

---

## 7.1 Complete Project Structure

```
project/
├── database.py      # Engine, Session, Base, get_db
├── models.py        # SQLAlchemy models
├── schemas.py       # Pydantic schemas
├── routers/
│   └── users.py     # API endpoints
└── main.py          # FastAPI app
```

---

## 7.2 Pydantic Schemas (schemas.py)

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

# Create ke liye (request body)
class UserCreate(BaseModel):
    name: str
    email: EmailStr

# Update ke liye
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

# Response ke liye
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    
    class Config:
        orm_mode = True  # SQLAlchemy objects se read kar sake
```

---

## 7.3 Router with CRUD (routers/users.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserUpdate, UserOut

router = APIRouter(prefix="/users", tags=["Users"])

# CREATE
@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# READ ALL
@router.get("/", response_model=List[UserOut])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

# READ ONE
@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# UPDATE
@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

# DELETE
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return None
```

---

## 7.4 Main App (main.py)

```python
from fastapi import FastAPI
from .database import engine, Base
from .routers import users

# Tables create karo
Base.metadata.create_all(bind=engine)

app = FastAPI(title="My API")

# Routers include karo
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "API is running!"}
```

---

# 📚 PART 8: Common Mistakes & Solutions

---

## Mistake 1: Session Close Na Karna

❌ **Problem:**
```python
db = SessionLocal()
users = db.query(User).all()
# db.close() missing!
```

✅ **Solution:**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Always close!
```

---

## Mistake 2: Commit Bhool Jana

❌ **Problem:**
```python
db.add(user)
# db.commit() missing - data save nahi hoga!
```

✅ **Solution:**
```python
db.add(user)
db.commit()
db.refresh(user)
```

---

## Mistake 3: Tables Create Na Karna

❌ **Problem:**
```python
# Models banaye but tables create nahi kiye
# Error: Table doesn't exist
```

✅ **Solution:**
```python
# main.py mein add karo
Base.metadata.create_all(bind=engine)
```

---

## Mistake 4: Wrong Import Path

❌ **Problem:**
```python
from database import Base  # ImportError!
```

✅ **Solution:**
```python
from .database import Base  # Relative import
# Ya
from project.database import Base  # Absolute import
```

---

## Mistake 5: SQLite Threading Issue

❌ **Problem:**
```python
engine = create_engine("sqlite:///./app.db")
# Error: SQLite objects created in a thread...
```

✅ **Solution:**
```python
engine = create_engine(
    "sqlite:///./app.db",
    connect_args={"check_same_thread": False}
)
```

---

# 📚 PART 9: Best Practices

---

## 1. Always Use Transactions

```python
try:
    db.add(user)
    db.add(order)
    db.commit()
except Exception:
    db.rollback()
    raise
```

## 2. Use Indexes for Frequently Searched Columns

```python
email = Column(String, index=True)  # Fast search
```

## 3. Use Soft Delete Instead of Hard Delete

```python
user.is_active = False  # Soft delete
# Instead of
db.delete(user)  # Hard delete
```

## 4. Validate Data with Pydantic

```python
class UserCreate(BaseModel):
    email: EmailStr  # Automatic email validation
    name: str
```

## 5. Use Environment Variables for DB Credentials

```python
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
```

---

# 📚 PART 10: Quick Reference Cheatsheet

---

## Imports
```python
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
```

## Setup
```python
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```

## CRUD Quick Reference
```python
# Create
db.add(obj); db.commit(); db.refresh(obj)

# Read
db.query(Model).all()
db.query(Model).filter(Model.id == 1).first()

# Update
obj.field = "value"; db.commit()

# Delete
db.delete(obj); db.commit()
```

## Common Filters
```python
.filter(Model.field == value)
.filter(Model.field.like("%search%"))
.filter(Model.field.in_([1, 2, 3]))
.filter(Model.field.between(10, 20))
.filter(Model.field.is_(None))
.filter(Model.field.isnot(None))
```

---

# 🎯 Summary

1. **Engine** = DB connection
2. **Session** = Transaction manager
3. **Base** = Models ka parent
4. **Model** = Table ka Python class
5. **CRUD** = Create, Read, Update, Delete
6. **Relationships** = Tables ko connect karna
7. **Pydantic** = Request/Response validation
8. **get_db** = Dependency injection

---

**Yeh documentation complete hai! Isko bookmark karo aur reference ke liye use karo.**
