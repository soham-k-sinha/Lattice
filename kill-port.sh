#!/bin/bash

# Kill Port Helper Script
# Usage: ./kill-port.sh [PORT_NUMBER]
# Example: ./kill-port.sh 3000

PORT=${1:-3000}

echo "🔍 Checking port $PORT..."

PID=$(lsof -ti:$PORT)

if [ -z "$PID" ]; then
    echo "✅ Port $PORT is already free!"
    exit 0
fi

echo "📋 Process $PID is using port $PORT"
echo "🔫 Killing process..."

kill -9 $PID

sleep 1

# Verify
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "❌ Failed to kill process on port $PORT"
    exit 1
else
    echo "✅ Port $PORT is now free!"
    exit 0
fi

