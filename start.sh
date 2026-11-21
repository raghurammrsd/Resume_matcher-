#!/usr/bin/env bash
set -e

echo "=================================================="
echo "    TalentMatch AI - Starting Development Servers"
echo "=================================================="

# Activate virtualenv
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ensure sample resumes exist
if [ ! -d "backend/data/sample_resumes" ] || [ $(ls -1 backend/data/sample_resumes | wc -l) -lt 5 ]; then
    echo "[1/3] Generating benchmark synthetic candidate resumes..."
    python3 backend/data/generate_synthetic_resumes.py
fi

# Start FastAPI Backend in background
echo "[2/3] Starting FastAPI backend on http://127.0.0.1:8000..."
export PYTHONPATH=.
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Function to kill backend on exit
trap "kill $BACKEND_PID 2>/dev/null || true" EXIT

# Start Frontend
echo "[3/3] Starting Vite React frontend on http://localhost:5173..."
cd frontend
npm run dev

wait
