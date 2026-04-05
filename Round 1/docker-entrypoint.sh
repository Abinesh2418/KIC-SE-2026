#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
while ! python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('${DB_HOST:-db}', ${DB_PORT:-5432}))
    s.close()
    exit(0)
except:
    exit(1)
" 2>/dev/null; do
    echo "PostgreSQL is not ready yet... retrying in 2s"
    sleep 2
done
echo "PostgreSQL is ready!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Importing questions..."
python manage.py import_questions

echo "Creating superuser (if not exists)..."
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlfest.settings')
django.setup()
from django.contrib.auth.models import User
username = os.environ.get('ADMIN_USERNAME', 'teamqernels@gmail.com')
password = os.environ.get('ADMIN_PASSWORD', 'teamqernels@iQube42')
email = os.environ.get('ADMIN_EMAIL', 'teamqernels@gmail.com')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superuser {username} created')
else:
    print(f'Superuser {username} already exists')
"

echo "Starting gunicorn on 0.0.0.0:7737..."
exec gunicorn mlfest.wsgi --bind 0.0.0.0:7737 --workers 3 --log-file -
