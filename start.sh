#!/bin/bash

# E-commerce Product Recommender Startup Script

echo "🚀 Starting E-commerce Product Recommender System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
pip install requests

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env_example.txt .env
    echo "📝 Please edit .env file and add your OpenAI API key"
    echo "   You can get an API key from: https://platform.openai.com/api-keys"
fi

# Initialize database
echo "🗄️  Initializing database with sample data..."
python init_db.py

# Start the Flask server
echo "🌐 Starting Flask server..."
echo "📱 Frontend will be available at: http://localhost:8080/frontend.html"
echo "🔗 API will be available at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Flask server in background
/Users/milindranjan/Downloads/Unthinkable/new_venv/bin/python -m flask run --host=0.0.0.0 --port=5000 &
FLASK_PID=$!

# Start simple HTTP server for frontend
python3 -m http.server 8080 &
HTTP_PID=$!

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $FLASK_PID 2>/dev/null
    kill $HTTP_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Wait for processes
wait
