# 02 — FastAPI Basics & Routing (Complete In-Depth Guide - Hinglish)

> 🎯 **Goal**: Is guide ke baad tum FastAPI mein complete API build kar paoge - routing, parameters, validation, error handling sab.

---

## 📚 Table of Contents
1. [FastAPI Kya Hai?](#fastapi-kya-hai)
2. [Installation & First App](#installation--first-app)
3. [HTTP Methods & Routes](#http-methods--routes)
4. [Path Parameters](#path-parameters)
5. [Query Parameters](#query-parameters)
6. [Request Body](#request-body)
7. [Response Models](#response-models)
8. [Status Codes](#status-codes)
9. [HTTPException & Error Handling](#httpexception--error-handling)
10. [Headers & Cookies](#headers--cookies)
11. [Form Data & File Uploads](#form-data--file-uploads)
12. [Auto Documentation (Swagger/Redoc)](#auto-documentation)
13. [Testing with TestClient](#testing-with-testclient)
14. [Industry Patterns](#industry-patterns)
15. [Complete Example](#complete-example)
16. [Practice Exercises](#practice-exercises)

---

## FastAPI Kya Hai?

FastAPI ek modern, fast (high-performance) Python web framework hai jo APIs banane ke liye use hota hai.

### Why FastAPI?
```
✅ Bahut Fast - Node.js aur Go ke barabar performance
✅ Type Hints - Automatic validation aur documentation
✅ Auto Docs - Swagger UI built-in
✅ Async Support - High concurrency handle kar sakta hai
✅ Modern Python - Python 3.7+ features use karta hai
```

### FastAPI vs Other Frameworks
```
| Feature        | FastAPI    | Flask      | Django REST |
|----------------|------------|------------|-------------|
| Speed          | Very Fast  | Medium     | Medium      |
| Auto Docs      | Yes        | No (addon) | Yes (addon) |
| Async Support  | Native     | Limited    | Limited     |
| Type Safety    | Built-in   | No         | No          |
| Learning Curve | Easy       | Easy       | Medium      |
```

---

## Installation & First App

### Installation
```bash
# Virtual environment banao
python -m venv .venv

# Activate karo
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# FastAPI install karo
pip install fastapi

# Uvicorn install karo (ASGI server)
pip install uvicorn

# Ya ek saath
pip install fastapi uvicorn
```

### First App - Hello World
```python
# main.py
from fastapi import FastAPI

# App instance create karo
app = FastAPI()

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Hello World"}

# Ek aur endpoint
@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}!"}
```

### Server Run Karna
```bash
# Development server start karo
uvicorn main:app --reload

# main:app ka matlab:
# main = main.py file
# app = FastAPI() instance

# --reload = code change pe auto restart

# Server: http://127.0.0.1:8000
# Docs: http://127.0.0.1:8000/docs
# Alternative docs: http://127.0.0.1:8000/redoc
```

### App Configuration
```python
from fastapi import FastAPI

# Detailed configuration
app = FastAPI(
    title="My Awesome API",
    description="Ye mera first FastAPI project hai",
    version="1.0.0",
    docs_url="/docs",           # Swagger UI URL
    redoc_url="/redoc",         # ReDoc URL
    openapi_url="/openapi.json" # OpenAPI schema
)

# Startup aur Shutdown events
@app.on_event("startup")
async def startup():
    print("🚀 Server starting...")
    # Database connect karo, cache initialize karo, etc.

@app.on_event("shutdown")
async def shutdown():
    print("👋 Server shutting down...")
    # Cleanup karo
```

---

## HTTP Methods & Routes

### HTTP Methods Explained
```python
from fastapi import FastAPI

app = FastAPI()

# GET - Data fetch karne ke liye
# Idempotent: Multiple times call karo, same result
@app.get("/users")
def get_users():
    return [{"id": 1, "name": "Tarun"}]

# POST - Naya resource create karne ke liye
# Not idempotent: Har call naya resource banata hai
@app.post("/users")
def create_user():
    return {"id": 2, "name": "New User"}

# PUT - Pura resource replace karne ke liye
# Idempotent: Same data bhejo, same result
@app.put("/users/{user_id}")
def update_user(user_id: int):
    return {"id": user_id, "name": "Updated"}

# PATCH - Partial update
# Resource ka sirf kuch part update karo
@app.patch("/users/{user_id}")
def partial_update(user_id: int):
    return {"id": user_id, "updated_field": "email"}

# DELETE - Resource delete karo
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    return {"message": f"User {user_id} deleted"}

# HEAD - GET jaisa but body nahi milta
# OPTIONS - Allowed methods check karo
# Ye rarely manually define karte hain
```

### When to Use Which Method?
```
| Action              | Method | Example                    |
|---------------------|--------|----------------------------|
| List resources      | GET    | GET /users                 |
| Get single resource | GET    | GET /users/1               |
| Create resource     | POST   | POST /users                |
| Full update         | PUT    | PUT /users/1               |
| Partial update      | PATCH  | PATCH /users/1             |
| Delete resource     | DELETE | DELETE /users/1            |
| Search (complex)    | POST   | POST /users/search         |
```

---

## Path Parameters

Path parameters URL ka part hote hain.

### Basic Path Parameters
```python
from fastapi import FastAPI

app = FastAPI()

# Simple path parameter
@app.get("/users/{user_id}")
def get_user(user_id: int):  # Automatic int conversion
    return {"user_id": user_id}

# Call: GET /users/123
# Response: {"user_id": 123}

# Multiple path parameters
@app.get("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: int, post_id: int):
    return {
        "user_id": user_id,
        "post_id": post_id
    }
# Call: GET /users/1/posts/5

# String path parameter
@app.get("/files/{file_path:path}")
def get_file(file_path: str):
    # :path allows slashes in parameter
    return {"file_path": file_path}
# Call: GET /files/home/user/document.pdf
# file_path = "home/user/document.pdf"
```

### Path Parameter Validation
```python
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/items/{item_id}")
def get_item(
    item_id: int = Path(
        ...,                    # ... means required
        title="Item ID",
        description="The ID of the item",
        ge=1,                   # Greater than or equal to 1
        le=1000,                # Less than or equal to 1000
        example=42
    )
):
    return {"item_id": item_id}

# Validation fail hone pe automatic 422 error
```

### Enum Path Parameters
```python
from enum import Enum
from fastapi import FastAPI

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

app = FastAPI()

@app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model": model_name, "message": "Deep Learning FTW!"}
    
    if model_name.value == "lenet":
        return {"model": model_name, "message": "LeCNN all the way"}
    
    return {"model": model_name}

# Only alexnet, resnet, lenet allowed
# Other values = 422 error
```

---

## Query Parameters

Query parameters URL ke `?` ke baad aate hain.

### Basic Query Parameters
```python
from fastapi import FastAPI

app = FastAPI()

# Simple query parameter
@app.get("/items")
def get_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# Call: GET /items?skip=20&limit=50
# Response: {"skip": 20, "limit": 50}

# Call: GET /items
# Response: {"skip": 0, "limit": 10}  # Defaults

# Optional query parameter
from typing import Optional

@app.get("/search")
def search(q: Optional[str] = None):
    if q:
        return {"query": q, "results": ["item1", "item2"]}
    return {"message": "No query provided"}

# Call: GET /search?q=python
# Call: GET /search  (q is None)
```

### Query Parameter Validation
```python
from fastapi import FastAPI, Query
from typing import Optional, List

app = FastAPI()

@app.get("/items")
def get_items(
    q: Optional[str] = Query(
        None,                      # Default value
        min_length=3,              # Minimum 3 characters
        max_length=50,             # Maximum 50 characters
        regex="^[a-zA-Z]+$",       # Only letters
        title="Search Query",
        description="Search string for items",
        example="laptop"
    ),
    skip: int = Query(0, ge=0),    # Greater than or equal to 0
    limit: int = Query(10, le=100) # Less than or equal to 100
):
    return {"q": q, "skip": skip, "limit": limit}
```

### Multiple Values (List)
```python
from fastapi import FastAPI, Query
from typing import List

app = FastAPI()

@app.get("/items")
def get_items(
    tags: List[str] = Query(
        default=[],
        description="Filter by tags"
    )
):
    return {"tags": tags}

# Call: GET /items?tags=python&tags=fastapi&tags=web
# Response: {"tags": ["python", "fastapi", "web"]}
```

### Required Query Parameters
```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/search")
def search(
    q: str = Query(..., min_length=1)  # ... makes it required
):
    return {"query": q}

# GET /search  -> 422 Error (q is required)
# GET /search?q=test -> OK
```

---

## Request Body

POST/PUT/PATCH requests mein data body mein bhejte hain.

### Basic Request Body with Pydantic
```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

app = FastAPI()

# Schema define karo
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    bio: Optional[str] = None

# POST endpoint
@app.post("/users")
def create_user(user: UserCreate):
    return {
        "message": "User created",
        "user": user.dict()
    }

# Request body:
# {
#     "name": "Tarun",
#     "email": "tarun@example.com",
#     "age": 25,
#     "bio": "Developer"
# }
```

### Multiple Bodies
```python
from fastapi import FastAPI, Body
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

class User(BaseModel):
    username: str

@app.post("/items")
def create_item(item: Item, user: User):
    return {"item": item, "user": user}

# Request body:
# {
#     "item": {"name": "Laptop", "price": 999.99},
#     "user": {"username": "tarun"}
# }

# Single value in body
@app.post("/process")
def process(
    importance: int = Body(..., embed=True)
):
    return {"importance": importance}

# Request body:
# {"importance": 5}
```

### Body with Path and Query
```python
from fastapi import FastAPI, Path, Query, Body
from pydantic import BaseModel

app = FastAPI()

class ItemUpdate(BaseModel):
    name: str
    price: float

@app.put("/items/{item_id}")
def update_item(
    item_id: int = Path(..., ge=1),           # Path parameter
    q: Optional[str] = Query(None),           # Query parameter
    item: ItemUpdate = Body(...)              # Request body
):
    result = {"item_id": item_id, "item": item}
    if q:
        result["q"] = q
    return result

# Call: PUT /items/5?q=update
# Body: {"name": "New Name", "price": 199.99}
```

### Nested Models
```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float

class Order(BaseModel):
    user_id: int
    items: List[OrderItem]
    shipping_address: Address
    notes: Optional[str] = None

@app.post("/orders")
def create_order(order: Order):
    total = sum(item.price * item.quantity for item in order.items)
    return {
        "order": order,
        "total": total
    }

# Request:
# {
#     "user_id": 1,
#     "items": [
#         {"product_id": 10, "quantity": 2, "price": 29.99},
#         {"product_id": 20, "quantity": 1, "price": 49.99}
#     ],
#     "shipping_address": {
#         "street": "123 Main St",
#         "city": "Mumbai",
#         "zip_code": "400001"
#     }
# }
```

---

## Response Models

Response model define karta hai ki API kya return karega.

### Basic Response Model
```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from typing import Optional

app = FastAPI()

# Input model (with password)
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

# Output model (without password)
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    
    class Config:
        orm_mode = True  # SQLAlchemy objects bhi convert ho jayenge

# Fake database
fake_db = {}
next_id = 1

@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    global next_id
    new_user = {
        "id": next_id,
        "name": user.name,
        "email": user.email,
        "password": user.password  # Stored but not returned
    }
    fake_db[next_id] = new_user
    next_id += 1
    return new_user  # Password automatically filtered out!
```

### Response Model Options
```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    tax: Optional[float] = None

items_db = [
    {"name": "Laptop", "price": 999.99, "description": None, "tax": None},
    {"name": "Phone", "price": 599.99, "description": "Smartphone", "tax": 50.0}
]

# Exclude None values from response
@app.get("/items", response_model=List[Item], response_model_exclude_unset=True)
def get_items():
    return items_db
# Response mein description/tax sirf tab aayega jab set ho

# Exclude specific fields
@app.get("/items-no-tax", response_model=List[Item], response_model_exclude={"tax"})
def get_items_no_tax():
    return items_db

# Include only specific fields
@app.get("/items-names", response_model=List[Item], response_model_include={"name", "price"})
def get_item_names():
    return items_db
```

### Multiple Response Models (Union)
```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union

app = FastAPI()

class Cat(BaseModel):
    type: str = "cat"
    name: str
    meows: bool

class Dog(BaseModel):
    type: str = "dog"
    name: str
    barks: bool

@app.get("/animals/{animal_id}", response_model=Union[Cat, Dog])
def get_animal(animal_id: int):
    if animal_id == 1:
        return Cat(name="Whiskers", meows=True)
    return Dog(name="Buddy", barks=True)
```

---

## Status Codes

HTTP status codes response ke status batate hain.

### Common Status Codes
```python
from fastapi import FastAPI, status

app = FastAPI()

# 200 OK - Default for GET
@app.get("/items")
def get_items():
    return {"items": []}

# 201 Created - Resource created
@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item():
    return {"id": 1, "name": "New Item"}

# 204 No Content - Success but nothing to return
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    return None  # Empty response

# 202 Accepted - Request accepted, processing async
@app.post("/tasks", status_code=status.HTTP_202_ACCEPTED)
def create_task():
    return {"task_id": 123, "status": "processing"}
```

### Status Code Reference
```
| Code | Name                  | When to Use                    |
|------|-----------------------|--------------------------------|
| 200  | OK                    | Successful GET/PUT/PATCH       |
| 201  | Created               | Successful POST (new resource) |
| 204  | No Content            | Successful DELETE              |
| 400  | Bad Request           | Invalid input                  |
| 401  | Unauthorized          | Not logged in                  |
| 403  | Forbidden             | No permission                  |
| 404  | Not Found             | Resource doesn't exist         |
| 409  | Conflict              | Duplicate resource             |
| 422  | Unprocessable Entity  | Validation error               |
| 500  | Internal Server Error | Server crashed                 |
```

---

## HTTPException & Error Handling

### Basic HTTPException
```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

fake_db = {1: {"name": "Item 1"}, 2: {"name": "Item 2"}}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return fake_db[item_id]

# Response when not found:
# {
#     "detail": "Item 99 not found"
# }
```

### Custom Exception with Headers
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/protected")
def protected_route():
    raise HTTPException(
        status_code=401,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"}
    )
```

### Custom Exception Classes
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Custom Exception Class
class ItemNotFoundException(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

# Exception Handler register karo
@app.exception_handler(ItemNotFoundException)
async def item_not_found_handler(request: Request, exc: ItemNotFoundException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "ITEM_NOT_FOUND",
            "message": f"Item with ID {exc.item_id} was not found",
            "item_id": exc.item_id
        }
    )

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id > 100:
        raise ItemNotFoundException(item_id)
    return {"item_id": item_id}
```

### Global Exception Handler
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback

app = FastAPI()

# Catch all unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the error
    print(f"Error: {exc}")
    print(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "Something went wrong. Please try again.",
            "path": str(request.url)
        }
    )

# Validation error handler
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "details": errors
        }
    )
```

---

## Headers & Cookies

### Reading Headers
```python
from fastapi import FastAPI, Header
from typing import Optional

app = FastAPI()

@app.get("/items")
def get_items(
    user_agent: Optional[str] = Header(None),
    x_token: Optional[str] = Header(None, alias="X-Token"),
    accept_language: Optional[str] = Header(None)
):
    return {
        "User-Agent": user_agent,
        "X-Token": x_token,
        "Accept-Language": accept_language
    }

# FastAPI automatically converts:
# X-Token -> x_token (underscore to hyphen)
```

### Setting Response Headers
```python
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/items")
def get_items(response: Response):
    response.headers["X-Custom-Header"] = "Custom Value"
    response.headers["Cache-Control"] = "max-age=3600"
    return {"items": []}
```

### Cookies
```python
from fastapi import FastAPI, Cookie, Response
from typing import Optional

app = FastAPI()

# Read cookie
@app.get("/items")
def get_items(
    session_id: Optional[str] = Cookie(None),
    tracking_id: Optional[str] = Cookie(None)
):
    return {
        "session_id": session_id,
        "tracking_id": tracking_id
    }

# Set cookie
@app.post("/login")
def login(response: Response):
    response.set_cookie(
        key="session_id",
        value="abc123",
        max_age=3600,        # 1 hour
        httponly=True,       # JavaScript can't access
        secure=True,         # HTTPS only
        samesite="lax"       # CSRF protection
    )
    return {"message": "Logged in"}

# Delete cookie
@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("session_id")
    return {"message": "Logged out"}
```

---

## Form Data & File Uploads

### Form Data
```python
from fastapi import FastAPI, Form

app = FastAPI()

# Install: pip install python-multipart

@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...)
):
    return {"username": username}

# HTML form se submit hoga:
# <form method="post" action="/login">
#     <input name="username">
#     <input name="password" type="password">
#     <button type="submit">Login</button>
# </form>
```

### File Upload
```python
from fastapi import FastAPI, File, UploadFile
from typing import List

app = FastAPI()

# Simple file upload
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }

# Multiple files
@app.post("/upload-multiple")
async def upload_files(files: List[UploadFile] = File(...)):
    return {
        "filenames": [file.filename for file in files],
        "count": len(files)
    }

# Save file to disk
import shutil
from pathlib import Path

@app.post("/upload-and-save")
async def upload_and_save(file: UploadFile = File(...)):
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"saved_path": str(file_path)}

# File with form data
@app.post("/upload-with-data")
async def upload_with_data(
    file: UploadFile = File(...),
    description: str = Form(...),
    tags: str = Form(None)
):
    return {
        "filename": file.filename,
        "description": description,
        "tags": tags.split(",") if tags else []
    }
```

---

## Auto Documentation

FastAPI automatically documentation generate karta hai.

### Swagger UI
```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="""
    ## My Awesome API
    
    This API does amazing things:
    
    * **Create** items
    * **Read** items
    * **Update** items
    * **Delete** items
    
    ### Authentication
    Use Bearer token in Authorization header.
    """,
    version="1.0.0",
    terms_of_service="https://example.com/terms",
    contact={
        "name": "Tarun",
        "url": "https://example.com",
        "email": "tarun@example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Access Swagger UI: http://127.0.0.1:8000/docs
# Access ReDoc: http://127.0.0.1:8000/redoc
```

### Documenting Endpoints
```python
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    """
    Item model representing a product.
    
    Attributes:
        name: The name of the item
        price: Price in USD
        description: Optional description
    """
    name: str
    price: float
    description: str = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Laptop",
                "price": 999.99,
                "description": "A powerful laptop"
            }
        }

@app.post(
    "/items",
    response_model=Item,
    summary="Create an item",
    description="Create an item with name, price, and optional description.",
    response_description="The created item",
    tags=["Items"],
    deprecated=False
)
def create_item(item: Item):
    """
    Create an item with all the information:

    - **name**: required, unique name
    - **price**: required, must be positive
    - **description**: optional description
    """
    return item

@app.get(
    "/items",
    tags=["Items"],
    responses={
        200: {"description": "List of items"},
        404: {"description": "No items found"}
    }
)
def get_items(
    q: str = Query(
        None,
        title="Query string",
        description="Search query for items",
        example="laptop"
    )
):
    """Get all items, optionally filtered by query."""
    return []
```

### Tags for Organization
```python
from fastapi import FastAPI

app = FastAPI()

tags_metadata = [
    {
        "name": "Users",
        "description": "Operations with users. Login and registration.",
    },
    {
        "name": "Items",
        "description": "Manage items. CRUD operations.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://example.com/items-docs"
        }
    }
]

app = FastAPI(openapi_tags=tags_metadata)

@app.get("/users", tags=["Users"])
def get_users():
    return []

@app.get("/items", tags=["Items"])
def get_items():
    return []
```

---

## Testing with TestClient

### Basic Testing
```python
# test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_item():
    response = client.post(
        "/items",
        json={"name": "Test Item", "price": 10.5}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Item"

def test_get_item_not_found():
    response = client.get("/items/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
```

### Testing with Headers and Cookies
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_with_headers():
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer fake-token"}
    )
    assert response.status_code == 200

def test_with_cookies():
    response = client.get(
        "/items",
        cookies={"session_id": "abc123"}
    )
    assert response.status_code == 200
```

### Testing File Upload
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_file():
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"file content", "text/plain")}
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "test.txt"
```

### Running Tests
```bash
# Install pytest
pip install pytest

# Run tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest test_main.py

# Run with coverage
pip install pytest-cov
pytest --cov=. --cov-report=html
```

---

## Industry Patterns

### 1. API Versioning
```python
from fastapi import FastAPI, APIRouter

app = FastAPI()

# Version 1
v1_router = APIRouter(prefix="/api/v1")

@v1_router.get("/users")
def get_users_v1():
    return {"version": "v1", "users": []}

# Version 2
v2_router = APIRouter(prefix="/api/v2")

@v2_router.get("/users")
def get_users_v2():
    return {"version": "v2", "users": [], "total": 0}

app.include_router(v1_router)
app.include_router(v2_router)
```

### 2. Consistent Response Format
```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import TypeVar, Generic, Optional, List

app = FastAPI()

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    errors: Optional[List[str]] = None

class User(BaseModel):
    id: int
    name: str

@app.get("/users/{user_id}", response_model=APIResponse[User])
def get_user(user_id: int):
    user = User(id=user_id, name="Tarun")
    return APIResponse(
        success=True,
        message="User found",
        data=user
    )

# Response:
# {
#     "success": true,
#     "message": "User found",
#     "data": {"id": 1, "name": "Tarun"},
#     "errors": null
# }
```

### 3. Error Response Format
```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import time

app = FastAPI()

class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[List[str]] = None
    timestamp: float
    path: str

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=f"ERR_{exc.status_code}",
            message=exc.detail,
            timestamp=time.time(),
            path=str(request.url.path)
        ).dict()
    )
```

### 4. Request ID for Tracing
```python
from fastapi import FastAPI, Request
import uuid

app = FastAPI()

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response

@app.get("/")
def root(request: Request):
    return {"request_id": request.state.request_id}
```

---

## Complete Example

```python
# main.py - Complete CRUD API
from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

app = FastAPI(
    title="User Management API",
    description="A complete CRUD API for managing users",
    version="1.0.0"
)

# Models
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    bio: Optional[str] = Field(None, max_length=500)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Tarun",
                "email": "tarun@example.com",
                "age": 25,
                "bio": "Python Developer"
            }
        }

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    age: Optional[int] = Field(None, ge=0, le=150)
    bio: Optional[str] = Field(None, max_length=500)

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int
    bio: Optional[str]
    created_at: datetime
    
    class Config:
        orm_mode = True

# Fake Database
users_db = {}
next_id = 1

# Endpoints
@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/users", response_model=List[UserResponse], tags=["Users"])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=1)
):
    """Get all users with pagination and search."""
    users = list(users_db.values())
    
    if search:
        users = [u for u in users if search.lower() in u["name"].lower()]
    
    return users[skip:skip + limit]

@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: int):
    """Get a specific user by ID."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return users_db[user_id]

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: UserCreate):
    """Create a new user."""
    global next_id
    
    # Check duplicate email
    for existing in users_db.values():
        if existing["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
    
    new_user = {
        "id": next_id,
        **user.dict(),
        "created_at": datetime.utcnow()
    }
    users_db[next_id] = new_user
    next_id += 1
    
    return new_user

@app.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user(user_id: int, user: UserUpdate):
    """Update an existing user."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    existing = users_db[user_id]
    update_data = user.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        existing[field] = value
    
    return existing

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def delete_user(user_id: int):
    """Delete a user."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    del users_db[user_id]
    return None
```

---

## Practice Exercises

### Exercise 1: Todo API
```python
# Create a Todo API with:
# - GET /todos - List all todos (with filters: completed, priority)
# - GET /todos/{id} - Get single todo
# - POST /todos - Create todo
# - PUT /todos/{id} - Update todo
# - DELETE /todos/{id} - Delete todo
# - PATCH /todos/{id}/complete - Mark as complete
```

### Exercise 2: Product Search API
```python
# Create a Product API with:
# - Advanced search with multiple filters
# - Pagination (skip, limit)
# - Sorting (by name, price, created_at)
# - Price range filter (min_price, max_price)
# - Category filter
```

### Exercise 3: File Management API
```python
# Create a File API with:
# - Upload single/multiple files
# - List uploaded files
# - Download file by ID
# - Delete file
# - File metadata (size, type, upload date)
```

---

## Quick Reference

```python
# Basic route
@app.get("/path")
def handler(): pass

# Path parameter
@app.get("/items/{item_id}")
def handler(item_id: int): pass

# Query parameter
@app.get("/items")
def handler(skip: int = 0, limit: int = 10): pass

# Request body
@app.post("/items")
def handler(item: ItemCreate): pass

# Response model
@app.get("/items", response_model=List[Item])

# Status code
@app.post("/items", status_code=201)

# Exception
raise HTTPException(status_code=404, detail="Not found")

# Header
user_agent: str = Header(None)

# Cookie
session: str = Cookie(None)

# Form
username: str = Form(...)

# File
file: UploadFile = File(...)
```

---

## Next Steps

1. **Practice karo** - Exercises complete karo
2. **Test likho** - TestClient use karo
3. **Next doc padho** - `03_pydantic_validation.md`

---

> **Note**: Is doc ko bookmark karo for FastAPI quick reference!
