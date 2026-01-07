FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (use production requirements if exists, fallback to regular)
COPY requirements*.txt ./

# Install Python dependencies (prefer production requirements)
RUN pip install --no-cache-dir -r $(test -f requirements-production.txt && echo requirements-production.txt || echo requirements.txt)

# Copy application
COPY . .

# Create storage and logs directories
RUN mkdir -p storage/images storage/audio logs

# Expose port
EXPOSE 8000

# Run migrations and start application (using ; to allow debug even if migration fails)
CMD ["sh", "-c", "alembic upgrade head; uvicorn main:app --host 0.0.0.0 --port 8000"]
