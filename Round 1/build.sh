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
