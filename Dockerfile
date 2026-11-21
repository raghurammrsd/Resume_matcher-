# Multi-stage build for unified full-stack container

# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend & Unified Server
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install lightweight CPU-only PyTorch (saves ~2GB and prevents 512MB RAM OOM)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY backend/requirements.txt .
RUN grep -v "^torch" requirements.txt > reqs_no_torch.txt && pip install --no-cache-dir -r reqs_no_torch.txt

# Pre-download SentenceTransformer model weights at BUILD time so NO runtime downloads occur
RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy backend source
COPY backend/ ./backend/

# Pre-generate sample resumes during build so boot time is instant
RUN python3 backend/data/generate_synthetic_resumes.py

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

ENV PYTHONPATH=/app
ENV PORT=10000
EXPOSE 10000

# Start server reading $PORT dynamically
CMD ["python3", "-m", "backend.app.run"]
