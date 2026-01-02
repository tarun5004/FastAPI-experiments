# 20 — Docker, Deployment & CI/CD (Complete In-Depth Guide)

> 🎯 **Goal**: Apni app ko production mein deploy karo - har jagah same chalegi!

---

## 📚 Table of Contents
1. [Docker Kyun?](#docker-kyun)
2. [Docker Basics](#docker-basics)
3. [Dockerfile for FastAPI](#dockerfile-for-fastapi)
4. [Docker Compose](#docker-compose)
5. [Production Deployment](#production-deployment)
6. [Cloud Deployment](#cloud-deployment)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [GitHub Actions](#github-actions)
9. [Best Practices](#best-practices)
10. [Practice Exercises](#practice-exercises)

---

## Docker Kyun?

### The Problem

```
Development Machine:
─────────────────────────────────────────────────────────
Python 3.11, PostgreSQL 15, Redis 7
All libraries installed
"Works on my machine!" ✅


Production Server:
─────────────────────────────────────────────────────────
Python 3.9, PostgreSQL 13, Redis 6
Different versions, missing libraries
"It doesn't work!" ❌


Different Developer's Machine:
─────────────────────────────────────────────────────────
Windows, different paths, different Python
"Nothing works!" ❌
```

### The Solution

```
Docker:
─────────────────────────────────────────────────────────
Package entire environment in a "container"

Container = Code + Dependencies + OS Libraries + Config

Same container runs EVERYWHERE:
- Development laptop ✅
- CI/CD server ✅
- Production server ✅
- Colleague's machine ✅

"Works on any machine!" 🚀
```

### Docker vs Virtual Machine

```
Virtual Machine:
┌─────────────────────────────────────┐
│           Guest OS (5GB)            │
│   ┌─────────────────────────────┐   │
│   │        App + Libraries      │   │
│   └─────────────────────────────┘   │
├─────────────────────────────────────┤
│          Hypervisor                 │
├─────────────────────────────────────┤
│           Host OS                   │
└─────────────────────────────────────┘
Heavy, slow to start (minutes)


Docker Container:
┌─────────────────────────────────────┐
│        App + Libraries (100MB)      │
├─────────────────────────────────────┤
│          Docker Engine              │
├─────────────────────────────────────┤
│           Host OS                   │
└─────────────────────────────────────┘
Lightweight, fast to start (seconds)
```

---

## Docker Basics

### Key Concepts

```
IMAGE (Recipe):
- Blueprint/template for container
- Read-only
- Built from Dockerfile
- Example: python:3.11-slim

CONTAINER (Running App):
- Running instance of image
- Has its own filesystem, network
- Can be started, stopped, deleted
- Like a lightweight VM

DOCKERFILE:
- Instructions to build image
- FROM, COPY, RUN, CMD

DOCKER HUB:
- Registry of public images
- Like GitHub for Docker images
```

### Basic Commands

```bash
# Pull image from Docker Hub
docker pull python:3.11-slim

# List images
docker images

# Run container
docker run python:3.11-slim python --version
# Output: Python 3.11.x

# Run container interactively
docker run -it python:3.11-slim bash

# Run container with port mapping
docker run -p 8000:8000 myapp

# Run container in background
docker run -d --name myapp myapp

# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop container
docker stop myapp

# Remove container
docker rm myapp

# Remove image
docker rmi python:3.11-slim
```

---

## Dockerfile for FastAPI

### Basic Dockerfile

```dockerfile
# Dockerfile

# 1. Base image - Official Python
FROM python:3.11-slim

# 2. Set working directory inside container
WORKDIR /app

# 3. Copy requirements first (for caching)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy application code
COPY . .

# 6. Expose port
EXPOSE 8000

# 7. Command to run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Optimized Production Dockerfile

```dockerfile
# Dockerfile.prod

# ============================================
# Stage 1: Builder (install dependencies)
# ============================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ============================================
# Stage 2: Production (minimal image)
# ============================================
FROM python:3.11-slim as production

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with production server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Build and Run

```bash
# Build image
docker build -t myapp:latest .

# Build production image
docker build -f Dockerfile.prod -t myapp:prod .

# Run container
docker run -d -p 8000:8000 --name myapp myapp:latest

# View logs
docker logs myapp
docker logs -f myapp  # Follow logs

# Execute command in running container
docker exec -it myapp bash
docker exec myapp python -c "print('Hello')"

# Check container resource usage
docker stats myapp
```

### .dockerignore

```dockerignore
# .dockerignore - Files to NOT copy into image

# Python
__pycache__/
*.py[cod]
*.pyo
.Python
*.egg-info/
.eggs/
*.egg

# Virtual environment
venv/
.venv/
ENV/

# IDE
.vscode/
.idea/
*.swp

# Git
.git/
.gitignore

# Docker
Dockerfile*
docker-compose*
.dockerignore

# Tests
tests/
pytest.ini
.pytest_cache/

# Other
*.md
*.log
.env
.env.*
```

---

## Docker Compose

### What is Docker Compose?

```
Docker Compose = Run multiple containers together

Your App needs:
- FastAPI (web server)
- PostgreSQL (database)
- Redis (cache)
- Celery (background tasks)

Without Compose: Run 4 separate docker run commands
With Compose: One docker-compose up command
```

### Basic docker-compose.yml

```yaml
# docker-compose.yml
version: "3.8"

services:
  # FastAPI Application
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - .:/app  # Mount code for development
    restart: unless-stopped

  # PostgreSQL Database
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Celery Worker
  celery_worker:
    build: .
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
  redis_data:
```

### Docker Compose Commands

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Start specific service
docker-compose up -d web

# Stop all services
docker-compose down

# Stop and remove volumes (careful!)
docker-compose down -v

# View logs
docker-compose logs
docker-compose logs -f web

# Rebuild images
docker-compose build
docker-compose up --build

# Scale services
docker-compose up -d --scale celery_worker=3

# Execute command in service
docker-compose exec web bash
docker-compose exec db psql -U postgres
```

### Production docker-compose

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  web:
    image: myapp:prod  # Use pre-built image
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: always
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
  redis_data:
```

---

## Production Deployment

### Deployment Options

```
Option 1: VPS (DigitalOcean, Linode, AWS EC2)
─────────────────────────────────────────────────────────
✅ Full control
✅ Cheaper for consistent workloads
❌ Manual server management
❌ Manual scaling

Option 2: Platform as a Service (Heroku, Railway, Render)
─────────────────────────────────────────────────────────
✅ Easy deployment
✅ Automatic scaling
❌ Less control
❌ Can get expensive

Option 3: Kubernetes (AWS EKS, GCP GKE)
─────────────────────────────────────────────────────────
✅ Enterprise-grade scaling
✅ Self-healing
❌ Complex setup
❌ Overkill for small apps

Option 4: Serverless (AWS Lambda, Cloud Run)
─────────────────────────────────────────────────────────
✅ Pay per request
✅ Auto-scaling
❌ Cold starts
❌ Different architecture needed
```

### VPS Deployment Steps

```bash
# 1. Connect to server
ssh user@your-server-ip

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Clone your repo
git clone https://github.com/yourusername/myapp.git
cd myapp

# 5. Create .env file
cp .env.example .env
nano .env  # Edit with production values

# 6. Start application
docker-compose -f docker-compose.prod.yml up -d

# 7. Check logs
docker-compose logs -f
```

### Nginx Configuration

```nginx
# nginx.conf

upstream fastapi {
    server web:8000;
}

server {
    listen 80;
    server_name myapp.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name myapp.com;
    
    # SSL certificates
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket support
    location /ws {
        proxy_pass http://fastapi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Static files
    location /static {
        alias /app/static;
        expires 30d;
    }
}
```

---

## Cloud Deployment

### Railway (Easiest)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Open app
railway open
```

### Render

```yaml
# render.yaml
services:
  - type: web
    name: myapp
    env: docker
    dockerfilePath: ./Dockerfile.prod
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: mydb
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
    healthCheckPath: /health

databases:
  - name: mydb
    databaseName: myapp
    user: myapp
```

### AWS with Docker

```bash
# Push image to ECR (Elastic Container Registry)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

docker tag myapp:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:latest

# Deploy to ECS (Elastic Container Service)
# Use AWS Console or terraform
```

---

## CI/CD Pipeline

### What is CI/CD?

```
CI (Continuous Integration):
─────────────────────────────────────────────────────────
Every code push:
1. Run tests automatically
2. Check code quality (linting)
3. Build Docker image
4. Report results

If anything fails → Block the merge


CD (Continuous Deployment):
─────────────────────────────────────────────────────────
After code merges to main:
1. Build production image
2. Push to registry
3. Deploy to staging
4. Run integration tests
5. Deploy to production
6. Notify team

Fully automated deployment!
```

### Pipeline Visualization

```
Developer pushes code
         │
         ▼
    ┌─────────┐
    │  Build  │ ── Build Docker image
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  Test   │ ── Run pytest, coverage
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  Lint   │ ── Check code style
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  Push   │ ── Push to container registry
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │ Deploy  │ ── Deploy to server
    └─────────┘
```

---

## GitHub Actions

### Basic CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
        run: |
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install linters
        run: pip install ruff mypy
      
      - name: Run Ruff (linting)
        run: ruff check .
      
      - name: Run MyPy (type checking)
        run: mypy app/
```

### Full CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    # ... same as above ...

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha
            type=ref,event=branch
            latest
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: Dockerfile.prod
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /app
            docker pull ghcr.io/${{ github.repository }}:latest
            docker-compose -f docker-compose.prod.yml up -d
            docker image prune -f
      
      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: "Deployment ${{ job.status }}"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Environment Secrets Setup

```
GitHub Repository → Settings → Secrets → Actions

Required secrets:
- SERVER_HOST: your-server-ip
- SERVER_USER: deploy
- SERVER_SSH_KEY: (your private SSH key)
- SLACK_WEBHOOK: (optional, for notifications)
```

---

## Best Practices

### 1. Use Multi-Stage Builds

```dockerfile
# Reduces final image size from 1GB to ~200MB

FROM python:3.11 as builder
# Install all build tools, compile stuff

FROM python:3.11-slim as production
# Copy only compiled results
```

### 2. Don't Run as Root

```dockerfile
RUN adduser --disabled-password appuser
USER appuser
```

### 3. Use .env for Configuration

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 4. Health Checks

```python
# main.py
@app.get("/health")
async def health_check():
    # Check database
    try:
        await db.execute("SELECT 1")
    except:
        return JSONResponse({"status": "unhealthy"}, status_code=503)
    
    return {"status": "healthy"}
```

### 5. Logging

```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Don't log to files in containers - use stdout
# Docker/Kubernetes will capture stdout
```

### 6. Graceful Shutdown

```python
@app.on_event("shutdown")
async def shutdown_event():
    # Close database connections
    await database.disconnect()
    # Close Redis
    await redis.close()
    # Cancel background tasks
    for task in background_tasks:
        task.cancel()
```

---

## Practice Exercises

### Exercise 1: Dockerize FastAPI
```bash
# Create:
# 1. Dockerfile for development
# 2. Dockerfile.prod for production
# 3. docker-compose.yml with PostgreSQL
# 4. Test locally with docker-compose up
```

### Exercise 2: CI Pipeline
```yaml
# Create GitHub Actions workflow:
# 1. Run tests on every push
# 2. Check code style with Ruff
# 3. Build Docker image
# 4. Push to GitHub Container Registry
```

### Exercise 3: Full Deployment
```bash
# Deploy to VPS:
# 1. Set up server with Docker
# 2. Configure Nginx with SSL
# 3. Deploy with docker-compose
# 4. Set up automated deployments
```

---

## Quick Reference

```bash
# Docker
docker build -t myapp .
docker run -p 8000:8000 myapp
docker ps / docker logs / docker exec

# Docker Compose
docker-compose up -d
docker-compose down
docker-compose logs -f

# GitHub Actions
# Trigger: push, pull_request
# Jobs: test, build, deploy
# Secrets: Settings → Secrets

# Deployment
# 1. Build image
# 2. Push to registry
# 3. Pull on server
# 4. Restart containers
```

---

> **Pro Tip**: "Pehle local mein docker-compose se test karo, phir production deploy karo!" 🚀
