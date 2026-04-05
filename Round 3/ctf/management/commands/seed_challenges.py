"""
Management command: seed_challenges
Populates Challenge, Flag, and ChallengeResource models from the catalog.
Usage:  python manage.py seed_challenges
"""
from django.core.management.base import BaseCommand
from ctf.models import Challenge, Flag, ChallengeResource
from ctf.challenge_catalog import CATALOG


class Command(BaseCommand):
    help = "Seed (or update) challenges, flags, and resources from the catalog."

    def handle(self, *args, **options):
        created_c = 0
        updated_c = 0
        created_f = 0
        created_r = 0

        for entry in CATALOG:
            challenge, was_created = Challenge.objects.update_or_create(
                order=entry['order'],
                defaults={
                    'title': entry['title'],
                    'description': entry['description'],
                    'category': entry['category'],
                    'difficulty': entry['difficulty'],
                    'total_points': entry['total_points'],
                    'flag_points_max': entry['flag_points_max'],
                    'explanation_points_max': entry['explanation_points_max'],
                },
            )
            if was_created:
                created_c += 1
            else:
                updated_c += 1

            # Flags
            for flag_data in entry.get('flags', []):
                _, fc = Flag.objects.update_or_create(
                    challenge=challenge,
                    flag_order=flag_data['flag_order'],
                    defaults={
                        'flag_content': flag_data['flag_content'],
                        'points_value': flag_data['points_value'],
                        'description': flag_data.get('description', ''),
                    },
                )
                if fc:
                    created_f += 1

            # Resources
            for res_data in entry.get('resources', []):
                _, rc = ChallengeResource.objects.update_or_create(
                    challenge=challenge,
                    local_name=res_data['local_name'],
                    defaults={
                        'display_name': res_data['display_name'],
                    },
                )
                if rc:
                    created_r += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done! Challenges created={created_c}, updated={updated_c}. "
            f"Flags created={created_f}. Resources created={created_r}."
        ))
