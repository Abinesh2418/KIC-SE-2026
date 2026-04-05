#!/bin/bash
set -e

echo "=== ML Fest Round 2 — Starting ==="

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! python -c "
import socket
s = socket.create_connection(('${DB_HOST:-db}', int('${DB_PORT:-5432}')), timeout=2)
s.close()
" 2>/dev/null; do
    echo "  DB not ready, retrying in 2s..."
    sleep 2
done
echo "PostgreSQL is ready!"

# Generate migrations for debugchallenge
echo "Generating migrations..."
python manage.py makemigrations debugchallenge --noinput 2>&1 || true

# Apply migrations (shared_auth already applied by R1, will skip)
echo "Applying migrations..."
max_retries=5
retry=0
until python manage.py migrate --noinput 2>&1; do
    retry=$((retry + 1))
    if [ $retry -ge $max_retries ]; then
        echo "Migration failed after $max_retries retries."
        exit 1
    fi
    echo "  Migration attempt $retry failed, retrying in 5s..."
    sleep 5
done

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Setup challenges
echo "Setting up challenges..."
python manage.py setup_challenges 2>&1 || true

# Create superuser if env vars are set
if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_PASSWORD" ]; then
    echo "Creating admin user (Round 2)..."
    DJANGO_SETTINGS_MODULE=mlfest.settings python -c "
import django; django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${ADMIN_USERNAME}').exists():
    User.objects.create_superuser('${ADMIN_USERNAME}', '${ADMIN_EMAIL:-teamqernels@gmail.com}', '${ADMIN_PASSWORD}')
    print('Admin user created.')
else:
    print('Admin user already exists.')
" 2>&1 || true
fi

echo "=== Round 2 ready on port 8000 ==="
exec gunicorn mlfest.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile -
