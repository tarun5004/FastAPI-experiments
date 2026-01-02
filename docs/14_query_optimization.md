# 14 — Query Optimization (Complete In-Depth Guide)

> 🎯 **Goal**: Slow queries ko identify karo aur fast banao - Production-ready performance!

---

## 📚 Table of Contents
1. [Query Optimization Kyun?](#query-optimization-kyun)
2. [N+1 Problem](#n1-problem)
3. [Indexes](#indexes)
4. [Query Analysis (EXPLAIN)](#query-analysis-explain)
5. [Eager Loading Strategies](#eager-loading-strategies)
6. [Pagination](#pagination)
7. [Query Optimization Techniques](#query-optimization-techniques)
8. [Monitoring & Profiling](#monitoring--profiling)
9. [Best Practices](#best-practices)
10. [Practice Exercises](#practice-exercises)

---

## Query Optimization Kyun?

### Slow Query Ka Impact

```python
# ❌ Slow Query Reality

# Scenario: E-commerce website
# - 1000 users browsing
# - Each page load = 5 queries
# - Each query = 500ms (slow!)

# Result:
# - Page load time = 2.5 seconds
# - Users frustrated = 40% leave!
# - Database overloaded = crashes!
# - Revenue loss = lakhs per day!

# ✅ Optimized Query Reality
# - Each query = 10ms (fast!)
# - Page load = 50ms
# - Happy users = more sales!
```

### Query Speed Matters!

```
Response Time    User Perception
─────────────────────────────────
< 100ms          Instant ⚡
100-300ms        Smooth 😊
300-1000ms       Noticeable 😐
1-3 seconds      Slow 😤
> 3 seconds      Unacceptable 😡 (users leave)
```

---

## N+1 Problem

### Yeh Kya Hai?

```python
# N+1 = 1 query for parent + N queries for children
# The MOST COMMON performance problem!

# Scenario: Get all users with their posts

# ❌ N+1 Problem Code
async def get_users_with_posts_bad(db: AsyncSession):
    # Query 1: Get all users
    users = await db.execute(select(User))
    users = users.scalars().all()
    
    # Yahan problem hai!
    for user in users:
        # Query 2, 3, 4, ... N+1: Each user ke posts alag query!
        posts = user.posts  # Lazy loading triggers query!
    
    return users

# Agar 100 users hain:
# 1 (users) + 100 (each user's posts) = 101 queries! 😱
```

### Visual Explanation

```
N+1 Problem:
─────────────────────────────────────
Query 1: SELECT * FROM users
         → Returns [User1, User2, ..., User100]

Query 2: SELECT * FROM posts WHERE user_id = 1
Query 3: SELECT * FROM posts WHERE user_id = 2
Query 4: SELECT * FROM posts WHERE user_id = 3
...
Query 101: SELECT * FROM posts WHERE user_id = 100

Total: 101 queries for what should be 1-2 queries!

Each query has overhead:
- Network round-trip: ~1-5ms
- Query parsing: ~0.5ms
- Result processing: ~1ms

101 queries × 5ms = 500ms wasted! 🐌
```

### Solution: Eager Loading

```python
# ✅ Solution: Load everything in 1-2 queries
from sqlalchemy.orm import selectinload

async def get_users_with_posts_good(db: AsyncSession):
    query = (
        select(User)
        .options(selectinload(User.posts))  # ⭐ Load posts together!
    )
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users

# Now:
# Query 1: SELECT * FROM users
# Query 2: SELECT * FROM posts WHERE user_id IN (1, 2, 3, ..., 100)
# Total: 2 queries! 🚀
```

---

## Indexes

### Index Kya Hai?

```
Index = Database ki "Table of Contents"

Book example:
─────────────────────────────────────
Without Index:
"Python" word dhundhna hai → Har page padho (1000 pages) 😓

With Index:
Index mein dekho: "Python → Page 45, 123, 456"
Direct wahan jaao! 🎯

Database mein:
Without Index: Full Table Scan (sab rows check)
With Index: Direct jump to matching rows!
```

### Creating Indexes

```python
# SQLAlchemy mein Index

from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)  # Auto-indexed (PK)
    
    # Single column index
    email = Column(String(100), unique=True, index=True)  # ⭐ Indexed!
    
    # This is NOT indexed by default
    name = Column(String(100))
    status = Column(String(20))
    created_at = Column(DateTime)
    
    # Composite index (multiple columns)
    __table_args__ = (
        Index('ix_user_status_created', 'status', 'created_at'),  # ⭐
    )


# SQL equivalent:
# CREATE INDEX ix_users_email ON users(email);
# CREATE INDEX ix_user_status_created ON users(status, created_at);
```

### Kab Index Banao?

```python
# ✅ Index banao jab:
# 1. WHERE clause mein frequently use ho
# 2. JOIN conditions mein use ho
# 3. ORDER BY mein use ho
# 4. Unique constraint chahiye

# ❌ Index mat banao jab:
# 1. Column rarely searched
# 2. Table bahut choti hai (<1000 rows)
# 3. Column bahut baar update hota hai
# 4. Column mein bahut kam unique values (e.g., boolean)

# Example queries and indexes:

# Query: WHERE email = 'x@y.com'
# Index: Column(email, index=True) ✅

# Query: WHERE status = 'active' ORDER BY created_at
# Index: Index('ix', 'status', 'created_at') ✅

# Query: WHERE created_at > '2024-01-01'
# Index: Column(created_at, index=True) ✅

# Query: WHERE is_active = True (only 2 values: True/False)
# Index: Usually NOT worth it ❌
```

### Index Types

```python
# 1. B-Tree Index (default, most common)
# Good for: =, <, >, <=, >=, BETWEEN, LIKE 'abc%'
Column(email, index=True)

# 2. Hash Index (exact match only)
# Good for: = only (not range queries)
# PostgreSQL: 
Index('ix_hash', 'email', postgresql_using='hash')

# 3. GIN Index (for arrays, full-text search)
# PostgreSQL specific
Index('ix_gin', 'tags', postgresql_using='gin')

# 4. Partial Index (conditional)
# Index only certain rows
Index('ix_active', 'email', postgresql_where=text("status = 'active'"))
```

---

## Query Analysis (EXPLAIN)

### EXPLAIN Kya Dikhata Hai?

```python
# EXPLAIN = Query execution plan
# Database batata hai "Main yeh query kaise run karunga"

# SQLAlchemy mein EXPLAIN
from sqlalchemy import text

async def analyze_query(db: AsyncSession):
    query = select(User).where(User.email == "test@test.com")
    
    # Get execution plan
    result = await db.execute(text(f"EXPLAIN ANALYZE {query}"))
    plan = result.fetchall()
    
    for row in plan:
        print(row)
```

### Reading EXPLAIN Output

```sql
-- PostgreSQL EXPLAIN ANALYZE output

EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@test.com';

-- Output WITHOUT index:
Seq Scan on users  (cost=0.00..25.00 rows=1 width=100)
  Filter: (email = 'test@test.com'::text)
  Rows Removed by Filter: 999
  Actual time: 0.523..5.234 ms

-- Seq Scan = Full table scan (BAD! 🐌)
-- Checked 1000 rows, found 1

-- Output WITH index:
Index Scan using ix_users_email on users  (cost=0.29..8.31 rows=1 width=100)
  Index Cond: (email = 'test@test.com'::text)
  Actual time: 0.023..0.025 ms

-- Index Scan = Using index (GOOD! 🚀)
-- Directly found the row
```

### Key EXPLAIN Terms

```
Term              Meaning                    Good/Bad
─────────────────────────────────────────────────────
Seq Scan          Full table scan           BAD (for large tables)
Index Scan        Using index               GOOD ✅
Index Only Scan   Using only index          BEST ✅✅
Bitmap Scan       Multiple index rows       GOOD for many matches
Nested Loop       Row by row join           OK for small data
Hash Join         Hash table join           GOOD for large joins
Merge Join        Sorted merge join         GOOD if pre-sorted

cost              Estimated work units      Lower = Better
rows              Estimated row count       Accuracy matters
actual time       Real execution time       Lower = Better
```

### Common EXPLAIN Patterns

```sql
-- 1. Missing Index Pattern
Seq Scan on users  (cost=0.00..1000.00 rows=50000)
  Filter: (status = 'active')
-- FIX: CREATE INDEX ix_status ON users(status);

-- 2. Index Not Used Pattern  
Seq Scan on users  (cost=0.00..500.00 rows=100)
  Filter: (LOWER(email) = 'test@test.com')
-- Problem: Function on column prevents index use
-- FIX: CREATE INDEX ix_lower_email ON users(LOWER(email));
--      Or: Store lowercase email

-- 3. Wrong Index Pattern
Index Scan using ix_created_at on users
  Filter: (status = 'active')
-- Using created_at index but filtering on status
-- FIX: CREATE INDEX ix_status_created ON users(status, created_at);
```

---

## Eager Loading Strategies

### Strategy 1: selectinload (Recommended)

```python
from sqlalchemy.orm import selectinload

# selectinload = SELECT ... WHERE id IN (...)
# 2 queries total

query = (
    select(User)
    .options(selectinload(User.posts))
)

# Query 1: SELECT * FROM users
# Query 2: SELECT * FROM posts WHERE user_id IN (1, 2, 3, ...)
```

**When to use:**
- One-to-Many relationships
- Large number of parent objects
- Default choice for most cases

### Strategy 2: joinedload (Single Query)

```python
from sqlalchemy.orm import joinedload

# joinedload = LEFT JOIN
# 1 query with JOIN

query = (
    select(User)
    .options(joinedload(User.posts))
)

# Query: SELECT users.*, posts.* FROM users LEFT JOIN posts ON ...
```

**When to use:**
- One-to-One relationships
- Small one-to-many
- When you need single query

**⚠️ Caution:**
```python
# Problem with joinedload + many children:
# User has 100 posts → 100 duplicate user rows in result!
# Wastes memory and network bandwidth

# Solution: Use unique()
result = await db.execute(query)
users = result.unique().scalars().all()
```

### Strategy 3: subqueryload

```python
from sqlalchemy.orm import subqueryload

# subqueryload = Subquery
# 2 queries with subquery

query = (
    select(User)
    .options(subqueryload(User.posts))
)

# Query 2: SELECT * FROM posts WHERE user_id IN (SELECT id FROM users)
```

**When to use:**
- Complex parent queries
- When IN clause would be too large

### Strategy 4: Nested Loading

```python
# Load multiple levels deep

query = (
    select(User)
    .options(
        selectinload(User.posts)
        .selectinload(Post.comments)  # Nested!
    )
)

# Query 1: SELECT * FROM users
# Query 2: SELECT * FROM posts WHERE user_id IN (...)
# Query 3: SELECT * FROM comments WHERE post_id IN (...)
```

### Comparison Table

```
Strategy      Queries  Best For                    Caution
─────────────────────────────────────────────────────────────
selectinload  2        One-to-Many, default        Large IN clause
joinedload    1        One-to-One, small data      Duplicates
subqueryload  2        Complex queries             Subquery overhead
lazyload      N+1      ❌ Avoid in async!          Performance killer
```

---

## Pagination

### Offset Pagination (Simple but Slow)

```python
# ❌ Offset pagination - gets slower as offset increases

async def get_users_offset(db: AsyncSession, page: int, per_page: int):
    offset = (page - 1) * per_page
    
    query = (
        select(User)
        .order_by(User.id)
        .offset(offset)  # Skip rows
        .limit(per_page)
    )
    
    result = await db.execute(query)
    return result.scalars().all()

# Problem:
# Page 1: offset=0 → Fast ✅
# Page 100: offset=9900 → Database skips 9900 rows 🐌
# Page 1000: offset=99900 → Very slow! 🐢

# SQL:
# SELECT * FROM users ORDER BY id OFFSET 99900 LIMIT 100
# Database has to count through 99900 rows to skip them!
```

### Cursor Pagination (Efficient)

```python
# ✅ Cursor/Keyset pagination - consistent performance

async def get_users_cursor(
    db: AsyncSession, 
    last_id: int | None, 
    per_page: int
):
    query = select(User).order_by(User.id).limit(per_page)
    
    if last_id:
        query = query.where(User.id > last_id)  # Start from last_id
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Return next cursor
    next_cursor = users[-1].id if users else None
    
    return {
        "data": users,
        "next_cursor": next_cursor
    }

# SQL:
# SELECT * FROM users WHERE id > 99900 ORDER BY id LIMIT 100
# Uses index! Always fast regardless of position! 🚀
```

### Cursor Pagination Visual

```
Offset Pagination:
Page 1000: Skip 99900 rows, take 100
[Skip][Skip][Skip]...[Skip][Take 100]
         ↑ Must count all these!

Cursor Pagination:
After ID 99900: Jump directly, take 100
[Jump to ID > 99900][Take 100]
         ↑ Index lookup, instant!
```

### Pagination Best Practices

```python
# 1. Always use ORDER BY
query.order_by(User.created_at.desc(), User.id.desc())

# 2. Include unique column in cursor (handle duplicates)
# If created_at is same for multiple rows, use id as tiebreaker
async def paginate_by_date(db, last_date, last_id, per_page):
    query = (
        select(User)
        .order_by(User.created_at.desc(), User.id.desc())
        .limit(per_page)
    )
    
    if last_date and last_id:
        query = query.where(
            or_(
                User.created_at < last_date,
                and_(
                    User.created_at == last_date,
                    User.id < last_id
                )
            )
        )
    
    return await db.execute(query)

# 3. Return total count separately (cache it!)
@cached(ttl=300)  # Cache for 5 minutes
async def get_total_users(db):
    result = await db.execute(select(func.count(User.id)))
    return result.scalar()
```

---

## Query Optimization Techniques

### 1. Select Only Needed Columns

```python
# ❌ BAD - Select all columns
query = select(User)  # SELECT * FROM users

# ✅ GOOD - Select only needed
query = select(User.id, User.email, User.name)

# Even better for read-only:
from sqlalchemy.orm import load_only

query = select(User).options(load_only(User.id, User.email))
```

### 2. Use exists() for Existence Check

```python
# ❌ BAD - Fetch all data just to check
users = await db.execute(select(User).where(User.status == "active"))
has_active = len(users.scalars().all()) > 0

# ✅ GOOD - Check existence only
from sqlalchemy import exists

query = select(exists(select(User).where(User.status == "active")))
result = await db.execute(query)
has_active = result.scalar()  # True or False
```

### 3. Use func.count() Properly

```python
# ❌ BAD - Fetch all rows to count
users = await db.execute(select(User))
count = len(users.scalars().all())  # Loads all rows into memory!

# ✅ GOOD - Count in database
from sqlalchemy import func

query = select(func.count(User.id))
result = await db.execute(query)
count = result.scalar()  # Single number returned
```

### 4. Batch Operations

```python
# ❌ BAD - One query per insert
for user_data in users_list:
    user = User(**user_data)
    db.add(user)
    await db.commit()  # 100 commits for 100 users!

# ✅ GOOD - Batch insert
for user_data in users_list:
    user = User(**user_data)
    db.add(user)
await db.commit()  # Single commit!

# ✅ BETTER - Bulk insert
from sqlalchemy import insert

await db.execute(
    insert(User),
    [u.dict() for u in users_list]
)
await db.commit()
```

### 5. Avoid Functions on Indexed Columns

```python
# ❌ BAD - Function on column prevents index use
query = select(User).where(func.lower(User.email) == "test@test.com")
# Full table scan because LOWER() applied to each row!

# ✅ GOOD - Store lowercase or use expression index
query = select(User).where(User.email_lower == "test@test.com")
# Or create expression index: INDEX ON users(LOWER(email))

# ✅ ALTERNATIVE - Case-insensitive collation
# PostgreSQL: Column(String, ... , collation='und-x-icu')
```

---

## Monitoring & Profiling

### SQLAlchemy Query Logging

```python
# Enable SQL logging
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Or in engine:
engine = create_async_engine(
    DATABASE_URL,
    echo=True  # Print all SQL queries
)
```

### Query Timing

```python
from sqlalchemy import event
import time

# Track slow queries
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info["query_start_time"] = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info["query_start_time"]
    if total > 0.5:  # Log slow queries (>500ms)
        logger.warning(f"Slow query ({total:.2f}s): {statement}")
```

### FastAPI Query Profiling Middleware

```python
from fastapi import Request
import time

@app.middleware("http")
async def log_slow_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    if process_time > 1.0:  # Log requests taking > 1 second
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"took {process_time:.2f}s"
        )
    
    return response
```

---

## Best Practices

### 1. Profile Before Optimizing

```python
# Don't guess - measure!
# 1. Enable query logging
# 2. Use EXPLAIN ANALYZE
# 3. Find actual slow queries
# 4. Optimize those specific queries
```

### 2. Index Strategy

```python
# Start with:
# - Primary keys (auto)
# - Foreign keys
# - Columns in WHERE clauses
# - Columns in ORDER BY

# Add more based on:
# - EXPLAIN showing Seq Scan
# - Actual slow queries in logs
```

### 3. Connection Pool Tuning

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,           # Connections to keep open
    max_overflow=10,       # Extra connections when busy
    pool_timeout=30,       # Wait time for connection
    pool_recycle=1800,     # Refresh connections every 30 min
    pool_pre_ping=True,    # Check connection before use
)
```

### 4. Caching for Read-Heavy

```python
# Cache frequently read, rarely changed data
from functools import lru_cache
import redis

# Simple in-memory cache
@lru_cache(maxsize=1000)
def get_user_cached(user_id: int):
    return db.query(User).get(user_id)

# Redis cache for distributed
async def get_user_redis(user_id: int):
    cache_key = f"user:{user_id}"
    cached = await redis.get(cache_key)
    if cached:
        return User.parse_raw(cached)
    
    user = await db.execute(select(User).where(User.id == user_id))
    await redis.setex(cache_key, 300, user.json())  # Cache 5 min
    return user
```

---

## Practice Exercises

### Exercise 1: Find N+1 Problem
```python
# Given code has N+1 problem. Fix it:
async def get_orders():
    orders = await db.execute(select(Order))
    for order in orders.scalars().all():
        print(order.customer.name)  # N+1!
        for item in order.items:     # N+1!
            print(item.product.name) # N+1!
```

### Exercise 2: Create Proper Indexes
```python
# Common queries in your app:
# 1. SELECT * FROM products WHERE category_id = ? AND is_active = True
# 2. SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC
# 3. SELECT * FROM users WHERE email = ?
# Create appropriate indexes for these.
```

### Exercise 3: Implement Cursor Pagination
```python
# Implement cursor pagination for products:
# - Order by created_at DESC, id DESC
# - Handle duplicate timestamps
# - Return next_cursor
```

---

## Quick Reference

```python
# Eager Loading
select(X).options(selectinload(X.children))  # 2 queries
select(X).options(joinedload(X.child))       # 1 query with JOIN

# Indexes
Column(name, index=True)
Index('ix_name', 'col1', 'col2')

# Select specific columns
select(User.id, User.email)

# Count
select(func.count(User.id))

# Exists check
select(exists(select(User).where(...)))

# Pagination
.offset(skip).limit(take)  # Offset (slow for large offsets)
.where(id > last_id).limit(take)  # Cursor (fast always)

# EXPLAIN
EXPLAIN ANALYZE SELECT ...
```

---

> **Pro Tip**: "Premature optimization is the root of all evil" - BUT knowing these patterns helps you write efficient code from the start! 🚀
