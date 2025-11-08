#!/bin/bash

echo "🚀 Lattice with Knot - Quick Start"
echo ""
echo "📋 Prerequisites:"
echo "  • Backend: Poetry installed"
echo "  • Frontend: pnpm installed"
echo "  • Knot credentials in backend/.env"
echo ""
echo "Starting servers..."
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this from the project root directory"
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup INT TERM

# Start backend
echo "🔧 Starting backend..."
cd backend
poetry run uvicorn app.main:app --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
pnpm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Servers started!"
echo ""
echo "🌐 URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "🧪 Test Flow:"
echo "  1. Go to http://localhost:3000/login"
echo "  2. Login as demo@example.com / demo123"
echo "  3. Should redirect to /onboarding"
echo "  4. Click 'Connect with Knot'"
echo "  5. Knot popup should appear!"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait

