# 15 — Caching & Redis (Complete In-Depth Guide)

> 🎯 **Goal**: Caching se app 100x fast banao - Redis master karo!

---

## 📚 Table of Contents
1. [Caching Kya Hai?](#caching-kya-hai)
2. [Caching Strategies](#caching-strategies)
3. [Redis Introduction](#redis-introduction)
4. [Redis with FastAPI](#redis-with-fastapi)
5. [Caching Patterns](#caching-patterns)
6. [Cache Invalidation](#cache-invalidation)
7. [Advanced Redis Features](#advanced-redis-features)
8. [Session Management](#session-management)
9. [Best Practices](#best-practices)
10. [Practice Exercises](#practice-exercises)

---

## Caching Kya Hai?

### Real-Life Example

```
Bina Cache:
─────────────────────────────────────
You: "Bhai, 2 + 2 kitna hota hai?"
Friend: *Calculator nikaala* "4"

You: "Bhai, 2 + 2 kitna hota hai?"
Friend: *Phir calculator nikaala* "4"

Har baar calculator! 🐌

With Cache:
─────────────────────────────────────
You: "Bhai, 2 + 2 kitna hota hai?"
Friend: *Calculator nikaala* "4" (yaad kar liya)

You: "Bhai, 2 + 2 kitna hota hai?"
Friend: "4" (turant bola, bina calculator!) 🚀

Yaad = Cache!
```

### Database vs Cache

```
Database Query:
User → API → Database → Disk Read → Result
             ↓
        Time: 50-500ms

Cached Result:
User → API → Cache (Memory) → Result
             ↓
        Time: 1-5ms

Cache is 10-100x FASTER because:
- Data in RAM (memory) not Disk
- No complex query processing
- Already computed/formatted
```

### What to Cache?

```python
# ✅ CACHE these:
# - Frequently read data (homepage, product listings)
# - Expensive computations (aggregations, reports)
# - External API responses
# - User sessions
# - Configuration data

# ❌ DON'T CACHE these:
# - Frequently changing data (real-time stock prices)
# - User-specific sensitive data (be careful!)
# - Very large data that rarely accessed
# - Data that must always be fresh
```

---

## Caching Strategies

### Strategy 1: Cache-Aside (Lazy Loading)

```python
# Most common pattern!
# App manages cache itself

async def get_user(user_id: int):
    """
    Cache-Aside Pattern:
    1. Check cache first
    2. If not found, get from DB
    3. Store in cache for next time
    """
    cache_key = f"user:{user_id}"
    
    # Step 1: Check cache
    cached = await redis.get(cache_key)
    if cached:
        return User.parse_raw(cached)  # Cache hit! 🎯
    
    # Step 2: Cache miss - get from DB
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalars().first()
    
    if user:
        # Step 3: Store in cache (expire in 5 minutes)
        await redis.setex(cache_key, 300, user.json())
    
    return user

# Timeline:
# First request:  Cache Miss → DB Query → Save to Cache
# Second request: Cache Hit! → Return immediately
```

### Strategy 2: Write-Through

```python
# Write to cache AND database together
# Cache always up-to-date

async def create_user(user_data: UserCreate):
    """
    Write-Through Pattern:
    1. Write to database
    2. Immediately update cache
    """
    # Step 1: Create in database
    user = User(**user_data.dict())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Step 2: Update cache immediately
    cache_key = f"user:{user.id}"
    await redis.setex(cache_key, 300, user.json())
    
    return user

# Pros: Cache always fresh
# Cons: Slower writes (2 operations)
```

### Strategy 3: Write-Behind (Write-Back)

```python
# Write to cache first, sync to DB later
# Very fast writes, eventual consistency

async def update_view_count(post_id: int):
    """
    Write-Behind Pattern:
    1. Update cache immediately
    2. Sync to DB periodically (background job)
    """
    cache_key = f"post:views:{post_id}"
    
    # Immediate cache update
    await redis.incr(cache_key)
    
    # Background job (every 5 minutes) syncs to DB
    # See background jobs documentation

# Pros: Super fast writes
# Cons: Risk of data loss if cache crashes
```

### Strategy Comparison

```
Pattern          Write Speed    Read Speed    Consistency
─────────────────────────────────────────────────────────
Cache-Aside      Normal         Fast*         Eventual
Write-Through    Slower         Fast          Strong
Write-Behind     Very Fast      Fast          Eventual

* First read is slow (cache miss)
```

---

## Redis Introduction

### Redis Kya Hai?

```
Redis = Remote Dictionary Server
     = In-Memory Data Store

Think of it as:
- Super fast dictionary (key-value store)
- Lives in RAM (memory)
- Supports complex data types
- Can persist to disk
- Distributed/clustered for scale
```

### Redis Data Types

```python
# 1. STRING - Simple key-value
await redis.set("name", "Tarun")
name = await redis.get("name")  # "Tarun"

# 2. HASH - Like Python dict
await redis.hset("user:1", mapping={
    "name": "Tarun",
    "email": "tarun@example.com"
})
user = await redis.hgetall("user:1")  # {"name": "Tarun", ...}

# 3. LIST - Ordered list
await redis.lpush("queue", "task1", "task2")
task = await redis.rpop("queue")  # "task1"

# 4. SET - Unique values
await redis.sadd("tags", "python", "fastapi", "python")  # Only 2 items
tags = await redis.smembers("tags")  # {"python", "fastapi"}

# 5. SORTED SET - Set with scores
await redis.zadd("leaderboard", {"player1": 100, "player2": 200})
top = await redis.zrange("leaderboard", 0, 9, withscores=True)

# 6. STREAMS - For message queues
await redis.xadd("events", {"type": "click", "page": "home"})
```

### When to Use Which?

```
Data Type     Use Case
─────────────────────────────────────────────
STRING        Simple cache, counters, flags
HASH          Object storage (user profiles)
LIST          Queues, recent items, activity feed
SET           Tags, unique visitors, relationships
SORTED SET    Leaderboards, time-based data
STREAMS       Event sourcing, message queues
```

---

## Redis with FastAPI

### Installation

```bash
# Redis server (choose one):
# - Windows: Use Docker or WSL
# - Linux: sudo apt install redis-server
# - Mac: brew install redis
# - Docker: docker run -p 6379:6379 redis

# Python client
pip install redis[hiredis]  # hiredis for speed
# or for async:
pip install aioredis
```

### Basic Setup

```python
# redis_client.py
import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Redis connection pool
redis_pool: redis.Redis | None = None

async def init_redis():
    """Initialize Redis connection pool"""
    global redis_pool
    redis_pool = redis.Redis(
        host="localhost",
        port=6379,
        db=0,  # Database number (0-15)
        decode_responses=True,  # Return strings instead of bytes
        # For production:
        # password="your-password",
        # ssl=True,
    )
    # Test connection
    await redis_pool.ping()
    print("✅ Redis connected!")

async def close_redis():
    """Close Redis connection"""
    global redis_pool
    if redis_pool:
        await redis_pool.close()
        print("✅ Redis disconnected!")

def get_redis() -> redis.Redis:
    """Dependency to get Redis client"""
    return redis_pool


# FastAPI integration
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()

app = FastAPI(lifespan=lifespan)
```

### Using Redis in Endpoints

```python
from fastapi import FastAPI, Depends
import redis.asyncio as redis
from redis_client import get_redis

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    r: redis.Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user with caching
    """
    cache_key = f"user:{user_id}"
    
    # Try cache first
    cached = await r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Cache miss - get from DB
    user = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user.scalars().first()
    
    if not user:
        raise HTTPException(404, "User not found")
    
    # Cache for 5 minutes
    user_dict = UserResponse.from_orm(user).dict()
    await r.setex(cache_key, 300, json.dumps(user_dict))
    
    return user_dict
```

---

## Caching Patterns

### Pattern 1: Function Decorator

```python
# cache_decorator.py
from functools import wraps
import json
import hashlib

def cache(ttl: int = 300, prefix: str = ""):
    """
    Caching decorator for async functions
    
    Usage:
    @cache(ttl=60, prefix="user")
    async def get_user(user_id: int):
        ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_data = f"{prefix}:{func.__name__}:{args}:{kwargs}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Get Redis client (assume global)
            r = get_redis()
            
            # Check cache
            cached = await r.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await r.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

# Usage
@cache(ttl=300, prefix="user")
async def get_user_expensive(user_id: int):
    # Expensive database query
    await asyncio.sleep(1)  # Simulate slow query
    return {"id": user_id, "name": "User"}
```

### Pattern 2: Cache Key Strategies

```python
# Good cache key design is CRUCIAL!

# 1. Simple key
cache_key = f"user:{user_id}"  # user:123

# 2. With version (for cache invalidation)
VERSION = "v1"
cache_key = f"{VERSION}:user:{user_id}"  # v1:user:123
# Change VERSION to invalidate all caches

# 3. With parameters
cache_key = f"products:category:{cat_id}:page:{page}"  
# products:category:5:page:2

# 4. With hash for complex queries
import hashlib
params = {"category": 5, "min_price": 100, "sort": "price"}
params_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()[:8]
cache_key = f"products:search:{params_hash}"  # products:search:a1b2c3d4

# 5. User-specific
cache_key = f"user:{user_id}:cart"  # user:123:cart
```

### Pattern 3: Request-Level Caching

```python
# Cache response for entire endpoint

from fastapi import Response
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_cache.backends.redis import RedisBackend

# Setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(RedisBackend(redis_pool), prefix="fastapi-cache")
    yield

# Usage - cache entire response
@app.get("/products")
@cache(expire=60)  # Cache for 60 seconds
async def get_products(category: str = None):
    # This entire response will be cached
    products = await fetch_products(category)
    return products
```

### Pattern 4: Computed/Aggregated Data

```python
# Cache expensive computations

async def get_dashboard_stats(r: redis.Redis, db: AsyncSession):
    """
    Dashboard stats - expensive to compute, cache longer
    """
    cache_key = "dashboard:stats"
    
    # Check cache
    cached = await r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Expensive aggregations
    total_users = await db.scalar(select(func.count(User.id)))
    total_orders = await db.scalar(select(func.count(Order.id)))
    revenue = await db.scalar(select(func.sum(Order.total)))
    
    stats = {
        "total_users": total_users,
        "total_orders": total_orders,
        "total_revenue": float(revenue or 0),
        "computed_at": datetime.utcnow().isoformat()
    }
    
    # Cache for 15 minutes (aggregates don't need real-time)
    await r.setex(cache_key, 900, json.dumps(stats))
    
    return stats
```

---

## Cache Invalidation

### "There are only two hard things in CS..."

```
"There are only two hard things in Computer Science:
cache invalidation and naming things."
- Phil Karlton

Cache Invalidation = Knowing when to delete/update cache
It's HARD because:
- Data changes in DB, cache becomes stale
- Multiple places might update same data
- Distributed systems make it harder
```

### Strategy 1: Time-Based Expiration (TTL)

```python
# Simple but imprecise
await redis.setex("user:123", 300, data)  # Expire in 5 minutes

# Pros: Simple, automatic cleanup
# Cons: Data might be stale until expiry
#       Fresh data waits for cache to expire
```

### Strategy 2: Event-Based Invalidation

```python
# Delete cache when data changes

async def update_user(user_id: int, data: UserUpdate, r: redis.Redis, db: AsyncSession):
    """Update user and invalidate cache"""
    # Update database
    user = await crud.update_user(db, user_id, data)
    
    # Invalidate cache immediately
    await r.delete(f"user:{user_id}")
    
    # Also invalidate related caches
    await r.delete(f"user:{user_id}:profile")
    await r.delete("users:list")  # List might be stale too
    
    return user


# Pattern: Delete on write
async def delete_user(user_id: int, r: redis.Redis, db: AsyncSession):
    await crud.delete_user(db, user_id)
    
    # Delete all related cache keys
    keys_to_delete = [
        f"user:{user_id}",
        f"user:{user_id}:*",  # All user-related keys
    ]
    
    # Use pattern matching for related keys
    async for key in r.scan_iter(f"user:{user_id}:*"):
        await r.delete(key)
```

### Strategy 3: Cache Tags

```python
# Tag related cache entries for bulk invalidation

async def cache_with_tags(key: str, value: str, tags: list, ttl: int = 300):
    """Cache value with tags for group invalidation"""
    r = get_redis()
    
    # Store value
    await r.setex(key, ttl, value)
    
    # Store key in tag sets
    for tag in tags:
        await r.sadd(f"tag:{tag}", key)
        await r.expire(f"tag:{tag}", ttl)

async def invalidate_tag(tag: str):
    """Invalidate all cache entries with this tag"""
    r = get_redis()
    
    # Get all keys with this tag
    keys = await r.smembers(f"tag:{tag}")
    
    # Delete all keys
    if keys:
        await r.delete(*keys)
    
    # Delete tag set
    await r.delete(f"tag:{tag}")

# Usage
await cache_with_tags(
    key="products:123",
    value=product_json,
    tags=["products", "category:electronics"]
)

# Invalidate all products
await invalidate_tag("products")
```

### Strategy 4: Version-Based Invalidation

```python
# Change version = invalidate all
CACHE_VERSION = "v3"  # Increment when schema changes

def cache_key(entity: str, id: int) -> str:
    return f"{CACHE_VERSION}:{entity}:{id}"

# Old cached data (v2) won't be found with new keys (v3)
# Old data expires naturally with TTL
```

---

## Advanced Redis Features

### Rate Limiting

```python
from fastapi import HTTPException

async def check_rate_limit(
    user_id: int,
    r: redis.Redis,
    limit: int = 100,
    window: int = 60
):
    """
    Sliding window rate limiting
    
    limit: Max requests
    window: Time window in seconds
    """
    key = f"ratelimit:{user_id}"
    
    # Increment counter
    current = await r.incr(key)
    
    # Set expiry on first request
    if current == 1:
        await r.expire(key, window)
    
    if current > limit:
        ttl = await r.ttl(key)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {ttl} seconds."
        )

# Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    user_id = get_user_id(request)  # Extract from token/header
    await check_rate_limit(user_id, redis_pool)
    return await call_next(request)
```

### Distributed Locks

```python
# Prevent concurrent operations on same resource

async def with_lock(key: str, timeout: int = 10):
    """
    Distributed lock using Redis
    
    Only one process can hold the lock
    Prevents race conditions across multiple servers
    """
    r = get_redis()
    lock_key = f"lock:{key}"
    lock_value = str(uuid.uuid4())  # Unique identifier
    
    # Try to acquire lock
    acquired = await r.set(lock_key, lock_value, nx=True, ex=timeout)
    
    if not acquired:
        raise Exception("Could not acquire lock")
    
    try:
        yield
    finally:
        # Release lock (only if we own it)
        # Use Lua script for atomic check-and-delete
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        await r.eval(script, 1, lock_key, lock_value)

# Usage
async def process_payment(order_id: int):
    async with with_lock(f"order:{order_id}"):
        # Only one process can process this order at a time
        await do_payment_processing(order_id)
```

### Pub/Sub for Real-time

```python
# Publisher
async def publish_event(channel: str, message: dict):
    r = get_redis()
    await r.publish(channel, json.dumps(message))

# Subscriber (background task)
async def listen_for_events():
    r = get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe("events")
    
    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            await handle_event(data)

# Usage
await publish_event("events", {
    "type": "order_created",
    "order_id": 123
})
```

---

## Session Management

### Redis for Sessions

```python
# Much better than database sessions!

from uuid import uuid4

async def create_session(user_id: int, r: redis.Redis) -> str:
    """Create new session"""
    session_id = str(uuid4())
    session_data = {
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Store session (expire in 24 hours)
    await r.setex(
        f"session:{session_id}",
        86400,  # 24 hours
        json.dumps(session_data)
    )
    
    return session_id

async def get_session(session_id: str, r: redis.Redis) -> dict | None:
    """Get session data"""
    data = await r.get(f"session:{session_id}")
    if data:
        # Refresh TTL on access (sliding expiration)
        await r.expire(f"session:{session_id}", 86400)
        return json.loads(data)
    return None

async def delete_session(session_id: str, r: redis.Redis):
    """Logout - delete session"""
    await r.delete(f"session:{session_id}")

async def delete_all_user_sessions(user_id: int, r: redis.Redis):
    """Logout from all devices"""
    # Need to track sessions per user
    async for key in r.scan_iter(f"session:*"):
        data = await r.get(key)
        if data:
            session = json.loads(data)
            if session.get("user_id") == user_id:
                await r.delete(key)
```

---

## Best Practices

### 1. Set Appropriate TTL

```python
# Different data, different TTL

# Frequently changing: short TTL
await r.setex("active_users", 60, data)  # 1 minute

# Stable data: longer TTL
await r.setex("product:123", 3600, data)  # 1 hour

# Static data: very long TTL
await r.setex("config:settings", 86400, data)  # 24 hours

# Don't set infinite TTL unless needed
# Memory will fill up!
```

### 2. Handle Cache Failures Gracefully

```python
async def get_user_safe(user_id: int, r: redis.Redis, db: AsyncSession):
    """Cache failure shouldn't break the app"""
    try:
        cached = await r.get(f"user:{user_id}")
        if cached:
            return json.loads(cached)
    except redis.RedisError as e:
        logger.warning(f"Redis error: {e}")
        # Continue to database - don't fail!
    
    # Fallback to database
    user = await db.execute(select(User).where(User.id == user_id))
    return user.scalars().first()
```

### 3. Use Connection Pool

```python
# Pool connections for efficiency
redis_pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=20,  # Adjust based on load
    decode_responses=True
)

r = redis.Redis(connection_pool=redis_pool)
```

### 4. Monitor Cache Hit Rate

```python
# Track cache effectiveness
cache_hits = 0
cache_misses = 0

async def get_cached(key: str):
    global cache_hits, cache_misses
    
    data = await r.get(key)
    if data:
        cache_hits += 1
        return data
    else:
        cache_misses += 1
        return None

# Log periodically
hit_rate = cache_hits / (cache_hits + cache_misses) * 100
logger.info(f"Cache hit rate: {hit_rate:.2f}%")

# Good hit rate: > 80%
# Low hit rate: Review what you're caching
```

---

## Practice Exercises

### Exercise 1: Implement Cache-Aside
```python
# Create caching for product endpoint:
# - Cache product by ID
# - TTL: 10 minutes
# - Invalidate on update/delete
```

### Exercise 2: Rate Limiter
```python
# Implement rate limiting:
# - 10 requests per minute per user
# - Return 429 when exceeded
# - Show remaining requests in header
```

### Exercise 3: Leaderboard
```python
# Build leaderboard with Redis sorted sets:
# - Add/update player scores
# - Get top 10 players
# - Get player rank
```

---

## Quick Reference

```python
# Basic operations
await r.set("key", "value")
await r.get("key")
await r.setex("key", 300, "value")  # With TTL
await r.delete("key")
await r.exists("key")

# Increment
await r.incr("counter")
await r.incrby("counter", 5)

# Hash
await r.hset("user:1", mapping={"name": "Tarun"})
await r.hget("user:1", "name")
await r.hgetall("user:1")

# List
await r.lpush("queue", "item")
await r.rpop("queue")

# Set
await r.sadd("tags", "python")
await r.smembers("tags")

# Sorted Set
await r.zadd("scores", {"player1": 100})
await r.zrange("scores", 0, 9, withscores=True)

# TTL
await r.expire("key", 300)
await r.ttl("key")
```

---

> **Pro Tip**: "Cache everything you can, but know when to invalidate!" 🚀
