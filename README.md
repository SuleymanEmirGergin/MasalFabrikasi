# Masal Fabrikası AI - Backend & Frontend

AI-powered interactive story generation platform for children.

## 🚀 Quick Start (Docker)

The fastest way to get the system up and running is via Docker Compose.

### Prerequisites
- Docker & Docker Compose
- Environment variables (copy `.env.example` to `backend/.env`)

### System Up
One command to start Database, Redis, Backend API, Celery Worker, and Frontend:

```bash
make up
# OR
docker-compose up --build -d
```

### Verification
1. **API Health**: `curl http://localhost:8000/health/live`
2. **Docs**: Open `http://localhost:8000/docs`
3. **Frontend**: Open `http://localhost:19006`
4. **Celery**: Check logs `docker-compose logs -f celery_worker`

### Database Migrations
Migrations are applied automatically in the container (via entrypoint) or can be run manually:

```bash
docker-compose exec backend alembic upgrade head
```

### Running Tests
Run the full test suite in the container:

```bash
docker-compose exec backend pytest
```

## 🛠 Operational Guides

### Security
- **Auth**: Tokens are hashed (SHA256) and single-use.
- **Secrets**: Logs are redacted. Check `backend/app/core/logging_config.py`.
- **Environment**: Critical variables are validated on startup.

### Migrations
See [Migration Rollback Guide](docs/runbooks/migrations.md) for handling database schema changes.

### Monitoring
- **Metrics**: Prometheus metrics available at `/metrics` (protect in production).
- **Sentry**: Configure `SENTRY_DSN` for error tracking with PII scrubbing.

## 🏗 Architecture
- **Backend**: FastAPI (Python 3.12)
- **Frontend**: Expo (React Native)
- **Database**: PostgreSQL 15 (AsyncPG + SQLAlchemy)
- **Queue**: Celery + Redis
