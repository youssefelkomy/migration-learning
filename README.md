# SQLAlchemy & Alembic Migration Guide

A comprehensive guide to using Alembic for database migrations with SQLAlchemy 2.0.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Setup and Configuration](#setup-and-configuration)
- [Creating Models](#creating-models)
- [Alembic Commands](#alembic-commands)
- [Migration Workflow](#migration-workflow)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

This project demonstrates how to use Alembic with SQLAlchemy 2.0 for database schema migrations. Alembic is a lightweight database migration tool for usage with SQLAlchemy, providing a way to manage database schema changes over time.

### Key Features

- Modern SQLAlchemy 2.0 syntax with type hints
- PostgreSQL database with Neon cloud hosting
- Automatic migration generation
- Comprehensive indexing strategy
- Strict type checking with mypy
- Code quality enforcement with ruff

## Project Structure

```
migration-learning/
├── models/
│   ├── __init__.py          # Model exports
│   ├── base.py              # DeclarativeBase configuration
│   └── user.py              # User model definition
├── alembic/
│   ├── versions/            # Migration files
│   ├── env.py              # Alembic environment configuration
│   └── script.py.mako      # Migration template
├── alembic.ini             # Alembic configuration
├── pyproject.toml          # Project dependencies and tool configuration
└── verify_migration.py     # Database verification script
```

## Setup and Configuration

### 1. Dependencies

The project uses the following key dependencies:

```toml
dependencies = [
    "alembic>=1.16.4",
    "psycopg2-binary>=2.9.10",
    "sqlalchemy>=2.0.43",
]
```

### 2. Database Configuration

Database connection is configured in `alembic.ini`:

```ini
sqlalchemy.url = postgresql://username:password@host:port/database?sslmode=require
```

### 3. Alembic Environment Setup

The `alembic/env.py` file is configured to:
- Import your models for autogenerate support
- Set target_metadata to your Base.metadata
- Handle both online and offline migrations

Key configuration in `alembic/env.py`:

```python
from models import Base
target_metadata = Base.metadata
```

## Creating Models

### Base Model Configuration

```python
# models/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all database models."""
    pass
```

### Model Definition with SQLAlchemy 2.0

```python
# models/user.py
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from models.base import Base

class User(Base):
    """User model representing application users."""

    __tablename__ = "users"

    # Primary key with UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Required fields
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    # Optional fields using modern union syntax
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Boolean fields with defaults
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamp fields with automatic values
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Custom indexes for performance
    __table_args__ = (
        Index("idx_user_email_active", "email", "is_active"),
        Index("idx_user_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation of the User model."""
        return f"<User(id={self.id}, username='{self.username}')>"
```

## Alembic Commands

### Basic Commands

#### Initialize Alembic (one-time setup)
```bash
alembic init alembic
```

#### Check current migration version
```bash
alembic current
```

#### View migration history
```bash
alembic history
```

#### Show detailed history with ranges
```bash
alembic history -r-3:current
```

### Creating Migrations

#### Auto-generate migration from model changes
```bash
alembic revision --autogenerate -m "Description of changes"
```

#### Create empty migration file
```bash
alembic revision -m "Description of changes"
```

#### Create migration with specific revision ID
```bash
alembic revision --rev-id=001 -m "Initial migration"
```

### Applying Migrations

#### Upgrade to latest migration
```bash
alembic upgrade head
```

#### Upgrade to specific revision
```bash
alembic upgrade ae1027a6acf
```

#### Upgrade by relative number
```bash
alembic upgrade +2
```

#### Downgrade to previous revision
```bash
alembic downgrade -1
```

#### Downgrade to specific revision
```bash
alembic downgrade ae1027a6acf
```

#### Downgrade to base (remove all migrations)
```bash
alembic downgrade base
```

### Advanced Commands

#### Show SQL without executing
```bash
alembic upgrade head --sql
```

#### Generate SQL for offline use
```bash
alembic upgrade head --sql > migration.sql
```

#### Stamp database with specific revision (without running migration)
```bash
alembic stamp head
```

#### Show differences between current database and models
```bash
alembic check
```

## Migration Workflow

### 1. Model Development Workflow

1. **Create or modify models** in the `models/` directory
2. **Import models** in `models/__init__.py`
3. **Generate migration**:
   ```bash
   alembic revision --autogenerate -m "Add user table"
   ```
4. **Review generated migration** in `alembic/versions/`
5. **Apply migration**:
   ```bash
   alembic upgrade head
   ```
6. **Verify migration** by checking database schema

### 2. Team Development Workflow

1. **Pull latest changes** from repository
2. **Check current migration status**:
   ```bash
   alembic current
   ```
3. **Apply any pending migrations**:
   ```bash
   alembic upgrade head
   ```
4. **Make model changes**
5. **Generate new migration**
6. **Test migration** on development database
7. **Commit migration files** to version control

### 3. Production Deployment Workflow

1. **Backup production database**
2. **Test migrations** on staging environment
3. **Deploy code** to production
4. **Apply migrations**:
   ```bash
   alembic upgrade head
   ```
5. **Verify application** functionality
6. **Monitor** for any issues

## Best Practices

### Model Design

- Use type hints with `Mapped[T]` for all columns
- Prefer `mapped_column()` over `Column()` for SQLAlchemy 2.0
- Use appropriate data types (UUID for IDs, timezone-aware datetime)
- Add indexes for frequently queried columns
- Include `__repr__` methods for debugging

### Migration Management

- Always review auto-generated migrations before applying
- Use descriptive migration messages
- Test migrations on development data first
- Keep migrations small and focused
- Never edit applied migrations
- Use `alembic check` to verify model-database consistency

### Database Schema

- Use consistent naming conventions
- Add appropriate constraints and indexes
- Consider performance implications of schema changes
- Plan for data migration when changing column types
- Use database-specific features when beneficial

### Version Control

- Always commit migration files
- Include both upgrade and downgrade functions
- Test downgrade migrations
- Use meaningful commit messages for migrations
- Tag releases that include schema changes

## Troubleshooting

### Common Issues

#### Migration conflicts
```bash
# If you have conflicting migrations
alembic merge -m "Merge migrations" revision1 revision2
```

#### Reset migration history
```bash
# Dangerous: only for development
alembic stamp base
alembic upgrade head
```

#### Fix broken migration state
```bash
# Check current state
alembic current
# Manually stamp to correct revision
alembic stamp <correct_revision_id>
```

### Database Connection Issues

- Verify database URL in `alembic.ini`
- Check database credentials and permissions
- Ensure database server is accessible
- Verify SSL requirements for cloud databases

### Model Import Issues

- Ensure all models are imported in `alembic/env.py`
- Check that `target_metadata` is set correctly
- Verify model imports in `models/__init__.py`
- Check for circular import issues

### Performance Considerations

- Large table migrations may require downtime
- Consider using `op.bulk_insert()` for data migrations
- Test migration performance on production-sized data
- Use database-specific migration strategies when needed

## Code Quality

This project enforces strict code quality standards:

- **Type checking**: mypy with strict configuration
- **Code formatting**: ruff with comprehensive rule set
- **Import sorting**: automatic import organization
- **Line length**: 88 characters maximum

Run quality checks:
```bash
# Check code formatting
ruff check

# Run type checking
mypy .

# Auto-fix formatting issues
ruff check --fix
```

## Verification

Use the included verification script to check migration success:

```bash
python verify_migration.py
```

This script will:
- Test database connectivity
- Verify table structure
- Check indexes and constraints
- Validate model functionality
- Display current migration version

## Additional Resources

### Official Documentation

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Useful Commands Reference

```bash
# Development workflow
alembic revision --autogenerate -m "Add new feature"
alembic upgrade head
alembic current

# Production deployment
alembic upgrade head --sql > migration.sql  # Review first
alembic upgrade head

# Troubleshooting
alembic history
alembic show <revision>
alembic check

# Rollback if needed
alembic downgrade -1
```

### Environment Variables

For production deployments, consider using environment variables:

```bash
# Set database URL via environment
export DATABASE_URL="postgresql://user:pass@host:port/db"
alembic upgrade head
```

### Docker Integration

Example Dockerfile snippet for migrations:

```dockerfile
# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Run migrations on container start
CMD ["sh", "-c", "alembic upgrade head && python main.py"]
```