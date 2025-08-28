#!/bin/bash

# Start services for production with concurrency improvements

echo "🚀 Starting services with concurrency optimizations..."

# Start Redis server (if not already running)
echo "📦 Starting Redis server..."
redis-server --daemonize yes --port 6379

# Start Celery worker in background
echo "🔄 Starting Celery worker..."
celery -A personal_site worker --loglevel=info --detach

# Start Celery beat scheduler for periodic tasks
echo "⏰ Starting Celery beat scheduler..."
celery -A personal_site beat --loglevel=info --detach

# Start Django application with Gunicorn (async workers)
echo "🌐 Starting Django with Gunicorn (async workers)..."
gunicorn personal_site.asgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 60 \
    --keep-alive 2 \
    --access-logfile - \
    --error-logfile -

echo "✅ All services started successfully!"
echo ""
echo "🔧 Service URLs:"
echo "  - Django App: http://localhost:8000"
echo "  - Redis: localhost:6379"
echo ""
echo "📊 Monitor services:"
echo "  - Celery workers: celery -A personal_site inspect active"
echo "  - Redis status: redis-cli ping"