# 17 — Authentication & Security (Complete In-Depth Guide)

> 🎯 **Goal**: Apne API ko secure karo - koi bhi unauthorized access na kar sake!

---

## 📚 Table of Contents
1. [Security Kya Hai?](#security-kya-hai)
2. [Password Hashing](#password-hashing)
3. [JWT Authentication](#jwt-authentication)
4. [OAuth2 with Password Flow](#oauth2-with-password-flow)
5. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
6. [OAuth2 with Third-Party (Google, GitHub)](#oauth2-with-third-party)
7. [API Keys](#api-keys)
8. [Security Best Practices](#security-best-practices)
9. [Common Vulnerabilities](#common-vulnerabilities)
10. [Practice Exercises](#practice-exercises)

---

## Security Kya Hai?

### The Three Pillars

```
Security ke 3 main concepts:

1. AUTHENTICATION (कौन हो तुम?) - Who are you?
   → Login, JWT token, OAuth

2. AUTHORIZATION (क्या करने की permission है?) - What can you do?
   → Roles, Permissions, Access Control

3. PROTECTION (हमलों से बचाव) - Protection from attacks
   → HTTPS, CORS, Input Validation
```

### Visual: Auth Flow

```
User Login:
─────────────────────────────────────────────────────────
1. User: "email: a@b.com, password: 123456"
                    ↓
2. Server: Verify password hash
                    ↓
3. Server: Generate JWT token
                    ↓
4. Response: { "access_token": "eyJhbG..." }
─────────────────────────────────────────────────────────

Protected API Call:
─────────────────────────────────────────────────────────
1. User: GET /users/me
         Header: Authorization: Bearer eyJhbG...
                    ↓
2. Server: Verify JWT token
                    ↓
3. Server: Extract user_id from token
                    ↓
4. Response: { "id": 1, "email": "a@b.com" }
─────────────────────────────────────────────────────────
```

---

## Password Hashing

### Password Hashing Kyun?

```python
# ❌ NEVER store passwords as plain text!
# Database leak = All passwords exposed!

users_table = [
    {"email": "user1@example.com", "password": "123456"},  # 😱 Plain text!
    {"email": "user2@example.com", "password": "password123"},
]

# ✅ ALWAYS hash passwords
# Even if database leaks, hackers can't reverse the hash!

users_table = [
    {"email": "user1@example.com", "password": "$2b$12$LQv3..."},  # Hash
    {"email": "user2@example.com", "password": "$2b$12$xyz1..."},
]
```

### Hashing vs Encryption

```
Hashing (One-way):
password → [Hash Function] → $2b$12$LQv3c9... ← Cannot reverse!

Encryption (Two-way):
data → [Encrypt + Key] → encrypted_data → [Decrypt + Key] → data

For passwords: ALWAYS use hashing (bcrypt, argon2)
```

### Using passlib with bcrypt

```python
# Installation
# pip install passlib[bcrypt]

from passlib.context import CryptContext

# Create password context
pwd_context = CryptContext(
    schemes=["bcrypt"],  # Algorithm
    deprecated="auto"    # Auto-upgrade old hashes
)

def hash_password(password: str) -> str:
    """
    Hash a plain password
    
    Same password gives DIFFERENT hash each time (salt)
    "123456" → "$2b$12$abc..."
    "123456" → "$2b$12$xyz..."  (different!)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    
    Returns True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


# Usage
hashed = hash_password("mysecretpassword")
# "$2b$12$LQv3c9L.H5xVDJC8yqM0l.O0y5a5N5QZ7D2Q5K9X1Y2Z3A4B5C6D7"

verify_password("mysecretpassword", hashed)  # True
verify_password("wrongpassword", hashed)     # False
```

### User Registration with Hashing

```python
# schemas.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
class UserResponse(BaseModel):
    id: int
    email: str
    # Note: password field NOT included in response!
    
    class Config:
        from_attributes = True


# crud.py
from sqlalchemy.orm import Session
from models import User
from security import hash_password

async def create_user(db: Session, user: UserCreate) -> User:
    # Hash password before storing
    hashed_password = hash_password(user.password)
    
    db_user = User(
        email=user.email,
        hashed_password=hashed_password  # Store hash, not plain password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# main.py
@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing = await get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return await create_user(db, user)
```

---

## JWT Authentication

### JWT Kya Hai?

```
JWT = JSON Web Token

Structure: header.payload.signature

Example:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxIiwiZXhwIjoxNjQxMDAwMDAwfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

Parts:
1. Header (Base64): {"alg": "HS256", "typ": "JWT"}
2. Payload (Base64): {"sub": "1", "exp": 1641000000}  ← User data
3. Signature: HMAC(header + payload, SECRET_KEY)      ← Verification
```

### Why JWT?

```
Traditional Session:
─────────────────────────────────────────────────────────
User → Login → Server stores session in memory/database
              ↓
User → Request + Session ID → Server looks up session
                              ↓
Problem: Server needs to store ALL sessions (not scalable)

JWT (Stateless):
─────────────────────────────────────────────────────────
User → Login → Server creates JWT with user info
              ↓
User → Request + JWT → Server verifies signature (no lookup!)
                       ↓
Advantage: No session storage needed, horizontally scalable
```

### JWT Implementation

```python
# Installation
# pip install python-jose[cryptography]

from datetime import datetime, timedelta
from jose import JWTError, jwt

# Configuration
SECRET_KEY = "your-super-secret-key-keep-it-safe"  # Use env variable!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create JWT access token
    
    data = {"sub": user_id} - Payload data
    Returns: JWT string
    """
    to_encode = data.copy()
    
    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    
    # Create token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict | None:
    """
    Verify and decode JWT token
    
    Returns payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# Usage
token = create_access_token({"sub": "user123", "role": "admin"})
# "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

payload = verify_token(token)
# {"sub": "user123", "role": "admin", "exp": 1641000000}
```

---

## OAuth2 with Password Flow

### Complete Implementation

```python
# security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel

# Configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
# tokenUrl = endpoint that accepts username/password and returns token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency that extracts and validates user from JWT token
    
    How it works:
    1. OAuth2PasswordBearer extracts token from "Authorization: Bearer xxx" header
    2. We decode and verify the token
    3. We fetch and return the user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user
```

### Login Endpoint

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()

@app.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login
    
    Expects form data:
    - username (email in our case)
    - password
    
    Returns:
    - access_token
    - token_type
    """
    # Find user
    user = await get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}
```

### Protected Endpoints

```python
@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current logged-in user
    
    Requires: Authorization header with Bearer token
    Example: Authorization: Bearer eyJhbGci...
    """
    return current_user


@app.get("/users/me/items")
async def read_my_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get items belonging to current user"""
    items = await get_user_items(db, current_user.id)
    return items
```

### Refresh Tokens (Longer Sessions)

```python
# Schema
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/token", response_model=TokenPair)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # ... verify credentials ...
    
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@app.post("/token/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str):
    """Get new access token using refresh token"""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")
        
        user_id = payload.get("sub")
        new_access_token = create_access_token(data={"sub": user_id})
        
        return {"access_token": new_access_token, "token_type": "bearer"}
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
```

---

## Role-Based Access Control (RBAC)

### User Roles

```python
# models.py
from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLEnum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
```

### Role-Based Dependencies

```python
# dependencies.py
from fastapi import Depends, HTTPException, status

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Check if user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class RoleChecker:
    """
    Reusable dependency for role-based access
    
    Usage:
    @app.get("/admin", dependencies=[Depends(RoleChecker(["admin"]))])
    """
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return user


# Create reusable checkers
admin_only = RoleChecker(["admin"])
moderator_or_admin = RoleChecker(["admin", "moderator"])
```

### Using Role Checkers

```python
@app.get("/admin/users")
async def list_all_users(
    user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    """Admin only endpoint"""
    return await get_all_users(db)


@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    user: User = Depends(moderator_or_admin),
    db: Session = Depends(get_db)
):
    """Moderators and admins can delete posts"""
    await delete_post_db(db, post_id)
    return {"message": "Post deleted"}


# Alternative: Using dependencies parameter
@app.get(
    "/admin/stats",
    dependencies=[Depends(admin_only)]  # Runs check but doesn't inject
)
async def admin_stats():
    return calculate_stats()
```

### Permission-Based Access

```python
# models.py
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import relationship

# Many-to-many: users <-> permissions
user_permissions = Table(
    "user_permissions",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("permission_id", ForeignKey("permissions.id")),
)

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)  # "create:post", "delete:user", etc.

class User(Base):
    # ... other fields ...
    permissions = relationship("Permission", secondary=user_permissions)


# dependencies.py
class PermissionChecker:
    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions
    
    def __call__(self, user: User = Depends(get_current_user)):
        user_permissions = {p.name for p in user.permissions}
        
        for permission in self.required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=403,
                    detail=f"Missing permission: {permission}"
                )
        return user


# Usage
can_create_post = PermissionChecker(["create:post"])
can_delete_user = PermissionChecker(["delete:user"])

@app.post("/posts")
async def create_post(user: User = Depends(can_create_post)):
    pass
```

---

## OAuth2 with Third-Party

### Google OAuth2

```python
# Install: pip install authlib httpx

from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

config = Config(".env")
oauth = OAuth(config)

# Register Google provider
oauth.register(
    name="google",
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@app.get("/auth/google")
async def google_login(request: Request):
    """Redirect to Google login page"""
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    # Get token from Google
    token = await oauth.google.authorize_access_token(request)
    
    # Get user info
    user_info = token.get("userinfo")
    email = user_info["email"]
    name = user_info.get("name", "")
    
    # Find or create user
    user = await get_user_by_email(db, email)
    if not user:
        user = await create_user_oauth(db, email=email, name=name, provider="google")
    
    # Create our JWT token
    access_token = create_access_token(data={"sub": user.id})
    
    # Redirect to frontend with token
    return RedirectResponse(
        url=f"http://localhost:3000/auth?token={access_token}"
    )
```

### GitHub OAuth2

```python
oauth.register(
    name="github",
    client_id=config("GITHUB_CLIENT_ID"),
    client_secret=config("GITHUB_CLIENT_SECRET"),
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)


@app.get("/auth/github")
async def github_login(request: Request):
    redirect_uri = request.url_for("github_callback")
    return await oauth.github.authorize_redirect(request, redirect_uri)


@app.get("/auth/github/callback")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.github.authorize_access_token(request)
    
    # Fetch user profile
    resp = await oauth.github.get("user", token=token)
    profile = resp.json()
    
    # Fetch email (might be private)
    resp = await oauth.github.get("user/emails", token=token)
    emails = resp.json()
    primary_email = next(e["email"] for e in emails if e["primary"])
    
    # Create/get user and return token
    user = await get_or_create_oauth_user(db, primary_email, profile["name"], "github")
    access_token = create_access_token(data={"sub": user.id})
    
    return RedirectResponse(f"http://localhost:3000/auth?token={access_token}")
```

---

## API Keys

### Simple API Key Auth

```python
from fastapi import Security
from fastapi.security import APIKeyHeader, APIKeyQuery

API_KEY = "your-secret-api-key"  # Store in env/database

# Header-based API key
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Query parameter API key (less secure)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


async def get_api_key(
    api_key_header: str = Security(api_key_header),
    api_key_query: str = Security(api_key_query),
):
    """Accept API key from header or query parameter"""
    if api_key_header == API_KEY:
        return api_key_header
    elif api_key_query == API_KEY:
        return api_key_query
    else:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key"
        )


@app.get("/api/data")
async def get_data(api_key: str = Depends(get_api_key)):
    return {"data": "secret data"}

# Usage:
# curl -H "X-API-Key: your-secret-api-key" http://localhost:8000/api/data
# or
# curl http://localhost:8000/api/data?api_key=your-secret-api-key
```

### Database-Stored API Keys

```python
# models.py
import secrets

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)  # "Production", "Testing", etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="api_keys")
    
    @staticmethod
    def generate_key():
        return secrets.token_urlsafe(32)


# dependencies.py
async def get_api_key_user(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
):
    key = await db.execute(
        select(APIKey).where(APIKey.key == api_key, APIKey.is_active == True)
    )
    api_key_obj = key.scalar_one_or_none()
    
    if not api_key_obj:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return api_key_obj.user


# Endpoint to create API keys
@app.post("/api-keys")
async def create_api_key(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    key = APIKey(
        key=APIKey.generate_key(),
        user_id=current_user.id,
        name=name
    )
    db.add(key)
    db.commit()
    
    return {"api_key": key.key, "name": name}
```

---

## Security Best Practices

### 1. Use HTTPS

```python
# Production: Always use HTTPS
# Development: Can use HTTP

from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Force HTTPS in production
if os.getenv("ENV") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 2. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

# ❌ BAD - Allow everything
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Insecure!
    allow_methods=["*"],
)

# ✅ GOOD - Specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myapp.com",
        "https://admin.myapp.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 3. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/data")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def get_data(request: Request):
    return {"data": "value"}
```

### 4. Input Validation

```python
from pydantic import BaseModel, validator, EmailStr
import re

class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    password: str
    
    @validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain a digit")
        return v
```

### 5. Security Headers

```python
from fastapi import Response

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    
    # Prevent XSS
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Content Security Policy
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    # HTTPS enforcement
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    
    return response
```

---

## Common Vulnerabilities

### SQL Injection (Prevented by SQLAlchemy)

```python
# ❌ BAD - Raw SQL with string formatting
query = f"SELECT * FROM users WHERE email = '{email}'"  # Hackable!

# ✅ GOOD - SQLAlchemy ORM
user = db.query(User).filter(User.email == email).first()

# ✅ GOOD - Parameterized query
from sqlalchemy import text
result = db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
```

### XSS (Cross-Site Scripting)

```python
# ❌ BAD - Returning user input directly in HTML
@app.get("/greet")
def greet(name: str):
    return HTMLResponse(f"<h1>Hello {name}</h1>")
# name="<script>alert('hacked')</script>" = XSS attack!

# ✅ GOOD - Escape HTML
from html import escape
@app.get("/greet")
def greet(name: str):
    return HTMLResponse(f"<h1>Hello {escape(name)}</h1>")

# ✅ BETTER - Use JSON responses
@app.get("/greet")
def greet(name: str):
    return {"message": f"Hello {name}"}  # JSON is safe
```

### CSRF (Cross-Site Request Forgery)

```python
# For cookie-based auth, use CSRF tokens
from fastapi_csrf_protect import CsrfProtect

@app.get("/form")
def get_form(csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.generate_csrf()
    return {"csrf_token": csrf_token}

@app.post("/submit")
def submit(csrf_protect: CsrfProtect = Depends()):
    csrf_protect.validate_csrf()  # Raises if invalid
    return {"success": True}
```

---

## Practice Exercises

### Exercise 1: Complete Auth System
```python
# Build:
# 1. User registration with password hashing
# 2. JWT login endpoint
# 3. Protected /me endpoint
# 4. Role-based admin endpoint
```

### Exercise 2: API Key System
```python
# Build:
# 1. Create API key for user
# 2. List user's API keys
# 3. Revoke API key
# 4. Protected endpoint using API key
```

### Exercise 3: OAuth Integration
```python
# Build:
# 1. Google login
# 2. Link Google to existing account
# 3. Unlink Google from account
```

---

## Quick Reference

```python
# Password hashing
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])
hashed = pwd_context.hash(password)
verified = pwd_context.verify(password, hashed)

# JWT
from jose import jwt
token = jwt.encode({"sub": user_id}, SECRET_KEY, algorithm="HS256")
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

# OAuth2 dependency
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Decode and verify token
    # Return user

# Protected endpoint
@app.get("/protected")
async def protected(user: User = Depends(get_current_user)):
    return user
```

---

> **Pro Tip**: "Security mein shortcut mat lo - ek vulnerability se poora system hack ho sakta hai!" 🔐
