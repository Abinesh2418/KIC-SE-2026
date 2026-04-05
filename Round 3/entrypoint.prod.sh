#!/bin/bash
set -e

echo "=== ML Fest Round 3 — Starting ==="

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

# Generate migrations for ctf
echo "Generating migrations..."
python manage.py makemigrations ctf --noinput 2>&1 || true

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

# Seed challenges
echo "Seeding challenges..."
python manage.py seed_challenges 2>&1 || true

# Create admin user
echo "Creating admin user..."
if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_PASSWORD" ]; then
    python manage.py create_admin \
        --username "${ADMIN_USERNAME}" \
        --email "${ADMIN_EMAIL:-teamqernels@gmail.com}" \
        --password "${ADMIN_PASSWORD}" 2>&1 || true
else
    python manage.py create_admin 2>&1 || true
fi

echo "=== Round 3 ready on port 8000 ==="
exec gunicorn mlfest.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile -
