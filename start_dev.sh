#!/bin/bash

# Development setup with concurrency improvements

echo "🔧 Starting development environment with concurrency..."

# Install requirements if needed
echo "📦 Installing/updating requirements..."
pip install -r requirements.txt

# Start Redis server in background (development)
echo "🔴 Starting Redis server..."
redis-server --port 6379 &

# Wait a moment for Redis to start
sleep 2

# Start Celery worker in background
echo "🔄 Starting Celery worker (development)..."
celery -A personal_site worker --loglevel=info &

# Start Django development server with async support
echo "🌐 Starting Django development server..."
python manage.py runserver 0.0.0.0:8000

echo "🎉 Development environment ready!"
echo ""
echo "🔧 Development URLs:"
echo "  - Django App: http://localhost:8000"
echo "  - Admin: http://localhost:8000/admin/"
echo "  - Redis: localhost:6379"