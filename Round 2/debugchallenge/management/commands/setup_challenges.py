from django.core.management.base import BaseCommand
from debugchallenge.models import Event, Challenge


class Command(BaseCommand):
    help = 'Set up the two debugging challenges for ML Fest Round 2'

    def handle(self, *args, **options):
        # Create or get the event
        event, created = Event.objects.get_or_create(
            id=1,
            defaults={
                'name': 'ML Fest Round 2 - ML Debugging Challenge',
                'duration_minutes': 60,
                'max_tab_switches': 3,
                'leaderboard_public': True,
                'show_score_to_participant': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created event: {event.name}'))
        else:
            self.stdout.write(f'Event already exists: {event.name}')

        # Classification challenge
        c1, created1 = Challenge.objects.get_or_create(
            event=event,
            challenge_type='classification',
            defaults={
                'title': 'Titanic Survival Classification',
                'description': (
                    'This notebook contains a machine learning pipeline for predicting '
                    'Titanic passenger survival using classification techniques. '
                    'The code has several intentional bugs in data preprocessing, '
                    'feature engineering, model training, and evaluation steps. '
                    'Your task is to identify and fix ALL the bugs so the pipeline '
                    'runs correctly end-to-end and produces valid predictions.'
                ),
                'notebook_filename': 'ml_debug_classification_final.ipynb',
                'total_bugs': 12,
                'order': 1,
            }
        )
        if created1:
            self.stdout.write(self.style.SUCCESS('Created classification challenge (12 bugs)'))
        else:
            self.stdout.write('Classification challenge already exists')

        # Regression challenge
        c2, created2 = Challenge.objects.get_or_create(
            event=event,
            challenge_type='regression',
            defaults={
                'title': 'California Housing Price Regression',
                'description': (
                    'This notebook contains a machine learning pipeline for predicting '
                    'California housing prices using regression techniques. '
                    'The code has several intentional bugs in data loading, preprocessing, '
                    'model configuration, and evaluation steps. '
                    'Your task is to identify and fix ALL the bugs so the pipeline '
                    'runs correctly end-to-end and produces valid price predictions.'
                ),
                'notebook_filename': 'ml_debug_regression_final.ipynb',
                'total_bugs': 6,
                'order': 2,
            }
        )
        if created2:
            self.stdout.write(self.style.SUCCESS('Created regression challenge (6 bugs)'))
        else:
            self.stdout.write('Regression challenge already exists')

        self.stdout.write(self.style.SUCCESS('\nRound 2 setup complete! Two challenges ready.'))
