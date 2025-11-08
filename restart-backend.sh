#!/bin/bash

echo "🔄 Restarting Backend..."

# Kill existing backend
echo "Stopping existing backend..."
kill -9 $(lsof -ti:8000) 2>/dev/null
sleep 2

# Start backend
cd /Users/aryamangoenka/Desktop/Lattice./code-2/backend
echo "Starting backend..."
poetry run uvicorn app.main:app --reload


