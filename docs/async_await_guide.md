# 🚀 Async/Await Complete Guide - Hindi + English

## 📖 Table of Contents
1. [Basic Definitions](#1-basic-definitions)
2. [Why Async/Await?](#2-why-asyncawait)
3. [Sleep Explained](#3-sleep-explained)
4. [async Keyword](#4-async-keyword)
5. [await Keyword](#5-await-keyword)
6. [asyncio Module](#6-asyncio-module)
7. [Real Examples](#7-real-examples)
8. [Common Mistakes](#8-common-mistakes)
9. [When to Use](#9-when-to-use)
10. [Quick Reference](#10-quick-reference)

---

## 1. Basic Definitions

### 🔹 Synchronous (Sync)
**English:** Code runs line by line, one after another. Each line waits for previous to complete.

**Hindi:** Ek line complete hogi, tab doosri chalegi. Sab wait karte hain.

```python
print("Line 1")  # Pehle ye
print("Line 2")  # Phir ye
print("Line 3")  # Phir ye
```

### 🔹 Asynchronous (Async)
**English:** Code can "pause" and let other code run while waiting for something.

**Hindi:** Code ruk sakta hai aur doosra kaam hone deta hai wait karte hue.

```python
async def task():
    print("Start")
    await something()  # Yahan ruka, doosre kaam ho gaye
    print("End")
```

### 🔹 Blocking
**English:** Operation that freezes everything until it's done.

**Hindi:** Jab tak ye complete nahi, kuch nahi hoga.

```python
import time
time.sleep(5)  # 5 sec tak SARI cheezein ruki 🛑
```

### 🔹 Non-Blocking
**English:** Operation that allows other things to happen while waiting.

**Hindi:** Wait karte hue bhi doosre kaam ho sakte hain.

```python
await asyncio.sleep(5)  # 5 sec wait, but doosre tasks chalu ✅
```

---

## 2. Why Async/Await?

### 🍔 Restaurant Example

#### Sync Waiter (Blocking):
```
Customer 1 order → Waiter kitchen gaya → 10 min wait 😴 → Khana laya
Customer 2 order → 10 min baad
Customer 3 order → 20 min baad

Total time for 3 customers = 30 minutes ❌
```

#### Async Waiter (Non-Blocking):
```
Customer 1 order → Kitchen mein order diya → Wapas aaya
Customer 2 order → Kitchen mein order diya → Wapas aaya  
Customer 3 order → Kitchen mein order diya → Wapas aaya
Kitchen ready → Sabko serve kiya

Total time for 3 customers = ~10 minutes ✅
```

### 💻 Server Example

#### Sync Server:
```
Request 1 (Database 2 sec) → Wait... → Response
Request 2 → Blocked! Wait for Request 1
Request 3 → Blocked!

1000 users = 2000 seconds = 33 minutes 😱
```

#### Async Server:
```
Request 1 → Database call → Server free
Request 2 → Database call → Server free  
Request 3 → Database call → Server free
All responses ready → Send all

1000 users = ~2 seconds 🚀
```

---

## 3. Sleep Explained

### 🔹 `time.sleep()` - Blocking Sleep

**English:** Completely stops the program. Nothing else can run.

**Hindi:** Poora program freeze. Kuch nahi chalega.

```python
import time

print("Start")
time.sleep(3)   # 3 sec tak FREEZE 🥶
print("End")    # 3 sec baad ye chalega

# Problem: Agar server mein use kiya, 3 sec tak koi request nahi handle hogi!
```

**Use When:** Simple scripts, testing, not in production servers.

---

### 🔹 `asyncio.sleep()` - Non-Blocking Sleep

**English:** Pauses current function, but lets other async tasks run.

**Hindi:** Current function ruka, but doosre async kaam chal rahe hain.

```python
import asyncio

async def task1():
    print("Task 1 start")
    await asyncio.sleep(3)  # 3 sec wait, but task2 chal sakta hai
    print("Task 1 end")

async def task2():
    print("Task 2 start")
    await asyncio.sleep(1)
    print("Task 2 end")

# Output:
# Task 1 start
# Task 2 start
# Task 2 end     ← 1 sec baad
# Task 1 end     ← 3 sec baad
```

**Use When:** API servers, async applications, when you want concurrency.

---

### 🔹 Comparison Table

| Feature | `time.sleep()` | `asyncio.sleep()` |
|---------|----------------|-------------------|
| Blocking | ✅ Yes - Sab ruk jata | ❌ No - Doosre chalu |
| Server mein | ❌ Bad | ✅ Good |
| `await` chahiye | ❌ No | ✅ Yes |
| `async def` mein | Optional | Required |
| Real-world use | Scripts | Production APIs |

---

## 4. async Keyword

### 🔹 Definition

**English:** Declares a function that CAN use `await` and CAN be paused.

**Hindi:** Batata hai ki ye function `await` use kar sakta hai aur ruk sakta hai.

### 🔹 Syntax

```python
# Normal function
def normal_function():
    return "Hello"

# Async function
async def async_function():
    return "Hello"
```

### 🔹 Key Points

```python
# 1️⃣ async function returns a "Coroutine" object, not direct value
async def greet():
    return "Hello"

result = greet()  # <coroutine object> - NOT "Hello"!
result = await greet()  # "Hello" ✅

# 2️⃣ async function ke andar hi await use hota hai
async def process():
    data = await fetch_data()  # ✅ Sahi
    
def process():
    data = await fetch_data()  # ❌ Error! await without async

# 3️⃣ async function ko call karne ke liye await chahiye
async def main():
    result = await greet()  # ✅
```

### 🔹 Visual

```
Normal Function:          Async Function:
┌─────────────┐           ┌─────────────┐
│ def func(): │           │async def f():│
│   code...   │           │   code...   │
│   return x  │           │   await ... │ ← Can pause here!
└─────────────┘           │   code...   │
       │                  └─────────────┘
       ▼                         │
   Runs to end               Can pause & resume
```

---

## 5. await Keyword

### 🔹 Definition

**English:** Pauses the async function and waits for the operation to complete. During wait, other async tasks can run.

**Hindi:** Async function ko pause karta hai aur operation complete hone ka wait karta hai. Wait ke time doosre async tasks chal sakte hain.

### 🔹 Syntax

```python
async def my_function():
    result = await some_async_operation()
    #        ^^^^^ 
    #        "Yahan ruk, ye complete hone de, 
    #         but server free hai doosro ke liye"
```

### 🔹 What Can Be Awaited?

```python
# ✅ Can await - Coroutines
await asyncio.sleep(1)
await fetch_from_database()
await call_external_api()
await read_file_async()

# ❌ Cannot await - Regular values
await 5                    # Error!
await "hello"              # Error!
await [1, 2, 3]            # Error!
await normal_function()    # Error! (non-async function)
```

### 🔹 await = "Smart Wait"

```python
# ❌ Dumb Wait (Blocking)
import time
def slow_task():
    time.sleep(5)      # Sab freeze 🥶
    return "done"

# ✅ Smart Wait (Non-Blocking)
import asyncio
async def smart_task():
    await asyncio.sleep(5)  # Wait, but free for others 🚀
    return "done"
```

### 🔹 Real World Analogy

```
await = Phone order karna

1. Order diya (function call)
2. Wait kar raha hoon (await)
3. But TV dekh sakta hoon (other tasks)
4. Delivery aa gayi (await complete)
5. Aage ka kaam (next line of code)

Without await = Personally shop jaake line mein khade rehna
   - Kuch aur nahi kar sakta
   - Time waste
```

---

## 6. asyncio Module

### 🔹 Definition

**English:** Python's built-in library for writing async code.

**Hindi:** Python ka async code likhne ka library.

### 🔹 Important Functions

```python
import asyncio

# 1️⃣ asyncio.sleep(seconds) - Async delay
await asyncio.sleep(2)  # 2 sec smart wait

# 2️⃣ asyncio.gather(*tasks) - Run multiple tasks together
results = await asyncio.gather(
    task1(),
    task2(),
    task3()
)  # Sab parallel chalte hain!

# 3️⃣ asyncio.create_task(coro) - Background task
task = asyncio.create_task(background_job())

# 4️⃣ asyncio.run(main()) - Start async program
asyncio.run(main())  # Normal Python script mein async start karo
```

### 🔹 asyncio.gather() - Parallel Execution

```python
import asyncio

async def fetch_users():
    await asyncio.sleep(2)  # 2 sec
    return ["user1", "user2"]

async def fetch_orders():
    await asyncio.sleep(3)  # 3 sec
    return ["order1", "order2"]

async def fetch_products():
    await asyncio.sleep(1)  # 1 sec
    return ["product1", "product2"]

# ❌ Sequential - 6 seconds total
async def slow_dashboard():
    users = await fetch_users()      # 2 sec
    orders = await fetch_orders()    # 3 sec
    products = await fetch_products() # 1 sec
    return {"users": users, "orders": orders, "products": products}

# ✅ Parallel - 3 seconds total (longest one)
async def fast_dashboard():
    users, orders, products = await asyncio.gather(
        fetch_users(),
        fetch_orders(), 
        fetch_products()
    )
    return {"users": users, "orders": orders, "products": products}
```

**Visual:**
```
Sequential (6 sec):
|--users (2s)--|--orders (3s)--|--products (1s)--|

Parallel (3 sec):
|--users (2s)--|
|----orders (3s)----|
|--products (1s)--|
```

---

## 7. Real Examples

### 🔹 Example 1: Basic FastAPI

```python
from fastapi import FastAPI
import asyncio

app = FastAPI()

# Sync endpoint - Simple, no I/O wait
@app.get("/sync")
def sync_endpoint():
    return {"message": "Hello"}  # Instant, no await needed

# Async endpoint - When you need to wait for something
@app.get("/async")
async def async_endpoint():
    await asyncio.sleep(1)  # Simulate slow operation
    return {"message": "Hello after 1 sec"}
```

### 🔹 Example 2: Database Query

```python
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession):
    # Database query - I/O operation
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    # ^^^^^ Database response ka wait
    # But server free hai doosri requests ke liye
    
    user = result.scalar()
    return user
```

### 🔹 Example 3: External API Call

```python
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/weather/{city}")
async def get_weather(city: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weather.com/{city}"
        )
        # ^^^^^ External API response ka wait
        # Server free for other requests
        
    return response.json()
```

### 🔹 Example 4: Multiple API Calls (Parallel)

```python
from fastapi import FastAPI
import httpx
import asyncio

app = FastAPI()

async def get_github_user(username: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://api.github.com/users/{username}")
        return resp.json()

async def get_github_repos(username: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://api.github.com/users/{username}/repos")
        return resp.json()

@app.get("/github/{username}")
async def github_profile(username: str):
    # ✅ Parallel - Both calls at same time
    user, repos = await asyncio.gather(
        get_github_user(username),
        get_github_repos(username)
    )
    
    return {
        "user": user,
        "repos_count": len(repos)
    }
```

### 🔹 Example 5: File Operations

```python
import aiofiles
from fastapi import FastAPI

app = FastAPI()

@app.post("/log")
async def write_log(message: str):
    async with aiofiles.open("app.log", "a") as f:
        await f.write(f"{message}\n")
        # ^^^^^ File write complete hone ka wait
    
    return {"status": "logged"}

@app.get("/logs")
async def read_logs():
    async with aiofiles.open("app.log", "r") as f:
        content = await f.read()
        # ^^^^^ File read complete hone ka wait
    
    return {"logs": content}
```

---

## 8. Common Mistakes

### ❌ Mistake 1: await without async

```python
# ❌ WRONG
def my_function():
    result = await some_async_call()  # SyntaxError!

# ✅ RIGHT
async def my_function():
    result = await some_async_call()
```

### ❌ Mistake 2: Forgetting await

```python
# ❌ WRONG - Returns coroutine object, not actual data
async def get_data():
    return await db.query()

async def main():
    data = get_data()  # <coroutine object>
    print(data)  # Not the actual data!

# ✅ RIGHT
async def main():
    data = await get_data()  # Actual data ✅
    print(data)
```

### ❌ Mistake 3: Using time.sleep() in async

```python
# ❌ WRONG - Blocks everything!
import time
async def slow_task():
    time.sleep(5)  # Freezes server 🥶
    return "done"

# ✅ RIGHT
import asyncio
async def smart_task():
    await asyncio.sleep(5)  # Non-blocking ✅
    return "done"
```

### ❌ Mistake 4: Awaiting non-async functions

```python
# ❌ WRONG
def normal_func():
    return "hello"

async def main():
    result = await normal_func()  # Error!

# ✅ RIGHT
async def async_func():
    return "hello"

async def main():
    result = await async_func()  # ✅
```

### ❌ Mistake 5: Sequential instead of Parallel

```python
# ❌ SLOW - 6 seconds
async def slow_way():
    a = await api_call_1()  # 2 sec
    b = await api_call_2()  # 2 sec
    c = await api_call_3()  # 2 sec
    return a, b, c

# ✅ FAST - 2 seconds
async def fast_way():
    a, b, c = await asyncio.gather(
        api_call_1(),
        api_call_2(),
        api_call_3()
    )
    return a, b, c
```

---

## 9. When to Use

### ✅ Use async/await When:

| Situation | Example | Why |
|-----------|---------|-----|
| Database queries | `await db.execute()` | Network I/O wait |
| External API calls | `await client.get()` | Network I/O wait |
| File read/write | `await file.read()` | Disk I/O wait |
| Multiple slow operations | `await asyncio.gather()` | Parallel execution |
| WebSocket connections | `await websocket.receive()` | Long-lived connections |
| Message queues | `await queue.get()` | Waiting for messages |

### ❌ DON'T Use async/await When:

| Situation | Example | Why |
|-----------|---------|-----|
| Simple calculations | `2 + 2` | Instant, no wait needed |
| In-memory operations | `list.append()` | Instant |
| CPU-heavy tasks | Image processing | Use multiprocessing instead |
| Simple data access | `dict["key"]` | Instant |

### 🤔 Decision Flowchart:

```
Is there I/O operation? (Network/Database/File)
    │
    ├── YES → Use async/await ✅
    │
    └── NO → Is it CPU intensive?
              │
              ├── YES → Use multiprocessing
              │
              └── NO → Use normal sync function ✅
```

---

## 10. Quick Reference

### 🔹 Keywords

| Keyword | Meaning | Hindi |
|---------|---------|-------|
| `async` | Function can pause | Ye function ruk sakta hai |
| `await` | Pause here, wait for result | Yahan ruk, result ka wait kar |
| `asyncio` | Async library | Async tools ka collection |

### 🔹 Common Patterns

```python
# Pattern 1: Simple async function
async def simple():
    result = await some_operation()
    return result

# Pattern 2: Multiple awaits
async def multiple():
    a = await operation_1()
    b = await operation_2(a)  # Depends on a
    return b

# Pattern 3: Parallel execution
async def parallel():
    a, b, c = await asyncio.gather(
        operation_1(),
        operation_2(),
        operation_3()
    )
    return a, b, c

# Pattern 4: FastAPI endpoint
@app.get("/data")
async def get_data():
    data = await fetch_from_db()
    return data
```

### 🔹 Libraries for Async

| Purpose | Sync Library | Async Library |
|---------|--------------|---------------|
| HTTP Requests | `requests` | `httpx`, `aiohttp` |
| Database | `psycopg2` | `asyncpg`, `databases` |
| File I/O | `open()` | `aiofiles` |
| Redis | `redis-py` | `aioredis` |
| MongoDB | `pymongo` | `motor` |

### 🔹 Memory Trick

```
async = "Main CAPABLE hoon rukne ka" (I CAN pause)
await = "Main ACTUALLY ruk raha hoon" (I AM pausing)

Without async → await use nahi kar sakte
Without await → async function ka result nahi milega
```

---

## 🎯 Final Summary

```
1. async def = Function jo ruk sakta hai
2. await = Yahan ruk, but doosre kaam hone de
3. asyncio.sleep() = Smart wait (non-blocking)
4. time.sleep() = Dumb wait (blocking)
5. asyncio.gather() = Parallel execution
6. Use async = I/O operations (DB, API, File)
7. Don't use async = CPU tasks, simple calculations
```

---

**Created for FastAPI Learning Journey** 📚
**Date:** December 2024
