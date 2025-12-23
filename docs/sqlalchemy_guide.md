# 🚀 SQLAlchemy + FastAPI — Clean Industry Guide (Hindi / English mix)

---

## 📌 Overview
This guide explains SQLAlchemy (ORM and Core) with FastAPI integration, practical industry examples, common pitfalls, and solutions — written in a concise and clean format with mixed Hindi/English explanations.

Audience: beginners to intermediate (FastAPI backend devs who want production-level understanding).

---

## 📋 Table of Contents
1. Quick Summary
2. Why use SQLAlchemy? (Real reasons)
3. Core vs ORM — When to choose which
4. Quickstart: Engine, Session, Base
5. Models: defining tables with examples
6. CRUD: Create, Read, Update, Delete (in-depth)
7. Relationships: One-to-Many, Many-to-One, Many-to-Many
8. Dependency Injection with FastAPI (get_db)
9. Async SQLAlchemy — when & how
10. Real-world features: Search, Pagination, Soft Delete
11. Migrations (Alembic) — why and how
12. Testing, Logging, Monitoring
13. Common mistakes & solutions (detailed)
14. Performance & Optimization tips
15. Security and best practices
16. Quick snippets & cheatsheet
17. Further reading & references

---

## 1. Quick Summary
- SQLAlchemy = Python's DB toolkit (Core + ORM).
- ORM maps tables to Python classes — easy CRUD.
- Session = Unit of Work (add, commit, rollback).
- Use `async` SQLAlchemy + FastAPI for high-concurrency apps.

> Fast tip: Start with ORM for APIs; move to Core for very optimized/complex SQL.

---

## 2. Why use SQLAlchemy? (Real reasons)
- Clean code: SQL expressed through Python constructs.
- Security: parameterized queries by default -> less SQL injection risk.
- Maintainability: migrations, models, and tests keep code reliable.
- Team scale: clear structure (models/schemas/routers) helps teams collaborate.

Real-world example: In an e-commerce app, transactions (create order, deduct stock, save invoice) are safer when handled via sessions and explicit commits.

---

## 3. Core vs ORM — When to choose which
- Core: When you need full SQL control and micro-optimizations (reporting, complex joins).
- ORM: When you want speed of development and readable business logic.

Rule of thumb: Use ORM for CRUD endpoints; use Core or raw SQL for analytical/reporting queries.

---

## 4. Quickstart — Engine, Session, Base
File: `database.py` (single source of truth)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./app.db"  # dev; use PostgreSQL/MySQL in prod

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- `engine`: DB connection manager
- `SessionLocal()`: gives you a session (transaction scope)
- `Base`: models inherit from this, used to create tables

---

## 5. Models: Defining Tables (clean examples)
File: `models/user.py`

```python
from sqlalchemy import Column, Integer, String, Boolean
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)

    def greet(self):
        return f"Hi, {self.name}!"

    @staticmethod
    def table_info():
        return "users table: stores user accounts"

    @classmethod
    def create_active(cls, name, email):
        return cls(name=name, email=email, is_active=True)
```

Notes:
- Keep model logic minimal; heavier business logic belongs in service layer.
- OOP methods help for small helpers/tests.

---

## 6. CRUD — In-depth with patterns
Use Pydantic for validation (`schemas/user.py`), and keep DB logic inside routers or services.

### Create (best practice)
```python
# routers/user.py
@router.post("/users", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # load generated fields (id)
    return new_user
```

Why `db.refresh`? Because after commit SQLAlchemy can fetch DB-generated values (like `id`).

### Read
```python
@router.get("/users", response_model=list[UserOut])
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()
```

### Update (pattern)
```python
@router.put("/users/{id}")
def update_user(id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(404)
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user
```

### Delete (soft vs hard)
- Hard delete: `db.delete(user)` + `db.commit()`
- Soft delete (recommended in many apps): `user.is_active = False` + `db.commit()`

Reason: soft delete preserves history, enables recovery, and avoids accidental data loss.

---

## 7. Relationships — simple real-world patterns
### One-to-many (User → Posts)
```python
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="posts")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    posts = relationship("Post", back_populates="owner")
```

Use `join` or `selectinload` for efficient eager loading.

---

