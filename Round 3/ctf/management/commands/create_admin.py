"""
Management command: create_admin
Creates the initial admin superuser.
Usage:  python manage.py create_admin --username admin --email admin@mlfest.com --password secret
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create the initial admin user for ML Fest Round 3."

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin', help='Admin username')
        parser.add_argument('--email', default='admin@mlfest.com', help='Admin email')
        parser.add_argument('--password', default='teamqernels@iQube42', help='Admin password')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists."))
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        user.role = User.ROLE_ADMIN
        user.is_approved = True
        user.save(update_fields=['role', 'is_approved'])

        self.stdout.write(self.style.SUCCESS(f"Admin user '{username}' created successfully."))
