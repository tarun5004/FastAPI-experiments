# 06 — APIRouter & Project Structure (Complete In-Depth Guide)

> 🎯 **Goal**: Large FastAPI projects organize karna seekho - APIRouter, modular structure, best practices!

---

## 📚 Table of Contents
1. [Why APIRouter?](#why-apirouter)
2. [Basic APIRouter](#basic-apirouter)
3. [Router Parameters](#router-parameters)
4. [Including Routers](#including-routers)
5. [Nested Routers](#nested-routers)
6. [Project Structure Patterns](#project-structure-patterns)
7. [Complete Project Setup](#complete-project-setup)
8. [Configuration Management](#configuration-management)
9. [Environment Variables](#environment-variables)
10. [Factory Pattern](#factory-pattern)
11. [Blueprint Pattern](#blueprint-pattern)
12. [Modular Dependencies](#modular-dependencies)
13. [Error Handling Structure](#error-handling-structure)
14. [Industry Best Practices](#industry-best-practices)
15. [Practice Exercises](#practice-exercises)

---

## Why APIRouter?

### Without APIRouter (Messy Single File)
```python
# ❌ BAD - Everything in main.py
from fastapi import FastAPI

app = FastAPI()

# User routes
@app.get("/users")
def get_users(): ...

@app.post("/users")
def create_user(): ...

@app.get("/users/{id}")
def get_user(): ...

# Product routes
@app.get("/products")
def get_products(): ...

@app.post("/products")
def create_product(): ...

# Order routes
@app.get("/orders")
def get_orders(): ...

# ... 100 more endpoints in same file 😱
```

### With APIRouter (Clean & Organized)
```python
# ✅ GOOD - Separated by feature

# routers/users.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_users(): ...

@router.post("/")
def create_user(): ...

# routers/products.py
router = APIRouter()

@router.get("/")
def get_products(): ...

# main.py
from fastapi import FastAPI
from routers import users, products

app = FastAPI()
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(products.router, prefix="/products", tags=["products"])

# Clean, maintainable, team-friendly! 🎉
```

---

## Basic APIRouter

### Creating a Router
```python
from fastapi import APIRouter

# Create router instance
router = APIRouter()

# Add routes - same syntax as app
@router.get("/")
def get_items():
    return {"items": []}

@router.post("/")
def create_item(name: str):
    return {"name": name}

@router.get("/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}

@router.put("/{item_id}")
def update_item(item_id: int, name: str):
    return {"item_id": item_id, "name": name}

@router.delete("/{item_id}")
def delete_item(item_id: int):
    return {"deleted": item_id}
```

### Including in App
```python
from fastapi import FastAPI
from items_router import router as items_router

app = FastAPI()

# Include router with prefix
app.include_router(items_router, prefix="/items")

# Now all routes are:
# GET /items/
# POST /items/
# GET /items/{item_id}
# PUT /items/{item_id}
# DELETE /items/{item_id}
```

---

## Router Parameters

### All Router Options
```python
from fastapi import APIRouter, Depends

router = APIRouter(
    # URL prefix for all routes
    prefix="/users",
    
    # OpenAPI tag for documentation grouping
    tags=["users"],
    
    # Dependencies for all routes
    dependencies=[Depends(get_token_header)],
    
    # Response class for all routes
    # default_response_class=JSONResponse,
    
    # Responses for all routes (OpenAPI)
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"}
    },
    
    # Include in OpenAPI schema
    include_in_schema=True,
    
    # Deprecated (shows in docs)
    deprecated=False,
    
    # Redirect slashes
    redirect_slashes=True,
)

@router.get("/")  # Will be /users/
def get_users():
    return {"users": []}
```

### Multiple Tags
```python
router = APIRouter(
    prefix="/admin",
    tags=["admin", "management"]  # Multiple tags
)

@router.get("/users")
def admin_users():
    return {"admin": "users"}

# Can also add tags per route
@router.get("/stats", tags=["analytics"])  # Adds to existing tags
def admin_stats():
    return {"stats": {}}
```

---

## Including Routers

### Basic Include
```python
from fastapi import FastAPI
from routers.users import router as users_router
from routers.products import router as products_router
from routers.orders import router as orders_router

app = FastAPI(title="My API")

# Simple include
app.include_router(users_router)

# With prefix (recommended)
app.include_router(users_router, prefix="/users", tags=["users"])

# With multiple options
app.include_router(
    products_router,
    prefix="/products",
    tags=["products"],
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Product not found"}}
)

# Multiple routers
for router, prefix, tags in [
    (users_router, "/users", ["users"]),
    (products_router, "/products", ["products"]),
    (orders_router, "/orders", ["orders"]),
]:
    app.include_router(router, prefix=prefix, tags=tags)
```

### Conditional Includes
```python
import os
from fastapi import FastAPI

app = FastAPI()

# Include based on environment
if os.getenv("ENABLE_DEBUG", "false").lower() == "true":
    from routers.debug import router as debug_router
    app.include_router(debug_router, prefix="/debug", tags=["debug"])

# Include based on feature flag
if settings.FEATURE_NEW_API:
    from routers.v2 import router as v2_router
    app.include_router(v2_router, prefix="/api/v2")
```

---

## Nested Routers

### Router in Router
```python
# routers/users/profile.py
from fastapi import APIRouter

profile_router = APIRouter()

@profile_router.get("/")
def get_profile():
    return {"profile": "data"}

@profile_router.put("/")
def update_profile():
    return {"updated": True}

# routers/users/settings.py
settings_router = APIRouter()

@settings_router.get("/")
def get_settings():
    return {"settings": {}}

# routers/users/__init__.py
from fastapi import APIRouter
from .profile import profile_router
from .settings import settings_router

router = APIRouter()

# Include sub-routers
router.include_router(profile_router, prefix="/profile", tags=["profile"])
router.include_router(settings_router, prefix="/settings", tags=["settings"])

@router.get("/")
def get_users():
    return {"users": []}

# main.py
app.include_router(router, prefix="/users", tags=["users"])

# Final routes:
# GET /users/
# GET /users/profile/
# PUT /users/profile/
# GET /users/settings/
```

### Version-based Nesting
```python
# routers/v1/__init__.py
from fastapi import APIRouter
from .users import router as users_router
from .products import router as products_router

router = APIRouter()
router.include_router(users_router, prefix="/users", tags=["v1-users"])
router.include_router(products_router, prefix="/products", tags=["v1-products"])

# routers/v2/__init__.py
from fastapi import APIRouter
from .users import router as users_router  # New version

router = APIRouter()
router.include_router(users_router, prefix="/users", tags=["v2-users"])

# main.py
from routers import v1, v2

app.include_router(v1.router, prefix="/api/v1")
app.include_router(v2.router, prefix="/api/v2")

# Routes:
# /api/v1/users/
# /api/v1/products/
# /api/v2/users/
```

---

## Project Structure Patterns

### Pattern 1: Simple (Small Projects)
```
app/
├── main.py              # FastAPI app
├── routers/
│   ├── __init__.py
│   ├── users.py
│   └── products.py
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── database.py          # DB connection
└── requirements.txt
```

### Pattern 2: Feature-based (Medium Projects)
```
app/
├── main.py
├── core/
│   ├── __init__.py
│   ├── config.py        # Settings
│   ├── security.py      # Auth helpers
│   └── database.py      # DB setup
├── users/
│   ├── __init__.py
│   ├── router.py        # User routes
│   ├── models.py        # User models
│   ├── schemas.py       # User schemas
│   ├── service.py       # Business logic
│   └── dependencies.py  # User-specific deps
├── products/
│   ├── __init__.py
│   ├── router.py
│   ├── models.py
│   ├── schemas.py
│   └── service.py
└── requirements.txt
```

### Pattern 3: Domain-Driven (Large Projects)
```
src/
├── main.py
├── core/
│   ├── config.py
│   ├── events.py        # Startup/shutdown
│   ├── exceptions.py    # Custom exceptions
│   ├── middleware.py    # Custom middleware
│   └── security.py
├── infrastructure/
│   ├── database/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── migrations/
│   ├── cache/
│   │   └── redis.py
│   └── external/
│       └── stripe.py
├── domain/
│   ├── users/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repository.py  # Data access
│   │   └── service.py     # Business logic
│   ├── orders/
│   │   └── ...
│   └── products/
│       └── ...
├── api/
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── users.py
│   │   ├── products.py
│   │   └── orders.py
│   └── v2/
│       └── ...
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## Complete Project Setup

### Feature-based Structure (Recommended)
```python
# app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "My FastAPI App"
    DEBUG: bool = False
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
```

```python
# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
# app/users/models.py
from sqlalchemy import Column, Integer, String, Boolean
from core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
```

```python
# app/users/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    
    class Config:
        orm_mode = True
```

```python
# app/users/service.py
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_users(self, skip: int = 0, limit: int = 100):
        return self.db.query(models.User).offset(skip).limit(limit).all()
    
    def get_user(self, user_id: int):
        return self.db.query(models.User).filter(models.User.id == user_id).first()
    
    def get_user_by_email(self, email: str):
        return self.db.query(models.User).filter(models.User.email == email).first()
    
    def create_user(self, user: schemas.UserCreate):
        hashed_password = pwd_context.hash(user.password)
        db_user = models.User(
            email=user.email,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update_user(self, user_id: int, user_update: schemas.UserUpdate):
        db_user = self.get_user(user_id)
        if db_user:
            update_data = user_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_user, key, value)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user
    
    def delete_user(self, user_id: int):
        db_user = self.get_user(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
        return db_user
```

```python
# app/users/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from .service import UserService

def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)

def get_user_or_404(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return user
```

```python
# app/users/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from . import schemas
from .service import UserService
from .dependencies import get_user_service, get_user_or_404

router = APIRouter()

@router.get("/", response_model=List[schemas.UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_user_service)
):
    return service.get_users(skip=skip, limit=limit)

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: schemas.UserCreate,
    service: UserService = Depends(get_user_service)
):
    db_user = service.get_user_by_email(user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return service.create_user(user)

@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user = Depends(get_user_or_404)):
    return user

@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_update: schemas.UserUpdate,
    user = Depends(get_user_or_404),
    service: UserService = Depends(get_user_service)
):
    return service.update_user(user.id, user_update)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user = Depends(get_user_or_404),
    service: UserService = Depends(get_user_service)
):
    service.delete_user(user.id)
    return None
```

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import engine, Base
from users.router import router as users_router
# from products.router import router as products_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    print("Database tables created")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
# app.include_router(products_router, prefix="/api/v1/products", tags=["products"])

@app.get("/")
def root():
    return {"message": "Welcome to API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

---

## Configuration Management

### Using Pydantic Settings
```python
# core/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "FastAPI App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

class DevelopmentSettings(Settings):
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

class ProductionSettings(Settings):
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

class TestingSettings(Settings):
    DEBUG: bool = True
    ENVIRONMENT: str = "testing"
    DATABASE_URL: str = "sqlite:///./test.db"

@lru_cache
def get_settings() -> Settings:
    import os
    env = os.getenv("ENVIRONMENT", "development")
    
    settings_map = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
        "testing": TestingSettings,
    }
    
    return settings_map.get(env, DevelopmentSettings)()

settings = get_settings()
```

### Environment Variables
```bash
# .env file
APP_NAME=My FastAPI App
DEBUG=true
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-super-secret-key
CORS_ORIGINS=["http://localhost:3000","https://myapp.com"]
```

---

## Factory Pattern

### Application Factory
```python
# core/factory.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import engine, Base
from core.middleware import LoggingMiddleware

def create_app() -> FastAPI:
    """Application factory pattern"""
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        Base.metadata.create_all(bind=engine)
        yield
        # Shutdown
        pass
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
    )
    
    # Add middleware
    configure_middleware(app)
    
    # Include routers
    configure_routers(app)
    
    # Configure exception handlers
    configure_exception_handlers(app)
    
    return app

def configure_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

def configure_routers(app: FastAPI):
    from users.router import router as users_router
    from products.router import router as products_router
    from auth.router import router as auth_router
    
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
    app.include_router(products_router, prefix="/api/v1/products", tags=["products"])

def configure_exception_handlers(app: FastAPI):
    from core.exceptions import configure_exceptions
    configure_exceptions(app)

# main.py
from core.factory import create_app

app = create_app()
```

---

## Modular Dependencies

### Centralized Dependencies
```python
# core/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from .security import decode_token
from users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_role(roles: list):
    async def role_checker(user: User = Depends(get_current_active_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return role_checker
```

### Using in Routers
```python
# users/router.py
from fastapi import APIRouter, Depends
from core.dependencies import get_current_active_user, require_role

router = APIRouter()

@router.get("/me")
def get_current_user_profile(user = Depends(get_current_active_user)):
    return user

@router.get("/admin/users")
def admin_get_users(admin = Depends(require_role(["admin"]))):
    # Only admins can access
    ...
```

---

## Error Handling Structure

### Custom Exceptions
```python
# core/exceptions.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

class AppException(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code

class NotFoundException(AppException):
    def __init__(self, resource: str, id: any):
        super().__init__(
            status_code=404,
            detail=f"{resource} with id {id} not found",
            error_code="NOT_FOUND"
        )

class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="UNAUTHORIZED"
        )

class ForbiddenException(AppException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code="FORBIDDEN"
        )

class BadRequestException(AppException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=400,
            detail=detail,
            error_code="BAD_REQUEST"
        )

def configure_exceptions(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.detail
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"]
            })
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": errors
                }
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": "HTTP_ERROR",
                    "message": exc.detail
                }
            }
        )
```

### Using Custom Exceptions
```python
# users/service.py
from core.exceptions import NotFoundException, BadRequestException

class UserService:
    def get_user(self, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User", user_id)
        return user
    
    def create_user(self, user_data):
        if self.get_user_by_email(user_data.email):
            raise BadRequestException("Email already registered")
        # ...
```

---

## Industry Best Practices

### 1. Consistent Response Format
```python
# core/responses.py
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None

class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: list[T]
    total: int
    page: int
    per_page: int
    total_pages: int

# Usage in router
@router.get("/users", response_model=PaginatedResponse[UserResponse])
def get_users(skip: int = 0, limit: int = 10, service = Depends(get_user_service)):
    users = service.get_users(skip, limit)
    total = service.count_users()
    
    return {
        "success": True,
        "data": users,
        "total": total,
        "page": skip // limit + 1,
        "per_page": limit,
        "total_pages": (total + limit - 1) // limit
    }
```

### 2. Logging Setup
```python
# core/logging.py
import logging
import sys
from .config import settings

def setup_logging():
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )
    
    # Reduce noise from libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

logger = setup_logging()
```

### 3. Health Check Endpoint
```python
# core/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.get("/health/db")
def db_health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
```

### 4. Testing Structure
```
tests/
├── conftest.py           # Shared fixtures
├── unit/
│   ├── test_users.py
│   └── test_products.py
├── integration/
│   ├── test_users_api.py
│   └── test_products_api.py
└── e2e/
    └── test_user_flow.py
```

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from core.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

---

## Practice Exercises

### Exercise 1: Multi-module API
```python
# Create a complete API with:
# - users module (CRUD)
# - products module (CRUD)
# - orders module (with relationships)
# - Proper project structure
```

### Exercise 2: API Versioning
```python
# Implement:
# - /api/v1/users (old format)
# - /api/v2/users (new format)
# - Shared models, different routers
```

### Exercise 3: Feature Flags Router
```python
# Create a router that:
# - Enables/disables features via config
# - Conditionally includes routes
# - Returns 404 for disabled features
```

---

## Quick Reference

```python
from fastapi import APIRouter, FastAPI

# Create router
router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth)]
)

@router.get("/")
def list_items(): ...

# Include in app
app = FastAPI()
app.include_router(router)

# Nested routers
parent_router.include_router(child_router, prefix="/child")

# Project structure
# app/
#   main.py
#   core/config.py, database.py
#   feature/router.py, models.py, schemas.py, service.py
```

---

## Next Steps

1. **Practice karo** - Complete project structure banao
2. **Existing project reorganize karo**
3. **Next doc padho** - `07_sqlalchemy_basics.md`

---

> **Pro Tip**: Good project structure = Happy team, Easy maintenance, Faster development!
