# 10 — Alembic Migrations (Complete In-Depth Guide)

> 🎯 **Goal**: Database schema changes ko professionally manage karna seekho!

---

## 📚 Table of Contents
1. [Migrations Kya Hai?](#migrations-kya-hai)
2. [Alembic Setup](#alembic-setup)
3. [First Migration](#first-migration)
4. [Migration Commands](#migration-commands)
5. [Auto-generate Migrations](#auto-generate-migrations)
6. [Manual Migrations](#manual-migrations)
7. [Upgrade & Downgrade](#upgrade--downgrade)
8. [Data Migrations](#data-migrations)
9. [Multiple Databases](#multiple-databases)
10. [Best Practices](#best-practices)
11. [Common Problems & Solutions](#common-problems--solutions)
12. [Practice Exercises](#practice-exercises)

---

## Migrations Kya Hai?

### Problem Samjho Pehle

```python
# ❓ Scenario: Aapne ek table banaya

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(100))

# Abhi database mein users table hai with id, email

# ⏰ 2 weeks baad: Manager bola "phone number add karo"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(100))
    phone = Column(String(20))  # NEW COLUMN!

# ❌ PROBLEM: Model change kiya, but database mein column nahi add hua!
# Database schema khud se nahi badalta
```

### Solution: Migrations

```
Migration = Database schema change ka record

Socho jaise:
- Code ke liye: Git (version control)
- Database ke liye: Migrations (version control)

Migration file batati hai:
1. Kya change karna hai (add column, remove table, etc.)
2. Kaise wapas jaana hai (undo/rollback)
```

### Manual vs Alembic

```python
# ❌ Manual approach (BAD)
# Har baar SQL likho aur manually run karo
"""
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
"""
# Problems:
# - Track nahi hota kya changes hue
# - Team mein sync nahi rehta
# - Rollback mushkil

# ✅ Alembic approach (GOOD)
# Automatic migration files generate
# Team mein share kar sakte ho
# Easy rollback
```

---

## Alembic Setup

### Step 1: Install Alembic

```bash
pip install alembic
```

### Step 2: Initialize Alembic

```bash
# Project folder mein jaake
cd "C:\vscode tool\fast api"

# Alembic initialize karo
alembic init alembic
```

**Yeh command yeh files create karegi:**

```
project/
├── alembic/                 # Alembic folder
│   ├── versions/            # Migration files yahan
│   ├── env.py              # Configuration file
│   ├── README              # Info
│   └── script.py.mako      # Template for migrations
├── alembic.ini             # Main config file
└── app/
    ├── models.py
    └── database.py
```

### Step 3: Configure alembic.ini

```ini
# alembic.ini

[alembic]
# Migration files kahan hai
script_location = alembic

# Database URL - yahan set karo ya env.py mein
# SQLite example:
sqlalchemy.url = sqlite:///./app.db

# PostgreSQL example:
# sqlalchemy.url = postgresql://user:password@localhost/dbname
```

### Step 4: Configure env.py (Important!)

```python
# alembic/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# ⭐ IMPORTANT: Apne models import karo
# Yeh line add karo - path apne project ke according
import sys
sys.path.insert(0, '.')  # Current directory add karo

from app.models import Base  # Apna Base import karo
from app.database import DATABASE_URL  # Optional: database URL

# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ⭐ IMPORTANT: Apna metadata set karo
# Yeh batata hai Alembic ko ki konse models track karna hai
target_metadata = Base.metadata

# Optional: Database URL dynamically set karo
# config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """
    Offline mode: SQL script generate karo bina database connect kiye
    
    Use case: Production mein manually SQL run karna ho
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Online mode: Database se connect karke migrations run karo
    
    Normal use case - yeh usually hota hai
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**env.py Kya Karta Hai?**

```
1. Models load karta hai (Base.metadata)
2. Database connection banata hai
3. Migrations run karta hai

Socho jaise ek "bridge" hai:
Alembic Commands <--> env.py <--> Database
```

---

## First Migration

### Step 1: Model Banao

```python
# app/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Step 2: Migration Generate Karo

```bash
# Auto-generate migration based on model changes
alembic revision --autogenerate -m "Create users table"
```

**Yeh command:**
1. Models check karegi
2. Database schema check karegi
3. Difference nikaalegi
4. Migration file create karegi

### Step 3: Migration File Dekho

```python
# alembic/versions/xxxx_create_users_table.py
"""Create users table

Revision ID: a1b2c3d4e5f6
Revises: 
Create Date: 2024-01-15 10:30:00

Yeh file automatically generate hui hai
"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = 'a1b2c3d4e5f6'  # Unique ID for this migration
down_revision = None  # Previous migration (None = first migration)
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Forward migration - changes apply karo
    
    Jab tum 'alembic upgrade' run karoge, yeh function chalega
    """
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)


def downgrade() -> None:
    """
    Reverse migration - changes undo karo
    
    Jab tum 'alembic downgrade' run karoge, yeh function chalega
    Galti ho gayi toh wapas aa sakte ho
    """
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
```

### Step 4: Migration Apply Karo

```bash
# Database mein changes apply karo
alembic upgrade head

# Output:
# INFO  [alembic.runtime.migration] Running upgrade  -> a1b2c3d4e5f6, Create users table
```

**"head" kya hai?**
```
head = latest migration (sabse naya)

Migration chain:
None -> a1b2c3 -> b2c3d4 -> c3d4e5 (head)
                              ↑
                          Latest version
```

---

## Migration Commands (Detailed)

### Most Used Commands

```bash
# 1. Migration create karo (auto-generate)
alembic revision --autogenerate -m "Description of change"

# 2. Latest version pe upgrade karo
alembic upgrade head

# 3. One step upgrade
alembic upgrade +1

# 4. Specific version pe upgrade
alembic upgrade a1b2c3d4e5f6

# 5. One step downgrade (rollback)
alembic downgrade -1

# 6. Starting point pe jaao (sab undo)
alembic downgrade base

# 7. Current version dekho
alembic current

# 8. Migration history dekho
alembic history

# 9. Show SQL without running
alembic upgrade head --sql
```

### Commands Visualized

```
base     a1b2c3     b2c3d4     c3d4e5     (head)
  |---------|---------|---------|
  
Commands:
- upgrade head     → base se c3d4e5 tak sab apply
- upgrade +1       → ek step aage
- downgrade -1     → ek step peeche
- downgrade base   → starting point (sab undo)
- upgrade a1b2c3   → specific version tak
```

### Practical Examples

```bash
# Scenario: Galti se wrong migration apply ho gayi

# Current state dekho
alembic current
# Output: a1b2c3d4e5f6 (head)

# Ek step wapas jaao
alembic downgrade -1
# Output: Running downgrade a1b2c3d4e5f6 -> None

# Ab sahi migration banao aur apply karo
alembic revision --autogenerate -m "Fixed users table"
alembic upgrade head
```

---

## Auto-generate Migrations

### Kaise Kaam Karta Hai?

```
1. Alembic models padhta hai (Python code)
2. Database schema padhta hai (actual tables)
3. Difference nikalta hai
4. Migration file generate karta hai

Model:                     Database:
- User.id                  - users.id
- User.email              - users.email
- User.phone ← NEW        (missing!)

Migration generated:
op.add_column('users', sa.Column('phone', sa.String(20)))
```

### Example: Column Add Karo

```python
# BEFORE: models.py
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(100))

# AFTER: models.py (phone add kiya)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(100))
    phone = Column(String(20), nullable=True)  # NEW!
```

```bash
# Migration generate karo
alembic revision --autogenerate -m "Add phone to users"

# Generated migration:
def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

def downgrade():
    op.drop_column('users', 'phone')
```

### Example: New Table Add Karo

```python
# models.py mein Post model add karo
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    user_id = Column(Integer, ForeignKey("users.id"))
```

```bash
alembic revision --autogenerate -m "Add posts table"
```

### Auto-generate Limitations ⚠️

```python
# ❌ Yeh DETECT NAHI hoga:
# 1. Column rename
# 2. Table rename
# 3. Column type change (sometimes)

# OLD
class User(Base):
    name = Column(String(100))

# NEW (renamed to full_name)
class User(Base):
    full_name = Column(String(100))  # Alembic will DROP name, ADD full_name!

# ✅ Solution: Manual migration likho
def upgrade():
    op.alter_column('users', 'name', new_column_name='full_name')
```

---

## Manual Migrations

### Empty Migration Create Karo

```bash
# --autogenerate ke bina
alembic revision -m "Rename name to full_name"
```

### Common Manual Operations

```python
# alembic/versions/xxxx_rename_column.py

from alembic import op
import sqlalchemy as sa

def upgrade():
    # 1. Column Rename
    op.alter_column('users', 'name', new_column_name='full_name')
    
    # 2. Table Rename
    op.rename_table('old_name', 'new_name')
    
    # 3. Add Column with Default
    op.add_column('users', sa.Column(
        'status', 
        sa.String(20), 
        server_default='active'
    ))
    
    # 4. Drop Column
    op.drop_column('users', 'old_column')
    
    # 5. Create Index
    op.create_index('ix_users_email', 'users', ['email'])
    
    # 6. Drop Index
    op.drop_index('ix_users_old_index')
    
    # 7. Add Foreign Key
    op.create_foreign_key(
        'fk_posts_user_id',  # Constraint name
        'posts',              # Source table
        'users',              # Target table
        ['user_id'],          # Source columns
        ['id']                # Target columns
    )
    
    # 8. Change Column Type
    op.alter_column(
        'users', 
        'phone',
        type_=sa.String(30),  # Old was String(20)
        existing_type=sa.String(20)
    )

def downgrade():
    # Reverse order mein sab undo karo
    op.alter_column('users', 'phone', type_=sa.String(20))
    op.drop_constraint('fk_posts_user_id', 'posts', type_='foreignkey')
    op.create_index('ix_users_old_index', 'users', ['old_column'])
    op.drop_index('ix_users_email')
    op.add_column('users', sa.Column('old_column', sa.String(50)))
    op.drop_column('users', 'status')
    op.rename_table('new_name', 'old_name')
    op.alter_column('users', 'full_name', new_column_name='name')
```

---

## Data Migrations

### Data Migration Kya Hai?

```
Schema Migration = Table/column structure change
Data Migration = Data modify karna

Example:
- Existing users ko role = 'member' set karna
- Email lowercase mein convert karna
- Old data format se new format mein
```

### Example: Default Value Set Karo

```python
# Scenario: role column add kiya, existing users ko 'member' set karna hai

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Step 1: Column add karo (nullable=True temporarily)
    op.add_column('users', sa.Column('role', sa.String(50), nullable=True))
    
    # Step 2: Existing data update karo
    # execute() se raw SQL run kar sakte ho
    op.execute("UPDATE users SET role = 'member' WHERE role IS NULL")
    
    # Step 3: Column nullable=False karo
    op.alter_column('users', 'role', nullable=False)

def downgrade():
    op.drop_column('users', 'role')
```

### Example: Data Transform

```python
from alembic import op
from sqlalchemy.sql import table, column
from sqlalchemy import String

def upgrade():
    # Table reference banao (ORM model nahi chahiye)
    users = table('users', column('email', String))
    
    # Email lowercase karo
    op.execute(
        users.update().values(email=sa.func.lower(users.c.email))
    )

def downgrade():
    # Data transformation usually irreversible
    pass
```

### Example: Complex Data Migration

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

def upgrade():
    # Connection nikalo
    bind = op.get_bind()
    session = Session(bind=bind)
    
    # Data transform karo
    result = session.execute(sa.text("SELECT id, full_name FROM users"))
    for row in result:
        # Split full name into first and last
        parts = row.full_name.split(' ', 1) if row.full_name else ['', '']
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        
        session.execute(
            sa.text("UPDATE users SET first_name = :first, last_name = :last WHERE id = :id"),
            {"first": first_name, "last": last_name, "id": row.id}
        )
    
    session.commit()
```

---

## Upgrade & Downgrade Strategies

### Upgrade Flow

```bash
# Development
alembic upgrade head  # Sab migrations apply karo

# Production (careful!)
# Step 1: Check kya changes honge
alembic upgrade head --sql > migration.sql
# Review karo

# Step 2: Apply karo
alembic upgrade head
```

### Downgrade (Rollback) Scenarios

```bash
# ❌ Problem: Wrong migration apply ho gayi
alembic downgrade -1  # Ek step wapas

# ❌ Problem: Multiple wrong migrations
alembic downgrade a1b2c3d4  # Specific version tak wapas

# ❌ Problem: Sab galat ho gaya (nuclear option)
alembic downgrade base  # Starting point pe wapas
# WARNING: Sab data bhi jayega!
```

### Safe Deployment Strategy

```bash
# Production mein safe deployment:

# 1. Backup lo (ALWAYS!)
pg_dump mydb > backup_$(date +%Y%m%d).sql

# 2. Dry run (SQL dekho)
alembic upgrade head --sql

# 3. Test environment mein apply karo pehle
alembic upgrade head  # On staging

# 4. Verify karo
alembic current  # Check version

# 5. Production mein apply karo
alembic upgrade head  # On production
```

---

## Best Practices

### 1. Migration Naming

```bash
# ✅ GOOD - Clear description
alembic revision --autogenerate -m "Add phone column to users table"
alembic revision --autogenerate -m "Create posts table with user FK"
alembic revision --autogenerate -m "Add index on users email"

# ❌ BAD - Vague description
alembic revision --autogenerate -m "Update"
alembic revision --autogenerate -m "Changes"
alembic revision --autogenerate -m "Fix"
```

### 2. One Change Per Migration

```bash
# ✅ GOOD - Single responsibility
alembic revision -m "Add phone to users"
alembic revision -m "Create posts table"
alembic revision -m "Add published to posts"

# ❌ BAD - Multiple unrelated changes
alembic revision -m "Add phone, posts, comments, tags"
```

### 3. Review Auto-generated Migrations

```python
# ⚠️ ALWAYS check auto-generated files!

# Example: Alembic might generate
def upgrade():
    op.drop_column('users', 'name')  # ❌ DATA LOSS!
    op.add_column('users', sa.Column('full_name', ...))

# Instead, manually write:
def upgrade():
    op.alter_column('users', 'name', new_column_name='full_name')
```

### 4. Never Edit Applied Migrations

```bash
# ❌ BAD: Migration already applied, edit mat karo!
# Applied migrations database mein recorded hain
# Edit karoge toh checksum mismatch hoga

# ✅ GOOD: New migration banao
alembic revision -m "Fix previous migration"
```

### 5. Database-Specific Code

```python
# Different databases ke liye different SQL

from alembic import op
from sqlalchemy import engine_from_config
from alembic import context

def upgrade():
    bind = op.get_bind()
    
    if bind.dialect.name == 'postgresql':
        op.execute("CREATE EXTENSION IF NOT EXISTS 'uuid-ossp'")
    elif bind.dialect.name == 'sqlite':
        pass  # SQLite doesn't support extensions
```

---

## Common Problems & Solutions

### Problem 1: "Target database is not up to date"

```bash
# Error: Target database is not up to date
# Reason: Database version aur migration files mismatch

# Solution:
alembic current  # Check current version
alembic history  # Check available migrations
alembic upgrade head  # Upgrade to latest
```

### Problem 2: "Can't locate revision"

```bash
# Error: Can't locate revision identified by 'xxxx'
# Reason: Migration file missing ya corrupted

# Solution 1: alembic_version table clear karo (development only!)
# SQLite:
sqlite3 app.db "DELETE FROM alembic_version"

# PostgreSQL:
psql -c "DELETE FROM alembic_version" mydb

# Solution 2: Stamp karo specific version
alembic stamp head  # Current database state ko 'head' mark karo
```

### Problem 3: "No changes detected"

```bash
# Error: No changes detected
# Reason: Models import nahi hue env.py mein

# Solution: env.py check karo
# Make sure:
# 1. sys.path correct hai
# 2. Models import ho rahe hain
# 3. target_metadata = Base.metadata set hai
```

### Problem 4: Circular Import

```python
# ❌ Problem: Circular import error

# Solution: Lazy import use karo
# alembic/env.py

def get_target_metadata():
    from app.models import Base
    return Base.metadata

target_metadata = get_target_metadata()
```

### Problem 5: Production Migration Failed

```bash
# ⚠️ Production mein migration fail ho gayi!

# Step 1: DON'T PANIC!
# Step 2: Downgrade karo
alembic downgrade -1

# Step 3: Problem fix karo
# Step 4: New migration banao
# Step 5: Test karo thoroughly
# Step 6: Apply karo
```

---

## Multiple Databases

### Different Databases for Different Environments

```python
# config.py
import os

DATABASE_URLS = {
    "development": "sqlite:///./dev.db",
    "testing": "sqlite:///./test.db",
    "production": os.getenv("DATABASE_URL")
}

ENV = os.getenv("ENV", "development")
DATABASE_URL = DATABASE_URLS[ENV]
```

```python
# alembic/env.py
from config import DATABASE_URL

config.set_main_option("sqlalchemy.url", DATABASE_URL)
```

```bash
# Different environments
ENV=development alembic upgrade head
ENV=testing alembic upgrade head
ENV=production alembic upgrade head
```

---

## Practice Exercises

### Exercise 1: Basic Migration
```bash
# Create a new model 'Category' with:
# - id (primary key)
# - name (string, unique)
# - description (text)
# Generate and apply migration
```

### Exercise 2: Add Column
```python
# Add 'is_verified' boolean column to users
# Default value: False for existing users
# Create migration manually (not auto-generate)
```

### Exercise 3: Data Migration
```python
# Add 'slug' column to posts
# Generate slug from title for existing posts
# Example: "My First Post" -> "my-first-post"
```

### Exercise 4: Rollback Practice
```bash
# Create 3 migrations
# Apply all
# Rollback one
# Apply again
```

---

## Quick Reference

```bash
# Setup
pip install alembic
alembic init alembic

# Migration create
alembic revision --autogenerate -m "message"  # Auto
alembic revision -m "message"  # Manual

# Apply
alembic upgrade head    # Latest
alembic upgrade +1      # One step
alembic upgrade abc123  # Specific

# Rollback
alembic downgrade -1     # One step back
alembic downgrade base   # All back

# Info
alembic current         # Current version
alembic history         # All versions
alembic heads           # Latest versions

# SQL only (don't apply)
alembic upgrade head --sql
```

---

## Next Steps

1. **Practice karo** - Real migrations create karo
2. **Team mein share karo** - Git mein migrations commit karo
3. **Next doc padho** - `11_authentication.md`

---

> **Pro Tip**: Production mein migration run karne se pehle HAMESHA backup lo! 🛡️
