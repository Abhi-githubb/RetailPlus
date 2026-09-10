# RetailPulse Multi-Stage Production Container
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    STREAMLIT_PORT=8501

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies and install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project source code
COPY . .

# Run ETL pipeline if database doesn't exist
RUN python run_pipeline.py

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501

# Default entrypoint starts FastAPI; can be overridden in docker-compose or command line
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
