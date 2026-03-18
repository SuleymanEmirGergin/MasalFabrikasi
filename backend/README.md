# Masal Fabrikası AI 🎭

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-Latest-DC382D.svg?logo=redis&logoColor=white)](https://redis.io/)

**AI-powered story generation platform with 500+ features** - Create, customize, and analyze stories using advanced AI, complete with illustrations, voice narration, and interactive elements.

## 🌟 Features

- **🤖 AI Story Generation**: GPT-4 powered story creation in multiple languages
- **🎨 Image Generation**: Automatic illustration creation for stories
- **🎙️ Text-to-Speech**: High-quality voice narration with ElevenLabs
- **👥 Character Chat**: Interactive conversations with story characters
- **📊 Analytics Dashboard**: Reading statistics, streaks, and insights
- **🏆 Gamification**: Achievements, XP system, leaderboards
- **🌙 Bedtime Mode**: Specialized calm stories for sleep time
- **📚 Smart Organization**: Collections, tags, and smart filters
- **⏰ Scheduling**: Reading routines and reminders
- **👨‍👩‍👧 Parental Dashboard**: Child reading development tracking

## 🚀 Quick Start

### Prerequisites

- **Python 3.9–3.13** (recommended: **3.11** or **3.12**). Python 3.14 is not yet supported: `pydantic`/`pydantic-core` in this project require building from source on 3.14 and fail due to `ForwardRef` API changes. Use a 3.12 venv if you have 3.14 installed:
  ```powershell
  py -3.12 -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```
- PostgreSQL 15+
- Redis
- Docker & Docker Compose (recommended)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd masal-fabrikasi
```

2. **Setup environment**:
```bash
cd backend
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Run with Docker** (Recommended):
```bash
docker-compose up --build
```

4. **Or run manually**:
```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start API server
uvicorn main:app --reload

# Start Celery worker (separate terminal)
celery -A app.celery_app worker --loglevel=info
```

### Access the Application

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Celery Flower**: http://localhost:5555

## 📝 Environment Variables

Essential environment variables (see `.env.example` for complete list):

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/masal_fabrikasi
REDIS_URL=redis://localhost:6379/0

# AI Services
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...

# Storage (Supabase)
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_STORAGE_BUCKET=masal-fabrikasi

# Authentication & Security
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Optional: Monitoring
SENTRY_DSN=...
```

### Wiro (GPT-5 nano, gpt-oss-20b)

Story generation and several AI features use [Wiro](https://wiro.ai) Run API. Required:

- **WIRO_API_KEY** – API key from Wiro dashboard (required for story/gen). **Keep this only in `.env`; do not commit it to the repo or expose it in logs.**
- **GPT_BASE_URL** – `https://api.wiro.ai/v1` (default).
- **GPT_MODEL** – Model slug; e.g. `openai/gpt-oss-20b` or `openai/gpt-5-nano`.

To use GPT-5 nano for story generation, set in `.env`:

```bash
GPT_MODEL=openai/gpt-5-nano
WIRO_API_KEY=your_wiro_api_key
```

Optional: **WIRO_TASK_TIMEOUT_SECONDS** (default `120`) for task wait timeout; **WIRO_API_SECRET** for HMAC-signed requests where supported.

**Docker / env_file:** When running with Docker Compose, the backend service loads `backend/.env` via `env_file`. Set Wiro variables there (or in `docker-compose.yml` under `backend.environment`): `WIRO_API_KEY`, `GPT_MODEL`, `GPT_BASE_URL`, and optionally `WIRO_TASK_TIMEOUT_SECONDS`. Do not commit `.env`; use `.env.example` as a template.

## 🏗️ Architecture

```
masal-fabrikasi/
├── backend/
│   ├── app/
│   │   ├── core/          # Core functionality (config, database, exceptions)
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # Business logic
│   │   ├── tasks/         # Celery background tasks
│   │   ├── utils/         # Utilities (pagination, sanitization)
│   │   └── middleware/    # Custom middleware
│   ├── alembic/           # Database migrations
│   ├── tests/             # Test suite
│   └── scripts/           # Utility scripts
├── frontend/              # React frontend (separate repo)
└── docker-compose.yml     # Docker orchestration
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only

# View coverage report
open htmlcov/index.html

# Coverage: CI enforces minimum 30% (--cov-fail-under=30). Target for new code: 50%+.
pytest --cov=app --cov-report=term-missing

# Stripe tests (unit tests run without Docker; use SQLite + aiosqlite via DATABASE_URL=sqlite:///./test.db)
pytest tests/unit/test_stripe_service.py -v
# Integration tests that use TestClient may require full env (PostgreSQL + Redis) or Docker; see .github/workflows/ci-cd.yml.
```

## 📊 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/health/detailed` | Detailed system health |
| POST | `/api/generate-story` | Generate a new story |
| GET | `/api/stories` | List user stories |
| GET | `/api/stories/{id}` | Get story details |

### Feature Endpoints

- `/api/value/*` - Analytics, achievements, organization
- `/api/bedtime/*` - Bedtime mode features
- `/api/voice-cloning/*` - Voice cloning
- `/api/chat/*` - Character chat
- `/api/tools/*` - Magic canvas and AI tools

See [API Documentation](http://localhost:8000/docs) for complete reference.

## 🔧 Development

### Code Quality

```bash
# Format code
black app/

# Lint code
ruff check app/

# Type checking (if using mypy)
mypy app/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Background Tasks

Monitor Celery tasks via Flower:
```bash
celery -A app.celery_app flower --port=5555
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=false` in production
- [ ] Use strong `JWT_SECRET_KEY`
- [ ] Configure proper CORS origins
- [ ] Setup SSL/TLS certificates
- [ ] Configure database backups
- [ ] Setup monitoring (Sentry, etc.)
- [ ] Review rate limiting settings
- [ ] Setup CDN for static assets
- [ ] Configure Redis persistence
- [ ] Setup log aggregation

### Docker Production

```bash
# Build production image
docker build -t masal-fabrikasi:latest .

# Run with production config
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Monitoring

The application includes comprehensive health checks:

```bash
# Basic health
curl http://localhost:8000/health

# Detailed system health
curl http://localhost:8000/health/detailed
```

Monitors:
- Database connectivity
- Redis status
- Celery workers
- Disk space
- API response times

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Email**: support@masalfabrikasi.ai

## 🎯 Roadmap

- [x] Core story generation
- [x] Image and TTS integration
- [x] Analytics and gamification
- [x] Value features (cost-free)
- [x] Production improvements
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration
- [ ] Advanced AI features
- [ ] Multi-language support expansion

## 🙏 Acknowledgments

- OpenAI for GPT-4
- ElevenLabs for voice cloning
- FastAPI framework
- The open-source community

---

**Made with ❤️ for storytellers**
