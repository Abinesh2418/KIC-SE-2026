#!/usr/bin/env bash
# Build script for Render deployment
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate

# Import questions if not already imported
python manage.py import_questions

# Create superuser from env vars if not exists
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'software_engineer.settings')
django.setup()
from django.contrib.auth.models import User
username = os.environ.get('ADMIN_USERNAME', 'iqube@kic.ac.in')
password = os.environ.get('ADMIN_PASSWORD', 'iqube@KIC2026')
email = os.environ.get('ADMIN_EMAIL', 'iqube@kic.ac.in')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superuser {username} created')
else:
    print(f'Superuser {username} already exists')
"
