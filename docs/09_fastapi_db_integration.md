# 09 — FastAPI + Database Integration (Complete In-Depth Guide)

> 🎯 **Goal**: FastAPI ko SQLAlchemy se connect karna seekho - production-ready setup!

---

## 📚 Table of Contents
1. [Integration Kya Hai?](#integration-kya-hai)
2. [Setup Step by Step](#setup-step-by-step)
3. [Database Dependency](#database-dependency)
4. [Models aur Schemas](#models-aur-schemas)
5. [CRUD Endpoints](#crud-endpoints)
6. [Error Handling](#error-handling)
7. [Relationships in API](#relationships-in-api)
8. [Validation Patterns](#validation-patterns)
9. [Complete Example](#complete-example)
10. [Industry Best Practices](#industry-best-practices)
11. [Practice Exercises](#practice-exercises)

---

## Integration Kya Hai?

### Samjho Pehle - Kya Connect Karna Hai?

```
User Request --> FastAPI --> SQLAlchemy --> Database
                   ↓              ↓
              Pydantic        ORM Models
              (Validation)   (Database Tables)
```

**Teen cheezein connect ho rahi hain:**

1. **FastAPI** - Web framework jo HTTP requests handle karta hai
2. **Pydantic** - Data validation aur serialization (request/response)
3. **SQLAlchemy** - Database operations (CRUD)

### Kyun Do Alag Models (Pydantic + SQLAlchemy)?

```python
# ❓ Question: Kyun do models chahiye?

# SQLAlchemy Model - Database ke liye
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(100))
    hashed_password = Column(String(100))  # Hashed password store

# Pydantic Schema - API ke liye
class UserCreate(BaseModel):
    email: str
    password: str  # Plain password receive (hash karenge)

class UserResponse(BaseModel):
    id: int
    email: str
    # password NAHI - client ko nahi bhejna!
```

**Kyun alag?**
1. **Security**: Password hash database mein, plain API mein - alag handle
2. **Flexibility**: API response mein sab fields nahi bhejna hota
3. **Validation**: Pydantic automatic validate karta hai input
4. **Conversion**: SQLAlchemy object → JSON automatic

---

## Setup Step by Step

### Step 1: Directory Structure Banao

```
app/
├── main.py              # FastAPI app
├── database.py          # Database connection
├── models.py            # SQLAlchemy models (tables)
├── schemas.py           # Pydantic schemas (validation)
├── crud.py              # Database operations
└── requirements.txt
```

**Kyun alag files?**
- **Separation of Concerns**: Har file ka ek kaam
- **Maintainability**: Easy to find and fix issues
- **Testing**: Individual components test kar sakte ho

### Step 2: Database Connection (database.py)

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL - SQLite use kar rahe hain (simple)
# Format: dialect://username:password@host:port/database
DATABASE_URL = "sqlite:///./app.db"

# PostgreSQL example:
# DATABASE_URL = "postgresql://user:password@localhost:5432/mydb"

# Engine banao - yeh database se "connection factory" hai
# Socho ise as a "phone exchange" jo calls connect karta hai
engine = create_engine(
    DATABASE_URL,
    # SQLite specific setting - multiple threads allow karo
    connect_args={"check_same_thread": False}
)

# Session Factory - har request ke liye new session
# Session = ek conversation with database
# Socho jaise phone call - start, baat karo, end
SessionLocal = sessionmaker(
    autocommit=False,  # Manually commit karenge
    autoflush=False,   # Manually flush karenge
    bind=engine        # Konsa database use karna hai
)

# Base class for all models
# Sab models isse inherit karenge
Base = declarative_base()
```

**Concepts Explained:**

1. **Engine**: Database connection pool manage karta hai
   - Pool = pre-made connections ka set
   - Har baar new connection banana slow, pool se fast milta hai

2. **SessionLocal**: Session factory hai
   - Factory pattern: jab chahiye tab new session banao
   - Har request ke liye ek session - isolation

3. **Base**: Parent class for all models
   - SQLAlchemy ko batata hai ki "yeh sab tables hain"
   - `Base.metadata` mein sab tables ki info hoti hai

### Step 3: Models (models.py)

```python
# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    """
    User table - users ki information store karta hai
    
    Yeh SQLAlchemy model hai - database table represent karta hai
    Jab tum User object banate ho, woh database row ban jaata hai
    """
    __tablename__ = "users"  # Table ka naam database mein
    
    # Primary Key - har row ka unique identifier
    # index=True - searching fast hogi is column pe
    id = Column(Integer, primary_key=True, index=True)
    
    # Email - unique hona chahiye (2 users same email nahi)
    email = Column(String(100), unique=True, index=True, nullable=False)
    
    # Password - hashed store karenge, plain text nahi!
    hashed_password = Column(String(100), nullable=False)
    
    # Name - optional hai (nullable=True default)
    name = Column(String(100))
    
    # Active status - default True (new user active hai)
    is_active = Column(Boolean, default=True)
    
    # Timestamps - kab create hua, kab update hua
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship - User ke posts (One-to-Many)
    # back_populates: dono sides ko link karta hai
    posts = relationship("Post", back_populates="author")
    
    def __repr__(self):
        """Debug ke liye - print karne pe readable output"""
        return f"<User(id={self.id}, email='{self.email}')>"


class Post(Base):
    """
    Post table - blog posts store karta hai
    Har post ek user se belong karta hai (ForeignKey)
    """
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(String, nullable=False)  # TEXT type
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Key - kis user ka post hai?
    # ForeignKey("users.id") = users table ka id column reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationship reverse side
    author = relationship("User", back_populates="posts")
```

**Relationship Explained:**

```
User (1) -------- (*) Post
 |                     |
 | posts              | author
 ↓                     ↓
[Post1, Post2]       User object

# User side se:
user.posts  # List of posts by this user

# Post side se:  
post.author  # User who wrote this post
```

### Step 4: Pydantic Schemas (schemas.py)

```python
# schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# ============================================
# USER SCHEMAS
# ============================================

class UserBase(BaseModel):
    """
    Base schema - common fields jo create aur response dono mein hain
    
    Inheritance use karte hain taaki code repeat na ho:
    UserBase <-- UserCreate (add password)
             <-- UserResponse (add id, timestamps)
    """
    email: EmailStr  # Email validation automatic!
    name: Optional[str] = None  # Optional field

class UserCreate(UserBase):
    """
    User create karte waqt client yeh bhejega
    
    Password plain text mein aayega (HTTPS pe encrypted)
    Hum isko hash karke store karenge
    """
    password: str = Field(..., min_length=8, description="Minimum 8 characters")

class UserUpdate(BaseModel):
    """
    User update karte waqt - sab fields optional
    
    Kyun sab optional? Partial update ke liye!
    User sirf name change karna chahta hai toh sirf name bheje
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """
    API response mein yeh bhejenge
    
    Notice: password NAHI hai! Security ke liye
    orm_mode = True: SQLAlchemy object se directly convert
    """
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        # ORM mode allows: UserResponse.from_orm(sqlalchemy_user)
        # Bina iske, SQLAlchemy object se Pydantic object nahi ban sakta
        orm_mode = True

class UserWithPosts(UserResponse):
    """
    User with their posts - nested relationship
    
    Jab user details ke saath unke posts bhi chahiye
    """
    posts: List["PostResponse"] = []  # Forward reference

# ============================================
# POST SCHEMAS  
# ============================================

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)

class PostCreate(PostBase):
    """Post create - title aur content chahiye"""
    pass  # UserBase se sab aa gaya

class PostUpdate(BaseModel):
    """Post update - sab optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    is_published: Optional[bool] = None

class PostResponse(PostBase):
    """Post response with metadata"""
    id: int
    is_published: bool
    created_at: datetime
    user_id: int
    
    class Config:
        orm_mode = True

class PostWithAuthor(PostResponse):
    """Post with author details"""
    author: UserResponse

# Forward reference update karo
UserWithPosts.update_forward_refs()
```

**Schema Pattern Explained:**

```
                    BaseModel
                        |
                    UserBase (email, name)
                   /    |    \
                  /     |     \
         UserCreate  UserUpdate  UserResponse
         (+password) (all optional) (+id, +timestamps)
                                        |
                                  UserWithPosts
                                  (+posts list)
```

**Kyun yeh pattern?**
1. **DRY (Don't Repeat Yourself)**: Common fields ek jagah
2. **Flexibility**: Har operation ke liye sahi fields
3. **Security**: Response mein sensitive data nahi

---

## Database Dependency

### Dependency Injection Kaise Kaam Karta Hai

```python
# database.py mein add karo

def get_db():
    """
    Database session dependency
    
    Yeh function har request ke liye:
    1. New session create karta hai
    2. Endpoint ko deta hai (yield)
    3. Request complete hone pe close karta hai (finally)
    
    Yield + Finally = Resource Management
    Chahe error aaye ya na aaye, session close hoga
    """
    db = SessionLocal()  # Step 1: Create session
    try:
        yield db  # Step 2: Give to endpoint
    finally:
        db.close()  # Step 3: Cleanup (ALWAYS runs)
```

**Visualize karo:**

```
Request aaya
    ↓
get_db() called
    ↓
db = SessionLocal()  ← New session
    ↓
yield db  ← Endpoint ko mila
    ↓
Endpoint executes (uses db)
    ↓
finally: db.close()  ← Cleanup
    ↓
Response sent
```

**Kyun Dependency Injection?**

```python
# ❌ BAD - Har function mein session create
@app.get("/users")
def get_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return users
    finally:
        db.close()

@app.get("/posts")
def get_posts():
    db = SessionLocal()  # Same code repeat!
    try:
        posts = db.query(Post).all()
        return posts
    finally:
        db.close()

# ✅ GOOD - Dependency Injection
@app.get("/users")
def get_users(db: Session = Depends(get_db)):  # Automatic!
    return db.query(User).all()

@app.get("/posts")  
def get_posts(db: Session = Depends(get_db)):  # Clean!
    return db.query(Post).all()
```

---

## CRUD Operations

### crud.py - Database Operations

```python
# crud.py
from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext

import models
import schemas

# Password hashing setup
# bcrypt = industry standard, secure algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Plain password ko hash mein convert karo
    
    Hash = one-way encryption
    "password123" → "$2b$12$LQv3c1y..."
    Hash se original password nahi nikal sakta (secure!)
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check karo password sahi hai ya nahi
    
    User ne jo password diya, uska hash bana ke compare karo
    stored hash se
    """
    return pwd_context.verify(plain_password, hashed_password)

# ============================================
# USER CRUD
# ============================================

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    Get user by ID
    
    .first() = pehla matching record ya None
    Better than .one() because no exception if not found
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Get user by email
    
    Email se search - login ke time use hota hai
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    Get all users with pagination
    
    skip = kitne records skip karna (offset)
    limit = kitne records lena
    
    Page 1: skip=0, limit=10 (records 1-10)
    Page 2: skip=10, limit=10 (records 11-20)
    """
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Create new user
    
    Steps:
    1. Password hash karo
    2. SQLAlchemy object banao
    3. Database mein add karo
    4. Commit (save permanently)
    5. Refresh (get updated data like ID)
    """
    # Hash password - plain text store mat karo!
    hashed_password = get_password_hash(user.password)
    
    # SQLAlchemy model instance banao
    db_user = models.User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password
    )
    
    # Database mein add karo (abhi memory mein hai)
    db.add(db_user)
    
    # Commit = permanently save to database
    db.commit()
    
    # Refresh = database se latest data lo (auto-generated ID, etc.)
    db.refresh(db_user)
    
    return db_user

def update_user(
    db: Session, 
    user_id: int, 
    user_update: schemas.UserUpdate
) -> Optional[models.User]:
    """
    Update existing user
    
    Partial update: sirf jo fields bheje, wohi update
    exclude_unset=True: None values ignore karo
    """
    # Pehle user find karo
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Update data nikalo (only set fields)
    update_data = user_update.dict(exclude_unset=True)
    
    # Har field update karo
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    # Save changes
    db.commit()
    db.refresh(db_user)
    
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete user
    
    Returns True if deleted, False if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True

# ============================================
# POST CRUD
# ============================================

def create_post(
    db: Session, 
    post: schemas.PostCreate, 
    user_id: int
) -> models.Post:
    """
    Create new post for a user
    
    user_id parameter se owner set karte hain
    """
    db_post = models.Post(
        **post.dict(),  # Unpack all fields from schema
        user_id=user_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_posts(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None
) -> List[models.Post]:
    """
    Get posts with optional user filter
    
    user_id provided = only that user's posts
    user_id None = all posts
    """
    query = db.query(models.Post)
    
    if user_id:
        query = query.filter(models.Post.user_id == user_id)
    
    return query.offset(skip).limit(limit).all()

def get_post(db: Session, post_id: int) -> Optional[models.Post]:
    """Get single post by ID"""
    return db.query(models.Post).filter(models.Post.id == post_id).first()
```

---

## Complete API Endpoints

### main.py - FastAPI Application

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud
import models
import schemas
from database import engine, get_db, Base

# Create all tables (development only!)
# Production mein Alembic migrations use karo
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Blog API",
    description="Complete CRUD example with FastAPI + SQLAlchemy",
    version="1.0.0"
)

# ============================================
# USER ENDPOINTS
# ============================================

@app.post(
    "/users/", 
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
    summary="Create a new user"
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with email and password.
    
    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    - **name**: Optional display name
    
    Returns the created user (without password).
    """
    # Check if email already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return crud.create_user(db=db, user=user)


@app.get(
    "/users/",
    response_model=List[schemas.UserResponse],
    tags=["users"],
    summary="Get all users"
)
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Get list of all users with pagination.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get(
    "/users/{user_id}",
    response_model=schemas.UserWithPosts,
    tags=["users"],
    summary="Get user by ID"
)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID with their posts.
    
    Raises 404 if user not found.
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return db_user


@app.put(
    "/users/{user_id}",
    response_model=schemas.UserResponse,
    tags=["users"],
    summary="Update user"
)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user details. Only provided fields will be updated.
    
    Raises 404 if user not found.
    """
    db_user = crud.update_user(db, user_id, user_update)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return db_user


@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["users"],
    summary="Delete user"
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user permanently.
    
    Raises 404 if user not found.
    """
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return None  # 204 No Content


# ============================================
# POST ENDPOINTS
# ============================================

@app.post(
    "/users/{user_id}/posts/",
    response_model=schemas.PostResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["posts"],
    summary="Create post for user"
)
def create_post_for_user(
    user_id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new post for a specific user.
    
    - User must exist
    - Title and content required
    """
    # Verify user exists
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return crud.create_post(db=db, post=post, user_id=user_id)


@app.get(
    "/posts/",
    response_model=List[schemas.PostWithAuthor],
    tags=["posts"],
    summary="Get all posts"
)
def read_posts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all posts with author information.
    """
    posts = crud.get_posts(db, skip=skip, limit=limit)
    return posts


@app.get(
    "/posts/{post_id}",
    response_model=schemas.PostWithAuthor,
    tags=["posts"],
    summary="Get post by ID"
)
def read_post(post_id: int, db: Session = Depends(get_db)):
    """
    Get a specific post with author details.
    """
    db_post = crud.get_post(db, post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found"
        )
    return db_post


# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health", tags=["health"])
def health_check():
    """Check if API is running"""
    return {"status": "healthy"}
```

---

## Error Handling Patterns

### Custom Exception Handler

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

app = FastAPI()

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """
    Database integrity errors handle karo
    
    Yeh tab hota hai jab:
    - Duplicate unique value (email already exists)
    - Foreign key violation (user doesn't exist)
    - NULL constraint violation
    """
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Database constraint violation",
            "error_type": "integrity_error"
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """
    General database errors
    
    Connection failed, query error, etc.
    """
    # Log the actual error (don't send to client!)
    print(f"Database error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Database error occurred",
            "error_type": "database_error"
        }
    )
```

### Service Layer Pattern (Recommended)

```python
# services/user_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import crud
import schemas

class UserService:
    """
    Service layer - business logic yahan rakho
    
    Benefits:
    1. Endpoints clean rehte hain
    2. Business logic reusable
    3. Testing easy
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: schemas.UserCreate) -> schemas.UserResponse:
        """
        Create user with validation
        
        Business rules:
        - Email unique hona chahiye
        - Password minimum 8 characters (schema mein)
        """
        # Check duplicate email
        existing = crud.get_user_by_email(self.db, user_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = crud.create_user(self.db, user_data)
        return user
    
    def get_user_or_404(self, user_id: int):
        """
        Get user or raise 404
        
        Commonly used pattern - avoid repeating this check
        """
        user = crud.get_user(self.db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        return user

# Dependency
def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)

# Usage in endpoint
@app.post("/users/")
def create_user(
    user: schemas.UserCreate,
    service: UserService = Depends(get_user_service)
):
    return service.create_user(user)
```

---

## Complete Working Example

### File: requirements.txt
```
fastapi
uvicorn[standard]
sqlalchemy
pydantic[email]
passlib[bcrypt]
python-multipart
```

### Run the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload

# Open browser
# http://localhost:8000/docs  <-- Swagger UI
# http://localhost:8000/redoc <-- ReDoc
```

### Test with cURL

```bash
# Create user
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"email": "tarun@example.com", "password": "secret123", "name": "Tarun"}'

# Get all users
curl "http://localhost:8000/users/"

# Get specific user
curl "http://localhost:8000/users/1"

# Create post
curl -X POST "http://localhost:8000/users/1/posts/" \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Post", "content": "Hello World!"}'

# Get all posts
curl "http://localhost:8000/posts/"
```

---

## Industry Best Practices

### 1. Environment Variables for Config

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "change-this-in-production"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()

# database.py mein use karo
from config import settings
engine = create_engine(settings.DATABASE_URL)
```

### 2. Alembic for Migrations

```bash
# Production mein Base.metadata.create_all() mat use karo!
# Alembic use karo for migrations

pip install alembic
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 3. Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_user(db: Session, user: schemas.UserCreate):
    logger.info(f"Creating user with email: {user.email}")
    # ... create user
    logger.info(f"User created successfully: {db_user.id}")
    return db_user
```

---

## Practice Exercises

### Exercise 1: Add Comments
```python
# Blog posts pe comments add karo:
# - Comment model banao (content, post_id, user_id)
# - CRUD operations
# - Endpoints: POST /posts/{id}/comments, GET /posts/{id}/comments
```

### Exercise 2: Add Categories
```python
# Posts ke liye categories:
# - Category model (name, description)
# - Post mein category_id add karo
# - Filter posts by category
```

### Exercise 3: User Authentication
```python
# Login system:
# - POST /login endpoint
# - Verify password
# - Return JWT token (next doc mein detail)
```

---

## Quick Reference

```python
# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint pattern
@app.get("/items/{id}", response_model=ItemResponse)
def get_item(id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item
```

---

## Next Steps

1. **Code practice karo** - Khud se implement karo
2. **Swagger UI use karo** - `/docs` pe test karo
3. **Next doc padho** - `10_alembic_migrations.md`

---

> **Pro Tip**: Pehle samjho, phir likho. Copy-paste se kuch nahi seekhoge! 🚀
