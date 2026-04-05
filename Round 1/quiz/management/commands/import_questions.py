import csv
import os
from django.core.management.base import BaseCommand
from quiz.models import Event, Question


class Command(BaseCommand):
    help = 'Import questions from CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default='Final-Mixed_60_MCQ.csv',
            help='Path to the CSV file (default: Final-Mixed_60_MCQ.csv)',
        )
        parser.add_argument(
            '--event-name',
            type=str,
            default='ML Fest MCQ Round',
            help='Name of the event (default: ML Fest MCQ Round)',
        )

    def handle(self, *args, **options):
        csv_path = options['csv']
        event_name = options['event_name']

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
            return

        # Get or create the event
        event, created = Event.objects.get_or_create(
            name=event_name,
            defaults={'duration_minutes': 30, 'max_tab_switches': 3}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created event: {event_name}'))
        else:
            self.stdout.write(f'Using existing event: {event_name}')

        # Clear existing questions for this event
        deleted_count = Question.objects.filter(event=event).count()
        if deleted_count:
            Question.objects.filter(event=event).delete()
            self.stdout.write(f'Cleared {deleted_count} existing questions')

        # Import from CSV
        count = 0
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Question.objects.create(
                    event=event,
                    question_no=int(row['Question No']),
                    question_text=row['Question'],
                    option_a=row['Option A'],
                    option_b=row['Option B'],
                    option_c=row['Option C'],
                    option_d=row['Option D'],
                    correct_answer=row['Answer'],
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} questions!'))
