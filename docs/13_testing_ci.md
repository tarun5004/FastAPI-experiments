# 13 — Testing & CI/CD (Complete In-Depth Guide)

> 🎯 **Goal**: FastAPI apps ko professionally test karna aur CI/CD pipeline setup karna seekho!

---

## 📚 Table of Contents
1. [Testing Kyun Important Hai?](#testing-kyun-important-hai)
2. [Testing Types](#testing-types)
3. [Pytest Setup](#pytest-setup)
4. [FastAPI Testing](#fastapi-testing)
5. [Database Testing](#database-testing)
6. [Mocking](#mocking)
7. [Async Testing](#async-testing)
8. [Test Coverage](#test-coverage)
9. [CI/CD Pipeline](#cicd-pipeline)
10. [Best Practices](#best-practices)
11. [Practice Exercises](#practice-exercises)

---

## Testing Kyun Important Hai?

### Bina Testing Ke Kya Hota Hai?

```python
# ❌ Without Testing - The Horror Story

# Developer ne code likha
def calculate_discount(price, percentage):
    return price - (price * percentage)  # Bug: percentage 100 se divide nahi kiya!

# Production mein gaya
# Customer: ₹1000 ka item, 10% discount
# Expected: ₹900
# Actual: ₹1000 - (1000 * 10) = -₹9000 😱

# Result:
# - Customer ko paisa milega 😅
# - Company bankrupt! 💸
# - Developer ki job gayi! 🔥
```

### Testing Se Kya Milta Hai?

```python
# ✅ With Testing

def test_calculate_discount():
    # Simple case
    assert calculate_discount(1000, 10) == 900  # ❌ Test FAILS!
    # Bug caught BEFORE production! 🎉
    
    # Edge cases
    assert calculate_discount(0, 10) == 0       # Zero price
    assert calculate_discount(1000, 0) == 1000  # Zero discount
    assert calculate_discount(1000, 100) == 0   # Full discount

# Fixed code
def calculate_discount(price, percentage):
    return price - (price * percentage / 100)  # Now correct!
```

### Testing Benefits

```
1. 🛡️ CONFIDENCE: Code deploy karne mein darr nahi
2. 🐛 BUG DETECTION: Bugs production se pehle milte hain
3. 📚 DOCUMENTATION: Tests = living documentation
4. 🔄 REFACTORING: Safely change code
5. 👥 TEAM WORK: Others can understand your code
6. 💰 SAVE MONEY: Bugs fixing in production = 100x expensive
```

---

## Testing Types

### The Testing Pyramid

```
           /\
          /  \           <- End-to-End (E2E) Tests
         /    \             Few, slow, expensive
        /------\
       /        \        <- Integration Tests
      /          \          Medium amount
     /------------\
    /              \     <- Unit Tests
   /                \       Many, fast, cheap
  /------------------\

More unit tests, fewer E2E tests = Good pyramid!
```

### Unit Tests

```python
# Unit Test = Single function/method test in isolation
# Fast, many, should pass quickly

def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
```

### Integration Tests

```python
# Integration Test = Multiple components together
# Database + API + Business Logic

async def test_create_user_integration(client, db_session):
    # Test API endpoint with actual database
    response = await client.post(
        "/users/",
        json={"email": "test@test.com", "password": "secret123"}
    )
    
    assert response.status_code == 201
    
    # Verify database
    user = await db_session.execute(
        select(User).where(User.email == "test@test.com")
    )
    assert user.scalars().first() is not None
```

### End-to-End (E2E) Tests

```python
# E2E Test = Full user flow
# Browser/client → API → Database → Response

async def test_user_registration_flow(client):
    # 1. Register
    response = await client.post("/register", json={...})
    assert response.status_code == 201
    
    # 2. Login
    response = await client.post("/login", json={...})
    token = response.json()["access_token"]
    
    # 3. Access protected resource
    response = await client.get(
        "/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

---

## Pytest Setup

### Install Dependencies

```bash
pip install pytest                 # Test framework
pip install pytest-asyncio         # Async test support
pip install pytest-cov            # Coverage reporting
pip install httpx                  # Async HTTP client (for FastAPI)
pip install pytest-env             # Environment variables
pip install factory-boy            # Test data factories
pip install faker                  # Fake data generation
```

### Project Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── crud.py
│   └── schemas.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # ⭐ Shared fixtures
│   ├── test_users.py
│   ├── test_posts.py
│   └── unit/
│       ├── test_utils.py
│       └── test_services.py
├── pytest.ini             # Pytest config
└── requirements-test.txt
```

### pytest.ini Configuration

```ini
# pytest.ini
[pytest]
# Test file patterns
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Async mode
asyncio_mode = auto

# Markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests

# Warnings
filterwarnings =
    ignore::DeprecationWarning

# Coverage
addopts = --cov=app --cov-report=term-missing
```

---

## FastAPI Testing

### Basic Test Setup

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_engine():
    """
    Create test database engine
    
    In-memory = fresh database for each test session
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    """
    Create test database session
    
    Each test gets fresh session
    Changes rolled back after test
    """
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()  # Cleanup


@pytest.fixture
async def client(db_session):
    """
    FastAPI test client
    
    Overrides get_db dependency with test session
    """
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()
```

### Testing Endpoints

```python
# tests/test_users.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    """
    Test user creation endpoint
    
    Yeh test check karta hai:
    1. Valid data se 201 response aaye
    2. Response mein user data ho
    3. Password response mein NA ho (security)
    """
    # Arrange - Test data ready karo
    user_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "name": "Test User"
    }
    
    # Act - API call karo
    response = await client.post("/users/", json=user_data)
    
    # Assert - Check results
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert "password" not in data  # Security check!
    assert "id" in data  # ID generated


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient):
    """
    Test duplicate email rejection
    
    Same email se doosra user nahi banna chahiye
    """
    user_data = {"email": "dupe@example.com", "password": "password123"}
    
    # Create first user
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201
    
    # Try to create duplicate
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_user_invalid_email(client: AsyncClient):
    """Test invalid email validation"""
    response = await client.post("/users/", json={
        "email": "not-an-email",  # Invalid!
        "password": "password123"
    })
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_user(client: AsyncClient):
    """Test get user by ID"""
    # Create user first
    create_response = await client.post("/users/", json={
        "email": "get@example.com",
        "password": "password123"
    })
    user_id = create_response.json()["id"]
    
    # Get user
    response = await client.get(f"/users/{user_id}")
    
    assert response.status_code == 200
    assert response.json()["id"] == user_id


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    """Test 404 for non-existent user"""
    response = await client.get("/users/99999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient):
    """Test listing users with pagination"""
    # Create multiple users
    for i in range(5):
        await client.post("/users/", json={
            "email": f"user{i}@example.com",
            "password": "password123"
        })
    
    # Get list
    response = await client.get("/users/?limit=3")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3  # Limit respected
```

### Testing Authentication

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.fixture
async def authenticated_client(client: AsyncClient):
    """
    Client with authentication
    
    Creates user, logs in, returns authenticated client
    """
    # Create user
    await client.post("/users/", json={
        "email": "auth@test.com",
        "password": "password123"
    })
    
    # Login
    response = await client.post("/token", data={
        "username": "auth@test.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    
    # Add auth header
    client.headers["Authorization"] = f"Bearer {token}"
    
    return client


@pytest.mark.asyncio
async def test_protected_endpoint(authenticated_client: AsyncClient):
    """Test accessing protected route with valid token"""
    response = await authenticated_client.get("/users/me")
    
    assert response.status_code == 200
    assert response.json()["email"] == "auth@test.com"


@pytest.mark.asyncio
async def test_protected_endpoint_no_auth(client: AsyncClient):
    """Test accessing protected route without token"""
    response = await client.get("/users/me")
    
    assert response.status_code == 401
```

---

## Database Testing

### Fixtures for Test Data

```python
# tests/conftest.py
import pytest
from app.models import User, Post

@pytest.fixture
async def sample_user(db_session):
    """
    Create sample user for testing
    
    Use in tests that need existing user
    """
    user = User(
        email="sample@test.com",
        hashed_password="hashed_password",
        name="Sample User"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def sample_users(db_session):
    """Create multiple sample users"""
    users = []
    for i in range(5):
        user = User(
            email=f"user{i}@test.com",
            hashed_password="hashed",
            name=f"User {i}"
        )
        db_session.add(user)
        users.append(user)
    
    await db_session.commit()
    for user in users:
        await db_session.refresh(user)
    return users


@pytest.fixture
async def sample_post(db_session, sample_user):
    """Create sample post (depends on sample_user)"""
    post = Post(
        title="Sample Post",
        content="Sample content",
        user_id=sample_user.id
    )
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)
    return post
```

### Testing CRUD Operations

```python
# tests/test_crud.py
import pytest
from sqlalchemy import select
from app import crud, models, schemas

@pytest.mark.asyncio
async def test_create_user_crud(db_session):
    """Test CRUD create_user function"""
    user_data = schemas.UserCreate(
        email="crud@test.com",
        password="password123",
        name="CRUD Test"
    )
    
    user = await crud.create_user(db_session, user_data)
    
    assert user.id is not None
    assert user.email == user_data.email
    assert user.hashed_password != user_data.password  # Password hashed!


@pytest.mark.asyncio
async def test_get_user_crud(db_session, sample_user):
    """Test getting user by ID"""
    user = await crud.get_user(db_session, sample_user.id)
    
    assert user is not None
    assert user.id == sample_user.id
    assert user.email == sample_user.email


@pytest.mark.asyncio
async def test_get_user_not_found(db_session):
    """Test getting non-existent user returns None"""
    user = await crud.get_user(db_session, 99999)
    
    assert user is None


@pytest.mark.asyncio
async def test_update_user_crud(db_session, sample_user):
    """Test updating user"""
    update_data = schemas.UserUpdate(name="Updated Name")
    
    user = await crud.update_user(db_session, sample_user.id, update_data)
    
    assert user.name == "Updated Name"
    assert user.email == sample_user.email  # Unchanged


@pytest.mark.asyncio
async def test_delete_user_crud(db_session, sample_user):
    """Test deleting user"""
    result = await crud.delete_user(db_session, sample_user.id)
    
    assert result == True
    
    # Verify deletion
    user = await crud.get_user(db_session, sample_user.id)
    assert user is None
```

---

## Mocking

### Kya Hai Mocking?

```python
# Mocking = Fake objects/functions for testing
# Kyun? External dependencies ko isolate karo

# Real scenario:
# test_send_email():
#     send_email("user@test.com")  # Actually sends email! ❌

# With mocking:
# test_send_email():
#     mock_send_email()  # Pretends to send, doesn't actually ✅
```

### Using unittest.mock

```python
# tests/test_with_mocks.py
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Mock external API call
@pytest.mark.asyncio
async def test_create_user_with_email_notification(client):
    """
    Test user creation triggers email
    
    We don't want to actually send email in tests!
    """
    with patch("app.services.email.send_welcome_email") as mock_email:
        # Configure mock
        mock_email.return_value = True
        
        # Create user
        response = await client.post("/users/", json={
            "email": "new@test.com",
            "password": "password123"
        })
        
        assert response.status_code == 201
        
        # Verify email was "called" (not actually sent)
        mock_email.assert_called_once_with("new@test.com")


# Mock async function
@pytest.mark.asyncio
async def test_external_api_integration():
    """Mock external API call"""
    with patch("app.services.external.fetch_data", new_callable=AsyncMock) as mock:
        # Configure mock response
        mock.return_value = {"data": "mocked"}
        
        # Your code that calls external API
        result = await some_function_using_external_api()
        
        assert result["data"] == "mocked"
        mock.assert_called_once()


# Mock database query for unit test
@pytest.mark.asyncio
async def test_service_with_mocked_repo():
    """Unit test service layer with mocked repository"""
    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value=User(
        id=1, email="test@test.com", name="Test"
    ))
    
    service = UserService(mock_repo)
    user = await service.get_user(1)
    
    assert user.email == "test@test.com"
    mock_repo.get_by_id.assert_called_once_with(1)
```

### Mock Best Practices

```python
# 1. Mock at the right level
# ✅ Mock external services
# ❌ Don't mock everything

# 2. Use spec for type safety
mock = MagicMock(spec=ActualClass)

# 3. Verify calls
mock.assert_called()
mock.assert_called_once()
mock.assert_called_with(expected_arg)
mock.assert_not_called()

# 4. Reset between tests
mock.reset_mock()
```

---

## Async Testing

### pytest-asyncio Configuration

```python
# conftest.py
import pytest

# Automatically make all tests async-aware
@pytest.fixture(scope="session")
def event_loop_policy():
    """Windows specific - use selector event loop"""
    import sys
    if sys.platform == "win32":
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# Or in pytest.ini:
# asyncio_mode = auto
```

### Async Test Patterns

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    """Basic async test"""
    result = await some_async_function()
    assert result == expected


@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test multiple async operations"""
    # Run concurrently
    results = await asyncio.gather(
        async_func_1(),
        async_func_2(),
        async_func_3(),
    )
    
    assert all(r.success for r in results)


@pytest.mark.asyncio
async def test_async_timeout():
    """Test that operation completes in time"""
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(
            slow_operation(),
            timeout=1.0
        )


@pytest.mark.asyncio
async def test_async_exception():
    """Test async exception handling"""
    with pytest.raises(ValueError, match="Invalid input"):
        await async_function_that_raises()
```

---

## Test Coverage

### Running Coverage

```bash
# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# HTML report (detailed)
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80
```

### Coverage Report Example

```
---------- coverage: platform win32, python 3.11.0 -----------
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
app/__init__.py             0      0   100%
app/main.py                45      5    89%   23-27
app/crud.py                80      8    90%   45-52
app/models.py              35      0   100%
app/schemas.py             28      0   100%
-----------------------------------------------------
TOTAL                     188     13    93%

Lines 23-27 in main.py = Not tested!
```

### What to Test?

```python
# ✅ DO test:
# - Happy path (normal usage)
# - Edge cases (empty, null, max values)
# - Error cases (invalid input, not found)
# - Security (auth, validation)
# - Business logic

# ❌ DON'T obsess over:
# - 100% coverage (80-90% is good)
# - Testing framework code
# - Simple getters/setters
# - Third-party library internals
```

---

## CI/CD Pipeline

### GitHub Actions Setup

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      # Test database
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run linting
        run: |
          pip install ruff
          ruff check .
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
        run: |
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          # Add your deployment steps
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest --cov=app --cov-fail-under=80
        language: system
        types: [python]
        pass_filenames: false
```

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Now every commit will:
# 1. Format code
# 2. Run linting
# 3. Run tests
```

---

## Best Practices

### 1. Test Naming Convention

```python
# Pattern: test_<what>_<condition>_<expected>

def test_create_user_valid_data_returns_201():
    pass

def test_create_user_duplicate_email_returns_400():
    pass

def test_get_user_not_found_returns_404():
    pass
```

### 2. Arrange-Act-Assert (AAA)

```python
async def test_user_creation():
    # Arrange - Setup
    user_data = {"email": "test@test.com", "password": "secret"}
    
    # Act - Execute
    response = await client.post("/users/", json=user_data)
    
    # Assert - Verify
    assert response.status_code == 201
```

### 3. Test Isolation

```python
# Each test should be independent
# Don't rely on order or state from other tests

@pytest.fixture(autouse=True)
async def clean_db(db_session):
    """Clean database before each test"""
    yield
    await db_session.rollback()
```

### 4. Use Factories for Test Data

```python
# tests/factories.py
from faker import Faker
from app.models import User

fake = Faker()

class UserFactory:
    @staticmethod
    def build(**kwargs):
        return User(
            email=kwargs.get("email", fake.email()),
            name=kwargs.get("name", fake.name()),
            hashed_password=kwargs.get("password", "hashed"),
        )
    
    @staticmethod
    async def create(db_session, **kwargs):
        user = UserFactory.build(**kwargs)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

# Usage
user = await UserFactory.create(db_session, email="specific@test.com")
```

---

## Practice Exercises

### Exercise 1: Basic Tests
```python
# Write tests for:
# 1. Create product endpoint
# 2. List products with pagination
# 3. Update product
# 4. Delete product
# 5. Product not found (404)
```

### Exercise 2: Authentication Tests
```python
# Write tests for:
# 1. User registration
# 2. Login with correct password
# 3. Login with wrong password
# 4. Protected route with token
# 5. Protected route without token
# 6. Token expiration
```

### Exercise 3: CI Pipeline
```bash
# Create GitHub Actions workflow:
# 1. Run on push to main
# 2. Setup Python 3.11
# 3. Install dependencies
# 4. Run linting
# 5. Run tests with coverage
# 6. Fail if coverage < 80%
```

---

## Quick Reference

```bash
# Run tests
pytest                     # All tests
pytest tests/test_users.py # Specific file
pytest -k "create"         # Match pattern
pytest -v                  # Verbose
pytest -x                  # Stop on first failure
pytest --pdb              # Debug on failure

# Coverage
pytest --cov=app
pytest --cov-report=html

# Markers
pytest -m "unit"          # Only unit tests
pytest -m "not slow"      # Skip slow tests
```

```python
# Fixtures
@pytest.fixture
def sample_data():
    return {"key": "value"}

# Async tests
@pytest.mark.asyncio
async def test_async():
    pass

# Parameterized
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
])
def test_double(input, expected):
    assert double(input) == expected
```

---

> **Pro Tip**: "Agar tumhara code test nahi ho sakta, toh design mein problem hai!" 🧪
