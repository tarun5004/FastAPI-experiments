# 08 — SQLAlchemy CRUD Operations (Complete In-Depth Guide)

> 🎯 **Goal**: CRUD master ban jao - Create, Read, Update, Delete with all query techniques!

---

## 📚 Table of Contents
1. [CRUD Basics](#crud-basics)
2. [CREATE Operations](#create-operations)
3. [READ Operations](#read-operations)
4. [UPDATE Operations](#update-operations)
5. [DELETE Operations](#delete-operations)
6. [Query Object](#query-object)
7. [Filtering](#filtering)
8. [Ordering](#ordering)
9. [Pagination](#pagination)
10. [Aggregations](#aggregations)
11. [Joins](#joins)
12. [Subqueries](#subqueries)
13. [Raw SQL](#raw-sql)
14. [Bulk Operations](#bulk-operations)
15. [Industry Best Practices](#industry-best-practices)
16. [Practice Exercises](#practice-exercises)

---

## CRUD Basics

### Setup (Reference from previous doc)
```python
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    content = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author = relationship("User", back_populates="posts")

Base.metadata.create_all(bind=engine)

# Get session
db = SessionLocal()
```

---

## CREATE Operations

### Create Single Record
```python
# Method 1: Create and add
user = User(email="tarun@example.com", name="Tarun")
db.add(user)
db.commit()
db.refresh(user)  # Get updated data (like auto-generated id)
print(user.id)  # 1

# Method 2: Create with all fields
user = User(
    email="alice@example.com",
    name="Alice",
    is_active=True,
    created_at=datetime.utcnow()
)
db.add(user)
db.commit()
```

### Create Multiple Records
```python
# Method 1: add_all()
users = [
    User(email="user1@test.com", name="User 1"),
    User(email="user2@test.com", name="User 2"),
    User(email="user3@test.com", name="User 3"),
]
db.add_all(users)
db.commit()

# Method 2: Bulk insert (faster for large data)
from sqlalchemy import insert

db.execute(
    insert(User),
    [
        {"email": "bulk1@test.com", "name": "Bulk 1"},
        {"email": "bulk2@test.com", "name": "Bulk 2"},
        {"email": "bulk3@test.com", "name": "Bulk 3"},
    ]
)
db.commit()
```

### Create with Relationships
```python
# Method 1: Create separately
user = User(email="author@test.com", name="Author")
db.add(user)
db.commit()

post = Post(title="My Post", content="Hello!", user_id=user.id)
db.add(post)
db.commit()

# Method 2: Create together
user = User(email="author2@test.com", name="Author 2")
post = Post(title="My Post", content="Hello!", author=user)
db.add(post)  # User is added automatically!
db.commit()

# Method 3: Using relationship
user = User(email="author3@test.com", name="Author 3")
user.posts.append(Post(title="Post 1", content="Content 1"))
user.posts.append(Post(title="Post 2", content="Content 2"))
db.add(user)
db.commit()
```

### Get ID Before Commit (Using Flush)
```python
user = User(email="new@test.com", name="New User")
db.add(user)
db.flush()  # Send to database, don't commit yet
print(user.id)  # ID is now available!

post = Post(title="Post", content="Content", user_id=user.id)
db.add(post)
db.commit()  # Now commit both
```

---

## READ Operations

### Get Single Record
```python
# By primary key (recommended)
user = db.query(User).get(1)  # Returns None if not found
# SQLAlchemy 2.0 style:
user = db.get(User, 1)

# First matching record
user = db.query(User).filter(User.email == "tarun@example.com").first()

# Exactly one record (raises if 0 or >1)
try:
    user = db.query(User).filter(User.id == 1).one()
except NoResultFound:
    print("User not found")
except MultipleResultsFound:
    print("Multiple users found")

# One or None (raises if >1)
user = db.query(User).filter(User.id == 1).one_or_none()
```

### Get Multiple Records
```python
# All records
users = db.query(User).all()

# With filter
active_users = db.query(User).filter(User.is_active == True).all()

# Limited records
first_10 = db.query(User).limit(10).all()

# Offset and limit (pagination)
page_2 = db.query(User).offset(10).limit(10).all()

# Count
count = db.query(User).count()

# Exists
exists = db.query(User).filter(User.email == "tarun@example.com").first() is not None
# Or using exists()
from sqlalchemy import exists
exists_query = db.query(exists().where(User.email == "tarun@example.com")).scalar()
```

### Select Specific Columns
```python
# Select specific columns (returns tuples)
results = db.query(User.id, User.email).all()
for id, email in results:
    print(f"{id}: {email}")

# With labels
from sqlalchemy import func
results = db.query(
    User.id,
    User.name,
    func.count(Post.id).label("post_count")
).join(Post).group_by(User.id).all()

for row in results:
    print(f"{row.name}: {row.post_count} posts")
```

---

## UPDATE Operations

### Update Single Record
```python
# Method 1: Get and modify (ORM way)
user = db.query(User).filter(User.id == 1).first()
if user:
    user.name = "Updated Name"
    user.is_active = False
    db.commit()

# Method 2: Update query (efficient, no fetch)
db.query(User).filter(User.id == 1).update({"name": "Updated Name"})
db.commit()

# Method 3: Using update() with synchronize_session
db.query(User).filter(User.id == 1).update(
    {"name": "Updated Name"},
    synchronize_session="fetch"  # or "evaluate" or False
)
db.commit()
```

### Update Multiple Records
```python
# Update all matching records
db.query(User).filter(User.is_active == False).update({"is_active": True})
db.commit()

# Update with expression
from sqlalchemy import func
db.query(User).update({"name": func.upper(User.name)})
db.commit()
```

### Conditional Update
```python
from sqlalchemy import case

# Update based on condition
db.query(User).update({
    "role": case(
        (User.is_superuser == True, "admin"),
        else_="user"
    )
}, synchronize_session=False)
db.commit()
```

### Update or Create (Upsert)
```python
def get_or_create(db, model, defaults=None, **kwargs):
    """Get existing record or create new one"""
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = {**kwargs, **(defaults or {})}
        instance = model(**params)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance, True

# Usage
user, created = get_or_create(
    db, User,
    email="tarun@example.com",
    defaults={"name": "Tarun"}
)
print(f"Created: {created}")
```

---

## DELETE Operations

### Delete Single Record
```python
# Method 1: Get and delete
user = db.query(User).filter(User.id == 1).first()
if user:
    db.delete(user)
    db.commit()

# Method 2: Delete query (no fetch)
deleted_count = db.query(User).filter(User.id == 1).delete()
db.commit()
print(f"Deleted {deleted_count} records")
```

### Delete Multiple Records
```python
# Delete all matching
deleted_count = db.query(User).filter(User.is_active == False).delete()
db.commit()

# Delete all (be careful!)
db.query(User).delete()
db.commit()
```

### Soft Delete (Recommended)
```python
# Instead of deleting, mark as deleted
user = db.query(User).filter(User.id == 1).first()
if user:
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    db.commit()

# Query only active records
active_users = db.query(User).filter(User.is_deleted == False).all()
```

### Cascade Delete
```python
# If relationship has cascade="all, delete-orphan"
user = db.query(User).filter(User.id == 1).first()
db.delete(user)  # All related posts are also deleted!
db.commit()
```

---

## Query Object

### Query Methods Chain
```python
# Queries are chainable
query = db.query(User)
query = query.filter(User.is_active == True)
query = query.order_by(User.created_at.desc())
query = query.limit(10)
users = query.all()

# Or in one line
users = (
    db.query(User)
    .filter(User.is_active == True)
    .order_by(User.created_at.desc())
    .limit(10)
    .all()
)
```

### Query Execution Methods
```python
query = db.query(User)

# Get all records
users = query.all()  # Returns list

# Get first record
user = query.first()  # Returns one or None

# Get exactly one
user = query.one()  # Raises if 0 or >1
user = query.one_or_none()  # Returns one or None, raises if >1

# Get scalar value
count = db.query(func.count(User.id)).scalar()

# Get count
count = query.count()

# Check if exists
has_users = query.first() is not None

# Iterate (memory efficient for large datasets)
for user in query.yield_per(100):
    process(user)
```

---

## Filtering

### Basic Filters
```python
from sqlalchemy import and_, or_, not_

# Equals
users = db.query(User).filter(User.name == "Tarun").all()

# Not equals
users = db.query(User).filter(User.name != "Tarun").all()

# Greater than
users = db.query(User).filter(User.age > 18).all()

# Less than or equal
users = db.query(User).filter(User.age <= 65).all()

# Between
users = db.query(User).filter(User.age.between(18, 65)).all()

# IS NULL
users = db.query(User).filter(User.deleted_at == None).all()
users = db.query(User).filter(User.deleted_at.is_(None)).all()

# IS NOT NULL
users = db.query(User).filter(User.deleted_at != None).all()
users = db.query(User).filter(User.deleted_at.isnot(None)).all()
```

### String Filters
```python
# LIKE (case-sensitive)
users = db.query(User).filter(User.name.like("%arun%")).all()

# ILIKE (case-insensitive, PostgreSQL)
users = db.query(User).filter(User.name.ilike("%tarun%")).all()

# Starts with
users = db.query(User).filter(User.name.startswith("T")).all()

# Ends with
users = db.query(User).filter(User.email.endswith("@gmail.com")).all()

# Contains
users = db.query(User).filter(User.name.contains("aru")).all()

# Regex (database dependent)
users = db.query(User).filter(User.name.regexp_match("^T.*n$")).all()
```

### IN Clause
```python
# IN
ids = [1, 2, 3, 4, 5]
users = db.query(User).filter(User.id.in_(ids)).all()

# NOT IN
users = db.query(User).filter(User.id.notin_(ids)).all()

# IN with subquery
admin_ids = db.query(Admin.user_id).subquery()
admins = db.query(User).filter(User.id.in_(admin_ids)).all()
```

### Compound Filters
```python
from sqlalchemy import and_, or_, not_

# AND (multiple filter calls)
users = db.query(User).filter(User.is_active == True).filter(User.age > 18).all()

# AND (explicit)
users = db.query(User).filter(
    and_(
        User.is_active == True,
        User.age > 18
    )
).all()

# OR
users = db.query(User).filter(
    or_(
        User.role == "admin",
        User.role == "moderator"
    )
).all()

# NOT
users = db.query(User).filter(not_(User.is_active == True)).all()

# Complex combination
users = db.query(User).filter(
    and_(
        User.is_active == True,
        or_(
            User.role == "admin",
            and_(
                User.age >= 18,
                User.verified == True
            )
        )
    )
).all()
```

### Dynamic Filters
```python
def search_users(
    db,
    name: str = None,
    email: str = None,
    is_active: bool = None,
    role: str = None
):
    query = db.query(User)
    
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))
    
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if role:
        query = query.filter(User.role == role)
    
    return query.all()

# Usage
users = search_users(db, name="tarun", is_active=True)
```

---

## Ordering

### Basic Ordering
```python
# Ascending (default)
users = db.query(User).order_by(User.name).all()
users = db.query(User).order_by(User.name.asc()).all()

# Descending
users = db.query(User).order_by(User.name.desc()).all()

# Multiple columns
users = db.query(User).order_by(User.role, User.name.desc()).all()

# NULLS first/last
users = db.query(User).order_by(User.deleted_at.asc().nullsfirst()).all()
users = db.query(User).order_by(User.deleted_at.desc().nullslast()).all()
```

### Order by Expression
```python
from sqlalchemy import func, case

# Order by function result
users = db.query(User).order_by(func.length(User.name)).all()

# Order by case
users = db.query(User).order_by(
    case(
        (User.role == "admin", 1),
        (User.role == "moderator", 2),
        else_=3
    )
).all()

# Random order
users = db.query(User).order_by(func.random()).all()
```

---

## Pagination

### Offset-Limit Pagination
```python
def get_users_paginated(db, page: int = 1, per_page: int = 10):
    """Simple offset-limit pagination"""
    offset = (page - 1) * per_page
    
    total = db.query(User).count()
    users = db.query(User).offset(offset).limit(per_page).all()
    
    return {
        "items": users,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

# Usage
result = get_users_paginated(db, page=2, per_page=10)
```

### Cursor-based Pagination (Better for Large Data)
```python
def get_users_cursor(db, cursor: int = None, limit: int = 10):
    """Cursor-based pagination (more efficient)"""
    query = db.query(User).order_by(User.id)
    
    if cursor:
        query = query.filter(User.id > cursor)
    
    users = query.limit(limit + 1).all()  # Get one extra to check if more
    
    has_next = len(users) > limit
    if has_next:
        users = users[:-1]  # Remove extra
    
    next_cursor = users[-1].id if users and has_next else None
    
    return {
        "items": users,
        "next_cursor": next_cursor,
        "has_next": has_next
    }

# Usage
page1 = get_users_cursor(db, limit=10)
page2 = get_users_cursor(db, cursor=page1["next_cursor"], limit=10)
```

### Keyset Pagination (Most Efficient)
```python
def get_users_keyset(db, last_created_at=None, last_id=None, limit=10):
    """Keyset pagination with composite key"""
    query = db.query(User).order_by(User.created_at.desc(), User.id.desc())
    
    if last_created_at and last_id:
        query = query.filter(
            or_(
                User.created_at < last_created_at,
                and_(
                    User.created_at == last_created_at,
                    User.id < last_id
                )
            )
        )
    
    return query.limit(limit).all()
```

---

## Aggregations

### Count, Sum, Avg, Min, Max
```python
from sqlalchemy import func

# Count all
total = db.query(func.count(User.id)).scalar()

# Count with filter
active_count = db.query(func.count(User.id)).filter(User.is_active == True).scalar()

# Sum
total_price = db.query(func.sum(Order.total)).scalar()

# Average
avg_age = db.query(func.avg(User.age)).scalar()

# Min/Max
oldest = db.query(func.min(User.created_at)).scalar()
newest = db.query(func.max(User.created_at)).scalar()
```

### Group By
```python
# Count users per role
results = db.query(
    User.role,
    func.count(User.id).label("count")
).group_by(User.role).all()

for role, count in results:
    print(f"{role}: {count}")

# Sum orders per user
results = db.query(
    User.name,
    func.count(Order.id).label("order_count"),
    func.sum(Order.total).label("total_spent")
).join(Order).group_by(User.id).all()

# Having clause
results = db.query(
    User.role,
    func.count(User.id).label("count")
).group_by(User.role).having(func.count(User.id) > 10).all()
```

### Distinct
```python
# Distinct values
roles = db.query(User.role).distinct().all()

# Distinct count
unique_roles = db.query(func.count(func.distinct(User.role))).scalar()
```

---

## Joins

### Inner Join
```python
# Implicit join (using relationship)
results = db.query(User, Post).join(User.posts).all()

# Explicit join
results = db.query(User, Post).join(Post, User.id == Post.user_id).all()

# Join with filter
results = db.query(User).join(Post).filter(Post.title.like("%Python%")).all()

# Join and select specific columns
results = db.query(
    User.name,
    Post.title
).join(Post).all()
```

### Left Outer Join
```python
# Left join - include users without posts
results = db.query(User, Post).outerjoin(Post, User.id == Post.user_id).all()

# Or using relationship
results = db.query(User).outerjoin(User.posts).all()

# Users with post count (including 0)
results = db.query(
    User.name,
    func.count(Post.id).label("post_count")
).outerjoin(Post).group_by(User.id).all()
```

### Multiple Joins
```python
# Chain joins
results = db.query(User).join(Post).join(Comment).all()

# With conditions
results = db.query(
    User.name,
    Post.title,
    Comment.content
).join(Post, User.id == Post.user_id)\
 .join(Comment, Post.id == Comment.post_id)\
 .filter(Comment.is_approved == True).all()
```

### Self Join
```python
from sqlalchemy.orm import aliased

# Employee with manager
manager = aliased(Employee)
results = db.query(
    Employee.name,
    manager.name.label("manager_name")
).join(manager, Employee.manager_id == manager.id).all()
```

---

## Subqueries

### Subquery in Filter
```python
from sqlalchemy import select

# Users who have posts
subq = db.query(Post.user_id).distinct().subquery()
users_with_posts = db.query(User).filter(User.id.in_(select(subq))).all()

# Or simpler
users_with_posts = db.query(User).filter(
    User.id.in_(db.query(Post.user_id).distinct())
).all()
```

### Subquery in Select
```python
# User with post count as subquery
post_count_subq = (
    db.query(func.count(Post.id))
    .filter(Post.user_id == User.id)
    .correlate(User)
    .scalar_subquery()
)

results = db.query(
    User.name,
    post_count_subq.label("post_count")
).all()
```

### Correlated Subquery
```python
# Users with their latest post title
latest_post = (
    db.query(Post.title)
    .filter(Post.user_id == User.id)
    .order_by(Post.created_at.desc())
    .limit(1)
    .correlate(User)
    .scalar_subquery()
)

results = db.query(
    User.name,
    latest_post.label("latest_post")
).all()
```

### EXISTS
```python
from sqlalchemy import exists

# Users who have at least one post
has_posts = exists().where(Post.user_id == User.id)
users_with_posts = db.query(User).filter(has_posts).all()

# Users who don't have posts
users_without_posts = db.query(User).filter(~has_posts).all()
```

---

## Raw SQL

### Execute Raw SQL
```python
from sqlalchemy import text

# Simple query
result = db.execute(text("SELECT * FROM users WHERE is_active = :active"), {"active": True})
users = result.fetchall()

# With ORM mapping
users = db.query(User).from_statement(
    text("SELECT * FROM users WHERE is_active = :active")
).params(active=True).all()

# Raw SQL insert
db.execute(
    text("INSERT INTO users (email, name) VALUES (:email, :name)"),
    {"email": "raw@test.com", "name": "Raw User"}
)
db.commit()
```

### Text in Filters
```python
from sqlalchemy import text

# Raw SQL in filter
users = db.query(User).filter(
    text("is_active = true AND created_at > '2024-01-01'")
).all()

# With parameters (safe from SQL injection)
users = db.query(User).filter(
    text("name LIKE :pattern")
).params(pattern="%tarun%").all()
```

### Hybrid Raw and ORM
```python
# Mix raw SQL with ORM
from sqlalchemy import literal_column

users = db.query(
    User,
    literal_column("(SELECT COUNT(*) FROM posts WHERE posts.user_id = users.id)").label("post_count")
).all()
```

---

## Bulk Operations

### Bulk Insert
```python
# Method 1: add_all (ORM events fire)
users = [User(email=f"user{i}@test.com", name=f"User {i}") for i in range(1000)]
db.add_all(users)
db.commit()

# Method 2: bulk_save_objects (faster, some ORM features skipped)
users = [User(email=f"user{i}@test.com", name=f"User {i}") for i in range(1000)]
db.bulk_save_objects(users)
db.commit()

# Method 3: bulk_insert_mappings (fastest, no ORM)
user_dicts = [{"email": f"user{i}@test.com", "name": f"User {i}"} for i in range(1000)]
db.bulk_insert_mappings(User, user_dicts)
db.commit()

# Method 4: Core insert (raw speed)
from sqlalchemy import insert
db.execute(insert(User), user_dicts)
db.commit()
```

### Bulk Update
```python
# Method 1: Query update (single SQL statement)
db.query(User).filter(User.is_active == False).update({"is_active": True})
db.commit()

# Method 2: bulk_update_mappings
updates = [
    {"id": 1, "name": "Updated 1"},
    {"id": 2, "name": "Updated 2"},
    {"id": 3, "name": "Updated 3"},
]
db.bulk_update_mappings(User, updates)
db.commit()
```

### Bulk Delete
```python
# Single statement delete
deleted_count = db.query(User).filter(User.is_active == False).delete()
db.commit()

# Delete all
db.query(User).delete()
db.commit()
```

### Performance Comparison
```python
import time

# Slowest: Individual adds (1000 inserts)
start = time.time()
for i in range(1000):
    user = User(email=f"slow{i}@test.com", name=f"Slow {i}")
    db.add(user)
    db.commit()
print(f"Individual: {time.time() - start:.2f}s")

# Faster: add_all (1 commit)
start = time.time()
users = [User(email=f"batch{i}@test.com", name=f"Batch {i}") for i in range(1000)]
db.add_all(users)
db.commit()
print(f"add_all: {time.time() - start:.2f}s")

# Fastest: bulk_insert_mappings
start = time.time()
user_dicts = [{"email": f"bulk{i}@test.com", "name": f"Bulk {i}"} for i in range(1000)]
db.bulk_insert_mappings(User, user_dicts)
db.commit()
print(f"bulk_insert: {time.time() - start:.2f}s")
```

---

## Industry Best Practices

### 1. Repository Pattern
```python
# repositories/user_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def get_active(self) -> List[User]:
        return self.db.query(User).filter(User.is_active == True).all()
    
    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user: User, data: dict) -> User:
        for key, value in data.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
    
    def count(self) -> int:
        return self.db.query(User).count()
    
    def exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

# Usage
repo = UserRepository(db)
user = repo.get_by_id(1)
users = repo.get_active()
```

### 2. Generic Repository
```python
from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy.orm import Session

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj: T) -> T:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def update(self, obj: T, data: dict) -> T:
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, obj: T) -> None:
        self.db.delete(obj)
        self.db.commit()
    
    def count(self) -> int:
        return self.db.query(self.model).count()

# Usage
user_repo = BaseRepository(User, db)
post_repo = BaseRepository(Post, db)
```

### 3. Query Builder Pattern
```python
class UserQueryBuilder:
    def __init__(self, db: Session):
        self.query = db.query(User)
    
    def active_only(self):
        self.query = self.query.filter(User.is_active == True)
        return self
    
    def role(self, role: str):
        self.query = self.query.filter(User.role == role)
        return self
    
    def search(self, term: str):
        self.query = self.query.filter(
            or_(
                User.name.ilike(f"%{term}%"),
                User.email.ilike(f"%{term}%")
            )
        )
        return self
    
    def order_by_newest(self):
        self.query = self.query.order_by(User.created_at.desc())
        return self
    
    def paginate(self, page: int, per_page: int):
        self.query = self.query.offset((page - 1) * per_page).limit(per_page)
        return self
    
    def get_all(self):
        return self.query.all()
    
    def first(self):
        return self.query.first()
    
    def count(self):
        return self.query.count()

# Usage (chainable)
users = (
    UserQueryBuilder(db)
    .active_only()
    .role("admin")
    .search("tarun")
    .order_by_newest()
    .paginate(page=1, per_page=10)
    .get_all()
)
```

---

## Practice Exercises

### Exercise 1: Complete CRUD Service
```python
# Create a complete CRUD service for a Product model:
# - get_products(filters, pagination, sorting)
# - get_product(id)
# - create_product(data)
# - update_product(id, data)
# - delete_product(id)
# - search_products(query)
# - get_products_by_category(category_id)
```

### Exercise 2: Advanced Queries
```python
# Write queries for:
# 1. Top 10 users by post count
# 2. Posts with more than 100 comments
# 3. Users who haven't posted in 30 days
# 4. Average order value per user
# 5. Products that are low in stock
```

### Exercise 3: Pagination System
```python
# Implement a pagination system with:
# - Offset pagination
# - Cursor pagination
# - Sorting options
# - Filter options
# - Total count
```

---

## Quick Reference

```python
from sqlalchemy.orm import Session

# CREATE
db.add(obj)
db.add_all([obj1, obj2])
db.commit()

# READ
db.query(Model).all()
db.query(Model).filter(condition).first()
db.query(Model).get(id)

# UPDATE
obj.field = value
db.commit()
# OR
db.query(Model).filter(condition).update({"field": value})

# DELETE
db.delete(obj)
db.commit()
# OR
db.query(Model).filter(condition).delete()

# FILTER
.filter(Model.field == value)
.filter(Model.field.like("%pattern%"))
.filter(Model.field.in_([1, 2, 3]))
.filter(and_(cond1, cond2))
.filter(or_(cond1, cond2))

# ORDER
.order_by(Model.field.asc())
.order_by(Model.field.desc())

# PAGINATION
.offset(skip).limit(limit)

# JOIN
.join(Related).filter(...)
.outerjoin(Related)

# AGGREGATE
func.count(), func.sum(), func.avg()
.group_by().having()
```

---

## Next Steps

1. **Practice karo** - All query types try karo
2. **Repository pattern use karo** 
3. **Next doc padho** - `09_fastapi_db_integration.md`

---

> **Pro Tip**: SQLAlchemy bahut powerful hai - isko achhe se samjho!
