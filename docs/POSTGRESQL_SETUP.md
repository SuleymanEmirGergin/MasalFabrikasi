# PostgreSQL Setup Guide

## Quick Start with Docker

### 1. Start PostgreSQL

```bash
# Start all services (Redis + PostgreSQL + Backend)
docker-compose up -d

# Or just PostgreSQL
docker-compose up -d postgres
```

### 2. Verify PostgreSQL is Running

```bash
# Check status
docker-compose ps

# Should show postgres as "healthy"
```

### 3. Create Database Tables

```bash
cd backend

# Create initial migration
alembic revision --autogenerate -m "Initial database schema"

# Apply migration
alembic upgrade head
```

### 4. Verify Tables Created

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U masal_user -d masal_fabrikasi

# List tables
\dt

# Should show: users, stories, characters, achievements, comments, purchases, subscriptions, alembic_version

# Exit
\q
```

---

## Manual Setup (Without Docker)

### 1. Install PostgreSQL

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu:**
```bash
sudo apt update
sudo apt install postgresql-15
sudo systemctl start postgresql
```

**Windows:**
Download from https://www.postgresql.org/download/windows/

### 2. Create Database

```bash
# Login as postgres user
sudo -u postgres psql

# Create user and database
CREATE USER masal_user WITH PASSWORD 'masal_password';
CREATE DATABASE masal_fabrikasi OWNER masal_user;
GRANT ALL PRIVILEGES ON DATABASE masal_fabrikasi TO masal_user;

# Exit
\q
```

### 3. Update .env

```env
DATABASE_URL=postgresql://masal_user:masal_password@localhost:5432/masal_fabrikasi
```

### 4. Run Migrations

```bash
cd backend
alembic upgrade head
```

---

## Migration Commands

### Create New Migration

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Add new field to User"

# Manual migration
alembic revision -m "Custom migration"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Go to specific version
alembic upgrade <revision_id>
```

### Check Migration Status

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic show head
```

---

## Database Management

### Backup Database

```bash
# Using Docker
docker-compose exec postgres pg_dump -U masal_user masal_fabrikasi > backup.sql

# Or locally
pg_dump -U masal_user masal_fabrikasi > backup.sql
```

### Restore Database

```bash
# Using Docker
cat backup.sql | docker-compose exec -T postgres psql -U masal_user -d masal_fabrikasi

# Or locally
psql -U masal_user -d masal_fabrikasi < backup.sql
```

### Reset Database

```bash
# Drop and recreate
docker-compose exec postgres psql -U masal_user -d postgres -c "DROP DATABASE IF EXISTS masal_fabrikasi;"
docker-compose exec postgres psql -U masal_user -d postgres -c "CREATE DATABASE masal_fabrikasi OWNER masal_user;"

# Re-run migrations
cd backend
alembic upgrade head
```

---

## Data Migration from JSON

### Option 1: Automatic Migration Script

```bash
cd backend
python scripts/migrate_json_to_postgres.py
```

This will:
1. Read all JSON files
2. Create database records
3. Preserve IDs and timestamps
4. Report any errors

### Option 2: Dual-Write Mode

Backend will write to BOTH JSON and PostgreSQL:
1. Existing data stays in JSON
2. New data goes to both
3. Gradually migrate old data
4. Switch to PostgreSQL-only when ready

---

## Troubleshooting

### Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
- Check if PostgreSQL is running: `docker-compose ps`
- Verify DATABASE_URL in .env
- Check firewall settings

### Migration Conflict

```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solution:**
```bash
# Check current version
alembic current

# Force to a specific version
alembic stamp head

# Or reset completely
alembic downgrade base
alembic upgrade head
```

### Permission Denied

```
ERROR: permission denied for table users
```

**Solution:**
```bash
# Grant all permissions
docker-compose exec postgres psql -U postgres -d masal_fabrikasi -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO masal_user;"
```

---

## Production Setup

### Managed PostgreSQL (Recommended)

**Supabase (Free Tier):**
- 500 MB database
- Unlimited API requests
- https://supabase.com/

**Railway ($5/month):**
- Shared PostgreSQL
- Easy deployment
- https://railway.app/

**AWS RDS (~$15/month):**
- db.t3.micro instance
- Automated backups
- https://aws.amazon.com/rds/

### Update Production .env

```env
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require
```

### Enable SSL

For production, always use SSL:
```python
# In database.py
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)
```

---

## Monitoring

### Check Database Size

```bash
docker-compose exec postgres psql -U masal_user -d masal_fabrikasi -c "
SELECT 
  pg_size_pretty(pg_database_size('masal_fabrikasi')) as size;
"
```

### Check Table Sizes

```bash
docker-compose exec postgres psql -U masal_user -d masal_fabrikasi -c "
SELECT 
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

### Active Connections

```bash
docker-compose exec postgres psql -U masal_user -d masal_fabrikasi -c "
SELECT count(*) as active_connections
FROM pg_stat_activity
WHERE datname = 'masal_fabrikasi';
"
```

---

## Next Steps

1. ✅ Start PostgreSQL with Docker
2. ✅ Run migrations
3. ✅ Verify tables created
4. Update services to use database
5. Migrate existing JSON data
6. Test thoroughly
7. Switch to PostgreSQL-only mode

**You're ready to use PostgreSQL!** 🚀
