# Multi-stage build for smaller final image
# Stage 1: builder
FROM python:3.12-slim as builder

WORKDIR /app

# No build deps needed when using *-binary wheels (psycopg2-binary, etc.)

# Copy only requirements first for better layer caching
COPY requirements*.txt ./
RUN pip install --no-cache-dir --user -r $(test -f requirements-production.txt && echo requirements-production.txt || echo requirements.txt)

# Stage 2: runtime
FROM python:3.12-slim

WORKDIR /app

# Runtime deps only (no build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create storage and logs dirs
RUN mkdir -p storage/images storage/audio storage/video storage/exports storage/temp logs

# Optional: run as non-root (uncomment and add user if desired)
# RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
# USER appuser

EXPOSE 8000

# Migrations then start (use ; so container stays up for debug if migration fails)
CMD ["sh", "-c", "alembic upgrade head; uvicorn main:app --host 0.0.0.0 --port 8000"]
