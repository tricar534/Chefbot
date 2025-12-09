#!/bin/bash

echo "🚀 Setting up Chefbot..."

# Install backend dependencies
echo "📦 Installing Python packages..."
cd backend
pip install -r requirements.txt > /dev/null 2>&1
cd ..

# Install frontend dependencies
echo "📦 Installing Node packages..."
cd frontend
npm install > /dev/null 2>&1
cd ..

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Make port 5000 public in the PORTS tab"
echo "2. Run: cd backend && python app.py"
echo "3. Run (in new terminal): cd frontend && npm run dev"
echo ""