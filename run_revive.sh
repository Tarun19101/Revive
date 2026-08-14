#!/bin/bash

echo "🚀 Starting Revive..."
echo ""

cd "$(dirname "$0")"
source .venv/bin/activate

echo "Starting Django server..."
python manage.py runserver &
DJANGO_PID=$!

sleep 2

echo "Starting Tailwind CSS watcher..."
python manage.py tailwind start &
TAILWIND_PID=$!

echo ""
echo "✅ Revive is running!"
echo "📱 Open your browser: http://127.0.0.1:8000/"
echo ""
echo "Press Ctrl+C to stop both servers..."
echo ""

# Wait for Ctrl+C
trap "kill $DJANGO_PID $TAILWIND_PID 2>/dev/null; echo 'Revive stopped.'; exit" SIGINT
wait
