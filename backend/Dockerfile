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

# Create storage directories
RUN mkdir -p storage/images storage/audio

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
