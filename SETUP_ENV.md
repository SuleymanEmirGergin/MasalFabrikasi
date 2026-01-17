# Environment Setup Guide

This guide explains how to configure the environment variables for the Masal Fabrikası backend.

## Quick Start

1. Copy `.env.example` to `.env`:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Update the values in `.env` with your actual credentials.

## Configuration Sections

### Core Settings
- `SECRET_KEY`: Critical for security. Use `openssl rand -hex 32` to generate one.
- `DEBUG`: Set to `true` for development, `false` for production.
- `FRONTEND_URL`: URL where the frontend application is running (for CORS and email links).

### Database & Redis
- `DATABASE_URL`: Connection string for PostgreSQL.
  - Format: `postgresql://user:password@host:port/dbname`
- `REDIS_URL`: Connection string for Redis. Used for caching and Celery task queue.

### AI Providers
The platform uses a multi-provider strategy for cost optimization:
- **Google Gemini**: Used for story drafting and embeddings (Low cost/High speed).
- **OpenAI/Wiro**: Used for final story polishing and Speech-to-Text.
- **Imagen/Veo**: Used for Image and Video generation.

### Payments (Stripe)
- `STRIPE_SECRET_KEY`: Secret key from Stripe Dashboard.
- `STRIPE_WEBHOOK_SECRET`: Secret for validating webhooks. You can get this by running the Stripe CLI: `stripe listen --forward-to localhost:8000/api/stripe/webhook`.

### Email (SMTP)
Required for registration verification and password reset emails.
- For Gmail, use an "App Password" if 2FA is enabled.

### Monitoring (Sentry)
- `SENTRY_DSN`: Data Source Name from your Sentry project settings. Leave empty to disable Sentry logging.
