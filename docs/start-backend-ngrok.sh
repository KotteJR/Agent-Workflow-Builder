#!/bin/bash
# Start backend with ngrok tunnel

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    exit 0
}

# Set trap BEFORE starting processes
trap cleanup SIGINT SIGTERM EXIT

echo "🚀 Starting backend on port 8000..."
cd backend
source .venv/bin/activate

# Load environment variables from .env if it exists
if [ -f .env ]; then
    echo "📝 Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found. Make sure to set environment variables!"
    echo "   Create backend/.env or export them in your shell"
fi

# Start backend in background
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
sleep 2

echo ""
echo "🌐 Starting ngrok tunnel..."
echo "   Copy the HTTPS URL and set it in Vercel as BACKEND_URL"
echo ""

# Start ngrok (foreground - script waits here)
ngrok http 8000

