# 16 — Background Jobs & Task Queues (Complete In-Depth Guide)

> 🎯 **Goal**: Long-running tasks ko background mein handle karo - User ko wait mat karao!

---

## 📚 Table of Contents
1. [Background Tasks Kyun?](#background-tasks-kyun)
2. [FastAPI BackgroundTasks](#fastapi-backgroundtasks)
3. [Celery Introduction](#celery-introduction)
4. [Celery with FastAPI](#celery-with-fastapi)
5. [Task Patterns](#task-patterns)
6. [Scheduling (Periodic Tasks)](#scheduling-periodic-tasks)
7. [Error Handling & Retries](#error-handling--retries)
8. [Monitoring](#monitoring)
9. [Best Practices](#best-practices)
10. [Practice Exercises](#practice-exercises)

---

## Background Tasks Kyun?

### The Problem

```python
# ❌ Without Background Tasks

@app.post("/register")
async def register_user(user: UserCreate):
    # Create user in database (fast)
    user = await create_user(user)  # 50ms ✅
    
    # Send welcome email (SLOW!)
    await send_email(user.email, "Welcome!")  # 2000ms 🐌
    
    # Generate PDF invoice (SLOW!)
    await generate_invoice(user)  # 3000ms 🐌
    
    # Sync with CRM (SLOW!)
    await sync_crm(user)  # 1000ms 🐌
    
    return user

# Total response time: 6+ seconds! 😱
# User staring at loading screen...
# Server busy with one request...
```

### The Solution

```python
# ✅ With Background Tasks

@app.post("/register")
async def register_user(user: UserCreate, background_tasks: BackgroundTasks):
    # Create user in database (fast)
    user = await create_user(user)  # 50ms ✅
    
    # Queue background tasks (instant)
    background_tasks.add_task(send_email, user.email, "Welcome!")
    background_tasks.add_task(generate_invoice, user)
    background_tasks.add_task(sync_crm, user)
    
    return user  # Immediate response! 🚀

# Response time: 50ms
# Background tasks run after response sent
# User happy, server efficient!
```

### Visual Comparison

```
Without Background Tasks:
─────────────────────────────────────────────────
Request → [DB] → [Email] → [Invoice] → [CRM] → Response
          50ms   2000ms    3000ms      1000ms
                                                Total: 6050ms

With Background Tasks:
─────────────────────────────────────────────────
Request → [DB] → Response (50ms) 🚀
               ↓
         Background: [Email] [Invoice] [CRM] (runs after response)
```

---

## FastAPI BackgroundTasks

### Basic Usage

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def write_log(message: str):
    """
    Simple background task
    
    Note: This is a regular function, not async
    FastAPI will run it in a thread pool
    """
    with open("log.txt", "a") as f:
        f.write(f"{datetime.now()}: {message}\n")

@app.post("/items/")
async def create_item(item: Item, background_tasks: BackgroundTasks):
    """
    BackgroundTasks usage:
    1. Inject BackgroundTasks as parameter
    2. Call add_task(function, *args, **kwargs)
    3. Task runs AFTER response is sent
    """
    # Do immediate work
    saved_item = await save_item(item)
    
    # Queue background task
    background_tasks.add_task(write_log, f"Created item: {item.name}")
    
    # Return immediately
    return saved_item
```

### Async Background Tasks

```python
async def send_email_async(email: str, subject: str, body: str):
    """
    Async background task
    
    FastAPI handles both sync and async background tasks
    """
    async with aiosmtplib.SMTP("smtp.gmail.com", 587) as smtp:
        await smtp.starttls()
        await smtp.login("user", "password")
        await smtp.send_message(message)

@app.post("/contact")
async def contact_us(
    message: ContactMessage,
    background_tasks: BackgroundTasks
):
    # Save message
    await save_message(message)
    
    # Send confirmation email in background
    background_tasks.add_task(
        send_email_async,
        message.email,
        "Thanks for contacting us!",
        "We'll get back to you soon."
    )
    
    return {"status": "Message received"}
```

### Multiple Background Tasks

```python
@app.post("/orders/")
async def create_order(order: OrderCreate, background_tasks: BackgroundTasks):
    """Add multiple background tasks"""
    
    # Create order
    db_order = await create_order_db(order)
    
    # Queue multiple tasks
    background_tasks.add_task(send_confirmation_email, order.user_email)
    background_tasks.add_task(notify_warehouse, db_order.id)
    background_tasks.add_task(update_analytics, "order_created")
    background_tasks.add_task(sync_inventory, order.items)
    
    # All tasks will run after response, in order added
    return db_order
```

### BackgroundTasks in Dependencies

```python
from fastapi import Depends

async def log_request(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Dependency that adds background task"""
    
    # Add logging task
    background_tasks.add_task(
        log_to_file,
        request.method,
        request.url.path,
        datetime.now()
    )

@app.get("/users/", dependencies=[Depends(log_request)])
async def get_users():
    # Log task runs after response
    return await fetch_users()
```

### When to Use FastAPI BackgroundTasks

```python
# ✅ Good for:
# - Simple, short tasks
# - Fire-and-forget operations
# - Single server deployment
# - Tasks that don't need retry/monitoring

# ❌ Not good for:
# - Long-running tasks (>30 seconds)
# - Tasks that need retries
# - Tasks that need scheduling
# - Multi-server deployments (task lost if server restarts)
# - Tasks that need monitoring/tracking
```

---

## Celery Introduction

### Celery Kya Hai?

```
Celery = Distributed Task Queue

Components:
1. Producer (your FastAPI app) - Creates tasks
2. Broker (Redis/RabbitMQ) - Stores task queue
3. Worker (Celery process) - Executes tasks
4. Backend (Redis/PostgreSQL) - Stores results

Flow:
FastAPI ──► Redis Queue ──► Celery Worker ──► Task Done
  │                              │
  └─ Continues response          └─ Stores result in Backend
```

### Why Celery over BackgroundTasks?

```
Feature                  BackgroundTasks    Celery
─────────────────────────────────────────────────────
Retry on failure         ❌                 ✅
Scheduled tasks          ❌                 ✅
Multiple workers         ❌                 ✅
Survives restart         ❌                 ✅
Task monitoring          ❌                 ✅
Result tracking          ❌                 ✅
Rate limiting            ❌                 ✅
Priority queues          ❌                 ✅
Distributed             ❌                 ✅
Setup complexity         Low               Medium
```

### Installation

```bash
pip install celery
pip install redis  # For broker and backend
# or
pip install celery[redis]  # Celery with Redis support
```

---

## Celery with FastAPI

### Project Structure

```
project/
├── app/
│   ├── main.py           # FastAPI app
│   ├── celery_app.py     # Celery configuration
│   └── tasks.py          # Task definitions
├── requirements.txt
└── docker-compose.yml    # Redis + Celery workers
```

### Celery Configuration

```python
# app/celery_app.py
from celery import Celery

# Create Celery instance
celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",  # Task queue
    backend="redis://localhost:6379/1", # Result storage
)

# Configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task expiration
    task_soft_time_limit=60,   # Warning after 60s
    task_time_limit=120,       # Kill after 120s
    result_expires=3600,       # Results expire after 1 hour
    
    # Retry settings
    task_acks_late=True,       # Acknowledge after completion
    task_reject_on_worker_lost=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,  # One task at a time per worker
    worker_concurrency=4,          # 4 parallel workers
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
```

### Task Definitions

```python
# app/tasks.py
from celery import shared_task
from app.celery_app import celery_app
import time

@celery_app.task(name="send_email")
def send_email_task(to: str, subject: str, body: str):
    """
    Email sending task
    
    @celery_app.task = Register as Celery task
    name = Task identifier
    """
    # Simulate email sending
    time.sleep(2)  # SMTP connection, etc.
    
    print(f"Email sent to {to}: {subject}")
    return {"status": "sent", "to": to}


@celery_app.task(
    name="generate_report",
    bind=True,  # Access task instance
    max_retries=3,
    default_retry_delay=60,
)
def generate_report_task(self, report_type: str, user_id: int):
    """
    Complex task with retry logic
    
    bind=True: First argument is task instance (self)
    """
    try:
        # Long-running operation
        report = create_report(report_type, user_id)
        
        # Update progress (optional)
        self.update_state(state="PROCESSING", meta={"progress": 50})
        
        # More work
        save_report(report)
        
        return {"report_id": report.id, "status": "completed"}
        
    except TransientError as e:
        # Retry on transient errors
        raise self.retry(exc=e, countdown=60)
    
    except PermanentError as e:
        # Don't retry, just fail
        return {"status": "failed", "error": str(e)}


@celery_app.task(name="cleanup_old_files")
def cleanup_old_files_task():
    """Periodic cleanup task"""
    deleted_count = 0
    for file in get_old_files():
        delete_file(file)
        deleted_count += 1
    return {"deleted": deleted_count}
```

### Using Tasks in FastAPI

```python
# app/main.py
from fastapi import FastAPI
from app.tasks import send_email_task, generate_report_task

app = FastAPI()

@app.post("/register")
async def register(user: UserCreate):
    # Create user
    db_user = await create_user(user)
    
    # Queue email task (returns immediately!)
    task = send_email_task.delay(
        to=user.email,
        subject="Welcome!",
        body="Thanks for registering."
    )
    
    # task.id = unique task identifier
    # Can use to check status later
    
    return {
        "user": db_user,
        "email_task_id": task.id
    }


@app.post("/reports/")
async def create_report(report_type: str, user: User = Depends(get_current_user)):
    # Queue report generation
    task = generate_report_task.delay(
        report_type=report_type,
        user_id=user.id
    )
    
    return {
        "message": "Report generation started",
        "task_id": task.id
    }


@app.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Check task status"""
    from celery.result import AsyncResult
    
    result = AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": result.status,  # PENDING, STARTED, SUCCESS, FAILURE
        "result": result.result if result.ready() else None,
    }
```

### Running Celery Worker

```bash
# Start Celery worker
celery -A app.celery_app worker --loglevel=info

# Output:
# [2024-01-15 10:00:00] worker@hostname ready.
# [2024-01-15 10:00:05] Received task: send_email[abc123]
# [2024-01-15 10:00:07] Task send_email[abc123] succeeded

# Multiple workers (production)
celery -A app.celery_app worker --loglevel=info --concurrency=4

# With specific queue
celery -A app.celery_app worker -Q emails,reports --loglevel=info
```

---

## Task Patterns

### Pattern 1: Task Chaining

```python
from celery import chain

@celery_app.task
def step1(data):
    return process_step1(data)

@celery_app.task
def step2(result):
    return process_step2(result)

@celery_app.task
def step3(result):
    return finalize(result)

# Chain tasks: step1 → step2 → step3
# Each task receives result of previous
@app.post("/process")
async def process_data(data: ProcessRequest):
    workflow = chain(
        step1.s(data.dict()),
        step2.s(),
        step3.s()
    )
    result = workflow.apply_async()
    return {"workflow_id": result.id}
```

### Pattern 2: Parallel Execution (Group)

```python
from celery import group

@celery_app.task
def send_notification(user_id: int, message: str):
    # Send notification
    pass

@app.post("/broadcast")
async def broadcast_message(message: str, user_ids: list[int]):
    """Send notification to all users in parallel"""
    
    job = group(
        send_notification.s(user_id, message)
        for user_id in user_ids
    )
    
    result = job.apply_async()
    return {"group_id": result.id, "count": len(user_ids)}
```

### Pattern 3: Chord (Parallel + Callback)

```python
from celery import chord

@celery_app.task
def process_item(item_id: int):
    return calculate_value(item_id)

@celery_app.task
def aggregate_results(results: list):
    return sum(results)

@app.post("/calculate")
async def calculate_total(item_ids: list[int]):
    """
    Process all items in parallel,
    then aggregate results
    """
    workflow = chord(
        [process_item.s(item_id) for item_id in item_ids],
        aggregate_results.s()  # Callback receives list of results
    )
    
    result = workflow.apply_async()
    return {"chord_id": result.id}
```

### Pattern 4: Priority Queues

```python
# celery_app.py
celery_app.conf.task_routes = {
    "app.tasks.urgent_*": {"queue": "high_priority"},
    "app.tasks.normal_*": {"queue": "default"},
    "app.tasks.batch_*": {"queue": "low_priority"},
}

# Or per-task
@celery_app.task(queue="high_priority")
def urgent_task():
    pass

# Start workers for different queues
# celery -A app.celery_app worker -Q high_priority --concurrency=4
# celery -A app.celery_app worker -Q default --concurrency=2
# celery -A app.celery_app worker -Q low_priority --concurrency=1
```

---

## Scheduling (Periodic Tasks)

### Celery Beat

```python
# celery_app.py
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    # Run every minute
    "cleanup-every-minute": {
        "task": "app.tasks.cleanup_old_files",
        "schedule": 60.0,  # seconds
    },
    
    # Run every hour
    "hourly-report": {
        "task": "app.tasks.generate_hourly_report",
        "schedule": crontab(minute=0),  # Every hour at :00
    },
    
    # Run daily at midnight
    "daily-backup": {
        "task": "app.tasks.backup_database",
        "schedule": crontab(hour=0, minute=0),
    },
    
    # Run every Monday at 9 AM
    "weekly-digest": {
        "task": "app.tasks.send_weekly_digest",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),
    },
    
    # Run on 1st of every month
    "monthly-invoice": {
        "task": "app.tasks.generate_invoices",
        "schedule": crontab(day_of_month=1, hour=6, minute=0),
    },
}
```

### Crontab Examples

```python
from celery.schedules import crontab

# Every minute
crontab()

# Every 15 minutes
crontab(minute="*/15")

# Every hour at :30
crontab(minute=30)

# Every day at midnight
crontab(hour=0, minute=0)

# Every Monday at 9 AM
crontab(hour=9, minute=0, day_of_week=1)

# Every weekday at 8 AM
crontab(hour=8, minute=0, day_of_week="mon-fri")

# First day of month at 6 AM
crontab(day_of_month=1, hour=6, minute=0)
```

### Running Celery Beat

```bash
# Start scheduler (separate from workers!)
celery -A app.celery_app beat --loglevel=info

# Or combined with worker (development only)
celery -A app.celery_app worker --beat --loglevel=info
```

---

## Error Handling & Retries

### Automatic Retries

```python
@celery_app.task(
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError),  # Auto-retry these
    retry_kwargs={"max_retries": 5, "countdown": 60},
    retry_backoff=True,  # Exponential backoff
    retry_backoff_max=600,  # Max 10 minutes between retries
    retry_jitter=True,  # Random jitter to prevent thundering herd
)
def unreliable_task(self, data):
    """
    Task with automatic retry on specific errors
    
    Retry timeline (with backoff):
    1st retry: ~60 seconds
    2nd retry: ~120 seconds
    3rd retry: ~240 seconds
    ...
    """
    response = call_external_api(data)
    return response
```

### Manual Retry

```python
@celery_app.task(bind=True, max_retries=3)
def task_with_manual_retry(self, data):
    try:
        result = process_data(data)
        return result
    except TransientError as e:
        # Retry after 5 minutes
        raise self.retry(exc=e, countdown=300)
    except PermanentError as e:
        # Don't retry, just log and fail
        logger.error(f"Permanent error: {e}")
        raise
```

### Error Callbacks

```python
@celery_app.task
def success_handler(result):
    print(f"Task succeeded with result: {result}")

@celery_app.task
def error_handler(request, exc, traceback):
    print(f"Task {request.id} failed: {exc}")
    # Send alert, log to monitoring, etc.

# Apply callbacks
task = send_email_task.apply_async(
    args=["user@example.com", "Subject", "Body"],
    link=success_handler.s(),       # On success
    link_error=error_handler.s(),   # On error
)
```

---

## Monitoring

### Flower (Web UI)

```bash
# Install
pip install flower

# Run
celery -A app.celery_app flower --port=5555

# Open http://localhost:5555
# See:
# - Active workers
# - Task history
# - Task details
# - Queue lengths
# - Worker stats
```

### Programmatic Monitoring

```python
from celery import current_app

def get_celery_stats():
    """Get Celery worker stats"""
    inspect = current_app.control.inspect()
    
    return {
        "active": inspect.active(),      # Currently running tasks
        "scheduled": inspect.scheduled(), # Scheduled tasks
        "reserved": inspect.reserved(),   # Tasks received but not started
        "registered": inspect.registered(), # Registered task names
        "stats": inspect.stats(),         # Worker statistics
    }

@app.get("/admin/celery/stats")
async def celery_stats():
    return get_celery_stats()
```

### Health Check

```python
@app.get("/health/celery")
async def celery_health():
    """Check if Celery is healthy"""
    from celery import current_app
    
    try:
        # Ping workers
        inspect = current_app.control.inspect()
        workers = inspect.ping()
        
        if not workers:
            return {"status": "unhealthy", "error": "No workers responding"}
        
        return {
            "status": "healthy",
            "workers": list(workers.keys())
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

---

## Best Practices

### 1. Keep Tasks Idempotent

```python
# Idempotent = Running multiple times gives same result

# ❌ BAD - Not idempotent
@celery_app.task
def add_credits(user_id: int, amount: int):
    user = get_user(user_id)
    user.credits += amount  # Running twice = double credits!
    save_user(user)

# ✅ GOOD - Idempotent
@celery_app.task
def set_credits(user_id: int, transaction_id: str, amount: int):
    # Check if already processed
    if is_transaction_processed(transaction_id):
        return  # Already done, skip
    
    # Process and mark as done
    user = get_user(user_id)
    user.credits += amount
    save_user(user)
    mark_transaction_processed(transaction_id)
```

### 2. Use Task IDs for Deduplication

```python
@app.post("/send-email")
async def send_email(request: EmailRequest):
    # Create unique task ID based on content
    task_id = f"email:{request.to}:{hash(request.subject)}"
    
    # Check if already queued
    if task_id_exists(task_id):
        return {"message": "Already queued"}
    
    # Queue with specific ID
    send_email_task.apply_async(
        args=[request.to, request.subject, request.body],
        task_id=task_id
    )
```

### 3. Set Timeouts

```python
@celery_app.task(
    soft_time_limit=300,  # Warning after 5 min
    time_limit=360,       # Kill after 6 min
)
def long_running_task():
    try:
        do_work()
    except SoftTimeLimitExceeded:
        # Cleanup and save progress
        save_progress()
        raise
```

### 4. Proper Serialization

```python
# Always serialize to JSON-safe format

# ❌ BAD - Passing ORM objects
@celery_app.task
def process_user(user: User):  # SQLAlchemy object
    pass

# ✅ GOOD - Pass primitive types
@celery_app.task
def process_user(user_id: int):  # Just the ID
    user = get_user(user_id)  # Fetch fresh data in task
    pass
```

---

## Practice Exercises

### Exercise 1: Email Queue
```python
# Create email sending with:
# - FastAPI endpoint to queue email
# - Celery task with retry logic
# - Priority queue for urgent emails
```

### Exercise 2: Report Generator
```python
# Create report generation:
# - Queue report task
# - Track progress (0%, 50%, 100%)
# - Notify user when complete
```

### Exercise 3: Scheduled Cleanup
```python
# Create cleanup job:
# - Delete files older than 7 days
# - Run daily at 3 AM
# - Log deleted files count
```

---

## Quick Reference

```python
# FastAPI BackgroundTasks
@app.post("/")
async def endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(func, arg1, arg2)
    return response

# Celery Task
@celery_app.task
def my_task(arg):
    return result

# Call task
my_task.delay(arg)  # Simple
my_task.apply_async(args=[arg], countdown=60)  # With options

# Check status
from celery.result import AsyncResult
result = AsyncResult(task_id)
result.status  # PENDING, STARTED, SUCCESS, FAILURE
result.result  # Return value

# Run worker
celery -A app.celery_app worker --loglevel=info

# Run scheduler
celery -A app.celery_app beat --loglevel=info
```

---

> **Pro Tip**: "User ko wait mat karao - jo bhi background mein ho sakta hai, background mein karo!" 🚀
