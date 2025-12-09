#!/bin/bash

echo "🚀 Starting Chefbot..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "🔧 Starting backend on port 5000..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 2

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Both servers are running!"
echo ""
echo "⚠️  IMPORTANT: Go to the PORTS tab and make port 5000 PUBLIC"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user to stop
wait