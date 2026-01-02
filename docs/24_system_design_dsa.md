# 24 — System Design & DSA for Backend Developers (Complete In-Depth Guide)

> 🎯 **Goal**: System design aur DSA concepts jo interviews mein puchhe jaate hain!

---

## 📚 Table of Contents
1. [Why System Design & DSA?](#why-system-design--dsa)
2. [Essential DSA Concepts](#essential-dsa-concepts)
3. [System Design Fundamentals](#system-design-fundamentals)
4. [Common Design Patterns](#common-design-patterns)
5. [Caching Strategies](#caching-strategies)
6. [Database Design](#database-design)
7. [Microservices vs Monolith](#microservices-vs-monolith)
8. [Real System Design Examples](#real-system-design-examples)
9. [Interview Tips](#interview-tips)

---

## Why System Design & DSA?

### Kab Kahan Use Hota Hai?

```
DSA (Data Structures & Algorithms):
─────────────────────────────────────────────────────────
→ Efficient code likhne ke liye
→ Database queries optimize karne ke liye
→ API response time kam karne ke liye
→ Technical interviews crack karne ke liye

System Design:
─────────────────────────────────────────────────────────
→ Scalable systems build karne ke liye
→ Architecture decisions lene ke liye
→ Senior level interviews ke liye
→ Real-world problems solve karne ke liye
```

---

## Essential DSA Concepts

### 1. Big O Notation - Time Complexity

```python
# O(1) - Constant Time
# Same time regardless of input size
def get_first(arr):
    return arr[0]


# O(log n) - Logarithmic
# Binary search - half karte jao
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


# O(n) - Linear
# Loop through all elements
def find_max(arr):
    max_val = arr[0]
    for num in arr:
        if num > max_val:
            max_val = num
    return max_val


# O(n log n) - Merge Sort, Quick Sort
# Most efficient sorting algorithms
arr.sort()  # Python uses Timsort - O(n log n)


# O(n²) - Quadratic
# Nested loops
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
```

```
Time Complexity Comparison:
─────────────────────────────────────────────────────────
n=100 elements:

O(1)       →  1 operation
O(log n)   →  7 operations
O(n)       →  100 operations
O(n log n) →  700 operations
O(n²)      →  10,000 operations
O(2^n)     →  1.27 × 10^30 operations (impossible!)

Rule: Backend mein O(n²) se zyada avoid karo!
```

### 2. Hash Tables (Dict in Python)

```python
# O(1) average lookup - super fast!

# Use case 1: Counting
def count_chars(s):
    counts = {}
    for char in s:
        counts[char] = counts.get(char, 0) + 1
    return counts

# Use case 2: Caching
cache = {}
def expensive_operation(n):
    if n in cache:
        return cache[n]  # O(1) lookup
    result = compute_something(n)
    cache[n] = result
    return result

# Use case 3: Two Sum (Classic interview question)
def two_sum(nums, target):
    seen = {}  # num -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

### 3. Arrays & Lists

```python
# Python List Operations:
arr = [1, 2, 3, 4, 5]

arr[0]          # O(1) - Access by index
arr.append(6)   # O(1) - Add at end
arr.pop()       # O(1) - Remove from end
arr.insert(0, 0)  # O(n) - Insert at start (shifts all)
arr.pop(0)      # O(n) - Remove from start
x in arr        # O(n) - Search


# When to use List vs Set:
# List: Ordered, duplicates allowed, index access
# Set: Unique items, O(1) membership check

numbers = [1, 2, 2, 3, 3, 3]
unique = set(numbers)  # {1, 2, 3}

# Fast membership check
if user_id in active_user_ids:  # O(1) with set, O(n) with list
    pass
```

### 4. Stacks & Queues

```python
from collections import deque

# Stack - LIFO (Last In, First Out)
# Use: Undo functionality, parsing expressions
stack = []
stack.append("page1")
stack.append("page2")
stack.append("page3")
current = stack.pop()  # "page3"

# Queue - FIFO (First In, First Out)
# Use: Task queues, BFS, order processing
queue = deque()
queue.append("order1")  # Add to end
queue.append("order2")
next_order = queue.popleft()  # "order1" - Remove from front


# Real example: Rate limiting with sliding window
from collections import deque
from time import time

class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = deque()
    
    def allow_request(self):
        now = time()
        # Remove old requests
        while self.requests and self.requests[0] < now - self.window:
            self.requests.popleft()
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False
```

### 5. Trees & Graphs (Basics)

```python
# Binary Search Tree - for sorted data
# O(log n) search, insert, delete

class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def search_bst(root, target):
    if not root:
        return None
    if root.val == target:
        return root
    elif target < root.val:
        return search_bst(root.left, target)
    else:
        return search_bst(root.right, target)


# Graph - for connections/relationships
# Use: Social networks, recommendations, routing

graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A', 'D'],
    'D': ['B', 'C']
}

# BFS - Shortest path
def bfs(graph, start, end):
    from collections import deque
    
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        node, path = queue.popleft()
        if node == end:
            return path
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None
```

---

## System Design Fundamentals

### Key Concepts

```
1. Scalability
─────────────────────────────────────────────────────────
Vertical Scaling (Scale Up):
  → Bigger machine (more RAM, CPU)
  → Simple but limited
  → Expensive at scale

Horizontal Scaling (Scale Out):
  → More machines
  → Complex but unlimited
  → Cost effective


2. Availability
─────────────────────────────────────────────────────────
99.9% (Three 9s)   → 8.76 hours downtime/year
99.99% (Four 9s)   → 52 minutes downtime/year
99.999% (Five 9s)  → 5 minutes downtime/year


3. Consistency vs Availability (CAP Theorem)
─────────────────────────────────────────────────────────
→ You can only guarantee 2 of 3:
  - Consistency: All nodes see same data
  - Availability: System always responds
  - Partition Tolerance: Works despite network failures

→ In distributed systems, partition tolerance is mandatory
→ So choose between Consistency OR Availability
```

### Load Balancer

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    └────────┬────────┘
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ Server 1 │      │ Server 2 │      │ Server 3 │
    └──────────┘      └──────────┘      └──────────┘

Strategies:
─────────────────────────────────────────────────────────
Round Robin:     1 → 2 → 3 → 1 → 2 → 3
Least Connections: Send to server with fewest active
IP Hash:         Same user always goes to same server
Weighted:        Powerful servers get more requests
```

### Caching Layers

```
Request Flow:
─────────────────────────────────────────────────────────

User → CDN → Load Balancer → App Server → Cache → Database
       (1)        (2)           (3)        (4)       (5)

(1) CDN: Static files (images, CSS, JS)
(2) Load Balancer: Distribute requests
(3) App Server: Business logic
(4) Cache (Redis): Frequently accessed data
(5) Database: Source of truth


Cache Hit Ratio:
─────────────────────────────────────────────────────────
If 90% cache hit rate:
  1000 requests → 100 go to database
  10x less load on database!
```

---

## Common Design Patterns

### 1. API Gateway Pattern

```
                   ┌────────────────────┐
                   │   API Gateway      │
                   │ - Authentication   │
                   │ - Rate Limiting    │
                   │ - Request Routing  │
                   └─────────┬──────────┘
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ User Service│    │Order Service│    │Product Svc  │
   └─────────────┘    └─────────────┘    └─────────────┘
```

### 2. Event-Driven Architecture

```python
# Publisher/Subscriber Pattern

# Events:
# - user.created
# - order.placed
# - payment.received

# Publisher (Order Service)
async def create_order(order_data):
    order = await save_order(order_data)
    
    # Publish event
    await publish_event("order.placed", {
        "order_id": order.id,
        "user_id": order.user_id,
        "total": order.total
    })
    
    return order


# Subscribers
# Inventory Service listens to "order.placed" → reserve items
# Notification Service listens to "order.placed" → send email
# Analytics Service listens to "order.placed" → update metrics
```

### 3. CQRS (Command Query Responsibility Segregation)

```
                     ┌─────────────────┐
                     │   API Gateway   │
                     └────────┬────────┘
              ┌───────────────┴───────────────┐
              ▼                               ▼
       ┌────────────┐                  ┌────────────┐
       │  Commands  │                  │  Queries   │
       │ (Write)    │                  │  (Read)    │
       └──────┬─────┘                  └──────┬─────┘
              ▼                               ▼
       ┌────────────┐                  ┌────────────┐
       │ Write DB   │ ───sync/async──► │ Read DB    │
       │ (Primary)  │                  │ (Replicas) │
       └────────────┘                  └────────────┘

Benefits:
─────────────────────────────────────────────────────────
→ Read and write can scale independently
→ Read DB can be denormalized for fast queries
→ Write DB can be normalized for consistency
```

---

## Caching Strategies

### Cache Aside (Lazy Loading)

```python
import redis
import json

redis_client = redis.Redis()

async def get_user(user_id: int):
    # 1. Check cache first
    cache_key = f"user:{user_id}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # 2. Cache miss - get from DB
    user = await db.get_user(user_id)
    
    # 3. Store in cache for next time
    redis_client.setex(
        cache_key,
        3600,  # 1 hour TTL
        json.dumps(user.dict())
    )
    
    return user


async def update_user(user_id: int, data: dict):
    # Update DB
    user = await db.update_user(user_id, data)
    
    # Invalidate cache
    redis_client.delete(f"user:{user_id}")
    
    return user
```

### Write Through

```python
async def update_user(user_id: int, data: dict):
    # Update DB
    user = await db.update_user(user_id, data)
    
    # Update cache immediately
    redis_client.setex(
        f"user:{user_id}",
        3600,
        json.dumps(user.dict())
    )
    
    return user
```

### Cache Patterns Comparison

```
Cache Aside:
─────────────────────────────────────────────────────────
✅ Simple to implement
✅ Only caches what's needed
❌ First request always slow (cache miss)
❌ Cache and DB can be inconsistent

Write Through:
─────────────────────────────────────────────────────────
✅ Cache always fresh
✅ No cache miss after write
❌ Write latency increased
❌ May cache unused data

Write Behind (Write Back):
─────────────────────────────────────────────────────────
✅ Fast writes (async to DB)
✅ Reduces DB load
❌ Risk of data loss
❌ Complex to implement
```

---

## Database Design

### Normalization vs Denormalization

```
Normalized (3NF):
─────────────────────────────────────────────────────────
users: id, name, email
orders: id, user_id, total, created_at
order_items: id, order_id, product_id, quantity, price

✅ No data duplication
✅ Easy to update
❌ Requires JOINs for queries


Denormalized:
─────────────────────────────────────────────────────────
orders: id, user_id, user_name, user_email, 
        total, created_at, items_json

✅ Fast reads (no JOINs)
❌ Data duplication
❌ Hard to update (update in multiple places)


Rule: Normalize for writes, denormalize for reads
```

### Database Sharding

```
Vertical Sharding (by feature):
─────────────────────────────────────────────────────────
DB1: users, profiles
DB2: orders, payments
DB3: products, inventory

Horizontal Sharding (by data):
─────────────────────────────────────────────────────────
Shard 1: Users A-M
Shard 2: Users N-Z

Or by user_id % number_of_shards:
Shard 0: user_id % 3 == 0
Shard 1: user_id % 3 == 1
Shard 2: user_id % 3 == 2
```

### Database Replication

```
                    ┌─────────────┐
          Write ──► │   Primary   │
                    └──────┬──────┘
                           │ Replication
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
 Read ──│ Replica 1│ │ Replica 2│ │ Replica 3│
        └──────────┘ └──────────┘ └──────────┘

Benefits:
─────────────────────────────────────────────────────────
→ Read scaling (multiple read replicas)
→ High availability (if primary fails, promote replica)
→ Geographic distribution (replica near users)
```

---

## Microservices vs Monolith

### When to Use What?

```
Monolith (Start Here!):
─────────────────────────────────────────────────────────
✅ Simple to develop and deploy
✅ Easy debugging (one codebase)
✅ No network latency between components
✅ ACID transactions easy
❌ Scaling means scaling everything
❌ One bug can crash entire app
❌ Hard to use different technologies

Use when: Small team, new project, simple domain


Microservices:
─────────────────────────────────────────────────────────
✅ Independent scaling per service
✅ Team autonomy
✅ Technology flexibility
✅ Fault isolation
❌ Network complexity
❌ Distributed transactions hard
❌ Operational overhead
❌ Debugging across services difficult

Use when: Large team, complex domain, high scale needs
```

### Microservices Communication

```
Synchronous (HTTP/gRPC):
─────────────────────────────────────────────────────────
Order Service ──HTTP──► User Service
                       │
                       └── Get user details

✅ Simple, immediate response
❌ Tight coupling
❌ If User Service down, Order fails


Asynchronous (Message Queue):
─────────────────────────────────────────────────────────
Order Service ──publish──► [Message Queue] ──consume──► Email Service
                                          ──consume──► Analytics

✅ Loose coupling
✅ Better fault tolerance
✅ Can process later
❌ Eventual consistency
❌ More complex
```

---

## Real System Design Examples

### URL Shortener (bit.ly)

```
Requirements:
─────────────────────────────────────────────────────────
- Shorten long URLs
- Redirect to original URL
- Analytics (click count)
- 100M URLs, 1B redirects/month


Design:
─────────────────────────────────────────────────────────
           ┌────────────────────┐
    User ──│   Load Balancer    │
           └─────────┬──────────┘
                     ▼
           ┌────────────────────┐
           │   App Servers      │
           └─────────┬──────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  Redis Cache    │     │   PostgreSQL    │
│  (hot URLs)     │     │  (all URLs)     │
└─────────────────┘     └─────────────────┘


URL Shortening:
─────────────────────────────────────────────────────────
1. Generate unique ID (auto-increment or UUID)
2. Convert to Base62 (a-z, A-Z, 0-9)
3. Store: short_code → original_url

ID: 12345 → Base62: "dnh"
https://bit.ly/dnh → https://verylongurl.com/path/...


Code:
─────────────────────────────────────────────────────────
import string

CHARS = string.ascii_letters + string.digits  # 62 chars

def encode(num):
    result = []
    while num:
        result.append(CHARS[num % 62])
        num //= 62
    return ''.join(reversed(result))

def decode(s):
    num = 0
    for char in s:
        num = num * 62 + CHARS.index(char)
    return num
```

### Rate Limiter

```python
# Token Bucket Algorithm

import time
from dataclasses import dataclass

@dataclass
class TokenBucket:
    capacity: int       # Max tokens
    refill_rate: float  # Tokens per second
    tokens: float = 0
    last_refill: float = 0
    
    def allow_request(self) -> bool:
        now = time.time()
        
        # Refill tokens
        time_passed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + time_passed * self.refill_rate
        )
        self.last_refill = now
        
        # Check if request allowed
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


# Usage
limiter = TokenBucket(capacity=10, refill_rate=1)  # 10 req, 1/sec refill

for _ in range(15):
    if limiter.allow_request():
        print("Request allowed")
    else:
        print("Rate limited!")
```

### Chat System

```
Architecture:
─────────────────────────────────────────────────────────
           ┌────────────────────┐
    Users ─│   WebSocket LB     │
           └─────────┬──────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  Chat Server 1  │     │  Chat Server 2  │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
              ┌─────────────┐
              │ Redis Pub/Sub│
              └──────┬──────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   Message DB    │     │  User Service   │
│   (Cassandra)   │     │  (PostgreSQL)   │
└─────────────────┘     └─────────────────┘


Message Flow:
─────────────────────────────────────────────────────────
1. User A sends message via WebSocket
2. Chat Server 1 receives message
3. Save to Cassandra (for history)
4. Publish to Redis channel for that chat room
5. Chat Server 2 (where User B is) receives via Redis
6. Deliver to User B via WebSocket
```

---

## Interview Tips

### System Design Interview Structure

```
1. Clarify Requirements (5 min)
─────────────────────────────────────────────────────────
- Who are the users?
- How many users? (scale)
- What features are must-have vs nice-to-have?
- Read-heavy or write-heavy?

2. Estimate Scale (5 min)
─────────────────────────────────────────────────────────
- DAU (Daily Active Users)
- Requests per second
- Storage needed
- Bandwidth

3. High Level Design (10 min)
─────────────────────────────────────────────────────────
- Draw boxes and arrows
- Identify main components
- Data flow

4. Deep Dive (15 min)
─────────────────────────────────────────────────────────
- Database schema
- API design
- Specific algorithms

5. Identify Bottlenecks (5 min)
─────────────────────────────────────────────────────────
- Single points of failure
- How to scale
- Trade-offs
```

### Quick Estimation Cheat Sheet

```
Numbers to Remember:
─────────────────────────────────────────────────────────
1 day = 86,400 seconds ≈ 100,000 seconds
1 million requests/day ≈ 12 requests/second
1 billion requests/day ≈ 12,000 requests/second

Storage:
─────────────────────────────────────────────────────────
1 character = 1 byte (ASCII) or 2 bytes (Unicode)
1 KB = 1,000 bytes
1 MB = 1,000 KB
1 GB = 1,000 MB
1 TB = 1,000 GB

Typical sizes:
- Tweet: ~500 bytes
- Image: 1-5 MB
- Video (1 min): 50-100 MB
```

---

## Quick Reference

```python
# Time Complexity Quick Guide
O(1)       - Hash table lookup, array access
O(log n)   - Binary search, balanced tree
O(n)       - Linear search, single loop
O(n log n) - Efficient sorting (merge, quick)
O(n²)      - Nested loops, bubble sort

# Python Data Structure Choice
list    - Ordered, index access, duplicates OK
set     - Unique items, O(1) membership check
dict    - Key-value, O(1) lookup
deque   - Fast append/pop from both ends
heapq   - Priority queue, min/max operations
```

---

> **Pro Tip**: "Interview mein perfect solution nahi chahiye, interviewer dekhna chahte hain ki tum problem kaise approach karte ho aur trade-offs kaise consider karte ho!" 🎯
