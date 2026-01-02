# 25 — Performance Optimization & Scaling (Complete In-Depth Guide)

> 🎯 **Goal**: App ko fast aur scalable banao - millions of users handle karo!

---

## 📚 Table of Contents
1. [Performance Kyun Important?](#performance-kyun-important)
2. [Profiling & Bottleneck Finding](#profiling--bottleneck-finding)
3. [Database Optimization](#database-optimization)
4. [Caching Strategies](#caching-strategies)
5. [Async & Concurrency](#async--concurrency)
6. [API Optimization](#api-optimization)
7. [Horizontal Scaling](#horizontal-scaling)
8. [Load Testing](#load-testing)
9. [Best Practices Checklist](#best-practices-checklist)

---

## Performance Kyun Important?

### Business Impact

```
Page Load Time vs Conversion:
─────────────────────────────────────────────────────────
1 second delay → 7% less conversions
Amazon: 100ms delay → 1% revenue loss
Google: 500ms delay → 20% less traffic

User Expectations:
─────────────────────────────────────────────────────────
< 100ms  → Feels instant
100-300ms → Slight delay noticeable
> 1 second → User thinks something's wrong
> 3 seconds → User leaves
```

### Where Time Goes

```
Typical API Request Breakdown:
─────────────────────────────────────────────────────────
Total: 500ms

Network latency:     50ms  (10%)
App processing:      50ms  (10%)
Database queries:   300ms  (60%)  ← Main bottleneck!
External API calls: 100ms  (20%)

Focus on the 60% first!
```

---

## Profiling & Bottleneck Finding

### Python Profiling

```python
# Built-in profiler
import cProfile
import pstats

def slow_function():
    # Your code here
    pass

# Profile it
profiler = cProfile.Profile()
profiler.enable()
slow_function()
profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 slow functions


# Line-by-line profiling (pip install line_profiler)
from line_profiler import profile

@profile
def process_data(items):
    result = []
    for item in items:          # Line 1: 10ms
        processed = heavy_op(item)  # Line 2: 500ms ← Problem!
        result.append(processed)    # Line 3: 1ms
    return result
```

### FastAPI Request Timing Middleware

```python
import time
import logging
from fastapi import FastAPI, Request

app = FastAPI()
logger = logging.getLogger(__name__)

@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start
    
    # Log slow requests
    if duration > 1.0:  # More than 1 second
        logger.warning(
            f"SLOW REQUEST: {request.method} {request.url.path} "
            f"took {duration:.2f}s"
        )
    
    # Add timing header
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    
    return response
```

### Database Query Logging

```python
# SQLAlchemy query logging
import logging

# Enable SQL logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


# Or detailed timing
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop()
    if total > 0.1:  # Log queries taking > 100ms
        logger.warning(f"SLOW QUERY ({total:.2f}s): {statement[:100]}")
```

---

## Database Optimization

### 1. Proper Indexing

```python
# models.py
from sqlalchemy import Column, Integer, String, Index

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)  # Single index
    status = Column(String, index=True)
    created_at = Column(DateTime)
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_status_created', 'status', 'created_at'),
    )


# When to add index:
# ✅ Columns used in WHERE clauses
# ✅ Columns used in JOIN conditions
# ✅ Columns used in ORDER BY
# ❌ Columns with low cardinality (like boolean)
# ❌ Small tables (< 1000 rows)
# ❌ Write-heavy tables (indexes slow down writes)
```

### 2. Query Optimization

```python
# ❌ BAD: N+1 Query Problem
users = db.query(User).all()
for user in users:
    print(user.orders)  # Each loop = 1 query!
# 1 query for users + N queries for orders = N+1 queries


# ✅ GOOD: Eager Loading
from sqlalchemy.orm import joinedload

users = db.query(User).options(joinedload(User.orders)).all()
for user in users:
    print(user.orders)  # Already loaded!
# Only 1 query total!


# ✅ GOOD: Select only needed columns
# Instead of SELECT *
users = db.query(User.id, User.email).all()


# ✅ GOOD: Use LIMIT for pagination
users = db.query(User).offset(0).limit(20).all()
```

### 3. Connection Pooling

```python
from sqlalchemy import create_engine

# Connection pool settings
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # Max connections to keep
    max_overflow=10,     # Extra connections when pool full
    pool_timeout=30,     # Wait time for connection
    pool_recycle=1800,   # Recycle connections every 30 min
)

# Explanation:
# Without pooling: Open connection → Query → Close connection
# With pooling: Reuse existing connections
# Creating connection = 100-500ms, reusing = 0ms
```

### 4. Read Replicas

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random

# Primary for writes
primary_engine = create_engine(PRIMARY_DB_URL)
PrimarySession = sessionmaker(bind=primary_engine)

# Replicas for reads
replica_engines = [
    create_engine(REPLICA_1_URL),
    create_engine(REPLICA_2_URL),
]

def get_read_session():
    engine = random.choice(replica_engines)
    return sessionmaker(bind=engine)()

def get_write_session():
    return PrimarySession()


# Usage
# Read operations
with get_read_session() as db:
    users = db.query(User).all()

# Write operations
with get_write_session() as db:
    db.add(User(name="John"))
    db.commit()
```

---

## Caching Strategies

### Multi-Level Caching

```
Level 1: In-Memory (Python dict, lru_cache)
─────────────────────────────────────────────────────────
Speed: < 1ms
Size: Limited (100MB-1GB)
Scope: Single process only
Use for: Frequently accessed, rarely changing data


Level 2: Redis/Memcached
─────────────────────────────────────────────────────────
Speed: 1-5ms
Size: Large (GB-TB)
Scope: Shared across servers
Use for: Session data, API responses, computed results


Level 3: CDN (CloudFlare, CloudFront)
─────────────────────────────────────────────────────────
Speed: 10-50ms (from edge)
Size: Very large
Scope: Global
Use for: Static files, API responses (with cache headers)
```

### Python In-Memory Cache

```python
from functools import lru_cache
import time

# Simple LRU cache
@lru_cache(maxsize=1000)
def get_user_permissions(user_id: int):
    # Expensive database query
    return db.query(Permission).filter_by(user_id=user_id).all()


# Cache with TTL
from cachetools import TTLCache

cache = TTLCache(maxsize=1000, ttl=300)  # 5 min TTL

def get_user_cached(user_id: int):
    if user_id in cache:
        return cache[user_id]
    
    user = db.query(User).get(user_id)
    cache[user_id] = user
    return user
```

### Redis Caching Patterns

```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(ttl_seconds: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and args
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator


# Usage
@cache_response(ttl_seconds=60)
async def get_popular_products():
    # Expensive query
    return await db.query(Product).order_by(Product.views.desc()).limit(10).all()
```

### Cache Invalidation

```python
# Pattern 1: TTL-based (automatic expiry)
redis_client.setex("user:123", 3600, user_json)  # Expires in 1 hour


# Pattern 2: Event-based invalidation
async def update_user(user_id: int, data: dict):
    user = await db.update_user(user_id, data)
    
    # Invalidate all related caches
    redis_client.delete(f"user:{user_id}")
    redis_client.delete(f"user:{user_id}:permissions")
    redis_client.delete(f"user:{user_id}:orders")
    
    return user


# Pattern 3: Cache tags (invalidate by category)
def set_with_tags(key: str, value: str, tags: list, ttl: int):
    redis_client.setex(key, ttl, value)
    for tag in tags:
        redis_client.sadd(f"tag:{tag}", key)

def invalidate_tag(tag: str):
    keys = redis_client.smembers(f"tag:{tag}")
    if keys:
        redis_client.delete(*keys)
    redis_client.delete(f"tag:{tag}")


# Usage
set_with_tags("product:123", product_json, ["products", "category:electronics"], 3600)
invalidate_tag("products")  # Invalidates all product caches
```

---

## Async & Concurrency

### Async Database Queries

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Async engine
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# Async CRUD
async def get_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        return result.scalars().all()


# Parallel queries with asyncio.gather
async def get_dashboard_data(user_id: int):
    async with AsyncSessionLocal() as session:
        # Run all queries in parallel
        user_task = session.execute(select(User).where(User.id == user_id))
        orders_task = session.execute(
            select(Order).where(Order.user_id == user_id).limit(10)
        )
        notifications_task = session.execute(
            select(Notification).where(Notification.user_id == user_id).limit(5)
        )
        
        user_result, orders_result, notif_result = await asyncio.gather(
            user_task, orders_task, notifications_task
        )
        
        return {
            "user": user_result.scalar_one(),
            "orders": orders_result.scalars().all(),
            "notifications": notif_result.scalars().all()
        }
```

### Background Tasks

```python
from fastapi import BackgroundTasks

@app.post("/orders")
async def create_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks
):
    # Create order (fast)
    new_order = await db.create_order(order)
    
    # Send email in background (slow, don't wait)
    background_tasks.add_task(send_order_email, new_order)
    
    # Update inventory in background
    background_tasks.add_task(update_inventory, order.items)
    
    # Return immediately
    return new_order


# For heavy background work, use Celery
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task
def process_video(video_id: int):
    # Heavy processing
    pass

# Trigger from API
@app.post("/videos/upload")
async def upload_video(file: UploadFile):
    video = await save_video(file)
    process_video.delay(video.id)  # Async task
    return {"status": "processing"}
```

---

## API Optimization

### Response Compression

```python
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# Compress responses > 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)

# Compression ratios:
# JSON: 70-90% reduction
# HTML: 60-80% reduction
# Images: Already compressed, skip
```

### Pagination

```python
from fastapi import Query
from typing import List, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int


@app.get("/users", response_model=PaginatedResponse[UserResponse])
async def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    offset = (page - 1) * per_page
    
    # Count total (can cache this)
    total = await db.query(func.count(User.id)).scalar()
    
    # Get page
    users = await db.query(User).offset(offset).limit(per_page).all()
    
    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page
    )
```

### Cursor-Based Pagination (Better for Large Data)

```python
@app.get("/users")
async def get_users(
    cursor: str = None,  # Last seen ID, encoded
    limit: int = Query(20, le=100)
):
    query = select(User).order_by(User.id)
    
    if cursor:
        last_id = decode_cursor(cursor)
        query = query.where(User.id > last_id)
    
    users = await db.execute(query.limit(limit + 1))
    users = users.scalars().all()
    
    has_more = len(users) > limit
    if has_more:
        users = users[:-1]
    
    return {
        "items": users,
        "next_cursor": encode_cursor(users[-1].id) if has_more else None
    }
```

### Selective Field Loading

```python
from pydantic import BaseModel
from typing import Optional, List

class UserBasic(BaseModel):
    id: int
    name: str

class UserFull(UserBasic):
    email: str
    created_at: datetime
    orders: List[OrderResponse]


@app.get("/users")
async def get_users(
    fields: str = Query(None, description="Comma-separated fields")
):
    if fields:
        requested = fields.split(",")
        columns = [getattr(User, f) for f in requested if hasattr(User, f)]
        query = select(*columns)
    else:
        query = select(User)
    
    return await db.execute(query).all()


# Or use GraphQL for complex field selection
```

---

## Horizontal Scaling

### Stateless Application Design

```python
# ❌ BAD: Storing state in memory
user_sessions = {}  # Lost when server restarts or scales

@app.post("/login")
def login(credentials):
    session_id = create_session()
    user_sessions[session_id] = user_data
    return {"session_id": session_id}


# ✅ GOOD: Store state in Redis
@app.post("/login")
async def login(credentials):
    session_id = create_session()
    await redis.setex(
        f"session:{session_id}",
        3600,
        json.dumps(user_data)
    )
    return {"session_id": session_id}
```

### Docker Compose Scaling

```yaml
# docker-compose.yml
version: "3.8"

services:
  app:
    build: .
    deploy:
      replicas: 3  # 3 instances
    environment:
      - REDIS_URL=redis://redis:6379
  
  nginx:
    image: nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
  
  redis:
    image: redis:alpine
```

```nginx
# nginx.conf - Load balancing
upstream backend {
    server app:8000;
    # Docker Compose will load balance across replicas
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }
}
```

### Kubernetes Auto-Scaling

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: myapp:latest
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
---
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Load Testing

### Locust (Python Load Testing)

```python
# locustfile.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 sec between tasks
    
    def on_start(self):
        # Login before tests
        response = self.client.post("/token", data={
            "username": "test@example.com",
            "password": "password"
        })
        self.token = response.json()["access_token"]
    
    @task(3)  # Weight 3 - more frequent
    def get_products(self):
        self.client.get("/products", headers={
            "Authorization": f"Bearer {self.token}"
        })
    
    @task(1)  # Weight 1 - less frequent
    def create_order(self):
        self.client.post("/orders", json={
            "product_id": 1,
            "quantity": 1
        }, headers={
            "Authorization": f"Bearer {self.token}"
        })


# Run: locust -f locustfile.py --host=http://localhost:8000
# Open: http://localhost:8089
```

### Performance Targets

```
API Response Times:
─────────────────────────────────────────────────────────
P50 (Median):  < 100ms
P95:           < 500ms
P99:           < 1000ms

Throughput:
─────────────────────────────────────────────────────────
Small app:     100-500 RPS
Medium app:    1,000-10,000 RPS
Large app:     100,000+ RPS

Error Rate:
─────────────────────────────────────────────────────────
Target:        < 0.1% (1 in 1000)
Acceptable:    < 1%
Bad:           > 5%
```

---

## Best Practices Checklist

### Database

```
□ Indexes on frequently queried columns
□ Connection pooling configured
□ N+1 queries eliminated (use joinedload)
□ Pagination on all list endpoints
□ Query logging in development
□ EXPLAIN ANALYZE on slow queries
```

### Caching

```
□ Cache hot data in Redis
□ Appropriate TTL values
□ Cache invalidation strategy
□ Cache hit ratio monitoring
□ Local cache for static data
```

### API

```
□ Response compression enabled
□ Async endpoints for I/O operations
□ Background tasks for slow operations
□ Rate limiting in place
□ Request timeout configured
```

### Monitoring

```
□ Response time tracking
□ Error rate alerts
□ Database connection monitoring
□ Memory/CPU usage alerts
□ Slow query logging
```

---

## Quick Reference

```python
# Performance Quick Wins

# 1. Add database indexes
Index('idx_user_email', User.email)

# 2. Enable caching
@lru_cache(maxsize=1000)
def expensive_function(): ...

# 3. Use async
async def get_data():
    return await db.query(...)

# 4. Compress responses
app.add_middleware(GZipMiddleware)

# 5. Limit query results
query.limit(20)

# 6. Use connection pooling
engine = create_engine(url, pool_size=20)
```

---

> **Pro Tip**: "Premature optimization is the root of all evil - pehle measure karo, phir optimize karo! Profiler use karo, guessing se kuch nahi hota." 🚀
