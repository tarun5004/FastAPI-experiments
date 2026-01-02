# 11 — Async SQLAlchemy (Complete In-Depth Guide)

> 🎯 **Goal**: Async SQLAlchemy 2.0 master karo - FastAPI ke saath perfect integration!

---

## 📚 Table of Contents
1. [Sync vs Async Database](#sync-vs-async-database)
2. [Kyun Async SQLAlchemy?](#kyun-async-sqlalchemy)
3. [Setup & Configuration](#setup--configuration)
4. [Async Session Management](#async-session-management)
5. [CRUD Operations (Async)](#crud-operations-async)
6. [Relationships & Lazy Loading](#relationships--lazy-loading)
7. [FastAPI Integration](#fastapi-integration)
8. [Transaction Management](#transaction-management)
9. [Common Patterns](#common-patterns)
10. [Performance Tips](#performance-tips)
11. [Practice Exercises](#practice-exercises)

---

## Sync vs Async Database

### Problem Samjho Pehle

```python
# ❓ Synchronous Database Call kya karta hai?

# Sync approach
def get_users():
    users = db.query(User).all()  # ⏳ Yahan BLOCK ho jayega
    return users

# Timeline:
# Request aya ──────────────────────────────────────────► Response
#              │                    │
#              │ Database query     │
#              │ (500ms wait)       │
#              │   ⏳ BLOCKED       │
#              │   (kuch nahi       │
#              │    kar sakta)      │
#              └────────────────────┘
```

**Problem**: Jab database query chal rahi hai, Python WAIT kar raha hai!
- Ek thread ek hi request handle kar sakta hai
- 1000 concurrent users = 1000 threads chahiye
- Resources waste!

### Async Solution

```python
# ✅ Asynchronous Database Call

async def get_users():
    users = await db.execute(select(User))  # ⏳ Yahan YIELD karega
    return users.scalars().all()

# Timeline:
# Request 1 ─────┐                    ┌─────► Response 1
# Request 2 ─────┼────┐          ┌────┼─────► Response 2
# Request 3 ─────┼────┼────┐┌────┼────┼─────► Response 3
#                │    │    ││    │    │
#                │ DB │ DB ││ DB │    │
#              ──┴────┴────┴┴────┴────┴──
#                 All running concurrently!
```

**Benefit**: Ek thread bahut saari requests handle kar sakta hai!

### Visual Comparison

```
SYNC (Blocking):
Thread 1: [Request 1]----[DB Wait]----[Response 1]
Thread 2:                              [Request 2]----[DB Wait]----[Response 2]
          ←───── 200ms ─────→←───── 200ms ─────→
          Total: 400ms for 2 requests

ASYNC (Non-Blocking):
Thread 1: [Request 1]─┐    ┌─[Response 1]
          [Request 2]─┼────┼─[Response 2]
                      │    │
                    [DB Queries Running Together]
          ←───── 200ms total ─────→
          Total: 200ms for 2 requests!
```

---

## Kyun Async SQLAlchemy?

### Use Cases Jahan Async Best Hai

```python
# 1. High Concurrency APIs
# Jab bahut saare users ek saath requests bhej rahe hon
# E-commerce checkout, Social media feed, etc.

# 2. I/O Bound Operations
# Database queries, File reads, API calls
# CPU kaam nahi kar raha, sirf wait kar raha hai

# 3. Real-time Applications
# WebSockets, Live updates, Chat apps

# 4. Microservices
# Multiple services ko parallel call karna ho
```

### Kab Async USE MAT KARO

```python
# ❌ CPU-Intensive Tasks
# Image processing, ML model inference, Heavy calculations
# Yahan async help nahi karega kyunki CPU busy hai

# ❌ Simple CRUD Apps
# Agar 100 users/day hai, sync kaafi hai
# Async complexity add karti hai

# ❌ Legacy Codebase
# Agar sab kuch sync hai, async migrate karna mushkil
```

---

## Setup & Configuration

### Step 1: Dependencies Install Karo

```bash
# Async database drivers
pip install sqlalchemy[asyncio]  # SQLAlchemy 2.0 async support
pip install aiosqlite            # SQLite async driver
pip install asyncpg              # PostgreSQL async driver (production)
pip install aiomysql             # MySQL async driver
```

### Step 2: Database Configuration

```python
# database.py
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase

# ⭐ Async Database URL
# Notice: "sqlite+aiosqlite" instead of "sqlite"
# Notice: "postgresql+asyncpg" instead of "postgresql"

# SQLite (Development)
DATABASE_URL = "sqlite+aiosqlite:///./app.db"

# PostgreSQL (Production)
# DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"

# MySQL
# DATABASE_URL = "mysql+aiomysql://user:password@localhost:3306/dbname"


# ⭐ Async Engine
# Engine = connection pool manager
# echo=True: SQL queries console pe print hogi (debug ke liye)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Development mein True, Production mein False
    # Connection pool settings
    pool_size=5,          # Kitne connections rakho
    max_overflow=10,      # Extra connections allowed
    pool_timeout=30,      # Wait time for connection
    pool_recycle=1800,    # Recycle connections after 30 min
)


# ⭐ Async Session Factory
# expire_on_commit=False: Object refresh nahi hoga commit ke baad
# Yeh important hai async mein - avoid lazy loading issues
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Important for async!
)


# ⭐ Base Class for Models
class Base(DeclarativeBase):
    """
    SQLAlchemy 2.0 style base class
    
    Old style: Base = declarative_base()
    New style: class Base(DeclarativeBase): pass
    """
    pass


# ⭐ Create Tables (Async version)
async def create_tables():
    """
    Development ke liye - tables create karo
    Production mein Alembic use karo!
    """
    async with engine.begin() as conn:
        # run_sync: sync function ko async context mein run karo
        await conn.run_sync(Base.metadata.create_all)


# ⭐ Cleanup (Application shutdown pe)
async def close_db():
    """Engine dispose karo - connections close hogi"""
    await engine.dispose()
```

**Key Differences Explained:**

| Sync | Async |
|------|-------|
| `create_engine()` | `create_async_engine()` |
| `sessionmaker()` | `async_sessionmaker()` |
| `Session` | `AsyncSession` |
| `sqlite:///` | `sqlite+aiosqlite:///` |
| `postgresql://` | `postgresql+asyncpg://` |

### Step 3: Models (Same as Sync!)

```python
# models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import List, Optional

from database import Base

# ⭐ SQLAlchemy 2.0 Style with Type Hints
class User(Base):
    """
    User model - SQLAlchemy 2.0 style
    
    Mapped[] = type hint for ORM columns
    mapped_column() = new way to define columns
    """
    __tablename__ = "users"
    
    # New 2.0 style - with type hints
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationship
    # lazy="selectin" = async-friendly loading strategy
    posts: Mapped[List["Post"]] = relationship(
        back_populates="author",
        lazy="selectin"  # ⭐ Important for async!
    )

class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(String)
    is_published: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")
```

---

## Async Session Management

### Dependency Injection Pattern

```python
# dependencies.py
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session
from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session dependency
    
    Kaise kaam karta hai:
    1. Request aayi -> Session create
    2. Endpoint use kare -> yield se session milta hai
    3. Request complete -> finally mein close
    
    AsyncGenerator = async version of generator
    yield + async = AsyncGenerator
    """
    async with async_session() as session:
        try:
            yield session
            # Auto-commit nahi hota, manually karna padega
            # ya endpoint mein commit karo
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

**Alternative: Auto-commit Pattern**

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    With auto-commit on success
    
    Success: commit ho jayega
    Error: rollback ho jayega
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()  # ⭐ Auto-commit
        except Exception:
            await session.rollback()
            raise
```

**Context Manager Explained:**

```python
# async with = async context manager

# Yeh:
async with async_session() as session:
    # use session
    pass

# Is equivalent to:
session = async_session()
try:
    # use session
    pass
finally:
    await session.close()
```

---

## CRUD Operations (Async)

### Create (INSERT)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models
import schemas

async def create_user(db: AsyncSession, user_data: schemas.UserCreate) -> models.User:
    """
    Create new user
    
    Sync vs Async differences:
    - db.add() = same
    - db.commit() → await db.commit()
    - db.refresh() → await db.refresh()
    """
    # Hash password (sync operation, await nahi chahiye)
    hashed_password = get_password_hash(user_data.password)
    
    # Model instance create karo
    db_user = models.User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password
    )
    
    # Session mein add karo (sync, await nahi)
    db.add(db_user)
    
    # Commit karo (async!)
    await db.commit()
    
    # Refresh karo - database se generated values lo (ID, timestamps)
    await db.refresh(db_user)
    
    return db_user
```

### Read (SELECT)

```python
async def get_user(db: AsyncSession, user_id: int) -> models.User | None:
    """
    Get single user by ID
    
    ⭐ SQLAlchemy 2.0 Style:
    - db.query(Model) → select(Model)
    - .filter() → .where()
    - .first() → scalars().first()
    """
    # Build query
    query = select(models.User).where(models.User.id == user_id)
    
    # Execute query (async!)
    result = await db.execute(query)
    
    # Get single result
    # scalars() = ORM objects nikalo
    # first() = pehla ya None
    return result.scalars().first()


async def get_users(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100
) -> list[models.User]:
    """
    Get multiple users with pagination
    
    .all() = list of results
    """
    query = (
        select(models.User)
        .offset(skip)
        .limit(limit)
        .order_by(models.User.created_at.desc())
    )
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_user_by_email(db: AsyncSession, email: str) -> models.User | None:
    """Get user by email"""
    query = select(models.User).where(models.User.email == email)
    result = await db.execute(query)
    return result.scalars().first()
```

**Query Result Explained:**

```python
# db.execute() returns a Result object, not ORM objects directly

result = await db.execute(select(User))

# Different ways to extract data:
result.scalars().all()      # List of User objects
result.scalars().first()    # First User or None
result.scalars().one()      # Exactly one User (error if 0 or >1)
result.scalars().one_or_none()  # One User or None (error if >1)

# For raw rows (not ORM):
result.all()        # List of Row tuples
result.fetchone()   # Single Row tuple
```

### Update

```python
async def update_user(
    db: AsyncSession,
    user_id: int,
    user_update: schemas.UserUpdate
) -> models.User | None:
    """
    Update user - two approaches
    """
    # Approach 1: Fetch and update (preferred when need returned object)
    db_user = await get_user(db, user_id)
    if not db_user:
        return None
    
    # Update only provided fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user_bulk(
    db: AsyncSession,
    user_id: int,
    user_update: schemas.UserUpdate
) -> bool:
    """
    Approach 2: Direct UPDATE query (faster, no fetch needed)
    
    Use when:
    - Don't need updated object
    - Bulk updates
    """
    from sqlalchemy import update
    
    query = (
        update(models.User)
        .where(models.User.id == user_id)
        .values(**user_update.dict(exclude_unset=True))
    )
    
    result = await db.execute(query)
    await db.commit()
    
    # rowcount = kitne rows affect hue
    return result.rowcount > 0
```

### Delete

```python
async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    Delete user
    """
    # Approach 1: Fetch then delete
    db_user = await get_user(db, user_id)
    if not db_user:
        return False
    
    await db.delete(db_user)
    await db.commit()
    return True


async def delete_user_direct(db: AsyncSession, user_id: int) -> bool:
    """
    Approach 2: Direct DELETE (faster)
    """
    from sqlalchemy import delete
    
    query = delete(models.User).where(models.User.id == user_id)
    result = await db.execute(query)
    await db.commit()
    
    return result.rowcount > 0
```

---

## Relationships & Lazy Loading

### ⚠️ The Async Lazy Loading Problem

```python
# ❌ PROBLEM: Lazy loading doesn't work with async!

async def get_user_posts_wrong(db: AsyncSession, user_id: int):
    user = await get_user(db, user_id)
    
    # ❌ This will FAIL!
    # user.posts tries to lazy-load, but we're in async context
    posts = user.posts  # MissingGreenlet error!
    return posts

# Error: sqlalchemy.exc.MissingGreenlet: 
# greenlet_spawn has not been called; can't call await_only() here.
```

**Lazy Loading kya hai?**
```
Lazy Loading = Data tab load karo jab access karo

user = get_user(1)  # User load hua
user.posts          # Ab posts load ho rahe (separate query)
                    # ↑ Yeh async mein kaam nahi karta!
```

### Solution 1: Eager Loading with selectinload

```python
from sqlalchemy.orm import selectinload

async def get_user_with_posts(db: AsyncSession, user_id: int):
    """
    Eager loading - related data pehle se load karo
    
    selectinload = SELECT ... WHERE user_id IN (...)
    Single extra query for all related items
    """
    query = (
        select(models.User)
        .options(selectinload(models.User.posts))  # ⭐ Load posts too!
        .where(models.User.id == user_id)
    )
    
    result = await db.execute(query)
    user = result.scalars().first()
    
    # ✅ Now this works!
    print(user.posts)  # Already loaded!
    return user
```

### Solution 2: joinedload (Single Query)

```python
from sqlalchemy.orm import joinedload

async def get_user_with_posts_joined(db: AsyncSession, user_id: int):
    """
    joinedload = LEFT JOIN in single query
    
    Good for one-to-one or small one-to-many
    """
    query = (
        select(models.User)
        .options(joinedload(models.User.posts))
        .where(models.User.id == user_id)
    )
    
    result = await db.execute(query)
    # unique() needed with joinedload to avoid duplicates
    user = result.unique().scalars().first()
    return user
```

### Solution 3: Model mein lazy="selectin" (Recommended)

```python
# models.py mein
class User(Base):
    __tablename__ = "users"
    
    # ... other columns ...
    
    posts: Mapped[List["Post"]] = relationship(
        back_populates="author",
        lazy="selectin"  # ⭐ Default eager loading!
    )

# Ab har jagah automatic load hoga
async def get_user(db: AsyncSession, user_id: int):
    query = select(models.User).where(models.User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    
    # ✅ Works! Posts already loaded
    print(user.posts)
    return user
```

### Loading Strategies Comparison

| Strategy | Query Count | When to Use |
|----------|-------------|-------------|
| `lazy="select"` | N+1 (bad) | ❌ Avoid in async |
| `lazy="selectin"` | 2 queries | ✅ Default for async |
| `joinedload()` | 1 query | Small one-to-one/few |
| `selectinload()` | 2 queries | One-to-many |
| `subqueryload()` | 2 queries | Complex relationships |

---

## FastAPI Integration

### Complete Working Example

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from typing import List

import crud
import schemas
from database import create_tables, close_db
from dependencies import get_db


# ⭐ Lifespan - Startup/Shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management
    
    Startup: Tables create karo
    Shutdown: Connections close karo
    """
    # Startup
    await create_tables()
    print("✅ Database tables created")
    
    yield  # Application running
    
    # Shutdown
    await close_db()
    print("✅ Database connections closed")


app = FastAPI(
    title="Async Blog API",
    lifespan=lifespan
)


# ============================================
# USER ENDPOINTS (All Async!)
# ============================================

@app.post(
    "/users/",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)  # ⭐ Async session
):
    """Create a new user"""
    # Check duplicate email
    existing = await crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    return await crud.create_user(db, user)


@app.get("/users/", response_model=List[schemas.UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all users with pagination"""
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.UserWithPosts)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID with their posts"""
    user = await crud.get_user_with_posts(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User {user_id} not found"
        )
    return user


@app.put("/users/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user details"""
    user = await crud.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a user"""
    success = await crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None
```

---

## Transaction Management

### Basic Transaction

```python
async def create_user_with_post(
    db: AsyncSession,
    user_data: schemas.UserCreate,
    post_data: schemas.PostCreate
) -> models.User:
    """
    Create user AND post in single transaction
    
    Either both succeed, or both fail (rollback)
    """
    try:
        # Create user
        user = models.User(**user_data.dict())
        db.add(user)
        await db.flush()  # Get user.id without committing
        
        # Create post with user ID
        post = models.Post(**post_data.dict(), user_id=user.id)
        db.add(post)
        
        # Commit both together
        await db.commit()
        await db.refresh(user)
        
        return user
        
    except Exception as e:
        await db.rollback()  # Undo everything!
        raise e
```

### Nested Transactions (Savepoints)

```python
async def complex_operation(db: AsyncSession):
    """
    Nested transactions with savepoints
    
    Outer transaction fail → sab rollback
    Inner transaction fail → sirf inner rollback, outer continue
    """
    try:
        # Outer transaction
        user = models.User(email="test@test.com")
        db.add(user)
        await db.flush()
        
        # Savepoint - inner transaction
        async with db.begin_nested() as savepoint:
            try:
                post = models.Post(title="Test", user_id=user.id)
                db.add(post)
                await db.flush()
                
                # Simulate error
                if some_condition:
                    raise ValueError("Post creation failed")
                    
            except Exception:
                # Only inner operation rolled back
                await savepoint.rollback()
                # Continue with outer transaction
        
        await db.commit()
        
    except Exception:
        await db.rollback()
        raise
```

---

## Common Patterns

### Pattern 1: Repository Pattern

```python
# repositories/user_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

class UserRepository:
    """
    Repository = Data access layer
    
    Benefits:
    - Business logic separate from database
    - Easy to test (mock repository)
    - Switch database easily
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_with_posts(self, user_id: int) -> User | None:
        query = (
            select(User)
            .options(selectinload(User.posts))
            .where(User.id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def create(self, user_data: dict) -> User:
        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()
        return user
    
    async def update(self, user: User, update_data: dict) -> User:
        for key, value in update_data.items():
            setattr(user, key, value)
        await self.session.flush()
        return user
    
    async def delete(self, user: User) -> None:
        await self.session.delete(user)


# Usage in FastAPI
async def get_user_repo(db: AsyncSession = Depends(get_db)):
    return UserRepository(db)

@app.get("/users/{id}")
async def get_user(id: int, repo: UserRepository = Depends(get_user_repo)):
    user = await repo.get_by_id(id)
    if not user:
        raise HTTPException(404)
    return user
```

### Pattern 2: Unit of Work

```python
# unit_of_work.py
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session

class UnitOfWork:
    """
    Unit of Work = Transaction boundary manager
    
    Sab repositories ek transaction mein
    Either all commit, or all rollback
    """
    
    def __init__(self):
        self.session: AsyncSession | None = None
    
    async def __aenter__(self):
        self.session = async_session()
        # Initialize repositories
        self.users = UserRepository(self.session)
        self.posts = PostRepository(self.session)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self.session.close()
    
    async def commit(self):
        await self.session.commit()
    
    async def rollback(self):
        await self.session.rollback()


# Usage
async def create_user_with_post(user_data, post_data):
    async with UnitOfWork() as uow:
        user = await uow.users.create(user_data)
        post = await uow.posts.create({**post_data, "user_id": user.id})
        await uow.commit()
        return user
```

---

## Performance Tips

### 1. Use Connection Pool Properly

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,       # Normal load ke liye connections
    max_overflow=10,   # Peak load ke liye extra
    pool_timeout=30,   # Wait time before error
    pool_recycle=1800, # Refresh stale connections
)
```

### 2. Batch Operations

```python
# ❌ BAD - One query per insert
for user_data in users_list:
    user = User(**user_data)
    db.add(user)
    await db.commit()

# ✅ GOOD - All in one transaction
for user_data in users_list:
    user = User(**user_data)
    db.add(user)
await db.commit()  # Single commit for all!

# ✅ BETTER - Bulk insert
from sqlalchemy import insert
await db.execute(
    insert(User),
    [user.dict() for user in users_list]
)
await db.commit()
```

### 3. Avoid N+1 Queries

```python
# ❌ N+1 Problem
users = await get_users(db)  # 1 query
for user in users:
    print(user.posts)  # N queries (one per user)!

# ✅ Solution: Eager loading
query = select(User).options(selectinload(User.posts))
result = await db.execute(query)
users = result.scalars().all()  # 2 queries total!
```

---

## Practice Exercises

### Exercise 1: Async CRUD
```python
# Async CRUD banao:
# - Product model (name, price, stock)
# - Create, Read, Update, Delete operations
# - FastAPI endpoints
```

### Exercise 2: Relationships
```python
# Order system:
# - Customer (one) → Orders (many)
# - Order (one) → OrderItems (many)
# - Proper eager loading
```

### Exercise 3: Transaction
```python
# Money transfer:
# - Deduct from sender
# - Add to receiver
# - Both in single transaction
# - Handle insufficient balance
```

---

## Quick Reference

```python
# Setup
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, class_=AsyncSession)

# CRUD
result = await db.execute(select(Model).where(...))
user = result.scalars().first()
users = result.scalars().all()

db.add(obj)
await db.commit()
await db.refresh(obj)

await db.delete(obj)
await db.commit()

# Eager loading
select(User).options(selectinload(User.posts))

# Transaction
try:
    db.add(obj)
    await db.commit()
except:
    await db.rollback()
    raise
```

---

> **Pro Tip**: Async sirf tab use karo jab I/O bound operations ho. Simple apps ke liye sync kaafi hai! 🚀
