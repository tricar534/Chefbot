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

# Set ports to public (if in Codespaces)
if [ -n "$CODESPACE_NAME" ]; then
    echo "🔓 Setting ports to public..."
    gh codespace ports visibility 5000:public -c $CODESPACE_NAME 2>/dev/null || echo "⚠️  Could not auto-set port 5000 to public. Please do it manually in PORTS tab."
    gh codespace ports visibility 5173:public -c $CODESPACE_NAME 2>/dev/null || echo "⚠️  Could not auto-set port 5173 to public. Please do it manually in PORTS tab."
    echo ""
fi

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
if [ -z "$CODESPACE_NAME" ]; then
    echo "📍 Running locally"
else
    echo "📍 Running in Codespaces"
    echo "🔗 Backend: https://$CODESPACE_NAME-5000.app.github.dev"
    echo "🔗 Frontend: https://$CODESPACE_NAME-5173.app.github.dev"
fi
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user to stop
wait