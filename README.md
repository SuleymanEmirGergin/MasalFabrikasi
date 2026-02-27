# Masal Fabrikası 🎨✨

[![CI/CD Pipeline](https://github.com/yourusername/masal-fabrikasi/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/yourusername/masal-fabrikasi/actions/workflows/ci-cd.yml)
[![codecov](https://codecov.io/gh/yourusername/masal-fabrikasi/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/masal-fabrikasi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React Native](https://img.shields.io/badge/React%20Native-0.76-61DAFB?logo=react)](https://reactnative.dev/)

![Masal Fabrikası Banner](./assets/banner.png)

**AI-Powered Interactive Storytelling Platform for Children**

Transform simple ideas into magical, personalized stories with multi-modal AI: text, images, audio, and video.

---

## 🌟 Features

### Core AI Features (Powered by Wiro AI & Supabase)
- 🤖 **Multi-Modal Story Generation**
  - **Text**: Google Gemini Flash & GPT-OSS for creative storytelling
  - **Images**: Google Imagen v4 (Fast & Ultra quality)
  - **Audio**: ElevenLabs TTS with voice cloning
  - **Video**: Google Veo3 for story animations
  - **Voice**: OpenAI Whisper for Turkish speech-to-text
- 🎨 **Magic Canvas** - Turn children's drawings into professional illustrations
- 🗣️ **Character Chat** - AI-powered conversations with story characters
- 🎭 **Interactive Stories** - Choose-your-own-adventure branching narratives
- 🌍 **Community Library** - Share and discover stories
- 🌙 **Bedtime Mode** - OLED-friendly dark theme with ambient sounds
- 💡 **Smart Room** - IoT light synchronization with story atmosphere

### Technical Excellence
- ⚡ **Real-time Updates** - WebSocket-based progress tracking with Socket.IO
- 🔒 **Enterprise Security** - Supabase Auth, rate limiting, circuit breakers
- 🚀 **Performance Optimized**
  - Async/await architecture (AsyncOpenAI, redis.asyncio)
  - Gzip compression
  - Redis caching with automatic expiration
  - Database connection pooling & query optimization
  - N+1 query prevention with eager loading
- 📊 **Production Monitoring**
  - Query performance profiling
  - Memory leak detection
  - Connection pool monitoring
  - Slow query logging
- 💳 **Monetization** - Stripe payment integration
- 🎯 **Gamification** - XP, levels, achievements, leaderboards

---

## 🏗️ Architecture

### Tech Stack
**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL with pgvector extension
- Redis (caching + Celery broker)
- Celery (async task processing)
- Supabase (Auth + Storage + Realtime)
- Socket.IO (realtime updates)

**Frontend:**
- React Native 0.76.5
- Expo SDK ~54
- Supabase Client
- Socket.IO Client

**AI Providers:**
- Wiro AI (unified API for Google Gemini, Imagen, Veo3, Whisper, ElevenLabs)
- Direct integrations as fallbacks

```
masal-fabrikası/
├── backend/              # FastAPI + PostgreSQL + Celery
│   ├── app/
│   │   ├── core/        # Config, DB, Middleware, Resilience
│   │   ├── models/      # SQLAlchemy models with indexes
│   │   ├── routers/     # API endpoints (40+ routers)
│   │   ├── services/    # Business logic (Wiro client, AI services)
│   │   ├── tasks/       # Celery async tasks
│   │   ├── middleware/  # Custom middleware (pagination, monitoring)
│   │   └── components/  # Reusable utilities
│   └── tests/           # pytest suite (80+ test files)
├── frontend/            # React Native (Expo)
│   ├── src/
│   │   ├── components/  # 16 reusable components (Toast, Loading, Skeleton, etc.)
│   │   ├── screens/     # 34 screens
│   │   ├── context/     # React contexts (Auth, Story, Bedtime, etc.)
│   │   └── services/    # API clients
│   └── __tests__/       # Jest tests
└── docker-compose.yml   # Full stack deployment
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- **Wiro AI API Key** - [Get it here](https://wiro.ai)
- **Supabase Account** - [Create project](https://supabase.com)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/masal-fabrikasi.git
cd masal-fabrikasi
```

### 2. Environment Setup
```bash
# Backend
cp backend/.env.example backend/.env

# Add your API keys to backend/.env:
# - W

IRO_API_KEY & WIRO_API_SECRET (from Wiro AI)
# - SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY
# - SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")

# Frontend
cp frontend/.env.example frontend/.env
# Add EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY
```

### 3. Start with Docker
```bash
docker-compose up -d
```

Services will be available at:
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 4. Run Database Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### 5. Start Frontend
```bash
cd frontend
npm install
npx expo start
```

---

## 📦 Manual Installation

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start services
uvicorn main:app --reload  # API server
celery -A app.celery_app worker -l info  # Background worker
```

### Frontend
```bash
cd frontend
npm install
npx expo start
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
# Coverage report: backend/htmlcov/index.html
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 🔒 Security

### Implemented Security Measures
- **Rate Limiting**: 10 stories/minute per worker (Celery), 5 requests/minute per IP on endpoints
- **Input Validation**: Pydantic models for all requests
- **SQL Injection**: Prevented via SQLAlchemy ORM
- **XSS Protection**: React auto-escaping
- **Authentication**: Supabase Auth with JWT validation
- **API Pagination**: Max 100 items per page enforced
- **Circuit Breakers**: Automatic failure handling for external APIs
- **Secret Management**: Environment variables only
- **CORS**: Configurable allowed origins

### Security Hardening Checklist
- [x] SECRET_KEY auto-generated with secure random
- [x] Database passwords changed from defaults
- [x] DEBUG=false in production
- [x] CORS restricted to known origins
- [x] Rate limiting enabled
- [x] Query logging available for monitoring
- [x] Connection limits on WebSocket (10k max)
- [x] API pagination enforced globally

---

## 📊 Monitoring & Performance

### Built-in Monitoring Endpoints
```bash
# Memory usage stats
GET /api/debug/memory

# WebSocket connections
GET /api/debug/connections

# Health check
GET /api/health
```

### Performance Features
- **Async Architecture**: Non-blocking I/O throughout
- **Caching**: Redis with auto-expiration (1 hour results, 5 min endpoints)
- **Compression**: Gzip for responses >1KB
- **Database Optimization**:
  - Connection pooling (20 connections, 10 overflow)
  - Eager loading to prevent N+1 queries
  - Indexed columns for common queries
- **Celery Optimization**:
  - Worker recycling (100 tasks)
  - Result compression
  - Task time limits (10 min hard, 9 min soft)

### Logging
- **Format**: Structured JSON logs (production) / Human-readable (dev)
- **Levels**: INFO, WARNING, ERROR
- **Slow Query Detection**: Logs queries >1 second (enable with ENABLE_QUERY_LOGGING=true)

---

## 🌐 Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive production deployment guide including:
- Railway / Render / Fly.io deployment
- Environment variables checklist
- Database backup strategies
- SSL/TLS setup
- Monitoring & alerting
- Scaling recommendations

---

## 🎨 Frontend Polish Features

Professionally designed UX components:
- **LoadingSpinner**: 3 variants (inline, overlay, fullscreen)
- **SkeletonLoader**: Shimmer animations for perceived performance
- **EmptyState**: Beautiful zero-data screens with CTAs
- **Toast Notifications**: Global feedback system (success, error, warning, info)
- **Animations**: Micro-interactions (button press, fade-in, slide, pulse)

---

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file.

---

## 🙏 Acknowledgments

- **Wiro AI** - Unified API for Google Gemini, Imagen, Veo3, Whisper, ElevenLabs
- **Supabase** - Authentication, Storage, Realtime database
- **OpenAI** - GPT models & embeddings
- **FastAPI** - Modern Python web framework
- **Expo** - React Native development platform

---

## 📞 Support

- **Email**: support@masalfabrikasi.app
- **Issues**: [GitHub Issues](https://github.com/yourusername/masal-fabrikasi/issues)
- **Documentation**: [Full API Docs](http://localhost:8000/docs)

---

**Made with ❤️ for children's imagination**

🌟 **Star us on GitHub if you find this project helpful!**
