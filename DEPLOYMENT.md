# Production Deployment Guide

## 🚀 Deployment Platforms

### Option 1: Railway (Recommended)

**Why Railway:**
- Automatic GitHub deployments
- Built-in PostgreSQL & Redis
- Environment variable management
- Easy scaling
- Free tier available

**Steps:**

1. **Connect Repository**
   ```bash
   # Push your code to GitHub first
   git push origin main
   ```

2. **Create New Project on Railway**
   - Visit [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

3. **Add Services**
   - **PostgreSQL**: Click "New" → "Database" → "PostgreSQL"
   - **Redis**: Click "New" → "Database" → "Redis"
   - **Backend**: Should auto-detect from Dockerfile
   - **Celery Worker**: Add new service, same repo, command: `celery -A app.celery_app worker -l info`

4. **Configure Environment Variables**
   Add to Backend service:
   ```bash
   # AI APIs
   WIRO_API_KEY=your_actual_key
   WIRO_API_SECRET=your_actual_secret
   
   # Database (auto-set by Railway)
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   
   # Security
   SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
   DEBUG=false
   
   # Supabase
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_KEY=your_service_key
   
   # CORS
   CORS_ORIGINS=https://your-frontend-url.app
   
   # Optional
   SENTRY_DSN=your_sentry_dsn
   ```

5. **Deploy**
   - Railway will auto-deploy on push to main
   - Check logs for any errors
   - Run migrations: `railway run alembic upgrade head`

---

### Option 2: Render

**Steps:**

1. **Create Web Service**
   - Go to [render.com](https://render.com)
   - "New" → "Web Service"
   - Connect GitHub repo
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Create Background Worker**
   - "New" → "Background Worker"
   - Same repo
   - Start Command: `cd backend && celery -A app.celery_app worker -l info`

3. **Add PostgreSQL & Redis**
   - "New" → "PostgreSQL"
   - "New" → "Redis"

4. **Environment Variables** (same as Railway)

---

### Option 3: Fly.io

**Steps:**

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   fly auth login
   ```

2. **Initialize App**
   ```bash
   cd backend
   fly launch
   # Follow prompts, say NO to deploy immediately
   ```

3. **Create Databases**
   ```bash
   fly postgres create
   fly redis create
   ```

4. **Set Environment Variables**
   ```bash
   fly secrets set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
   fly secrets set WIRO_API_KEY=your_key
   fly secrets set WIRO_API_SECRET=your_secret
   # ... add all other variables
   ```

5. **Deploy**
   ```bash
   fly deploy
   ```

---

## 📱 Frontend Deployment (Expo)

### Option 1: EAS Build (Recommended)

**For Production APK/IPA:**

1. **Install EAS CLI**
   ```bash
   npm install -g eas-cli
   eas login
   ```

2. **Configure**
   ```bash
   cd frontend
   eas build:configure
   ```

3. **Build for Android**
   ```bash
   # Development build (for testing)
   eas build --profile development --platform android
   
   # Production build
   eas build --profile production --platform android
   ```

4. **Build for iOS**
   ```bash
   # Requires Apple Developer Account
   eas build --profile production --platform ios
   ```

5. **Submit to Stores**
   ```bash
   # Google Play
   eas submit --platform android
   
   # App Store
   eas submit --platform ios
   ```

### Option 2: Expo Go (Development Only)

```bash
cd frontend
npx expo start
# Scan QR code with Expo Go app
```

---

## 🔒 Production Security Checklist

### Critical Security Steps

- [ ] **SECRET_KEY**: Generated with secure random (auto in config.py)
- [ ] **Database**: Change default password (`CHANGE_THIS_PASSWORD` in .env)
- [ ] **DEBUG**: Set to `false` in production
- [ ] **CORS**: Restrict to your actual frontend domain
- [ ] **HTTPS**: Use SSL/TLS certificate (auto with Railway/Render)
- [ ] **API Keys**: Never commit to Git (use .env only)
- [ ] **Rate Limits**: Review and adjust based on expected load
- [ ] **Firewall**: Restrict database access to app servers only
- [ ] **Backups**: Schedule daily database backups

### Environment Variable Validation

Run before deployment:
```bash
cd backend
python -c "from app.core.env_validator import validate_environment; validate_environment()"
```

---

## 📊 Post-Deployment Monitoring

### Health Checks

```bash
# Basic health
curl https://your-api.com/api/health

# Detailed health (includes dependencies)
curl https://your-api.com/api/health/detailed

# Memory usage
curl https://your-api.com/api/debug/memory

# WebSocket connections
curl https://your-api.com/api/debug/connections
```

### Performance Monitoring

1. **Enable Query Logging**
   ```bash
   # Add to .env
   ENABLE_QUERY_LOGGING=true
   ```

2. **Set Up Sentry** (Error Tracking)
   ```bash
   # Add to .env
   SENTRY_DSN=https://your-project@sentry.io/123456
   ```

3. **Monitor Logs**
   ```bash
   railway logs  # Railway
   fly logs      # Fly.io
   # Or check dashboard on Render
   ```

---

## 📈 Scaling Recommendations

### Database Optimization

**When to scale:**
- Query response time >200ms
- Connection pool exhaustion
- High CPU usage on database

**How to scale:**
```bash
# Increase connection pool (app/core/database.py)
pool_size=50  # from 20
max_overflow=20  # from 10

# Add read replicas for high-read workloads
# Enable DB query caching
```

### Redis Optimization

**When to scale:**
- Memory usage >80%
- High eviction rate

**How to scale:**
- Upgrade Redis instance size
- Implement Redis clustering
- Set appropriate TTLs on cache keys

### Celery Workers

**When to scale:**
- Queue length consistently >10
- Task processing time >5 minutes

**How to scale:**
```bash
# Horizontal scaling
railway scale backend-worker --replicas 3

# Vertical scaling (increase memory/CPU)
# Or use autoscaling based on queue length
```

### Rate Limiting

**Production recommendations:**
```python
# In app/celery_app.py
task_annotations={
    "app.tasks.story_tasks.generate_full_story_task": {
        "rate_limit": "50/m",  # Increase from 10/m based on load
    }
}
```

---

## 💾 Backup Strategy

### Database Backups

**Automatic (Railway/Render):**
- Built-in daily backups
- 7-day retention (free tier)
- Upgrade plan for longer retention

**Manual Backup:**
```bash
# Export database
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup-20260105.sql
```

### File Storage Backups

With Supabase Storage:
- Automatic backups included
- Point-in-time recovery available
- Export via Supabase CLI if needed

---

## 🔐 SSL/TLS Configuration

**Free SSL with Let's Encrypt:**
- Railway: Auto-enabled ✅
- Render: Auto-enabled ✅
- Fly.io: Auto-enabled ✅

**Custom Domain:**
```bash
# Railway
railway domain your-domain.com

# Fly.io
fly certs create your-domain.com
```

---

## 📞 Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql://user:password@host:port/dbname

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

**2. Celery Worker Not Starting**
```bash
# Check Redis connection
redis-cli -u $REDIS_URL ping

# Verify worker logs
celery -A app.celery_app inspect active
```

**3. High Memory Usage**
```bash
# Check memory endpoint
curl https://your-api.com/api/debug/memory

# If >80%, increase instance size or implement:
# - Result expiration (already set to 1 hour)
# - Worker recycling (already set to 100 tasks)
```

**4. Slow API Response**
```bash
# Enable query logging
ENABLE_QUERY_LOGGING=true

# Check for slow queries in logs
# Optimize with indexes or caching
```

---

## 🎯 Launch Checklist

**Pre-Launch:**
- [ ] All environment variables set
- [ ] Database migrations run
- [ ] SSL certificate active
- [ ] Health checks passing
- [ ] Test all critical user flows
- [ ] Load testing completed (optional but recommended)
- [ ] Monitoring & alerts configured
- [ ] Backup strategy implemented
- [ ] Documentation updated

**Post-Launch:**
- [ ] Monitor error rates (Sentry)
- [ ] Check performance metrics
- [ ] Verify WebSocket connections stable
- [ ] Test Celery task processing
- [ ] Monitor database query performance
- [ ] Check memory usage trends

---

## 📚 Additional Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Expo EAS Build](https://docs.expo.dev/build/introduction/)
- [Supabase Production](https://supabase.com/docs/guides/platform/going-into-prod)
- [Celery Best Practices](https://docs.celeryq.dev/en/stable/userguide/optimizing.html)

---

**Need Help?**
- Open an issue on GitHub
- Check application logs first
- Review this guide's troubleshooting section
- Contact support@masalfabrikasi.app
