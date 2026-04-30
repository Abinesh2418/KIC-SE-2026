#!/bin/bash
set -e

echo "=== KIC AIML 2026 Assessment — Starting ==="

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

# Generate migrations for quiz
echo "Generating migrations..."
python manage.py makemigrations quiz --noinput 2>&1 || true

# Apply all migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Import questions if not already done
echo "Importing questions..."
python manage.py import_questions --csv KIC-SE-MCQ.csv 2>&1 || true

# Create superuser if env vars are set
if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_PASSWORD" ]; then
    echo "Creating admin user..."
    DJANGO_SETTINGS_MODULE=software_engineer.settings python -c "
import django; django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${ADMIN_USERNAME}').exists():
    User.objects.create_superuser('${ADMIN_USERNAME}', '${ADMIN_EMAIL:-iqube@kic.ac.in}', '${ADMIN_PASSWORD}')
    print('Admin user created.')
else:
    print('Admin user already exists.')
" 2>&1 || true
fi

echo "=== KIC AIML 2026 Assessment ready on port 8000 ==="
exec gunicorn software_engineer.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile -
