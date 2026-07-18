#!/bin/bash

# Exit on error
set -e

echo "=========================================="
echo "🚀 Starting Backend (FastAPI)"
echo "=========================================="

if [ ! -d "venv" ]; then
  echo "📦 Setting up Python backend environment..."
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
else
  echo "✅ Backend Python environment already setup."
  source venv/bin/activate
fi

echo "📡 Starting backend on http://0.0.0.0:5001..."
uvicorn src.main:app --host 0.0.0.0 --port 5001 --reload
