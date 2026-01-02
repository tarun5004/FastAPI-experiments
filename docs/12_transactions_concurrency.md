# 12 — Transactions & Concurrency (Complete In-Depth Guide)

> 🎯 **Goal**: Database transactions aur concurrency problems master karo - data corruption se bachao!

---

## 📚 Table of Contents
1. [Transaction Kya Hai?](#transaction-kya-hai)
2. [ACID Properties](#acid-properties)
3. [Transaction Management](#transaction-management)
4. [Concurrency Problems](#concurrency-problems)
5. [Isolation Levels](#isolation-levels)
6. [Locking Strategies](#locking-strategies)
7. [Optimistic vs Pessimistic](#optimistic-vs-pessimistic)
8. [Deadlocks](#deadlocks)
9. [Best Practices](#best-practices)
10. [Practice Exercises](#practice-exercises)

---

## Transaction Kya Hai?

### Real-Life Example Se Samjho

```
Bank Transfer: ₹1000 transfer karo A se B ko

Step 1: A ke account se ₹1000 minus karo
Step 2: B ke account mein ₹1000 plus karo

❓ Kya hoga agar Step 1 complete ho gaya, but Step 2 fail?
- A ke paas ₹1000 kam ho gaye
- B ke paas paisa nahi aaya
- ₹1000 GAYAB! 💸

✅ Transaction Solution:
- EITHER both steps succeed
- OR both steps fail (rollback)
- Never partial!
```

### Database Transaction

```python
# Transaction = Group of operations as ONE unit

# Without Transaction (DANGEROUS!)
db.execute("UPDATE accounts SET balance = balance - 1000 WHERE id = 1")
# ⚡ CRASH HERE!
db.execute("UPDATE accounts SET balance = balance + 1000 WHERE id = 2")
# First update done, second not = DATA CORRUPTED!

# With Transaction (SAFE!)
try:
    db.begin()  # Transaction start
    db.execute("UPDATE accounts SET balance = balance - 1000 WHERE id = 1")
    db.execute("UPDATE accounts SET balance = balance + 1000 WHERE id = 2")
    db.commit()  # All success = save permanently
except Exception:
    db.rollback()  # Any error = undo everything
```

### Visual Representation

```
Transaction Timeline:
─────────────────────────────────────────────────
BEGIN       Operation 1    Operation 2    COMMIT
  │              │              │           │
  ▼              ▼              ▼           ▼
Start ──────► Work ──────► Work ──────► Save!
              (pending)     (pending)    (permanent)

Error at any point:
─────────────────────────────────────────────────
BEGIN       Operation 1    ERROR!     ROLLBACK
  │              │           │            │
  ▼              ▼           ▼            ▼
Start ──────► Work ──────► ❌ ──────► Undo All!
              (pending)              (back to start)
```

---

## ACID Properties

### A - Atomicity (All or Nothing)

```python
# Atomicity = Sab kuch ya kuch nahi

async def transfer_money(db, from_id, to_id, amount):
    """
    Atomic operation - dono updates ek saath
    
    Success: Dono accounts update
    Fail: Koi account update nahi
    """
    try:
        # Deduct from sender
        sender = await db.execute(
            update(Account)
            .where(Account.id == from_id)
            .values(balance=Account.balance - amount)
        )
        
        # Check if sender had enough balance
        if sender.rowcount == 0:
            raise ValueError("Sender not found")
        
        # Add to receiver
        receiver = await db.execute(
            update(Account)
            .where(Account.id == to_id)
            .values(balance=Account.balance + amount)
        )
        
        if receiver.rowcount == 0:
            raise ValueError("Receiver not found")
        
        await db.commit()  # ✅ Both done = permanent
        
    except Exception as e:
        await db.rollback()  # ❌ Any error = undo both
        raise e
```

### C - Consistency (Valid State to Valid State)

```python
# Consistency = Database rules hamesha follow honge

# Example: Balance never negative
class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    balance = Column(Integer, nullable=False)
    
    # Database level constraint
    __table_args__ = (
        CheckConstraint('balance >= 0', name='positive_balance'),
    )

# Agar transfer ke baad balance negative hoga:
# Transaction FAIL hogi = Consistency maintained!

# Before: Account A has ₹500
# Try to transfer ₹1000
# Database will reject because balance would be -500
# Consistency preserved!
```

### I - Isolation (Transactions Don't Interfere)

```python
# Isolation = Ek transaction doosre ko affect na kare

# Scenario: 2 users same time pe same account access kar rahe

# User 1                    # User 2
# Balance = ₹1000          # Balance = ₹1000
# Withdraw ₹500            # Withdraw ₹500
# New Balance = ₹500       # New Balance = ₹500
# 
# Expected final: ₹0
# Without isolation: ₹500 (wrong!)
# With proper isolation: ₹0 (correct!)

# Database ensures each transaction sees consistent view
```

### D - Durability (Permanent After Commit)

```python
# Durability = Commit ke baad data permanent

await db.commit()  # Data saved to disk
# Even if:
# - Server crashes
# - Power fails
# - Network goes down
# Data is SAFE because it's written to disk before commit confirms

# How? Write-Ahead Logging (WAL)
# 1. Changes written to log file first
# 2. Then applied to database
# 3. If crash, replay log on restart
```

---

## Transaction Management

### SQLAlchemy Transaction Patterns

#### Pattern 1: Auto-commit with Session

```python
# SQLAlchemy default: autocommit=False
# You manually commit or rollback

async def create_user(db: AsyncSession, user_data):
    user = User(**user_data)
    db.add(user)
    await db.commit()  # Explicit commit
    return user
```

#### Pattern 2: Context Manager

```python
# Automatic commit/rollback with context manager

async def transfer_with_context(from_id, to_id, amount):
    async with async_session() as session:
        async with session.begin():  # Auto-commit on success
            await session.execute(
                update(Account)
                .where(Account.id == from_id)
                .values(balance=Account.balance - amount)
            )
            await session.execute(
                update(Account)
                .where(Account.id == to_id)
                .values(balance=Account.balance + amount)
            )
        # Exiting `begin()` context = auto-commit
    # Exiting `session` context = auto-close
```

#### Pattern 3: Savepoints (Nested Transactions)

```python
async def complex_operation(db: AsyncSession):
    """
    Savepoint = Checkpoint within transaction
    
    Outer fails → All rolled back
    Inner fails → Only inner rolled back, continue outer
    """
    try:
        # Outer transaction
        user = User(email="test@test.com")
        db.add(user)
        await db.flush()  # Get user ID without committing
        
        # Savepoint (nested transaction)
        async with db.begin_nested() as savepoint:
            try:
                # Try to create profile
                profile = Profile(user_id=user.id, bio="Hello")
                db.add(profile)
                await db.flush()
                
                # Something went wrong!
                if not valid_profile:
                    raise ValueError("Invalid profile")
                    
            except ValueError:
                # Rollback only profile, keep user
                await savepoint.rollback()
                # Profile creation failed, but user is still pending
        
        # Continue with user (profile creation failed but user saved)
        await db.commit()
        
    except Exception:
        await db.rollback()
        raise
```

**Savepoint Visual:**

```
Transaction Start
     │
     ├── Create User (pending)
     │
     ├── SAVEPOINT ─┐
     │              │
     │              ├── Create Profile (pending)
     │              │
     │              ├── Error! ───► ROLLBACK TO SAVEPOINT
     │              │                (Profile undone, User still there)
     │              └─┘
     │
     ├── Create Other Stuff (pending)
     │
     └── COMMIT (User + Other saved, Profile not)
```

---

## Concurrency Problems

### Problem 1: Dirty Read

```python
# Dirty Read = Uncommitted data padhna

# Transaction 1              # Transaction 2
# Balance = ₹1000
#
# UPDATE balance = 500
# (not committed yet!)
#                            # SELECT balance
#                            # Returns ₹500 (dirty!)
#
# ROLLBACK!
# Balance back to ₹1000
#                            # Transaction 2 used wrong value!

# Result: Transaction 2 made decisions based on data that never existed!
```

### Problem 2: Non-Repeatable Read

```python
# Non-Repeatable Read = Same query, different results

# Transaction 1              # Transaction 2
# 
# SELECT balance
# Returns ₹1000
#                            # UPDATE balance = 500
#                            # COMMIT
#
# SELECT balance (again!)
# Returns ₹500 😱
#
# Same query, different answer within same transaction!
```

### Problem 3: Phantom Read

```python
# Phantom Read = New rows appear/disappear

# Transaction 1              # Transaction 2
#
# SELECT * WHERE status='active'
# Returns [User1, User2]
#                            # INSERT User3 (status='active')
#                            # COMMIT
#
# SELECT * WHERE status='active' (again!)
# Returns [User1, User2, User3]
#
# New "phantom" row appeared!
```

### Problem 4: Lost Update

```python
# Lost Update = Two transactions overwrite each other

# Initial: Balance = ₹1000

# Transaction 1              # Transaction 2
#
# Read Balance = ₹1000
#                            # Read Balance = ₹1000
#
# Calculate new = 1000 + 100
#                            # Calculate new = 1000 + 200
#
# Write Balance = ₹1100
#                            # Write Balance = ₹1200
#                            # (Overwrites T1's update!)
#
# Expected: ₹1300 (1000 + 100 + 200)
# Actual: ₹1200 (T1's update lost!)
```

---

## Isolation Levels

### 4 Standard Isolation Levels

```
Level               Dirty Read   Non-Repeatable   Phantom Read
───────────────────────────────────────────────────────────────
READ UNCOMMITTED    Possible     Possible         Possible
READ COMMITTED      ✗ No         Possible         Possible
REPEATABLE READ     ✗ No         ✗ No             Possible
SERIALIZABLE        ✗ No         ✗ No             ✗ No

Lower → Faster but less safe
Higher → Slower but more safe
```

### Setting Isolation Level

```python
# SQLAlchemy mein isolation level set karo

from sqlalchemy import create_engine

# Engine level (global)
engine = create_engine(
    DATABASE_URL,
    isolation_level="REPEATABLE READ"
)

# Connection level (per connection)
async with engine.connect() as conn:
    await conn.execution_options(isolation_level="SERIALIZABLE")
    # This connection uses SERIALIZABLE
```

### PostgreSQL Specific

```python
# PostgreSQL default: READ COMMITTED (safe for most cases)

# For critical operations:
from sqlalchemy import text

async def critical_operation(db: AsyncSession):
    # Set isolation for this transaction
    await db.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
    
    # Now do critical work
    # ...
```

### When to Use Which?

```python
# READ COMMITTED (default, most common)
# Use for: Normal CRUD operations
# Fast, good enough for most apps

# REPEATABLE READ
# Use for: Reports, analytics
# When you need consistent snapshot

# SERIALIZABLE
# Use for: Financial transactions, inventory
# When correctness > performance
```

---

## Locking Strategies

### Row-Level Locks

```python
from sqlalchemy import select

# SELECT FOR UPDATE = Lock rows for modification
async def withdraw_with_lock(db: AsyncSession, account_id: int, amount: int):
    """
    FOR UPDATE = "Main yeh row modify karunga, koi touch mat karo!"
    
    Doosre transactions wait karenge jab tak lock release na ho
    """
    # Lock the row
    query = (
        select(Account)
        .where(Account.id == account_id)
        .with_for_update()  # ⭐ Lock this row!
    )
    
    result = await db.execute(query)
    account = result.scalars().first()
    
    if not account:
        raise ValueError("Account not found")
    
    if account.balance < amount:
        raise ValueError("Insufficient balance")
    
    # Update (still locked)
    account.balance -= amount
    
    await db.commit()  # Lock released here!
    return account
```

### Lock Types

```python
# 1. FOR UPDATE - Exclusive lock
# No one else can read or write
query.with_for_update()

# 2. FOR UPDATE NOWAIT - Don't wait for lock
# If locked, raise error immediately
query.with_for_update(nowait=True)

# 3. FOR UPDATE SKIP LOCKED - Skip locked rows
# Process unlocked rows, skip locked ones
# Good for job queues
query.with_for_update(skip_locked=True)

# 4. FOR SHARE - Shared lock (read lock)
# Others can read but not write
query.with_for_update(read=True)
```

### Practical Example: Job Queue

```python
async def get_next_job(db: AsyncSession):
    """
    Job queue with SKIP LOCKED
    
    Multiple workers can run simultaneously
    Each picks different job (no conflicts!)
    """
    query = (
        select(Job)
        .where(Job.status == "pending")
        .order_by(Job.created_at)
        .limit(1)
        .with_for_update(skip_locked=True)  # Skip if another worker has it
    )
    
    result = await db.execute(query)
    job = result.scalars().first()
    
    if job:
        job.status = "processing"
        job.started_at = datetime.utcnow()
        await db.commit()
    
    return job
```

---

## Optimistic vs Pessimistic Locking

### Pessimistic Locking (Lock First)

```python
# Pessimistic = "Conflict hoga, lock karlo pehle se"
# Use FOR UPDATE

async def update_with_pessimistic_lock(db, product_id, new_stock):
    """
    Pessimistic: Lock row before reading
    
    Pros: Guaranteed no conflict
    Cons: Blocks other transactions (slower)
    """
    # Lock immediately
    query = select(Product).where(Product.id == product_id).with_for_update()
    result = await db.execute(query)
    product = result.scalars().first()
    
    # Safe to update (locked)
    product.stock = new_stock
    await db.commit()
```

### Optimistic Locking (Check Later)

```python
# Optimistic = "Conflict nahi hoga, but check kar lenge"
# Use version column

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    stock = Column(Integer)
    version = Column(Integer, default=1)  # ⭐ Version column!


async def update_with_optimistic_lock(db, product_id, new_stock, expected_version):
    """
    Optimistic: Check version at update time
    
    Pros: No blocking, high concurrency
    Cons: Need retry logic
    """
    query = (
        update(Product)
        .where(
            Product.id == product_id,
            Product.version == expected_version  # ⭐ Version check!
        )
        .values(
            stock=new_stock,
            version=Product.version + 1  # ⭐ Increment version!
        )
    )
    
    result = await db.execute(query)
    
    if result.rowcount == 0:
        # Version mismatch = someone else updated
        raise OptimisticLockError("Conflict! Please retry.")
    
    await db.commit()


# Usage with retry
async def update_product_stock_safe(db, product_id, new_stock, max_retries=3):
    """Retry on conflict"""
    for attempt in range(max_retries):
        try:
            # Get current version
            product = await db.execute(
                select(Product).where(Product.id == product_id)
            )
            product = product.scalars().first()
            
            # Try update with version check
            await update_with_optimistic_lock(
                db, product_id, new_stock, product.version
            )
            return  # Success!
            
        except OptimisticLockError:
            if attempt == max_retries - 1:
                raise  # Give up after max retries
            await asyncio.sleep(0.1)  # Brief pause before retry
```

### When to Use Which?

```
Pessimistic Locking:
├── High conflict scenarios (many users updating same row)
├── Short transactions (quick lock-unlock)
├── Financial/critical operations
└── Example: Bank transfers, inventory deduction

Optimistic Locking:
├── Low conflict scenarios (rare updates to same row)
├── Long transactions (reading, calculating)
├── High read, low write workloads
└── Example: Wiki edits, document updates
```

---

## Deadlocks

### What is Deadlock?

```
Deadlock = Do transactions ek doosre ka wait kar rahe

Transaction 1           Transaction 2
─────────────          ─────────────
Lock Row A ✓           Lock Row B ✓
Want Row B ⏳           Want Row A ⏳
(T2 has it!)           (T1 has it!)
     │                       │
     └───── WAITING ─────────┘
            FOREVER! 🔒

Neither can proceed = Deadlock!
```

### Deadlock Example

```python
# ❌ Deadlock prone code

# Transaction 1
async def transfer_1_to_2(db, amount):
    # Lock account 1 first
    acc1 = await db.execute(select(Account).where(Account.id == 1).with_for_update())
    await asyncio.sleep(0.1)  # Simulate some work
    # Try to lock account 2
    acc2 = await db.execute(select(Account).where(Account.id == 2).with_for_update())
    # ... transfer ...

# Transaction 2 (running simultaneously)
async def transfer_2_to_1(db, amount):
    # Lock account 2 first
    acc2 = await db.execute(select(Account).where(Account.id == 2).with_for_update())
    await asyncio.sleep(0.1)  # Simulate some work
    # Try to lock account 1  ← DEADLOCK!
    acc1 = await db.execute(select(Account).where(Account.id == 1).with_for_update())
    # ... transfer ...
```

### Deadlock Prevention

```python
# ✅ Solution 1: Consistent lock ordering

async def safe_transfer(db, from_id, to_id, amount):
    """
    Always lock in same order (lower ID first)
    
    This prevents circular wait!
    """
    # Sort IDs to ensure consistent order
    first_id, second_id = min(from_id, to_id), max(from_id, to_id)
    
    # Lock in consistent order
    first_acc = await db.execute(
        select(Account).where(Account.id == first_id).with_for_update()
    )
    second_acc = await db.execute(
        select(Account).where(Account.id == second_id).with_for_update()
    )
    
    # Now safely transfer
    # ...


# ✅ Solution 2: Lock timeout

async def transfer_with_timeout(db, from_id, to_id, amount):
    """Use NOWAIT or timeout to fail fast"""
    try:
        from_acc = await db.execute(
            select(Account)
            .where(Account.id == from_id)
            .with_for_update(nowait=True)  # Don't wait!
        )
    except Exception as e:
        # Lock not available, retry later
        raise RetryError("Please try again")


# ✅ Solution 3: Retry with exponential backoff

async def transfer_with_retry(from_id, to_id, amount, max_retries=3):
    """Retry on deadlock"""
    for attempt in range(max_retries):
        try:
            async with async_session() as db:
                await do_transfer(db, from_id, to_id, amount)
                return  # Success!
        except DeadlockError:
            if attempt == max_retries - 1:
                raise
            # Exponential backoff
            await asyncio.sleep(0.1 * (2 ** attempt))
```

---

## Best Practices

### 1. Keep Transactions Short

```python
# ❌ BAD - Long transaction
async def process_order(db, order_id):
    order = await get_order(db, order_id)
    
    await send_email(order.user)  # Takes 2 seconds!
    await update_inventory(db, order)
    await create_invoice(db, order)
    
    await db.commit()  # Transaction open for 2+ seconds!

# ✅ GOOD - Short transaction
async def process_order(db, order_id):
    # Quick database work
    order = await get_order(db, order_id)
    await update_inventory(db, order)
    await create_invoice(db, order)
    await db.commit()  # Done!
    
    # Slow work outside transaction
    await send_email(order.user)
```

### 2. Handle Errors Properly

```python
async def safe_operation(db: AsyncSession):
    """Always commit or rollback"""
    try:
        db.add(something)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise DuplicateError("Already exists")
    except Exception:
        await db.rollback()
        raise
```

### 3. Use Appropriate Isolation Level

```python
# Default (READ COMMITTED) for most operations
# SERIALIZABLE only for critical sections

async def critical_financial_operation(db):
    await db.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
    # Critical work here
    await db.commit()
```

### 4. Avoid Holding Locks During External Calls

```python
# ❌ BAD
async def bad_pattern(db):
    row = await db.execute(select(X).with_for_update())
    await external_api_call()  # 5 second delay, lock held!
    await db.commit()

# ✅ GOOD  
async def good_pattern(db):
    row = await db.execute(select(X))
    await external_api_call()  # No lock yet
    
    # Now lock and update
    row = await db.execute(select(X).with_for_update())
    row.status = "done"
    await db.commit()
```

---

## Practice Exercises

### Exercise 1: Safe Transfer
```python
# Implement money transfer:
# - Atomic (all or nothing)
# - Handle insufficient balance
# - Prevent negative balance
# - Use proper locking
```

### Exercise 2: Inventory System
```python
# Implement product purchase:
# - Check stock availability
# - Deduct stock
# - Create order
# - Handle concurrent purchases
# - Use optimistic locking
```

### Exercise 3: Job Queue
```python
# Implement job queue:
# - Multiple workers
# - SKIP LOCKED pattern
# - Retry failed jobs
# - Prevent duplicate processing
```

---

## Quick Reference

```python
# Transaction
try:
    db.add(obj)
    await db.commit()
except:
    await db.rollback()

# Savepoint
async with db.begin_nested():
    # nested work

# Row lock
select(X).with_for_update()
select(X).with_for_update(nowait=True)
select(X).with_for_update(skip_locked=True)

# Isolation level
engine = create_engine(url, isolation_level="REPEATABLE READ")

# Optimistic lock
.where(X.version == expected_version)
.values(version=X.version + 1)
```

---

> **Pro Tip**: Jab bhi concurrent access ho, sochlo - "Kya hoga agar do users ek saath yeh kare?" 🤔
