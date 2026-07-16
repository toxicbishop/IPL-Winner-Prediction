# Use official Python lightweight image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PostgreSQL (psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DB_ENGINE=postgres
ENV POSTGRES_HOST=db
ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=postgres
# Do NOT hardcode secrets here — pass POSTGRES_PASSWORD at runtime via docker-compose or -e flag
ENV POSTGRES_DB=ipl

# Default command: run the full pipeline with sanity check
CMD ["python", "main.py", "--mode", "all", "--sanity-check"]
