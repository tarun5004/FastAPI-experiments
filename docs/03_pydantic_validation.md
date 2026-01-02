# 03 — Pydantic & Validation (Complete In-Depth Guide - Hinglish)

> 🎯 **Goal**: Is guide ke baad tum Pydantic master ho jaoge - validation, serialization, custom validators sab.

---

## 📚 Table of Contents
1. [Pydantic Kya Hai?](#pydantic-kya-hai)
2. [Basic Models](#basic-models)
3. [Field Types](#field-types)
4. [Field Constraints](#field-constraints)
5. [Optional & Default Values](#optional--default-values)
6. [Nested Models](#nested-models)
7. [Custom Validators](#custom-validators)
8. [Model Config](#model-config)
9. [Serialization (dict/JSON)](#serialization)
10. [ORM Mode](#orm-mode)
11. [Schema Patterns (Create/Update/Response)](#schema-patterns)
12. [Advanced Features](#advanced-features)
13. [Error Handling](#error-handling)
14. [Industry Best Practices](#industry-best-practices)
15. [Practice Exercises](#practice-exercises)

---

## Pydantic Kya Hai?

Pydantic ek Python library hai jo:
- **Data Validation** - Input data validate karta hai
- **Data Parsing** - Strings ko correct types mein convert karta hai
- **Serialization** - Objects ko dict/JSON mein convert karta hai
- **Documentation** - Automatic schema generation

```python
# Without Pydantic - Manual validation (messy!)
def create_user(data: dict):
    if "name" not in data:
        raise ValueError("name required")
    if not isinstance(data["name"], str):
        raise ValueError("name must be string")
    if "age" in data and not isinstance(data["age"], int):
        raise ValueError("age must be integer")
    # ... bahut saari checks

# With Pydantic - Clean and automatic!
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

user = User(name="Tarun", age="25")  # "25" auto-converts to 25
print(user.age)  # 25 (int)
```

### Installation
```bash
pip install pydantic

# Email validation ke liye
pip install pydantic[email]
# OR
pip install email-validator
```

---

## Basic Models

### Creating a Model
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = True  # Default value
    created_at: datetime = None

# Creating instances
user1 = User(id=1, name="Tarun", email="tarun@example.com")
print(user1)
# id=1 name='Tarun' email='tarun@example.com' is_active=True created_at=None

# From dict
user_data = {"id": 2, "name": "Alice", "email": "alice@test.com"}
user2 = User(**user_data)
# OR
user2 = User.parse_obj(user_data)

# From JSON string
json_str = '{"id": 3, "name": "Bob", "email": "bob@test.com"}'
user3 = User.parse_raw(json_str)
```

### Automatic Type Conversion
```python
from pydantic import BaseModel

class Item(BaseModel):
    id: int
    price: float
    quantity: int

# Pydantic automatically converts
item = Item(id="123", price="99.99", quantity="5")
print(item.id)        # 123 (int, not "123")
print(item.price)     # 99.99 (float)
print(item.quantity)  # 5 (int)

# Kuch convert nahi ho sakta toh error
try:
    Item(id="abc", price=10, quantity=1)  # "abc" can't be int
except Exception as e:
    print(e)  # validation error
```

---

## Field Types

### Basic Types
```python
from pydantic import BaseModel
from typing import List, Dict, Set, Tuple, Optional, Any
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from uuid import UUID

class AllTypes(BaseModel):
    # Basic types
    name: str
    age: int
    price: float
    is_active: bool
    
    # Date/Time
    created_at: datetime
    birth_date: date
    start_time: time
    duration: timedelta
    
    # Collections
    tags: List[str]
    scores: Dict[str, int]
    unique_ids: Set[int]
    coordinates: Tuple[float, float]
    
    # Special types
    user_id: UUID
    amount: Decimal
    metadata: Any  # Any type allowed
    
    # Optional
    description: Optional[str] = None

# Usage
data = AllTypes(
    name="Test",
    age=25,
    price=99.99,
    is_active=True,
    created_at="2024-01-15T10:30:00",  # Auto-parsed!
    birth_date="1999-05-20",
    start_time="09:00:00",
    duration="P1DT2H",  # ISO 8601 duration
    tags=["python", "fastapi"],
    scores={"math": 90, "science": 85},
    unique_ids=[1, 2, 2, 3],  # Set removes duplicates
    coordinates=(28.6, 77.2),
    user_id="123e4567-e89b-12d3-a456-426614174000",
    amount="199.99"
)
```

### Special Pydantic Types
```python
from pydantic import (
    BaseModel, 
    EmailStr,           # Valid email
    HttpUrl,            # Valid HTTP URL
    AnyUrl,             # Any URL
    SecretStr,          # Hidden in logs
    FilePath,           # File must exist
    DirectoryPath,      # Directory must exist
    IPvAnyAddress,      # IP address
    PositiveInt,        # > 0
    NegativeInt,        # < 0
    PositiveFloat,
    NegativeFloat,
    conint,             # Constrained int
    constr,             # Constrained string
    confloat,           # Constrained float
    conlist,            # Constrained list
)

class SpecialTypes(BaseModel):
    email: EmailStr                    # Validated email
    website: HttpUrl                   # Must be valid HTTP URL
    password: SecretStr                # Won't show in logs
    ip: IPvAnyAddress                  # Valid IP address
    
    # Constrained types
    age: PositiveInt                   # Must be > 0
    rating: confloat(ge=0, le=5)       # 0 to 5
    username: constr(min_length=3, max_length=20, regex=r'^[a-z]+$')
    tags: conlist(str, min_items=1, max_items=10)

# Usage
user = SpecialTypes(
    email="tarun@example.com",
    website="https://example.com",
    password="secret123",
    ip="192.168.1.1",
    age=25,
    rating=4.5,
    username="tarun",
    tags=["python", "fastapi"]
)

# SecretStr hides value
print(user.password)              # SecretStr('**********')
print(user.password.get_secret_value())  # 'secret123'
```

---

## Field Constraints

### Using Field()
```python
from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    # Required field with constraints
    name: str = Field(
        ...,                          # ... means required
        min_length=1,
        max_length=100,
        title="Product Name",
        description="The name of the product",
        example="Laptop"
    )
    
    # Numeric constraints
    price: float = Field(
        ...,
        gt=0,                         # Greater than 0
        le=1000000,                   # Less than or equal
        description="Price in USD"
    )
    
    # With default
    quantity: int = Field(
        default=1,
        ge=0,                         # Greater than or equal
        le=10000
    )
    
    # Optional with constraints
    description: Optional[str] = Field(
        None,
        max_length=500
    )
    
    # Regex pattern
    sku: str = Field(
        ...,
        regex=r'^[A-Z]{3}-\d{4}$',    # ABC-1234 format
        example="PRD-1234"
    )

# Constraints summary:
# gt  = greater than (>)
# ge  = greater than or equal (>=)
# lt  = less than (<)
# le  = less than or equal (<=)
# min_length = minimum string length
# max_length = maximum string length
# regex = regular expression pattern
```

### Field Aliases
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    # When JSON uses different key names
    user_id: int = Field(..., alias="userId")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    
    class Config:
        populate_by_name = True  # Allow both alias and field name

# Can use either
user1 = User(userId=1, firstName="Tarun", lastName="Kumar")
user2 = User(user_id=2, first_name="Alice", last_name="Smith")

# Output uses alias by default
print(user1.dict(by_alias=True))
# {'userId': 1, 'firstName': 'Tarun', 'lastName': 'Kumar'}
```

---

## Optional & Default Values

### Optional Fields
```python
from pydantic import BaseModel, Field
from typing import Optional, Union, List

class UserProfile(BaseModel):
    # Required - must provide
    username: str
    email: str
    
    # Optional with None default
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Optional with actual default
    role: str = "user"
    is_active: bool = True
    
    # Complex default (use Field with default_factory)
    tags: List[str] = Field(default_factory=list)
    settings: dict = Field(default_factory=dict)

# Usage
user = UserProfile(username="tarun", email="tarun@test.com")
print(user.bio)       # None
print(user.role)      # "user"
print(user.tags)      # []
```

### Default Factory (Important!)
```python
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime

class Post(BaseModel):
    title: str
    
    # WRONG - Same list shared by all instances
    # tags: List[str] = []
    
    # RIGHT - New list for each instance
    tags: List[str] = Field(default_factory=list)
    
    # Dynamic default
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Custom factory
    metadata: Dict[str, str] = Field(
        default_factory=lambda: {"version": "1.0"}
    )
```

### Union Types
```python
from pydantic import BaseModel
from typing import Union, List

class Response(BaseModel):
    # Either int or str
    id: Union[int, str]
    
    # Either single item or list
    data: Union[dict, List[dict]]

# Both valid
r1 = Response(id=123, data={"key": "value"})
r2 = Response(id="abc-123", data=[{"a": 1}, {"b": 2}])
```

---

## Nested Models

### Basic Nesting
```python
from pydantic import BaseModel
from typing import List, Optional

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "India"

class Company(BaseModel):
    name: str
    website: Optional[str] = None

class User(BaseModel):
    id: int
    name: str
    email: str
    address: Address                    # Nested model
    company: Optional[Company] = None   # Optional nested
    
# Usage
user_data = {
    "id": 1,
    "name": "Tarun",
    "email": "tarun@example.com",
    "address": {
        "street": "123 Main St",
        "city": "Mumbai",
        "state": "Maharashtra",
        "zip_code": "400001"
    },
    "company": {
        "name": "TechCorp"
    }
}

user = User(**user_data)
print(user.address.city)  # Mumbai
print(user.company.name)  # TechCorp
```

### List of Nested Models
```python
from pydantic import BaseModel
from typing import List
from datetime import datetime

class OrderItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    
    @property
    def total(self) -> float:
        return self.quantity * self.unit_price

class Order(BaseModel):
    id: int
    user_id: int
    items: List[OrderItem]
    created_at: datetime
    
    @property
    def order_total(self) -> float:
        return sum(item.total for item in self.items)

# Usage
order = Order(
    id=1,
    user_id=100,
    items=[
        {"product_id": 1, "product_name": "Laptop", "quantity": 1, "unit_price": 999.99},
        {"product_id": 2, "product_name": "Mouse", "quantity": 2, "unit_price": 29.99}
    ],
    created_at="2024-01-15T10:30:00"
)

print(order.order_total)  # 1059.97
```

### Self-Referencing Models
```python
from pydantic import BaseModel
from typing import List, Optional, ForwardRef

# For recursive structures
class Category(BaseModel):
    name: str
    parent: Optional['Category'] = None
    children: List['Category'] = []
    
    class Config:
        # Required for self-reference
        pass

# Need to update forward references
Category.update_forward_refs()

# Usage
electronics = Category(name="Electronics")
phones = Category(name="Phones", parent=electronics)
laptops = Category(name="Laptops", parent=electronics)
electronics.children = [phones, laptops]
```

---

## Custom Validators

### Field Validators
```python
from pydantic import BaseModel, validator, root_validator
from typing import List
import re

class User(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
    age: int
    tags: List[str] = []
    
    # Single field validator
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('must be alphanumeric')
        if len(v) < 3:
            raise ValueError('must be at least 3 characters')
        return v.lower()  # Transform value
    
    # Email validation
    @validator('email')
    def email_valid(cls, v):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, v):
            raise ValueError('invalid email format')
        return v.lower()
    
    # Age validation
    @validator('age')
    def age_valid(cls, v):
        if v < 0 or v > 150:
            raise ValueError('age must be between 0 and 150')
        return v
    
    # Validate each item in list
    @validator('tags', each_item=True)
    def tag_valid(cls, v):
        if len(v) > 20:
            raise ValueError('tag too long')
        return v.lower()
    
    # Validate using other fields (pre=False, always runs after other validators)
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

# Usage
try:
    user = User(
        username="tarun123",
        email="TARUN@Example.COM",
        password="secret123",
        confirm_password="secret123",
        age=25,
        tags=["Python", "FastAPI"]
    )
    print(user.email)  # tarun@example.com (lowercased)
except Exception as e:
    print(e)
```

### Root Validators
```python
from pydantic import BaseModel, root_validator
from typing import Optional

class Discount(BaseModel):
    percentage: Optional[float] = None
    fixed_amount: Optional[float] = None
    
    # Validate whole model
    @root_validator
    def check_discount(cls, values):
        percentage = values.get('percentage')
        fixed_amount = values.get('fixed_amount')
        
        # At least one must be provided
        if percentage is None and fixed_amount is None:
            raise ValueError('Either percentage or fixed_amount required')
        
        # Can't have both
        if percentage is not None and fixed_amount is not None:
            raise ValueError('Cannot have both percentage and fixed_amount')
        
        # Validate ranges
        if percentage is not None and (percentage < 0 or percentage > 100):
            raise ValueError('percentage must be 0-100')
        
        return values

class DateRange(BaseModel):
    start_date: str
    end_date: str
    
    @root_validator
    def check_dates(cls, values):
        from datetime import datetime
        start = datetime.fromisoformat(values['start_date'])
        end = datetime.fromisoformat(values['end_date'])
        
        if end < start:
            raise ValueError('end_date must be after start_date')
        
        return values
```

### Pre Validators
```python
from pydantic import BaseModel, validator

class Item(BaseModel):
    name: str
    price: float
    
    # Pre-validator runs BEFORE type conversion
    @validator('price', pre=True)
    def parse_price(cls, v):
        if isinstance(v, str):
            # Handle "$99.99" format
            v = v.replace('$', '').replace(',', '')
        return v
    
    @validator('name', pre=True)
    def clean_name(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

# Works with different formats
item1 = Item(name="  Laptop  ", price="$1,299.99")
print(item1.name)   # "Laptop"
print(item1.price)  # 1299.99
```

---

## Model Config

### Configuration Options
```python
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    user_id: int
    user_name: str
    created_at: datetime
    
    class Config:
        # ORM mode (for SQLAlchemy)
        orm_mode = True
        
        # Allow field name or alias
        populate_by_name = True
        
        # Validate on assignment
        validate_assignment = True
        
        # Extra fields handling
        extra = 'forbid'  # 'allow', 'ignore', 'forbid'
        
        # Immutable model
        frozen = False  # True = can't change after creation
        
        # Custom JSON encoders
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        # Underscore attributes
        underscore_attrs_are_private = True
        
        # Schema customization
        schema_extra = {
            "example": {
                "user_id": 1,
                "user_name": "tarun",
                "created_at": "2024-01-15T10:30:00"
            }
        }

# Extra fields behavior
class StrictModel(BaseModel):
    name: str
    
    class Config:
        extra = 'forbid'  # Raises error for unknown fields

try:
    StrictModel(name="Test", unknown_field="value")  # Error!
except Exception as e:
    print("Extra field not allowed")
```

### Mutable vs Immutable
```python
from pydantic import BaseModel

class MutableUser(BaseModel):
    name: str
    age: int
    
    class Config:
        validate_assignment = True  # Validate when changing

user = MutableUser(name="Tarun", age=25)
user.age = 30  # OK - validates new value
# user.age = -5  # Error - validation fails

class ImmutableUser(BaseModel):
    name: str
    age: int
    
    class Config:
        frozen = True  # Can't change

frozen_user = ImmutableUser(name="Alice", age=25)
# frozen_user.age = 30  # Error - model is frozen
```

---

## Serialization

### Converting to Dict/JSON
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: int
    name: str
    email: str
    password: str
    created_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }

user = User(
    id=1,
    name="Tarun",
    email="tarun@example.com",
    password="secret",
    created_at=datetime.now()
)

# To dict
user_dict = user.dict()
print(user_dict)
# {'id': 1, 'name': 'Tarun', 'email': 'tarun@example.com', 
#  'password': 'secret', 'created_at': datetime(...), 'deleted_at': None}

# Exclude fields
user_dict = user.dict(exclude={'password'})
# No password in output

# Include only specific fields
user_dict = user.dict(include={'id', 'name', 'email'})

# Exclude None values
user_dict = user.dict(exclude_none=True)
# deleted_at won't appear

# Exclude unset values (fields not explicitly set)
user_dict = user.dict(exclude_unset=True)

# To JSON string
json_str = user.json()
print(json_str)

# To JSON with excludes
json_str = user.json(exclude={'password'})

# With alias
json_str = user.json(by_alias=True)
```

### Custom Serialization
```python
from pydantic import BaseModel
from typing import Any

class Product(BaseModel):
    name: str
    price: float
    
    def dict(self, **kwargs) -> dict:
        d = super().dict(**kwargs)
        # Add computed field
        d['price_with_tax'] = round(self.price * 1.18, 2)
        return d

product = Product(name="Laptop", price=1000)
print(product.dict())
# {'name': 'Laptop', 'price': 1000, 'price_with_tax': 1180.0}
```

---

## ORM Mode

### Working with SQLAlchemy
```python
from pydantic import BaseModel
from typing import List, Optional

# Pydantic model with ORM mode
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    posts: List['PostResponse'] = []
    
    class Config:
        orm_mode = True  # This is key!

class PostResponse(BaseModel):
    id: int
    title: str
    
    class Config:
        orm_mode = True

UserResponse.update_forward_refs()

# SQLAlchemy model (example)
# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     email = Column(String)
#     is_active = Column(Boolean)
#     posts = relationship("Post", back_populates="author")

# Usage in FastAPI
# @app.get("/users/{user_id}", response_model=UserResponse)
# def get_user(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == user_id).first()
#     return user  # Automatically converts SQLAlchemy -> Pydantic
```

### Why ORM Mode?
```python
# Without orm_mode, you'd need:
user_dict = {
    "id": db_user.id,
    "name": db_user.name,
    "email": db_user.email,
    # ... manually map every field
}
return UserResponse(**user_dict)

# With orm_mode, Pydantic reads attributes directly:
return db_user  # Works automatically!
```

---

## Schema Patterns

### CRUD Schema Pattern (Industry Standard)
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# ===== Base Schema (shared fields) =====
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr

# ===== Create Schema (for POST) =====
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    # No id, no created_at (server generates)

# ===== Update Schema (for PUT/PATCH) =====
class UserUpdate(BaseModel):
    # All optional for partial updates
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    # No password here (separate endpoint)
    # No id, no created_at (can't change)

# ===== Response Schema (for GET) =====
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    # No password (never expose)
    
    class Config:
        orm_mode = True

# ===== List Response =====
class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int

# ===== Password Change Schema =====
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('passwords do not match')
        return v

# Usage in FastAPI
# @app.post("/users", response_model=UserResponse)
# def create_user(user: UserCreate, db: Session = Depends(get_db)):
#     ...
#
# @app.put("/users/{id}", response_model=UserResponse)
# def update_user(id: int, user: UserUpdate, db: Session = Depends(get_db)):
#     ...
```

### Relationship Schemas
```python
from pydantic import BaseModel
from typing import List, Optional

# ===== Simple response (no relationships) =====
class PostSimple(BaseModel):
    id: int
    title: str
    
    class Config:
        orm_mode = True

class UserSimple(BaseModel):
    id: int
    name: str
    
    class Config:
        orm_mode = True

# ===== With relationship =====
class PostWithAuthor(PostSimple):
    author: UserSimple  # Include author info

class UserWithPosts(UserSimple):
    posts: List[PostSimple] = []  # Include posts

# ===== Full detail =====
class UserFull(BaseModel):
    id: int
    name: str
    email: str
    posts: List[PostSimple] = []
    profile: Optional['ProfileResponse'] = None
    
    class Config:
        orm_mode = True
```

---

## Advanced Features

### Computed Fields (Python 3.9+)
```python
from pydantic import BaseModel, computed_field
from typing import List

class Order(BaseModel):
    items: List[dict]  # [{price: 100, quantity: 2}, ...]
    tax_rate: float = 0.18
    
    @computed_field
    @property
    def subtotal(self) -> float:
        return sum(item['price'] * item['quantity'] for item in self.items)
    
    @computed_field
    @property
    def tax(self) -> float:
        return round(self.subtotal * self.tax_rate, 2)
    
    @computed_field
    @property
    def total(self) -> float:
        return round(self.subtotal + self.tax, 2)

order = Order(items=[
    {"price": 100, "quantity": 2},
    {"price": 50, "quantity": 3}
])
print(order.dict())
# {'items': [...], 'tax_rate': 0.18, 'subtotal': 350, 'tax': 63.0, 'total': 413.0}
```

### Generic Models
```python
from pydantic import BaseModel
from typing import TypeVar, Generic, List, Optional

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

class User(BaseModel):
    id: int
    name: str

class Product(BaseModel):
    id: int
    name: str
    price: float

# Usage
user_response: PaginatedResponse[User] = PaginatedResponse(
    items=[User(id=1, name="Tarun")],
    total=100,
    page=1,
    per_page=10,
    has_next=True,
    has_prev=False
)

product_response: PaginatedResponse[Product] = PaginatedResponse(
    items=[Product(id=1, name="Laptop", price=999.99)],
    total=50,
    page=1,
    per_page=10,
    has_next=True,
    has_prev=False
)
```

### Dynamic Model Creation
```python
from pydantic import create_model

# Create model dynamically
DynamicUser = create_model(
    'DynamicUser',
    name=(str, ...),           # Required
    age=(int, 25),             # Default 25
    email=(str, None)          # Optional
)

user = DynamicUser(name="Tarun")
print(user)  # name='Tarun' age=25 email=None
```

---

## Error Handling

### Understanding Validation Errors
```python
from pydantic import BaseModel, ValidationError, validator

class User(BaseModel):
    name: str
    age: int
    email: str

# Catch and process errors
try:
    user = User(name=123, age="not a number", email="invalid")
except ValidationError as e:
    print(e.json())  # JSON format
    
    # Access individual errors
    for error in e.errors():
        print(f"Field: {error['loc']}")
        print(f"Error: {error['msg']}")
        print(f"Type: {error['type']}")
        print("---")

# Output:
# Field: ('name',)
# Error: str type expected
# Type: type_error.str
# ---
# Field: ('age',)
# Error: value is not a valid integer
# Type: type_error.integer
# ---
```

### Custom Error Messages
```python
from pydantic import BaseModel, validator

class Product(BaseModel):
    name: str
    price: float
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v
    
    @validator('name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()
```

### FastAPI Error Response
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Validation failed",
            "errors": errors
        }
    )
```

---

## Industry Best Practices

### 1. Schema Organization
```
app/
├── schemas/
│   ├── __init__.py
│   ├── base.py           # Base schemas, common fields
│   ├── user.py           # User-related schemas
│   ├── product.py        # Product schemas
│   ├── order.py          # Order schemas
│   └── common.py         # Pagination, responses, etc.
```

### 2. Base Schema Pattern
```python
# schemas/base.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TimestampMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class IDMixin(BaseModel):
    id: int

# schemas/user.py
from .base import TimestampMixin, IDMixin

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase, IDMixin, TimestampMixin):
    is_active: bool
    
    class Config:
        orm_mode = True
```

### 3. Response Wrapper
```python
from pydantic import BaseModel
from typing import TypeVar, Generic, Optional, List

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None

class PaginatedData(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int

# Usage in FastAPI
# @app.get("/users", response_model=APIResponse[PaginatedData[UserResponse]])
```

### 4. Validation Best Practices
```python
from pydantic import BaseModel, validator, root_validator
from typing import Optional
import re

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    
    # Normalize data
    @validator('username', 'email', pre=True)
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v
    
    # Lowercase email
    @validator('email')
    def lowercase_email(cls, v):
        return v.lower()
    
    # Strong password validation
    @validator('password')
    def strong_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain a digit')
        return v
```

---

## Practice Exercises

### Exercise 1: E-commerce Schemas
```python
# Create complete schemas for:
# - Product (with variants, images, categories)
# - Cart (with items, quantities)
# - Order (with shipping address, payment method)
# - Include proper validation
```

### Exercise 2: User Registration
```python
# Create registration schema with:
# - Username (alphanumeric, 3-20 chars)
# - Email (valid format)
# - Password (strong validation)
# - Date of birth (must be 18+)
# - Terms acceptance (must be true)
```

### Exercise 3: API Response
```python
# Create generic response schemas:
# - Success response with data
# - Error response with details
# - Paginated list response
# - Use Generic types
```

---

## Quick Reference

```python
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List

class Model(BaseModel):
    # Required
    name: str
    
    # With constraints
    age: int = Field(..., ge=0, le=150)
    
    # Optional
    bio: Optional[str] = None
    
    # Default
    active: bool = True
    
    # List with default factory
    tags: List[str] = Field(default_factory=list)
    
    # Field validator
    @validator('name')
    def validate_name(cls, v):
        return v.strip()
    
    # Root validator
    @root_validator
    def validate_all(cls, values):
        return values
    
    class Config:
        orm_mode = True
        extra = 'forbid'

# Convert
model.dict()
model.json()
Model.parse_obj(dict)
Model.parse_raw(json_str)
```

---

## Next Steps

1. **Practice karo** - Exercises complete karo
2. **Project mein use karo** - Real schemas banao
3. **Next doc padho** - `04_async_await.md`

---

> **Note**: Pydantic FastAPI ki backbone hai. Isko achhe se samajh lo!
