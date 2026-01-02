# 04 — Async/Await in Python & FastAPI (Complete In-Depth Guide)

> 🎯 **Goal**: Async programming master ban jao - concurrency, parallelism, event loop sab samajh aayega!

---

## 📚 Table of Contents
1. [Synchronous vs Asynchronous](#synchronous-vs-asynchronous)
2. [Why Async Matters](#why-async-matters)
3. [Python Async Basics](#python-async-basics)
4. [Coroutines Deep Dive](#coroutines-deep-dive)
5. [Event Loop](#event-loop)
6. [asyncio Module](#asyncio-module)
7. [Async Context Managers](#async-context-managers)
8. [Async Iterators](#async-iterators)
9. [FastAPI mein Async](#fastapi-mein-async)
10. [Database Async Operations](#database-async-operations)
11. [HTTP Async Calls](#http-async-calls)
12. [Common Patterns](#common-patterns)
13. [Error Handling](#error-handling)
14. [Performance Tips](#performance-tips)
15. [Industry Best Practices](#industry-best-practices)
16. [Practice Exercises](#practice-exercises)

---

## Synchronous vs Asynchronous

### Synchronous (Blocking) Code
```python
import time

def task1():
    print("Task 1 start")
    time.sleep(2)  # Blocks everything for 2 seconds
    print("Task 1 done")

def task2():
    print("Task 2 start")
    time.sleep(2)  # Blocks everything for 2 seconds
    print("Task 2 done")

def main():
    start = time.time()
    task1()  # Wait 2 seconds
    task2()  # Wait 2 more seconds
    print(f"Total time: {time.time() - start:.2f}s")  # ~4 seconds

main()
# Output:
# Task 1 start
# Task 1 done (after 2s)
# Task 2 start
# Task 2 done (after 2s more)
# Total time: 4.00s
```

### Asynchronous (Non-Blocking) Code
```python
import asyncio

async def task1():
    print("Task 1 start")
    await asyncio.sleep(2)  # Non-blocking - lets other tasks run
    print("Task 1 done")

async def task2():
    print("Task 2 start")
    await asyncio.sleep(2)  # Non-blocking
    print("Task 2 done")

async def main():
    start = asyncio.get_event_loop().time()
    # Run both tasks concurrently
    await asyncio.gather(task1(), task2())
    print(f"Total time: {asyncio.get_event_loop().time() - start:.2f}s")

asyncio.run(main())
# Output:
# Task 1 start
# Task 2 start
# Task 1 done (after 2s)
# Task 2 done (after 2s - same time!)
# Total time: 2.00s  <-- Half the time!
```

### Real World Analogy
```
Synchronous (Restaurant with 1 waiter):
- Waiter takes order from Table 1
- Waiter goes to kitchen, WAITS for food
- Waiter serves Table 1
- THEN goes to Table 2
- Result: Slow service!

Asynchronous (Smart waiter):
- Waiter takes order from Table 1
- Sends order to kitchen (doesn't wait)
- Immediately takes order from Table 2
- Sends to kitchen
- When food ready, serves both
- Result: Fast service!
```

---

## Why Async Matters

### I/O Bound vs CPU Bound

```python
# I/O Bound - Waiting for external resources
# - Database queries
# - API calls
# - File reading/writing
# - Network operations
# ASYNC IS PERFECT FOR THIS!

# CPU Bound - Heavy computation
# - Image processing
# - Video encoding
# - Mathematical calculations
# - Data encryption
# USE MULTIPROCESSING FOR THIS!
```

### Web Server Comparison
```python
# Synchronous server (Flask default)
# 1000 users, each request takes 1 second (DB call)
# Time to serve all: 1000 seconds (16+ minutes!)

# Async server (FastAPI)
# 1000 users, each request takes 1 second (DB call)
# Time to serve all: ~1 second! (all concurrent)
```

### When to Use Async
```python
# ✅ USE ASYNC FOR:
# - Web APIs (FastAPI, aiohttp)
# - Database operations (asyncpg, databases)
# - HTTP client calls (httpx, aiohttp)
# - WebSocket connections
# - File I/O (aiofiles)
# - Message queues (aio-pika)

# ❌ DON'T USE ASYNC FOR:
# - CPU-heavy computations (use multiprocessing)
# - Simple scripts (overkill)
# - When libraries don't support async
```

---

## Python Async Basics

### async def - Defining Coroutines
```python
import asyncio

# Regular function
def regular_function():
    return "I'm regular"

# Async function (coroutine)
async def async_function():
    return "I'm async"

# Calling regular function
result1 = regular_function()  # Returns value directly
print(result1)  # "I'm regular"

# Calling async function
result2 = async_function()  # Returns coroutine object, NOT value!
print(result2)  # <coroutine object async_function at 0x...>

# To get value from coroutine, must await it
async def main():
    result = await async_function()  # Now we get the value
    print(result)  # "I'm async"

asyncio.run(main())
```

### await - Waiting for Coroutines
```python
import asyncio

async def fetch_data():
    print("Fetching data...")
    await asyncio.sleep(2)  # Simulate network delay
    return {"id": 1, "name": "Tarun"}

async def process_data():
    # await pauses this function until fetch_data completes
    # BUT it doesn't block the entire program!
    data = await fetch_data()
    print(f"Got data: {data}")
    return data

asyncio.run(process_data())
```

### Rules of await
```python
import asyncio

async def example():
    # ✅ Can await coroutines
    await asyncio.sleep(1)
    
    # ✅ Can await other async functions
    result = await some_async_function()
    
    # ❌ Cannot await regular functions
    # await regular_function()  # Error!
    
    # ❌ Cannot await in regular functions
    # def regular():
    #     await asyncio.sleep(1)  # SyntaxError!

# ❌ Cannot use await at top level (Python < 3.10)
# await asyncio.sleep(1)  # Error outside async function

# ✅ Python 3.10+ allows top-level await in some contexts
```

---

## Coroutines Deep Dive

### What is a Coroutine?
```python
import asyncio

# A coroutine is a special function that can be paused and resumed
async def my_coroutine():
    print("Start")
    await asyncio.sleep(1)  # Pause here, let others run
    print("After 1 second")
    await asyncio.sleep(1)  # Pause again
    print("After 2 seconds")
    return "Done!"

# Coroutine object vs execution
coro = my_coroutine()  # Creates coroutine object (doesn't run!)
print(type(coro))  # <class 'coroutine'>

# To run it:
result = asyncio.run(coro)  # Now it runs
print(result)  # "Done!"
```

### Coroutine States
```python
import asyncio
import inspect

async def sample():
    await asyncio.sleep(1)
    return "completed"

coro = sample()

# Check if it's a coroutine
print(inspect.iscoroutine(coro))  # True

# Coroutine states:
# 1. Created - just created, not started
# 2. Running - currently executing
# 3. Suspended - waiting at await
# 4. Closed - finished or cancelled
```

### Multiple Coroutines
```python
import asyncio

async def greet(name, delay):
    await asyncio.sleep(delay)
    print(f"Hello, {name}!")
    return f"Greeted {name}"

async def main():
    # Sequential (slow) - total 6 seconds
    result1 = await greet("Alice", 2)
    result2 = await greet("Bob", 2)
    result3 = await greet("Charlie", 2)
    
    # Concurrent (fast) - total 2 seconds
    results = await asyncio.gather(
        greet("Alice", 2),
        greet("Bob", 2),
        greet("Charlie", 2)
    )
    print(results)  # ['Greeted Alice', 'Greeted Bob', 'Greeted Charlie']

asyncio.run(main())
```

---

## Event Loop

### What is Event Loop?
```python
# Event Loop is the core of async programming
# It manages and distributes execution of coroutines

# Think of it as a traffic controller:
# - Keeps track of all pending tasks
# - Runs tasks when they're ready
# - Switches between tasks at await points

import asyncio

# Get current event loop
loop = asyncio.get_event_loop()

# Or new loop
loop = asyncio.new_event_loop()

# Run until complete
async def hello():
    print("Hello")
    await asyncio.sleep(1)
    print("World")

# Method 1: asyncio.run() (Python 3.7+) - RECOMMENDED
asyncio.run(hello())

# Method 2: loop.run_until_complete()
loop = asyncio.new_event_loop()
loop.run_until_complete(hello())
loop.close()
```

### Event Loop Internals
```python
import asyncio

async def task(name, duration):
    print(f"{name}: Starting")
    await asyncio.sleep(duration)
    print(f"{name}: Done after {duration}s")
    return name

async def main():
    # Event loop handles this:
    # 1. Start task A, B, C
    # 2. All hit await asyncio.sleep()
    # 3. Loop waits for first to complete
    # 4. B completes first (1s)
    # 5. A completes next (2s)
    # 6. C completes last (3s)
    
    results = await asyncio.gather(
        task("A", 2),
        task("B", 1),
        task("C", 3)
    )
    print(f"All done: {results}")

asyncio.run(main())
# Output:
# A: Starting
# B: Starting
# C: Starting
# B: Done after 1s
# A: Done after 2s
# C: Done after 3s
# All done: ['A', 'B', 'C']
```

---

## asyncio Module

### asyncio.gather() - Run Multiple Coroutines
```python
import asyncio

async def fetch_user(user_id):
    await asyncio.sleep(1)
    return {"id": user_id, "name": f"User{user_id}"}

async def fetch_posts(user_id):
    await asyncio.sleep(1)
    return [{"id": 1, "title": "Post 1"}]

async def main():
    # Run both concurrently - takes 1 second, not 2!
    user, posts = await asyncio.gather(
        fetch_user(1),
        fetch_posts(1)
    )
    print(user, posts)

    # With return_exceptions=True, errors don't stop others
    results = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3),
        return_exceptions=True  # Errors returned as results
    )

asyncio.run(main())
```

### asyncio.create_task() - Background Tasks
```python
import asyncio

async def background_job():
    while True:
        print("Background: doing work...")
        await asyncio.sleep(2)

async def main_work():
    for i in range(5):
        print(f"Main: step {i}")
        await asyncio.sleep(1)

async def main():
    # Create background task
    bg_task = asyncio.create_task(background_job())
    
    # Do main work
    await main_work()
    
    # Cancel background task when done
    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        print("Background task cancelled")

asyncio.run(main())
```

### asyncio.wait() - More Control
```python
import asyncio

async def task(n):
    await asyncio.sleep(n)
    return n

async def main():
    tasks = [
        asyncio.create_task(task(3)),
        asyncio.create_task(task(1)),
        asyncio.create_task(task(2))
    ]
    
    # Wait for first to complete
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED
    )
    print(f"First done: {[t.result() for t in done]}")
    
    # Cancel remaining
    for t in pending:
        t.cancel()

asyncio.run(main())
```

### asyncio.wait_for() - Timeout
```python
import asyncio

async def slow_operation():
    await asyncio.sleep(10)
    return "Completed"

async def main():
    try:
        # Wait maximum 3 seconds
        result = await asyncio.wait_for(
            slow_operation(),
            timeout=3.0
        )
        print(result)
    except asyncio.TimeoutError:
        print("Operation timed out!")

asyncio.run(main())
```

### asyncio.sleep() vs time.sleep()
```python
import asyncio
import time

async def main():
    # ❌ WRONG - blocks entire event loop
    # time.sleep(1)  
    
    # ✅ CORRECT - allows other tasks to run
    await asyncio.sleep(1)

# time.sleep() = Blocking (freezes everything)
# asyncio.sleep() = Non-blocking (others can run)
```

### Semaphore - Limit Concurrency
```python
import asyncio

async def fetch_url(url, semaphore):
    async with semaphore:  # Only N concurrent
        print(f"Fetching {url}")
        await asyncio.sleep(1)  # Simulate network
        return f"Data from {url}"

async def main():
    # Maximum 3 concurrent requests
    semaphore = asyncio.Semaphore(3)
    
    urls = [f"https://api.com/{i}" for i in range(10)]
    
    tasks = [fetch_url(url, semaphore) for url in urls]
    results = await asyncio.gather(*tasks)
    print(f"Got {len(results)} results")

asyncio.run(main())
```

---

## Async Context Managers

### async with
```python
import asyncio

class AsyncDatabase:
    async def __aenter__(self):
        print("Opening connection...")
        await asyncio.sleep(0.5)  # Simulate connect
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection...")
        await asyncio.sleep(0.5)  # Simulate disconnect
    
    async def query(self, sql):
        await asyncio.sleep(0.1)
        return [{"id": 1}]

async def main():
    async with AsyncDatabase() as db:
        result = await db.query("SELECT * FROM users")
        print(result)

asyncio.run(main())
# Output:
# Opening connection...
# [{'id': 1}]
# Closing connection...
```

### Using contextlib
```python
from contextlib import asynccontextmanager
import asyncio

@asynccontextmanager
async def async_timer():
    start = asyncio.get_event_loop().time()
    yield
    end = asyncio.get_event_loop().time()
    print(f"Elapsed: {end - start:.2f}s")

async def main():
    async with async_timer():
        await asyncio.sleep(2)

asyncio.run(main())
# Elapsed: 2.00s
```

---

## Async Iterators

### async for
```python
import asyncio

class AsyncRange:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop
    
    def __aiter__(self):
        self.current = self.start
        return self
    
    async def __anext__(self):
        if self.current >= self.stop:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)  # Simulate async operation
        value = self.current
        self.current += 1
        return value

async def main():
    async for num in AsyncRange(0, 5):
        print(num)

asyncio.run(main())
```

### Async Generators
```python
import asyncio

async def async_counter(n):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

async def main():
    async for num in async_counter(5):
        print(num)
    
    # Or collect all
    results = [num async for num in async_counter(5)]
    print(results)

asyncio.run(main())
```

---

## FastAPI mein Async

### Async Endpoints
```python
from fastapi import FastAPI
import asyncio

app = FastAPI()

# Sync endpoint (runs in thread pool)
@app.get("/sync")
def sync_endpoint():
    import time
    time.sleep(1)  # Blocks thread, but FastAPI handles it
    return {"message": "sync response"}

# Async endpoint (non-blocking)
@app.get("/async")
async def async_endpoint():
    await asyncio.sleep(1)  # Non-blocking
    return {"message": "async response"}

# When to use which?
# Use async def when:
# - Calling async functions (await ...)
# - Using async libraries (httpx, asyncpg)
# - Doing async I/O operations

# Use def when:
# - Calling sync/blocking code
# - Using sync libraries (requests, psycopg2)
# - CPU-intensive operations
```

### Async Database Operations
```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Async engine
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    return user
```

### Multiple Async Operations
```python
from fastapi import FastAPI
import httpx
import asyncio

app = FastAPI()

async def fetch_user_data(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        return response.json()

async def fetch_user_posts(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}/posts")
        return response.json()

@app.get("/users/{user_id}/complete")
async def get_complete_user(user_id: int):
    # Fetch both concurrently - FAST!
    user_data, posts = await asyncio.gather(
        fetch_user_data(user_id),
        fetch_user_posts(user_id)
    )
    return {
        "user": user_data,
        "posts": posts
    }
```

### Background Tasks in FastAPI
```python
from fastapi import FastAPI, BackgroundTasks
import asyncio

app = FastAPI()

async def send_email(email: str, message: str):
    await asyncio.sleep(3)  # Simulate sending email
    print(f"Email sent to {email}: {message}")

def write_log(message: str):
    # Sync function also works
    with open("log.txt", "a") as f:
        f.write(message + "\n")

@app.post("/register")
async def register_user(
    email: str,
    background_tasks: BackgroundTasks
):
    # Add tasks to run in background
    background_tasks.add_task(send_email, email, "Welcome!")
    background_tasks.add_task(write_log, f"User registered: {email}")
    
    # Response returns immediately, tasks run in background
    return {"message": "Registration successful"}
```

---

## Database Async Operations

### SQLAlchemy Async
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, select

# Async database URL
DATABASE_URL = "sqlite+aiosqlite:///./async_app.db"
# For PostgreSQL: "postgresql+asyncpg://user:pass@localhost/db"

# Async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Async session
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))

# Create tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# CRUD Operations
async def create_user(name: str, email: str):
    async with AsyncSessionLocal() as session:
        user = User(name=name, email=email)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

async def get_user(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

async def get_all_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        return result.scalars().all()

async def update_user(user_id: int, name: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.name = name
            await session.commit()
        return user

async def delete_user(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            await session.delete(user)
            await session.commit()
        return user
```

### Databases Library (Lightweight)
```python
from databases import Database
import asyncio

DATABASE_URL = "sqlite:///./app.db"
database = Database(DATABASE_URL)

async def main():
    # Connect
    await database.connect()
    
    # Execute query
    query = "INSERT INTO users(name, email) VALUES (:name, :email)"
    await database.execute(query, {"name": "Tarun", "email": "tarun@test.com"})
    
    # Fetch one
    query = "SELECT * FROM users WHERE id = :id"
    user = await database.fetch_one(query, {"id": 1})
    
    # Fetch all
    query = "SELECT * FROM users"
    users = await database.fetch_all(query)
    
    # Disconnect
    await database.disconnect()

asyncio.run(main())
```

---

## HTTP Async Calls

### httpx - Async HTTP Client
```python
import httpx
import asyncio

async def fetch_single():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com")
        return response.json()

async def fetch_multiple():
    async with httpx.AsyncClient() as client:
        # Multiple concurrent requests
        responses = await asyncio.gather(
            client.get("https://api.github.com/users/tarun5004"),
            client.get("https://api.github.com/repos/tarun5004/FastAPI-experiments"),
            client.get("https://api.github.com/rate_limit")
        )
        return [r.json() for r in responses]

async def post_data():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://httpbin.org/post",
            json={"name": "Tarun", "age": 25},
            headers={"Authorization": "Bearer token123"}
        )
        return response.json()

# With timeout and retry
async def fetch_with_timeout():
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get("https://slow-api.com")
            return response.json()
        except httpx.TimeoutException:
            return {"error": "Request timed out"}
```

### aiohttp (Alternative)
```python
import aiohttp
import asyncio

async def fetch_with_aiohttp():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.github.com") as response:
            return await response.json()

async def multiple_requests():
    async with aiohttp.ClientSession() as session:
        urls = [
            "https://api.github.com/users/user1",
            "https://api.github.com/users/user2",
            "https://api.github.com/users/user3"
        ]
        
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        
        results = []
        for response in responses:
            results.append(await response.json())
        
        return results
```

---

## Common Patterns

### Pattern 1: Concurrent API Calls
```python
import asyncio
import httpx

async def get_user_profile(user_id: int):
    """Fetch user profile from multiple services concurrently"""
    async with httpx.AsyncClient() as client:
        # All these run at the same time
        basic_info, posts, followers, settings = await asyncio.gather(
            client.get(f"https://api/users/{user_id}"),
            client.get(f"https://api/users/{user_id}/posts"),
            client.get(f"https://api/users/{user_id}/followers"),
            client.get(f"https://api/users/{user_id}/settings"),
        )
        
        return {
            "user": basic_info.json(),
            "posts": posts.json(),
            "followers": followers.json(),
            "settings": settings.json()
        }
```

### Pattern 2: Rate Limited Requests
```python
import asyncio

async def rate_limited_requests(urls: list, max_concurrent: int = 5):
    """Limit concurrent requests to avoid overwhelming server"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_with_limit(url):
        async with semaphore:
            async with httpx.AsyncClient() as client:
                return await client.get(url)
    
    tasks = [fetch_with_limit(url) for url in urls]
    return await asyncio.gather(*tasks)
```

### Pattern 3: Retry with Backoff
```python
import asyncio
import random

async def fetch_with_retry(url: str, max_retries: int = 3):
    """Retry failed requests with exponential backoff"""
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff with jitter
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Attempt {attempt + 1} failed, retrying in {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
```

### Pattern 4: Producer-Consumer
```python
import asyncio

async def producer(queue: asyncio.Queue, items: list):
    """Add items to queue"""
    for item in items:
        await queue.put(item)
        print(f"Produced: {item}")
        await asyncio.sleep(0.5)
    
    # Signal end
    await queue.put(None)

async def consumer(queue: asyncio.Queue, name: str):
    """Process items from queue"""
    while True:
        item = await queue.get()
        if item is None:
            await queue.put(None)  # Pass signal to other consumers
            break
        
        print(f"{name} processing: {item}")
        await asyncio.sleep(1)  # Simulate work
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    items = list(range(10))
    
    # Run producer and multiple consumers
    await asyncio.gather(
        producer(queue, items),
        consumer(queue, "Consumer-1"),
        consumer(queue, "Consumer-2"),
    )

asyncio.run(main())
```

### Pattern 5: Async Lock
```python
import asyncio

class AsyncCounter:
    def __init__(self):
        self.value = 0
        self.lock = asyncio.Lock()
    
    async def increment(self):
        async with self.lock:  # Only one at a time
            current = self.value
            await asyncio.sleep(0.1)  # Simulate work
            self.value = current + 1

async def main():
    counter = AsyncCounter()
    
    # Without lock, this would have race conditions
    await asyncio.gather(*[counter.increment() for _ in range(10)])
    
    print(f"Final value: {counter.value}")  # 10

asyncio.run(main())
```

---

## Error Handling

### Try-Except with Async
```python
import asyncio

async def risky_operation():
    await asyncio.sleep(1)
    raise ValueError("Something went wrong!")

async def safe_operation():
    try:
        result = await risky_operation()
        return result
    except ValueError as e:
        print(f"Caught error: {e}")
        return None
    finally:
        print("Cleanup done")

asyncio.run(safe_operation())
```

### Handling Multiple Task Errors
```python
import asyncio

async def task_that_fails():
    await asyncio.sleep(0.5)
    raise RuntimeError("Task failed!")

async def task_that_succeeds():
    await asyncio.sleep(1)
    return "Success!"

async def main():
    # Method 1: return_exceptions=True
    results = await asyncio.gather(
        task_that_fails(),
        task_that_succeeds(),
        return_exceptions=True
    )
    
    for result in results:
        if isinstance(result, Exception):
            print(f"Error: {result}")
        else:
            print(f"Success: {result}")

asyncio.run(main())
```

### Cancellation Handling
```python
import asyncio

async def long_running_task():
    try:
        while True:
            print("Working...")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Task was cancelled, cleaning up...")
        # Do cleanup here
        raise  # Re-raise to properly cancel

async def main():
    task = asyncio.create_task(long_running_task())
    
    await asyncio.sleep(3)  # Let it run for 3 seconds
    
    task.cancel()  # Cancel the task
    
    try:
        await task
    except asyncio.CancelledError:
        print("Task cancelled successfully")

asyncio.run(main())
```

---

## Performance Tips

### 1. Use gather() for Concurrent Operations
```python
# ❌ SLOW - Sequential
async def slow():
    result1 = await fetch_user(1)
    result2 = await fetch_posts(1)
    result3 = await fetch_comments(1)
    return result1, result2, result3

# ✅ FAST - Concurrent
async def fast():
    results = await asyncio.gather(
        fetch_user(1),
        fetch_posts(1),
        fetch_comments(1)
    )
    return results
```

### 2. Reuse HTTP Clients
```python
# ❌ SLOW - New client for each request
async def slow_fetch(urls):
    results = []
    for url in urls:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            results.append(response.json())
    return results

# ✅ FAST - Reuse client
async def fast_fetch(urls):
    async with httpx.AsyncClient() as client:  # One client for all
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]
```

### 3. Don't Block the Event Loop
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# ❌ WRONG - Blocks event loop
async def wrong():
    import time
    time.sleep(5)  # Blocks everything!
    return "done"

# ✅ RIGHT - Use asyncio.sleep
async def right():
    await asyncio.sleep(5)  # Non-blocking
    return "done"

# ✅ RIGHT - Run blocking code in thread pool
async def run_blocking_code():
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool,
            blocking_function  # Your sync function
        )
    return result
```

### 4. Use Connection Pooling
```python
from sqlalchemy.ext.asyncio import create_async_engine

# Connection pool settings
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,          # Base connections
    max_overflow=20,       # Extra connections if needed
    pool_pre_ping=True,    # Test connections before use
    pool_recycle=3600      # Recycle connections after 1 hour
)
```

---

## Industry Best Practices

### 1. Project Structure
```
app/
├── main.py
├── core/
│   ├── config.py
│   └── events.py        # Startup/shutdown events
├── db/
│   ├── base.py          # Async database setup
│   └── session.py       # Session management
├── services/
│   ├── user_service.py  # Async business logic
│   └── email_service.py
└── utils/
    └── http_client.py   # Shared async HTTP client
```

### 2. Startup/Shutdown Events
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
import httpx

# Global HTTP client
http_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global http_client
    http_client = httpx.AsyncClient()
    print("HTTP client created")
    
    yield  # App runs here
    
    # Shutdown
    await http_client.aclose()
    print("HTTP client closed")

app = FastAPI(lifespan=lifespan)
```

### 3. Dependency with Async
```python
from fastapi import Depends
import httpx

async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client

@app.get("/external-data")
async def get_external_data(client: httpx.AsyncClient = Depends(get_http_client)):
    response = await client.get("https://api.example.com/data")
    return response.json()
```

### 4. Testing Async Code
```python
import pytest
import asyncio
from httpx import AsyncClient

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.anyio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/async-endpoint")
        assert response.status_code == 200
```

---

## Practice Exercises

### Exercise 1: Concurrent Web Scraper
```python
# Create an async web scraper that:
# - Takes a list of URLs
# - Fetches all of them concurrently
# - Limits to 5 concurrent requests
# - Returns results as they complete
```

### Exercise 2: Async Chat Application
```python
# Create a simple async chat system:
# - Multiple users can connect
# - Messages broadcast to all users
# - Use asyncio.Queue for message passing
```

### Exercise 3: Async Database CRUD
```python
# Implement async CRUD operations:
# - Async create, read, update, delete
# - Bulk operations with gather()
# - Proper error handling
```

---

## Quick Reference

```python
import asyncio

# Define async function
async def my_async_func():
    await asyncio.sleep(1)
    return "done"

# Run coroutine
asyncio.run(my_async_func())

# Concurrent execution
await asyncio.gather(coro1(), coro2(), coro3())

# Create background task
task = asyncio.create_task(my_async_func())

# Wait with timeout
await asyncio.wait_for(coro(), timeout=5.0)

# Limit concurrency
semaphore = asyncio.Semaphore(5)
async with semaphore:
    await some_operation()

# Async context manager
async with SomeAsyncClass() as obj:
    await obj.do_something()

# Async iteration
async for item in async_generator():
    process(item)
```

---

## Next Steps

1. **Practice karo** - Exercises solve karo
2. **httpx use karo** - Real API calls try karo
3. **Next doc padho** - `05_dependency_injection.md`

---

> **Pro Tip**: Async programming initially confusing lagta hai, but practice se easy ho jayega. 
> Start with simple examples, then build up!
