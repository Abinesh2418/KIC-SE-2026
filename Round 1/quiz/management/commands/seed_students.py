from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from quiz.models import Event, Participant

User = get_user_model()

# (name, roll_no, email, domain)
STUDENTS = [
    # ── AIML — pending only ──────────────────────────────────
    ("Jaishanth L",       "24BCS107", "jaishanth.24cs@kct.ac.in",        "AIML"),
    ("Bavesh V",          "25BEC021", "bavesh.25ec@kct.ac.in",           "AIML"),
    ("Aparna V",          "24BCS025", "aparna.24cs@kct.ac.in",           "AIML"),
    ("Adithya Ragavan",   "25BIT002", "adithyaragavan.25it@kct.ac.in",   "AIML"),
    ("Gokul S",           "25BCS114", "gokul.25cs@kct.ac.in",            "AIML"),
    ("K K Shanmitha",     "25BCS352", "shanmitha.25cs@kct.ac.in",        "AIML"),
    ("Pugalendhi M",      "25BCS281", "pugalendhi.25cs@kct.ac.in",       "AIML"),
    ("Sanjith M",         "24BIT105", "sanjith.24it@kct.ac.in",          "AIML"),
    ("Anish S",           "25BME004", "anish.25me@kct.ac.in",            "AIML"),
    ("Suhani Parveen",    "25BAD119", "suhanipparveen.25ad@kct.ac.in",   "AIML"),
    ("Jashan Pratul G",   "25BCS157", "jashanpratul.25cs@kct.ac.in",     "AIML"),
    ("Vishal",            "25BAD129", "vishal.25ad@kct.ac.in",           "AIML"),
    ("Shreya",            "25BAD105", "shreya.25ad@kct.ac.in",           "AIML"),
    ("Thanesha V",        "25BAD125", "thanesha.25ad@kct.ac.in",         "AIML"),
    ("Nivetha S",         "25BAD074", "nivetha.25ad@kct.ac.in",          "AIML"),
    ("Deepika G",         "25BCS075", "deepika.25cs@kct.ac.in",          "AIML"),

    # ── Web & App Development — pending only ─────────────────
    ("Visagan A C",       "25BCS445", "visagan.25cs@kct.ac.in",          "Web & App Development"),
    ("Vinay Vasanth A A", "25BCS443", "vinayvasanth.25cs@kct.ac.in",     "Web & App Development"),
    ("Sanjay Raj G",      "25BCS331", "sanjayraj.25cs@kct.ac.in",        "Web & App Development"),
    ("Bhavan Raj S",      "25BCS059", "bhavanraj.25cs@kct.ac.in",        "Web & App Development"),
    ("Dakshata S P",      "25BAD133", "dakshata.25ad@kct.ac.in",         "Web & App Development"),
    ("Harshini V",        "25BCS138", "harshini1.25cs@kct.ac.in",        "Web & App Development"),
    ("Rakshana JK",       "25BIT075", "rakshana.25it@kct.ac.in",         "Web & App Development"),
    ("Guna K",            "25BEC047", "guna.25ec@kct.ac.in",             "Web & App Development"),
    ("Gokul K",           "25BCS112", "gokul3.25cs@kct.ac.in",           "Web & App Development"),
    ("Midunavarshini GR", "25BCS202", "midunavarshini.25cs@kct.ac.in",   "Web & App Development"),
    ("Venkateswaran N",   "25BCS430", "venkateswaran.25cs@kct.ac.in",    "Web & App Development"),
]

ADMINS = [
    ("Abinesh B",             "23BCS006", "abinesh.23cs@kct.ac.in"),
    ("Denistan B",            "23BCS030", "denistan.23cs@kct.ac.in"),
    ("Nivetha M",             "23BAD080", "nivetha.23ad@kct.ac.in"),
    ("Sakthi S",              "23BIT091", "sakthi.23it@kct.ac.in"),
    ]


class Command(BaseCommand):
    help = 'Seed 27 pending students (16 AIML + 11 Web) and 4 admins into the database'

    def handle(self, *args, **options):
        event, _ = Event.objects.get_or_create(
            name="KIC AIML 2026 Assessment",
            defaults={'duration_minutes': 30, 'max_tab_switches': 3}
        )

        # ── Admins ──────────────────────────────────────────
        for full_name, roll_no, email in ADMINS:
            parts = full_name.split(' ', 1)
            first, last = parts[0], parts[1] if len(parts) > 1 else ''
            user, created = User.objects.get_or_create(
                username=roll_no,
                defaults={
                    'email': email, 'first_name': first, 'last_name': last,
                    'is_staff': True, 'is_superuser': True,
                }
            )
            if created:
                user.set_password(roll_no)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  [ADMIN]   {full_name} ({roll_no}) created'))
            else:
                self.stdout.write(f'  [ADMIN]   {full_name} ({roll_no}) already exists — skipped')

        # ── Students ─────────────────────────────────────────
        aiml_count = web_count = 0
        for full_name, roll_no, email, domain in STUDENTS:
            parts = full_name.split(' ', 1)
            first, last = parts[0], parts[1] if len(parts) > 1 else ''
            user, created = User.objects.get_or_create(
                username=email,
                defaults={
                    'email': email, 'first_name': first, 'last_name': last,
                    'is_staff': False, 'is_superuser': False,
                }
            )
            if created:
                user.set_password(roll_no)
                user.save()

            participant, p_created = Participant.objects.get_or_create(
                user=user,
                defaults={
                    'event': event, 'roll_no': roll_no,
                    'domain': domain, 'status': 'pending',
                }
            )
            if not p_created:
                # Update domain if missing
                if not participant.domain or participant.domain == 'AIML' and domain != 'AIML':
                    participant.domain = domain
                if not participant.roll_no:
                    participant.roll_no = roll_no
                participant.save()

            if domain == 'AIML':
                aiml_count += 1
            else:
                web_count += 1

            status = 'created' if created else 'exists'
            tag = 'AIML' if domain == 'AIML' else 'WEB '
            self.stdout.write(
                (self.style.SUCCESS if created else str)(
                    f'  [{tag}] {full_name} ({roll_no}) — {status}'
                )
            )

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! {aiml_count} AIML + {web_count} Web & App Dev students seeded. '
            f'Default password = Roll No.'
        ))
