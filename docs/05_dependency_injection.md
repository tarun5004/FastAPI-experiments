# 05 — Dependency Injection in FastAPI (Complete In-Depth Guide)

> 🎯 **Goal**: Dependency Injection (DI) master ban jao - clean, testable, maintainable code likho!

---

## 📚 Table of Contents
1. [What is Dependency Injection?](#what-is-dependency-injection)
2. [Why Use DI?](#why-use-di)
3. [FastAPI Depends()](#fastapi-depends)
4. [Simple Dependencies](#simple-dependencies)
5. [Dependencies with Parameters](#dependencies-with-parameters)
6. [Class-Based Dependencies](#class-based-dependencies)
7. [Nested Dependencies](#nested-dependencies)
8. [Yield Dependencies](#yield-dependencies)
9. [Global Dependencies](#global-dependencies)
10. [Dependency Overrides](#dependency-overrides)
11. [Common Patterns](#common-patterns)
12. [Database Session Dependency](#database-session-dependency)
13. [Authentication Dependencies](#authentication-dependencies)
14. [Testing with DI](#testing-with-di)
15. [Industry Best Practices](#industry-best-practices)
16. [Practice Exercises](#practice-exercises)

---

## What is Dependency Injection?

### Without DI (Tightly Coupled Code)
```python
# ❌ BAD - Database connection hardcoded
class UserService:
    def __init__(self):
        # Hardcoded connection - can't change easily
        self.db = psycopg2.connect("postgresql://localhost/mydb")
    
    def get_user(self, user_id):
        return self.db.query(...)

# Problem:
# - Can't use different database for testing
# - Can't mock the database
# - Hard to change database later
```

### With DI (Loosely Coupled Code)
```python
# ✅ GOOD - Database connection injected
class UserService:
    def __init__(self, db):
        self.db = db  # Injected from outside
    
    def get_user(self, user_id):
        return self.db.query(...)

# Usage
real_db = get_production_database()
user_service = UserService(real_db)

# For testing
fake_db = FakeDatabase()
test_service = UserService(fake_db)  # Easy to test!
```

### Simple Analogy
```
Without DI (Making Tea yourself):
- You go to kitchen
- You boil water
- You add tea leaves
- You make everything yourself

With DI (Ordering Tea):
- You tell someone "I want tea"
- They bring you tea
- You don't care HOW it was made
- You just USE it

FastAPI Depends() = "Someone" who brings you things!
```

---

## Why Use DI?

### Benefits
```python
# 1. TESTABILITY - Easy to test with mocks
def test_get_users():
    fake_db = FakeDatabase()  # Inject fake
    response = get_users(db=fake_db)
    assert response == expected

# 2. REUSABILITY - Same dependency everywhere
@app.get("/users")
def get_users(db: Session = Depends(get_db)):  # Reuse get_db
    ...

@app.get("/products")
def get_products(db: Session = Depends(get_db)):  # Same dependency
    ...

# 3. MAINTAINABILITY - Change once, apply everywhere
# If database connection changes, only update get_db()

# 4. SEPARATION OF CONCERNS
# Endpoint handles HTTP
# Dependency handles database/auth/etc.

# 5. DECLARATIVE - Just declare what you need
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),           # Need database
    current_user: User = Depends(get_current_user)  # Need auth
):
    ...
```

---

## FastAPI Depends()

### Basic Syntax
```python
from fastapi import FastAPI, Depends

app = FastAPI()

# Define a dependency (simple function)
def get_query_params(q: str = None, skip: int = 0, limit: int = 10):
    return {"q": q, "skip": skip, "limit": limit}

# Use the dependency
@app.get("/items")
def read_items(params: dict = Depends(get_query_params)):
    return {"params": params}

# FastAPI will:
# 1. Call get_query_params() automatically
# 2. Pass query parameters to it
# 3. Inject result into read_items()
```

### How It Works
```python
# When request comes to /items?q=test&skip=5&limit=20

# FastAPI does this internally:
# 1. Sees Depends(get_query_params)
# 2. Calls get_query_params(q="test", skip=5, limit=20)
# 3. Gets result: {"q": "test", "skip": 5, "limit": 20}
# 4. Passes result to read_items(params=result)
# 5. Executes read_items()
```

---

## Simple Dependencies

### Function Dependency
```python
from fastapi import FastAPI, Depends, Query

app = FastAPI()

# Simple dependency - returns common query params
def common_parameters(
    q: str = Query(None, min_length=3),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/users")
def get_users(commons: dict = Depends(common_parameters)):
    return {"message": "Users", **commons}

@app.get("/items")
def get_items(commons: dict = Depends(common_parameters)):
    return {"message": "Items", **commons}

# Both endpoints now have same query param handling!
```

### Async Dependency
```python
from fastapi import Depends

async def async_dependency():
    await asyncio.sleep(0.1)  # Some async operation
    return {"async": True}

@app.get("/async")
async def async_endpoint(data: dict = Depends(async_dependency)):
    return data

# Both sync and async dependencies work!
```

### Dependency Without Return
```python
from fastapi import Depends, HTTPException

def verify_api_key(api_key: str = Query(...)):
    if api_key != "secret-key":
        raise HTTPException(status_code=403, detail="Invalid API key")
    # No return - just validates

@app.get("/protected")
def protected_route(_: None = Depends(verify_api_key)):
    return {"message": "You have access!"}
```

---

## Dependencies with Parameters

### Dependency with Configuration
```python
from fastapi import Depends, Query

def pagination(
    default_limit: int = 10  # Parameter for dependency itself
):
    def paginate(
        skip: int = Query(0, ge=0),
        limit: int = Query(default_limit, ge=1, le=100)
    ):
        return {"skip": skip, "limit": limit}
    return paginate

# Different defaults for different endpoints
@app.get("/users")
def get_users(pagination: dict = Depends(pagination(default_limit=20))):
    return pagination

@app.get("/products")
def get_products(pagination: dict = Depends(pagination(default_limit=50))):
    return pagination
```

### Configurable Validator
```python
from fastapi import Depends, HTTPException, Header

def require_role(allowed_roles: list):
    def role_checker(x_role: str = Header(...)):
        if x_role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role must be one of: {allowed_roles}"
            )
        return x_role
    return role_checker

@app.get("/admin")
def admin_route(role: str = Depends(require_role(["admin"]))):
    return {"message": f"Welcome {role}!"}

@app.get("/dashboard")
def dashboard(role: str = Depends(require_role(["admin", "moderator"]))):
    return {"message": f"Dashboard for {role}"}
```

---

## Class-Based Dependencies

### Basic Class Dependency
```python
from fastapi import Depends, Query

class CommonQueryParams:
    def __init__(
        self,
        q: str = Query(None),
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100)
    ):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/items")
def read_items(commons: CommonQueryParams = Depends(CommonQueryParams)):
    return {
        "q": commons.q,
        "skip": commons.skip,
        "limit": commons.limit
    }

# Shorthand (same thing):
@app.get("/items2")
def read_items2(commons: CommonQueryParams = Depends()):
    return {"q": commons.q}
```

### Class with __call__
```python
class VerifyToken:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def __call__(self, token: str = Header(...)):
        # Verify token logic
        if not self.verify(token):
            raise HTTPException(status_code=401, detail="Invalid token")
        return self.decode(token)
    
    def verify(self, token: str) -> bool:
        return token.startswith("Bearer ")
    
    def decode(self, token: str) -> dict:
        return {"user_id": 1, "role": "admin"}

# Create instance with config
token_verifier = VerifyToken(secret_key="my-secret")

@app.get("/profile")
def get_profile(user_data: dict = Depends(token_verifier)):
    return user_data
```

### Reusable Service Class
```python
from fastapi import Depends
from sqlalchemy.orm import Session

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):
        return self.db.query(User).all()
    
    def get_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create(self, user_data: dict):
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        return user

def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)

@app.get("/users")
def get_users(service: UserService = Depends(get_user_service)):
    return service.get_all()

@app.get("/users/{user_id}")
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    return service.get_by_id(user_id)
```

---

## Nested Dependencies

### Chain of Dependencies
```python
from fastapi import Depends, HTTPException, Header

# Level 1: Get API key
def get_api_key(x_api_key: str = Header(...)):
    return x_api_key

# Level 2: Verify API key
def verify_api_key(api_key: str = Depends(get_api_key)):
    if api_key != "valid-key":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# Level 3: Get user from API key
def get_current_user(api_key: str = Depends(verify_api_key)):
    # Look up user by API key
    return {"id": 1, "name": "Tarun", "api_key": api_key}

# Level 4: Check user permissions
def require_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    return user

# Endpoint uses top-level dependency
@app.get("/admin/dashboard")
def admin_dashboard(admin: dict = Depends(require_admin)):
    return {"message": f"Welcome admin {admin['name']}!"}

# Chain: get_api_key -> verify_api_key -> get_current_user -> require_admin
```

### Multiple Dependencies
```python
from fastapi import Depends

def dep_a():
    return "A"

def dep_b():
    return "B"

def dep_c(a: str = Depends(dep_a), b: str = Depends(dep_b)):
    return f"{a} + {b} = C"

@app.get("/combined")
def combined(result: str = Depends(dep_c)):
    return {"result": result}  # "A + B = C"
```

### Dependency Caching
```python
from fastapi import Depends

call_count = 0

def counted_dependency():
    global call_count
    call_count += 1
    print(f"Called {call_count} times")
    return call_count

def dep_that_uses_counted(val: int = Depends(counted_dependency)):
    return val

# By default, same dependency is cached per request
@app.get("/cached")
def cached_endpoint(
    val1: int = Depends(counted_dependency),
    val2: int = Depends(counted_dependency),  # NOT called again!
    val3: int = Depends(dep_that_uses_counted)
):
    return {"val1": val1, "val2": val2, "val3": val3}
    # All return same value - dependency called only once!

# To disable caching:
@app.get("/not-cached")
def not_cached(
    val1: int = Depends(counted_dependency, use_cache=False),
    val2: int = Depends(counted_dependency, use_cache=False)
):
    return {"val1": val1, "val2": val2}  # Different values!
```

---

## Yield Dependencies

### Resource Management
```python
from fastapi import Depends

def get_db():
    db = SessionLocal()  # Create
    try:
        yield db  # Provide to endpoint
    finally:
        db.close()  # Cleanup after endpoint finishes

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    # db is available here
    return db.query(User).all()
    # After this, db.close() is called automatically!
```

### Yield with Error Handling
```python
from fastapi import Depends, HTTPException

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Commit if no error
    except Exception:
        db.rollback()  # Rollback on error
        raise
    finally:
        db.close()  # Always close

# Or with context manager
from contextlib import contextmanager

@contextmanager
def get_db_context():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_db():
    with get_db_context() as db:
        yield db
```

### Async Yield Dependency
```python
from fastapi import Depends

async def get_async_db():
    db = await create_async_session()
    try:
        yield db
    finally:
        await db.close()

@app.get("/async-users")
async def get_users(db = Depends(get_async_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

### Multiple Yield Dependencies
```python
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_redis():
    redis = await aioredis.create_redis_pool("redis://localhost")
    try:
        yield redis
    finally:
        redis.close()
        await redis.wait_closed()

@app.get("/data")
async def get_data(
    db = Depends(get_db),
    redis = Depends(get_redis)
):
    # Both resources available
    # Both cleaned up after endpoint
    ...
```

---

## Global Dependencies

### Apply to All Routes
```python
from fastapi import FastAPI, Depends, HTTPException, Header

async def verify_token(x_token: str = Header(...)):
    if x_token != "valid-token":
        raise HTTPException(status_code=403, detail="Invalid token")

async def log_request():
    print("Request received")

# Apply to entire app
app = FastAPI(dependencies=[Depends(verify_token), Depends(log_request)])

@app.get("/items")
def get_items():
    return {"items": []}

@app.get("/users")
def get_users():
    return {"users": []}

# Both endpoints now require valid token!
```

### Apply to Router
```python
from fastapi import APIRouter, Depends

async def require_auth():
    # Auth check
    pass

# All routes in this router require auth
router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(require_auth)]
)

@router.get("/users")
def admin_users():
    return {"admin": "users"}

@router.get("/settings")
def admin_settings():
    return {"admin": "settings"}

app.include_router(router)
```

### Combine Global and Local
```python
from fastapi import FastAPI, Depends

def global_dep():
    return "global"

def local_dep():
    return "local"

app = FastAPI(dependencies=[Depends(global_dep)])

@app.get("/endpoint")
def endpoint(local: str = Depends(local_dep)):
    # global_dep runs first, then local_dep
    return {"local": local}
```

---

## Dependency Overrides

### For Testing
```python
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

app = FastAPI()

def get_db():
    return "Real Database"

@app.get("/items")
def get_items(db = Depends(get_db)):
    return {"db": db}

# In tests:
def test_get_items():
    def mock_db():
        return "Mock Database"
    
    # Override the dependency
    app.dependency_overrides[get_db] = mock_db
    
    client = TestClient(app)
    response = client.get("/items")
    assert response.json() == {"db": "Mock Database"}
    
    # Clear overrides after test
    app.dependency_overrides.clear()
```

### Complete Testing Example
```python
# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)
    return user

# test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    # Override dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test tables
    Base.metadata.create_all(bind=engine)
    
    yield TestClient(app)
    
    # Cleanup
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

def test_get_user(client):
    response = client.get("/users/1")
    assert response.status_code == 404  # No user yet
```

---

## Common Patterns

### Pattern 1: Pagination Dependency
```python
from fastapi import Depends, Query
from pydantic import BaseModel

class PaginationParams(BaseModel):
    skip: int
    limit: int
    
    class Config:
        frozen = True  # Immutable

def get_pagination(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Records to fetch")
) -> PaginationParams:
    return PaginationParams(skip=skip, limit=limit)

@app.get("/users")
def get_users(pagination: PaginationParams = Depends(get_pagination)):
    return {
        "skip": pagination.skip,
        "limit": pagination.limit
    }
```

### Pattern 2: Current User Dependency
```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

async def get_current_active_user(user: User = Depends(get_current_user)):
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

@app.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
```

### Pattern 3: Permission Dependency
```python
from fastapi import Depends, HTTPException
from enum import Enum
from typing import List

class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

def require_permissions(required: List[Permission]):
    async def check_permissions(user: User = Depends(get_current_user)):
        user_permissions = set(user.permissions)
        required_set = set(required)
        
        if not required_set.issubset(user_permissions):
            missing = required_set - user_permissions
            raise HTTPException(
                status_code=403,
                detail=f"Missing permissions: {missing}"
            )
        return user
    return check_permissions

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permissions([Permission.DELETE, Permission.ADMIN]))
):
    # Only users with DELETE and ADMIN permissions can access
    ...
```

### Pattern 4: Rate Limiter Dependency
```python
from fastapi import Depends, HTTPException, Request
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, requests: int, window: int):
        self.requests = requests
        self.window = window
        self.clients = defaultdict(list)
    
    def __call__(self, request: Request):
        client_ip = request.client.host
        now = time.time()
        
        # Clean old requests
        self.clients[client_ip] = [
            t for t in self.clients[client_ip]
            if now - t < self.window
        ]
        
        # Check limit
        if len(self.clients[client_ip]) >= self.requests:
            raise HTTPException(
                status_code=429,
                detail="Too many requests"
            )
        
        # Add current request
        self.clients[client_ip].append(now)
        return True

# 10 requests per 60 seconds
rate_limiter = RateLimiter(requests=10, window=60)

@app.get("/limited")
def limited_endpoint(_: bool = Depends(rate_limiter)):
    return {"message": "Success"}
```

---

## Database Session Dependency

### SQLAlchemy Session
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Async SQLAlchemy Session
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import Depends

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

### Transaction Management
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_transaction():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session
            # Auto-commits on success, rollbacks on error

async def get_db():
    async with get_db_transaction() as session:
        yield session
```

---

## Authentication Dependencies

### OAuth2 Password Bearer
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_from_db(username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### API Key Authentication
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader, APIKeyQuery

API_KEY = "your-api-key"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

async def get_api_key(
    api_key_header: str = Security(api_key_header),
    api_key_query: str = Security(api_key_query)
):
    api_key = api_key_header or api_key_query
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.get("/protected")
async def protected_route(api_key: str = Security(get_api_key)):
    return {"message": "Access granted", "api_key": api_key}
```

---

## Testing with DI

### Mocking Dependencies
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

# test_main.py
@pytest.fixture
def client():
    # Mock the database
    def mock_get_db():
        mock_db = Mock()
        mock_db.query.return_value.all.return_value = [
            {"id": 1, "name": "Test User"}
        ]
        yield mock_db
    
    app.dependency_overrides[get_db] = mock_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_get_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == 1
```

### Testing Auth Endpoints
```python
@pytest.fixture
def authenticated_client():
    def mock_get_current_user():
        return User(id=1, username="testuser", is_active=True)
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_protected_route(authenticated_client):
    response = authenticated_client.get("/protected")
    assert response.status_code == 200

def test_protected_route_no_auth():
    # Without override, should fail
    client = TestClient(app)
    response = client.get("/protected")
    assert response.status_code == 401
```

---

## Industry Best Practices

### 1. Organize Dependencies
```
app/
├── dependencies/
│   ├── __init__.py
│   ├── auth.py          # Authentication dependencies
│   ├── database.py      # Database session
│   ├── pagination.py    # Pagination
│   └── permissions.py   # Permission checks
├── services/
│   ├── user_service.py
│   └── product_service.py
└── main.py
```

### 2. Type Hints for Dependencies
```python
from typing import Annotated
from fastapi import Depends

# Create type alias
DB = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@app.get("/users")
def get_users(db: DB, user: CurrentUser):
    # Cleaner signature
    return db.query(User).all()
```

### 3. Dependency Factory Pattern
```python
class ServiceFactory:
    @staticmethod
    def get_user_service(db: Session = Depends(get_db)):
        return UserService(db)
    
    @staticmethod
    def get_product_service(db: Session = Depends(get_db)):
        return ProductService(db)

@app.get("/users")
def get_users(service: UserService = Depends(ServiceFactory.get_user_service)):
    return service.get_all()
```

### 4. Error Handling in Dependencies
```python
from fastapi import HTTPException, status

async def get_user_or_404(
    user_id: int,
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return user

@app.get("/users/{user_id}")
def get_user(user: User = Depends(get_user_or_404)):
    return user  # Already validated!
```

---

## Practice Exercises

### Exercise 1: Logging Dependency
```python
# Create a dependency that:
# - Logs request start time
# - Logs request end time (using yield)
# - Calculates and logs duration
```

### Exercise 2: Multi-tenant Dependency
```python
# Create a dependency that:
# - Extracts tenant ID from header
# - Validates tenant exists
# - Returns tenant-specific database session
```

### Exercise 3: Feature Flag Dependency
```python
# Create a dependency that:
# - Checks if a feature is enabled
# - Returns 404 if feature is disabled
# - Allows feature name as parameter
```

---

## Quick Reference

```python
from fastapi import Depends

# Simple dependency
def my_dep():
    return "value"

@app.get("/")
def endpoint(value = Depends(my_dep)):
    return value

# Class dependency
class MyDep:
    def __init__(self, param: str):
        self.param = param

@app.get("/")
def endpoint(dep: MyDep = Depends()):
    return dep.param

# Yield dependency (with cleanup)
def get_resource():
    resource = create()
    try:
        yield resource
    finally:
        resource.close()

# Global dependency
app = FastAPI(dependencies=[Depends(my_dep)])

# Router dependency
router = APIRouter(dependencies=[Depends(my_dep)])

# Override for testing
app.dependency_overrides[my_dep] = mock_dep
```

---

## Next Steps

1. **Practice karo** - Exercises complete karo
2. **Project mein use karo** - Real dependencies banao
3. **Next doc padho** - `06_database_sqlalchemy.md`

---

> **Pro Tip**: DI sahi se use karo toh code bahut clean aur testable ho jata hai.
> Start simple, phir complex patterns try karo!
