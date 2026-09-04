# ==============================================================================
# Multi-Stage Dockerfile for Unified Full-Stack Forensic Deployment on Render
# ==============================================================================

# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci --silent

COPY frontend/ ./
RUN npm run build

# Stage 2: Python FastAPI Backend with Embedded React Frontend
FROM python:3.11-slim AS production

WORKDIR /app

# Install system dependencies for build, libpq, and cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy compiled frontend production assets from Stage 1
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Create uploads directory for evidence processing
RUN mkdir -p /app/backend/uploads /app/uploads

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

CMD ["sh", "-c", "python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8000}"]
