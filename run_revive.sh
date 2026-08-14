#!/bin/bash

echo "🚀 Starting Revive..."
echo ""

cd "$(dirname "$0")"
source .venv/bin/activate

gnome-terminal -- bash -c "cd $(pwd) && source .venv/bin/activate && python manage.py runserver; exec bash" &
sleep 2
gnome-terminal -- bash -c "cd $(pwd) && source .venv/bin/activate && python manage.py tailwind start; exec bash" &

echo "✅ Revive is running!"
echo "📱 Open your browser: http://127.0.0.1:8000/"

wait
