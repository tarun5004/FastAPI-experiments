# 07 — SQLAlchemy Basics (Complete In-Depth Guide)

> 🎯 **Goal**: SQLAlchemy master ban jao - ORM, models, relationships sab samajh aayega!

---

## 📚 Table of Contents
1. [What is SQLAlchemy?](#what-is-sqlalchemy)
2. [Installation & Setup](#installation--setup)
3. [Engine & Connection](#engine--connection)
4. [Declarative Base](#declarative-base)
5. [Column Types](#column-types)
6. [Column Constraints](#column-constraints)
7. [Table Relationships](#table-relationships)
8. [One-to-Many](#one-to-many)
9. [Many-to-Many](#many-to-many)
10. [One-to-One](#one-to-one)
11. [Self-Referential](#self-referential)
12. [Session Management](#session-management)
13. [Model Methods](#model-methods)
14. [Mixins & Base Classes](#mixins--base-classes)
15. [Industry Best Practices](#industry-best-practices)
16. [Practice Exercises](#practice-exercises)

---

## What is SQLAlchemy?

### ORM Kya Hai?
```python
# Without ORM (Raw SQL)
cursor.execute("""
    INSERT INTO users (name, email, age) 
    VALUES ('Tarun', 'tarun@test.com', 25)
""")

# With ORM (SQLAlchemy)
user = User(name="Tarun", email="tarun@test.com", age=25)
db.add(user)
db.commit()

# ORM = Object Relational Mapper
# Python objects <-> Database tables
# Write Python, not SQL!
```

### SQLAlchemy Components
```
SQLAlchemy
├── Core (Low-level)
│   ├── Engine (Database connection)
│   ├── SQL Expression Language
│   └── Connection Pooling
│
└── ORM (High-level) - WE'LL USE THIS
    ├── Session (Transaction management)
    ├── Declarative Base (Model definition)
    └── Query Interface
```

### Sync vs Async
```python
# Sync (Traditional) - Simpler, use this first
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Async (Advanced) - Better performance
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
```

---

## Installation & Setup

### Install Dependencies
```bash
# Core SQLAlchemy
pip install sqlalchemy

# For SQLite (built-in, no extra install needed)

# For PostgreSQL
pip install psycopg2-binary

# For MySQL
pip install pymysql

# For async support
pip install aiosqlite asyncpg
```

### Basic Setup
```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URLs
# SQLite
DATABASE_URL = "sqlite:///./app.db"

# PostgreSQL
# DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"

# MySQL
# DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/dbname"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Only for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Engine & Connection

### Engine Configuration
```python
from sqlalchemy import create_engine

# Basic engine
engine = create_engine("sqlite:///./app.db")

# With options
engine = create_engine(
    "postgresql://user:pass@localhost/db",
    
    # Connection pool settings
    pool_size=5,           # Number of connections to keep
    max_overflow=10,       # Extra connections when pool is full
    pool_timeout=30,       # Seconds to wait for connection
    pool_recycle=1800,     # Recycle connections after 30 min
    pool_pre_ping=True,    # Test connections before use
    
    # Logging
    echo=True,             # Log all SQL statements
    echo_pool=True,        # Log connection pool events
    
    # Other options
    future=True,           # Use SQLAlchemy 2.0 style
)

# Engine methods
engine.connect()           # Get connection
engine.execute(text("SELECT 1"))  # Execute raw SQL
engine.dispose()           # Close all connections
```

### Connection URL Formats
```python
# SQLite
# Memory database
"sqlite:///:memory:"

# File database
"sqlite:///./app.db"           # Relative path
"sqlite:////absolute/path/app.db"  # Absolute path

# PostgreSQL
"postgresql://user:password@host:port/database"
"postgresql://user:pass@localhost:5432/mydb"

# MySQL
"mysql+pymysql://user:password@host:port/database"
"mysql+pymysql://user:pass@localhost:3306/mydb"

# With special characters in password (URL encode)
"postgresql://user:p%40ssword@localhost/db"  # @ = %40
```

---

## Declarative Base

### Creating Models
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    # Table name (required)
    __tablename__ = "users"
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    full_name = Column(String(100))
    bio = Column(Text)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Table configuration
    __table_args__ = (
        # Composite index
        # Index('idx_user_email_username', 'email', 'username'),
        # Unique constraint on multiple columns
        # UniqueConstraint('email', 'username', name='uq_user_email_username'),
    )
    
    # String representation
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

# Create all tables
Base.metadata.create_all(bind=engine)

# Drop all tables (careful!)
# Base.metadata.drop_all(bind=engine)
```

### Alternative: Mapped Class (SQLAlchemy 2.0 Style)
```python
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from typing import Optional
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    # Type hints with Mapped
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    username: Mapped[str] = mapped_column(String(50))
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

---

## Column Types

### Common Column Types
```python
from sqlalchemy import (
    Column, Integer, BigInteger, SmallInteger,
    String, Text, Unicode, UnicodeText,
    Boolean, 
    Float, Numeric, 
    Date, DateTime, Time, Interval,
    LargeBinary,
    Enum,
    JSON,
    ARRAY  # PostgreSQL only
)
from datetime import datetime, date, time
from decimal import Decimal
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class Example(Base):
    __tablename__ = "examples"
    
    id = Column(Integer, primary_key=True)
    
    # Integers
    small_num = Column(SmallInteger)        # -32768 to 32767
    regular_num = Column(Integer)           # -2B to 2B
    big_num = Column(BigInteger)            # Very large numbers
    
    # Strings
    short_text = Column(String(100))        # VARCHAR(100)
    long_text = Column(Text)                # TEXT (unlimited)
    unicode_text = Column(Unicode(100))     # NVARCHAR
    
    # Booleans
    is_active = Column(Boolean, default=True)
    
    # Numbers
    price = Column(Float)                   # Approximate decimals
    exact_price = Column(Numeric(10, 2))    # Exact: 10 digits, 2 decimal
    
    # Date/Time
    birth_date = Column(Date)               # Date only
    created_at = Column(DateTime)           # Date and time
    start_time = Column(Time)               # Time only
    duration = Column(Interval)             # Time interval
    
    # Binary
    file_data = Column(LargeBinary)         # Binary data
    
    # Enum
    role = Column(Enum(UserRole))           # Enum type
    
    # JSON (PostgreSQL, MySQL 5.7+, SQLite 3.9+)
    settings = Column(JSON)                 # JSON data
    
    # Array (PostgreSQL only)
    # tags = Column(ARRAY(String))
```

### Custom Types
```python
from sqlalchemy import TypeDecorator, String
import json

class JSONEncodedDict(TypeDecorator):
    """Store dict as JSON string"""
    impl = String(500)
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    metadata = Column(JSONEncodedDict)  # Custom type
```

---

## Column Constraints

### All Constraint Options
```python
from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, UniqueConstraint

class User(Base):
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Unique constraint
    email = Column(String(100), unique=True)
    
    # Not null
    username = Column(String(50), nullable=False)
    
    # Default value
    role = Column(String(20), default="user")
    
    # Server default (database-level)
    created_at = Column(DateTime, server_default=func.now())
    
    # Index for faster queries
    name = Column(String(100), index=True)
    
    # Foreign key
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    # Check constraint
    age = Column(Integer, CheckConstraint("age >= 0 AND age <= 150"))
    
    # On update
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Table-level constraints
    __table_args__ = (
        # Composite primary key
        # PrimaryKeyConstraint('id', 'email'),
        
        # Composite unique constraint
        UniqueConstraint('email', 'username', name='uq_user_email_username'),
        
        # Composite index
        # Index('idx_name_email', 'name', 'email'),
        
        # Check constraint
        CheckConstraint('age >= 18', name='check_adult'),
    )
```

### Foreign Key Options
```python
from sqlalchemy import Column, Integer, ForeignKey

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    
    # Basic foreign key
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # With cascade options
    category_id = Column(
        Integer, 
        ForeignKey(
            "categories.id",
            ondelete="CASCADE",    # Delete posts when category deleted
            onupdate="CASCADE"     # Update if category id changes
        )
    )
    
    # Options:
    # ondelete/onupdate:
    # - CASCADE: Delete/update related rows
    # - SET NULL: Set to NULL
    # - SET DEFAULT: Set to default value
    # - RESTRICT: Prevent delete/update if related rows exist
    # - NO ACTION: Similar to RESTRICT
```

---

## Table Relationships

### Relationship Basics
```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    
    # Relationship to posts (one user has many posts)
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationship to user (each post has one author)
    author = relationship("User", back_populates="posts")

# Usage
user = User(name="Tarun")
post = Post(title="My First Post", author=user)
# OR
user.posts.append(post)
```

---

## One-to-Many

### Parent-Child Relationship
```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# One User -> Many Posts
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    
    # One-to-many relationship
    posts = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan",  # Delete posts when user deleted
        lazy="dynamic"  # Return query object instead of list
    )

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    author = relationship("User", back_populates="posts")

# Usage
user = db.query(User).filter(User.id == 1).first()

# Access posts
for post in user.posts:
    print(post.title)

# With lazy="dynamic", you can filter
recent_posts = user.posts.filter(Post.created_at > some_date).all()

# Create post with author
post = Post(title="New Post", content="...", author=user)
db.add(post)
db.commit()
```

### Cascade Options
```python
# cascade options:
# - "save-update": Save related objects when parent saved
# - "merge": Merge related objects when parent merged
# - "expunge": Expunge related objects when parent expunged
# - "delete": Delete related objects when parent deleted
# - "delete-orphan": Delete orphaned objects (removed from relationship)
# - "refresh-expire": Refresh/expire related when parent refreshed
# - "all": All except delete-orphan

posts = relationship(
    "Post",
    cascade="all, delete-orphan",  # Most common for owned relationships
    passive_deletes=True  # Let database handle deletes (with ON DELETE CASCADE)
)
```

---

## Many-to-Many

### Association Table
```python
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

# Association table (no class needed)
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    
    # Many-to-many
    tags = relationship(
        "Tag",
        secondary=post_tags,       # Association table
        back_populates="posts",
        lazy="selectin"            # Eager load with separate SELECT IN
    )

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    
    posts = relationship(
        "Post",
        secondary=post_tags,
        back_populates="tags"
    )

# Usage
post = Post(title="My Post")
tag1 = Tag(name="python")
tag2 = Tag(name="fastapi")

# Add tags to post
post.tags.append(tag1)
post.tags.append(tag2)
# OR
post.tags = [tag1, tag2]

# Add post to tag
tag1.posts.append(post)

# Query
python_posts = db.query(Post).join(Post.tags).filter(Tag.name == "python").all()
```

### Association Object (Extra Data)
```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# When you need extra columns in association
class PostTag(Base):
    __tablename__ = "post_tags"
    
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    
    # Extra data
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    post = relationship("Post", back_populates="post_tags")
    tag = relationship("Tag", back_populates="post_tags")
    creator = relationship("User")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    
    post_tags = relationship("PostTag", back_populates="post")
    
    # Convenience property
    @property
    def tags(self):
        return [pt.tag for pt in self.post_tags]

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    
    post_tags = relationship("PostTag", back_populates="tag")

# Usage
post = Post(title="My Post")
tag = Tag(name="python")

# Create association with extra data
post_tag = PostTag(post=post, tag=tag, created_by=user.id)
db.add(post_tag)
```

---

## One-to-One

### One-to-One Relationship
```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    
    # One-to-one (uselist=False means single object, not list)
    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,           # Return single object
        cascade="all, delete-orphan"
    )

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True)
    bio = Column(Text)
    avatar_url = Column(String(500))
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)  # unique for 1-1
    
    user = relationship("User", back_populates="profile")

# Usage
user = User(name="Tarun")
profile = Profile(bio="Developer", avatar_url="https://...", user=user)
# OR
user.profile = profile

# Access
print(user.profile.bio)
```

---

## Self-Referential

### Parent-Child (Tree Structure)
```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    parent_id = Column(Integer, ForeignKey("categories.id"))
    
    # Self-referential relationship
    children = relationship(
        "Category",
        backref=backref("parent", remote_side=[id]),
        lazy="dynamic"
    )

# Usage
electronics = Category(name="Electronics")
phones = Category(name="Phones", parent=electronics)
laptops = Category(name="Laptops", parent=electronics)

# Access
print(phones.parent.name)  # Electronics
print(electronics.children.all())  # [Phones, Laptops]
```

### Employee-Manager
```python
class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    manager_id = Column(Integer, ForeignKey("employees.id"))
    
    # Reports (employees managed by this person)
    reports = relationship(
        "Employee",
        backref=backref("manager", remote_side=[id])
    )

# Usage
ceo = Employee(name="CEO")
vp = Employee(name="VP", manager=ceo)
developer = Employee(name="Developer", manager=vp)

print(vp.manager.name)  # CEO
print(ceo.reports)  # [VP]
```

---

## Session Management

### Session Basics
```python
from sqlalchemy.orm import sessionmaker, Session

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create session
db = SessionLocal()

try:
    # Do operations
    user = User(name="Tarun")
    db.add(user)
    db.commit()
except Exception:
    db.rollback()
    raise
finally:
    db.close()

# Better: Context manager
from contextlib import contextmanager

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# Usage
with get_db_session() as db:
    user = User(name="Tarun")
    db.add(user)
    # Auto-commits on exit
```

### Session Operations
```python
db = SessionLocal()

# Add single object
user = User(name="Tarun")
db.add(user)

# Add multiple objects
db.add_all([user1, user2, user3])

# Commit changes
db.commit()

# Rollback changes
db.rollback()

# Refresh object from database
db.refresh(user)

# Expunge (detach from session)
db.expunge(user)

# Expire (mark for reload)
db.expire(user)

# Delete
db.delete(user)
db.commit()

# Check if object in session
user in db  # True/False

# Get object state
from sqlalchemy import inspect
state = inspect(user)
state.pending    # Not yet in database
state.persistent # In database and session
state.detached   # Was in session, now detached
state.transient  # Never added to session
```

### Flush vs Commit
```python
# Flush: Send changes to database but don't commit transaction
db.add(user)
db.flush()  # User now has id, but transaction not committed
print(user.id)  # 1

# Commit: Flush + commit transaction
db.commit()  # Now permanent

# Example: Need ID before commit
user = User(name="Tarun")
db.add(user)
db.flush()  # Get ID
post = Post(title="Hello", user_id=user.id)
db.add(post)
db.commit()  # Commit both
```

---

## Model Methods

### Adding Methods to Models
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    posts = relationship("Post", back_populates="author")
    
    # Instance methods
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)
    
    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)
    
    @property
    def post_count(self) -> int:
        return len(self.posts)
    
    @property
    def is_new(self) -> bool:
        return (datetime.utcnow() - self.created_at).days < 7
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "post_count": self.post_count,
            "created_at": self.created_at.isoformat()
        }
    
    # Class methods
    @classmethod
    def create(cls, db: Session, email: str, password: str):
        user = cls(email=email)
        user.set_password(password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @classmethod
    def get_by_email(cls, db: Session, email: str):
        return db.query(cls).filter(cls.email == email).first()
    
    # String representation
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
```

### Hybrid Properties
```python
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Float)
    quantity = Column(Integer)
    
    @hybrid_property
    def total_value(self):
        """Works on both instance and query"""
        return self.price * self.quantity
    
    @hybrid_method
    def is_affordable(self, max_price: float):
        return self.price <= max_price

# Usage
product = Product(price=100, quantity=5)
print(product.total_value)  # 500

# Also works in queries!
expensive = db.query(Product).filter(Product.total_value > 1000).all()
affordable = db.query(Product).filter(Product.is_affordable(100)).all()
```

---

## Mixins & Base Classes

### Timestamp Mixin
```python
from sqlalchemy import Column, DateTime
from datetime import datetime

class TimestampMixin:
    """Adds created_at and updated_at to any model"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(TimestampMixin, Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    # Automatically has created_at and updated_at!

class Post(TimestampMixin, Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    # Also has timestamps!
```

### Complete Base Model
```python
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.orm import declared_attr
from datetime import datetime

class BaseModel(Base):
    """Abstract base model with common fields"""
    __abstract__ = True  # Won't create table
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)  # Soft delete
    
    @declared_attr
    def __tablename__(cls):
        """Auto-generate table name from class name"""
        # UserProfile -> user_profiles
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower() + 's'
    
    def soft_delete(self):
        self.is_deleted = True
    
    @classmethod
    def active(cls, db: Session):
        return db.query(cls).filter(cls.is_deleted == False)

class User(BaseModel):
    # __tablename__ = "users" (auto-generated)
    name = Column(String(100))
    email = Column(String(100))

class BlogPost(BaseModel):
    # __tablename__ = "blog_posts" (auto-generated)
    title = Column(String(200))
```

### Multiple Mixins
```python
class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

class AuditMixin:
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))

class User(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

class Post(TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
```

---

## Industry Best Practices

### 1. Model Organization
```
app/
├── models/
│   ├── __init__.py       # Import all models
│   ├── base.py           # Base class, mixins
│   ├── user.py
│   ├── post.py
│   └── product.py
```

```python
# models/__init__.py
from .base import Base, BaseModel
from .user import User
from .post import Post
from .product import Product

# Import all models here so Alembic can detect them
__all__ = ["Base", "BaseModel", "User", "Post", "Product"]
```

### 2. Naming Conventions
```python
from sqlalchemy import MetaData

# Define naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)
```

### 3. Soft Deletes
```python
from sqlalchemy import Column, Boolean, DateTime
from sqlalchemy.orm import Query

class SoftDeleteQuery(Query):
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj._with_deleted = kwargs.pop('_with_deleted', False)
        return obj
    
    def __init__(self, *args, **kwargs):
        kwargs.pop('_with_deleted', None)
        super().__init__(*args, **kwargs)
    
    def __iter__(self):
        return super().filter(self._entity.is_deleted == False).__iter__()
    
    def with_deleted(self):
        self._with_deleted = True
        return self

# Usage
active_users = db.query(User).all()  # Only non-deleted
all_users = db.query(User).with_deleted().all()  # Include deleted
```

### 4. Query Optimization Tips
```python
# Use eager loading to avoid N+1 queries
from sqlalchemy.orm import joinedload, selectinload

# Bad - N+1 queries
users = db.query(User).all()
for user in users:
    print(user.posts)  # Query for each user!

# Good - Single query with join
users = db.query(User).options(joinedload(User.posts)).all()

# Better for one-to-many - selectinload
users = db.query(User).options(selectinload(User.posts)).all()
```

---

## Practice Exercises

### Exercise 1: Blog System Models
```python
# Create models for:
# - User (id, username, email, password)
# - Post (id, title, content, author_id)
# - Comment (id, content, post_id, user_id)
# - Tag (id, name) - many-to-many with Post
# Include proper relationships and cascades
```

### Exercise 2: E-commerce Models
```python
# Create models for:
# - Product (id, name, price, category_id)
# - Category (id, name, parent_id) - self-referential
# - Order (id, user_id, total)
# - OrderItem (order_id, product_id, quantity, price)
```

### Exercise 3: Social Media Models
```python
# Create models for:
# - User (with followers - self-referential many-to-many)
# - Post (with likes - many-to-many with User)
# - Message (sender_id, receiver_id, content)
```

---

## Quick Reference

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Parent(Base):
    __tablename__ = "parents"
    id = Column(Integer, primary_key=True)
    children = relationship("Child", back_populates="parent")

class Child(Base):
    __tablename__ = "children"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parents.id"))
    parent = relationship("Parent", back_populates="children")

# Relationship options:
# - back_populates: Link both sides
# - backref: Create reverse relationship automatically
# - uselist: True=list, False=single object
# - cascade: What happens to related objects
# - lazy: How to load (select, joined, subquery, dynamic, selectin)
```

---

## Next Steps

1. **Practice karo** - Models banao
2. **Relationships try karo** - All types
3. **Next doc padho** - `08_sqlalchemy_crud.md`

---

> **Pro Tip**: Good models = Good database = Good application!