## 8. Dependency Injection (FastAPI) — why this pattern
- Each request gets its own DB session.
- Ensures proper closing and avoids shared sessions across requests.

Example (sync):
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
Use `Depends(get_db)` in routes.

---

## 9. Async SQLAlchemy (when to use)
- Use Async if your app is I/O bound and needs high concurrency (many simultaneous requests).
- Use `sqlalchemy.ext.asyncio` with `asyncpg` for PostgreSQL.

Quick example (async engine):
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@host/db")
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

Note: Async code patterns differ (use `await session.execute(...)`).

---

## 10. Real-world features & patterns
### Search (LIKE)
```python
users = db.query(User).filter(User.name.ilike(f"%{q}%")).all()
```
Use `ilike` for case-insensitive search (Postgres). For large datasets use full-text search or external search engines (Elasticsearch).

### Pagination
Use `offset` + `limit`, or cursor-based pagination for large datasets.

### Soft Delete & Archival
- Add `is_active` or `deleted_at` field.
- Keep records for auditing, analytics.

### Transactions across multiple operations
Wrap related DB changes in a single transaction to ensure atomicity.

---

## 11. Migrations (Alembic)
Why: Model changes need migration scripts to update DB schema safely.

Quick Alembic flow:
```
alembic init alembic
alembic revision --autogenerate -m "create users"
alembic upgrade head
```
Add migration scripts to repo; always review autogenerated migrations.

---

## 12. Testing, Logging, Monitoring
- Use a separate test DB (SQLite in-memory or test Postgres).
- Use `pytest` with `TestClient` for API tests.
- Add SQL logging (engine echo) for debugging; disable in prod.
- Monitor slow queries and add indexes for performance-critical columns.

---

## 13. Common mistakes & solutions (detailed)
1. Forgetting to close sessions → memory leak
   - Solution: use dependency pattern and `finally: db.close()`

2. Not committing after changes
   - Solution: always `db.commit()` after creates/updates/deletes

3. Using `.get()` without import or using stale API
   - Solution: prefer `session.query(Model).get(id)` in older versions, or `session.get(Model, id)` in newer API

4. Blocking calls in async endpoints (e.g., `time.sleep`)
   - Solution: use `await asyncio.sleep(…)` or run blocking calls in a threadpool

5. N+1 queries when loading relationships
   - Solution: use `selectinload` or `joinedload` to eager load

6. Wrong connect args for SQLite
   - Solution: `create_engine(DATABASE_URL, connect_args={"check_same_thread": False})`

7. Relying on ORM for heavy aggregations
   - Solution: write optimized SQL via Core or raw SQL for complex aggregations

---

## 14. Performance & Optimization tips
- Add indexes on frequently filtered columns (email, foreign keys)
- Use `selectinload` / `joinedload` to avoid N+1
- For bulk inserts use `session.bulk_save_objects` (but be aware of caveats)
- Use EXPLAIN ANALYZE to inspect slow queries

---

## 15. Security & Best Practices
- Validate input with Pydantic
- Avoid raw SQL unless necessary; use parameterized queries
- Use migrations for schema changes and review them
- Store DB credentials in environment variables
- Implement authentication/authorization (e.g., JWT)

---

## 16. Quick Snippets & Cheatsheet
Create:
```python
u = User(name="Tarun", email="t@example.com")
db.add(u); db.commit(); db.refresh(u)
```
Read:
```python
u = db.query(User).filter(User.email == "t@example.com").first()
```
Update:
```python
u.name = "New"; db.commit(); db.refresh(u)
```
Delete:
```python
db.delete(u); db.commit()
```

---

## 17. Further Reading
- Official SQLAlchemy docs: https://docs.sqlalchemy.org/
- FastAPI SQL Databases guide: https://fastapi.tiangolo.com/tutorial/sql-databases/
- Alembic Migrations: https://alembic.sqlalchemy.org/

---

### Final Note
Yeh guide production-ready concepts ko concise aur clear tarike se cover karta hai. Agar chaho, main isko aur expand karke: examples, tests, and a mini-project walkthrough (user->posts->comments) add kar dunga.

**Next step suggestion:** Add a small example app in the repo (`examples/sqlalchemy_app`) with tests and Alembic migrations so you can run and experiment.
