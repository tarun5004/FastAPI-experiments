# 21 — Monitoring & Logging (Complete In-Depth Guide)

> 🎯 **Goal**: Production mein problems detect karo before users complain!

---

## 📚 Table of Contents
1. [Monitoring & Logging Kyun?](#monitoring--logging-kyun)
2. [Structured Logging](#structured-logging)
3. [Request Logging](#request-logging)
4. [Metrics with Prometheus](#metrics-with-prometheus)
5. [Visualization with Grafana](#visualization-with-grafana)
6. [Error Tracking (Sentry)](#error-tracking-sentry)
7. [Distributed Tracing](#distributed-tracing)
8. [Health Checks](#health-checks)
9. [Alerting](#alerting)
10. [Best Practices](#best-practices)

---

## Monitoring & Logging Kyun?

### The Problem

```
Without Monitoring:
─────────────────────────────────────────────────────────
User: "App bahut slow hai!"
You: "Hmm, mujhe toh sab theek lag raha hai..."
User: "Error aa raha hai!"
You: "Kab? Kya error? Kaise reproduce karoon?"
User: "Pata nahi, bas kaam nahi kar raha"
You: 😰

Result: Hours of debugging with no clue


With Monitoring:
─────────────────────────────────────────────────────────
Alert: "API response time > 2 seconds!"
You: Check dashboard → Database queries slow
You: Check logs → N+1 query detected
You: Fix query → Problem solved in 10 minutes!

User didn't even notice! 🎉
```

### The Three Pillars of Observability

```
1. LOGS (What happened?)
─────────────────────────────────────────────────────────
   Detailed record of events
   "User 123 logged in at 10:30:45"
   "Error: Database connection failed"


2. METRICS (How much/many?)
─────────────────────────────────────────────────────────
   Numeric measurements over time
   "Response time: 150ms"
   "Active users: 1250"
   "Error rate: 0.5%"


3. TRACES (Where did it go?)
─────────────────────────────────────────────────────────
   Request journey through services
   "Request → API Gateway → Auth → Database → Cache → Response"
   "Time spent in each service"
```

---

## Structured Logging

### Why Structured Logging?

```
Unstructured Log (Bad):
─────────────────────────────────────────────────────────
User 123 created order #456 for $99.99 at 2024-01-15 10:30:45

Hard to parse! How to search orders > $100?


Structured Log (Good):
─────────────────────────────────────────────────────────
{
    "timestamp": "2024-01-15T10:30:45Z",
    "level": "INFO",
    "event": "order_created",
    "user_id": 123,
    "order_id": 456,
    "amount": 99.99,
    "currency": "USD"
}

Easy to query: WHERE amount > 100
```

### Python Logging Setup

```python
# logging_config.py
import logging
import sys
from datetime import datetime
import json

class JSONFormatter(logging.Formatter):
    """
    Format logs as JSON for structured logging
    
    Why JSON?
    - Easy to parse by log aggregators (ELK, Datadog)
    - Searchable fields
    - Consistent format
    """
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


def setup_logging():
    """Configure logging for the application"""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler with JSON format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # File handler for production
    # file_handler = logging.FileHandler("app.log")
    # file_handler.setFormatter(JSONFormatter())
    # logger.addHandler(file_handler)
    
    return logger


# Usage
logger = setup_logging()

logger.info("User logged in", extra={"extra_data": {"user_id": 123}})
# Output: {"timestamp": "2024-01-15T10:30:45", "level": "INFO", "message": "User logged in", "user_id": 123}
```

### Using structlog (Recommended)

```python
# pip install structlog

import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Get logger
logger = structlog.get_logger()

# Log with context
logger.info(
    "order_created",
    user_id=123,
    order_id=456,
    amount=99.99
)
# Output: {"event": "order_created", "user_id": 123, "order_id": 456, "amount": 99.99, "timestamp": "2024-01-15T10:30:45Z"}


# Bind context for request
log = logger.bind(request_id="abc123", user_id=456)
log.info("processing_started")  # Includes request_id and user_id
log.info("processing_completed")  # Same context
```

---

## Request Logging

### Logging Middleware

```python
# middleware/logging.py
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log every request with:
    - Request ID (for tracing)
    - Method and path
    - Response status
    - Duration
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Add to request state (for use in handlers)
        request.state.request_id = request_id
        
        # Log request start
        start_time = time.time()
        
        logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host,
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log request end
            logger.info(
                "request_completed",
                request_id=request_id,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error(
                "request_failed",
                request_id=request_id,
                error=str(e),
                duration_ms=round(duration_ms, 2),
            )
            raise


# main.py
from fastapi import FastAPI
from middleware.logging import RequestLoggingMiddleware

app = FastAPI()
app.add_middleware(RequestLoggingMiddleware)
```

### Context-Aware Logging

```python
from contextvars import ContextVar
import structlog

# Context variable to store request info
request_context: ContextVar[dict] = ContextVar("request_context", default={})


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Set context for this request
        context = {
            "request_id": str(uuid.uuid4())[:8],
            "user_id": None,  # Set after auth
            "path": request.url.path,
        }
        request_context.set(context)
        
        return await call_next(request)


def get_logger():
    """Get logger with current request context"""
    context = request_context.get()
    return structlog.get_logger().bind(**context)


# Usage in any module
logger = get_logger()
logger.info("processing_order")  # Automatically includes request_id, user_id, path
```

---

## Metrics with Prometheus

### What is Prometheus?

```
Prometheus = Time-series metrics database

Your App ──► Exposes /metrics endpoint
Prometheus ──► Scrapes /metrics every 15 seconds
Prometheus ──► Stores time-series data
Grafana ──► Visualizes data from Prometheus

Metric Types:
1. Counter: Only increases (requests_total)
2. Gauge: Can go up/down (active_users)
3. Histogram: Distribution (response_time)
4. Summary: Similar to histogram, with percentiles
```

### FastAPI with Prometheus

```python
# pip install prometheus-client prometheus-fastapi-instrumentator

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Auto-instrument with default metrics
Instrumentator().instrument(app).expose(app)

# Now /metrics endpoint available!
# Shows: request count, latency, response size, etc.
```

### Custom Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

ACTIVE_USERS = Gauge(
    "app_active_users",
    "Number of active users"
)

ORDER_AMOUNT = Histogram(
    "app_order_amount_dollars",
    "Order amounts in dollars",
    buckets=[10, 50, 100, 500, 1000, 5000]
)


# Middleware to track metrics
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(time.time() - start_time)
        
        return response


# Use in handlers
@app.post("/orders")
async def create_order(order: OrderCreate):
    db_order = await save_order(order)
    
    # Record order amount
    ORDER_AMOUNT.observe(order.amount)
    
    return db_order


# Track active users
async def user_connected(user_id: str):
    ACTIVE_USERS.inc()

async def user_disconnected(user_id: str):
    ACTIVE_USERS.dec()
```

### Prometheus Docker Setup

```yaml
# docker-compose.yml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
  
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "fastapi"
    static_configs:
      - targets: ["app:8000"]
    metrics_path: "/metrics"
```

---

## Visualization with Grafana

### Dashboard Queries (PromQL)

```promql
# Request rate (requests per second)
rate(app_requests_total[5m])

# Error rate percentage
sum(rate(app_requests_total{status=~"5.."}[5m]))
/
sum(rate(app_requests_total[5m]))
* 100

# 95th percentile latency
histogram_quantile(0.95, rate(app_request_latency_seconds_bucket[5m]))

# Active users
app_active_users

# Requests by endpoint
sum by (endpoint) (rate(app_requests_total[5m]))
```

### Key Metrics to Monitor

```
1. RED Method (for services):
   - Rate: Requests per second
   - Errors: Error rate percentage
   - Duration: Response time percentiles

2. USE Method (for resources):
   - Utilization: CPU/Memory usage %
   - Saturation: Queue lengths
   - Errors: System errors

Dashboard Panels:
┌────────────────────────────────────────────────────┐
│  Request Rate     │  Error Rate     │  Latency    │
│  ▂▃▅▆▇▆▅▃▂       │  ▁▁▁▂▁▁▁▁      │  p50: 50ms  │
│  1.5k req/s       │  0.5%           │  p95: 200ms │
├────────────────────────────────────────────────────┤
│  Active Users     │  CPU Usage      │  Memory     │
│  ▃▄▅▆▇▇▆▅▄       │  ▃▃▄▄▅▅▄▃      │  45%        │
│  1,250            │  35%            │  2.1 GB     │
└────────────────────────────────────────────────────┘
```

---

## Error Tracking (Sentry)

### Why Sentry?

```
Without Sentry:
─────────────────────────────────────────────────────────
Error happens → User sees 500 error
You check logs → Find "NullPointerException at line 42"
No context: What was the request? User? State?


With Sentry:
─────────────────────────────────────────────────────────
Error happens → Sentry captures everything:
- Full stack trace
- Request details
- User info
- Browser/device
- Release version
- How many users affected

Alert sent → Fix in minutes!
```

### Sentry Setup

```python
# pip install sentry-sdk[fastapi]

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn="https://xxx@sentry.io/123",  # Your Sentry DSN
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,  # 10% of transactions for performance
    profiles_sample_rate=0.1,  # 10% for profiling
    environment="production",
    release="myapp@1.0.0",
)

# FastAPI app
from fastapi import FastAPI

app = FastAPI()


# Errors are automatically captured!
@app.get("/error")
async def trigger_error():
    raise ValueError("Something went wrong!")
    # Sentry captures this with full context
```

### Adding Context

```python
from sentry_sdk import set_user, set_tag, capture_message

@app.middleware("http")
async def sentry_context_middleware(request: Request, call_next):
    # Set user context
    if hasattr(request.state, "user"):
        set_user({
            "id": request.state.user.id,
            "email": request.state.user.email,
        })
    
    # Set tags for filtering
    set_tag("endpoint", request.url.path)
    set_tag("method", request.method)
    
    return await call_next(request)


# Manual error capture with context
def process_payment(order_id: int, amount: float):
    try:
        result = payment_gateway.charge(amount)
    except PaymentError as e:
        sentry_sdk.capture_exception(e)
        sentry_sdk.set_context("payment", {
            "order_id": order_id,
            "amount": amount,
            "gateway_response": e.response,
        })
        raise


# Capture custom messages
capture_message("User reached 1000 orders!", level="info")
```

---

## Distributed Tracing

### What is Distributed Tracing?

```
Microservices Problem:
─────────────────────────────────────────────────────────
Request → API Gateway → Auth Service → User Service → Database
                      → Order Service → Payment Service → Database
                      
Where is the slowdown? Which service failed?


With Distributed Tracing:
─────────────────────────────────────────────────────────
Trace ID: abc123
│
├── Span: API Gateway (5ms)
│   │
│   ├── Span: Auth Service (15ms)
│   │   └── Span: JWT Verify (10ms)
│   │
│   └── Span: Order Service (150ms)  ← Slow!
│       ├── Span: Database Query (120ms)  ← Found it!
│       └── Span: Payment Service (25ms)
│
Total: 170ms
```

### OpenTelemetry Setup

```python
# pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

# Configure tracing
trace.set_tracer_provider(TracerProvider())

# Export to Jaeger/Zipkin/etc
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Auto-instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Auto-instrument SQLAlchemy
SQLAlchemyInstrumentor().instrument(engine=engine)

# Auto-instrument HTTP clients
HTTPXClientInstrumentor().instrument()


# Manual spans for custom logic
tracer = trace.get_tracer(__name__)

async def process_order(order_id: int):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order_id", order_id)
        
        with tracer.start_as_current_span("validate_order"):
            await validate_order(order_id)
        
        with tracer.start_as_current_span("charge_payment"):
            await charge_payment(order_id)
        
        with tracer.start_as_current_span("send_confirmation"):
            await send_confirmation(order_id)
```

---

## Health Checks

### Comprehensive Health Check

```python
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from enum import Enum

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


async def check_database():
    """Check database connectivity"""
    try:
        async with db.acquire() as conn:
            await conn.execute("SELECT 1")
        return {"status": "healthy", "latency_ms": 5}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_redis():
    """Check Redis connectivity"""
    try:
        await redis.ping()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_external_api():
    """Check external dependencies"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/health", timeout=5)
            return {"status": "healthy" if response.status_code == 200 else "degraded"}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


@app.get("/health")
async def health_check():
    """
    Comprehensive health check
    
    Returns:
    - 200: All systems healthy
    - 503: One or more systems unhealthy
    """
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "external_api": await check_external_api(),
    }
    
    # Determine overall status
    statuses = [c["status"] for c in checks.values()]
    
    if all(s == "healthy" for s in statuses):
        overall_status = HealthStatus.HEALTHY
        http_status = status.HTTP_200_OK
    elif any(s == "unhealthy" for s in statuses):
        overall_status = HealthStatus.UNHEALTHY
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        overall_status = HealthStatus.DEGRADED
        http_status = status.HTTP_200_OK
    
    return JSONResponse(
        content={
            "status": overall_status,
            "checks": checks,
            "version": "1.0.0",
        },
        status_code=http_status
    )


@app.get("/health/live")
async def liveness():
    """
    Kubernetes liveness probe
    
    Is the app running? (Not deadlocked)
    """
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    """
    Kubernetes readiness probe
    
    Is the app ready to receive traffic?
    """
    # Check critical dependencies
    db_check = await check_database()
    
    if db_check["status"] == "unhealthy":
        return JSONResponse(
            {"status": "not ready", "reason": "database"},
            status_code=503
        )
    
    return {"status": "ready"}
```

---

## Alerting

### Alert Rules Example

```yaml
# prometheus/alert_rules.yml
groups:
  - name: fastapi
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          sum(rate(app_requests_total{status=~"5.."}[5m]))
          /
          sum(rate(app_requests_total[5m]))
          > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      # Slow response time
      - alert: SlowResponseTime
        expr: |
          histogram_quantile(0.95, rate(app_request_latency_seconds_bucket[5m]))
          > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response times"
          description: "95th percentile latency is {{ $value }}s"

      # App down
      - alert: AppDown
        expr: up{job="fastapi"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "FastAPI app is down"
```

### Slack Alerting

```python
# Send alerts to Slack
import httpx

async def send_slack_alert(message: str, severity: str):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    color = {
        "critical": "#FF0000",
        "warning": "#FFA500",
        "info": "#0000FF"
    }.get(severity, "#808080")
    
    payload = {
        "attachments": [{
            "color": color,
            "title": f"Alert: {severity.upper()}",
            "text": message,
            "footer": "FastAPI Monitoring",
            "ts": int(time.time())
        }]
    }
    
    async with httpx.AsyncClient() as client:
        await client.post(webhook_url, json=payload)
```

---

## Best Practices

### 1. Log Levels

```python
# Use appropriate log levels
logger.debug("Detailed info for debugging")  # Development only
logger.info("Normal operations")              # Successful events
logger.warning("Something unexpected")        # Not error, but attention needed
logger.error("Error occurred")                # Errors that need attention
logger.critical("System is down")             # Immediate action needed

# In production, set level to INFO
```

### 2. Don't Log Sensitive Data

```python
# ❌ BAD
logger.info(f"User login: {email}, password: {password}")

# ✅ GOOD
logger.info("User login", extra={"user_id": user.id})
```

### 3. Correlation IDs

```python
# Always include request/trace ID
logger.info("Processing order", extra={
    "request_id": request.state.request_id,
    "order_id": order.id
})
```

### 4. Metric Cardinality

```python
# ❌ BAD - High cardinality
REQUEST_COUNT.labels(user_id=user.id)  # Millions of users = millions of metrics!

# ✅ GOOD - Low cardinality
REQUEST_COUNT.labels(endpoint="/users", method="GET", status="200")
```

---

## Quick Reference

```python
# Structured logging
import structlog
logger = structlog.get_logger()
logger.info("event", key="value")

# Prometheus metrics
from prometheus_client import Counter, Histogram
counter = Counter("name", "description", ["label"])
counter.labels(label="value").inc()

# Sentry
import sentry_sdk
sentry_sdk.capture_exception(error)

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

> **Pro Tip**: "Logs se pata chalta hai KYA hua, Metrics se pata chalta hai KITNA hua, Traces se pata chalta hai KAHAN hua!" 📊
