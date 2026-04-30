from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from quiz.models import Event, Participant

User = get_user_model()

# (name, roll_no, email, domain)
STUDENTS = [
    # ── AIML ────────────────────────────────────────────────
    ("Dhanesh VC",           "24BAD018", "dhanesh.24ad@kct.ac.in",           "AIML"),
    ("Sudarshini B",         "25BAD116", "sudarshini.25ad@kct.ac.in",        "AIML"),
    ("Raja Murugappa A",     "25BIT074", "rajamurugappa.25it@kct.ac.in",     "AIML"),
    ("Jaishanth L",          "24BCS107", "jaishanth.24cs@kct.ac.in",         "AIML"),
    ("Praneethan R P",       "25BCS267", "praneethan.25cs@kct.ac.in",        "AIML"),
    ("SaiSanjay R",          "24BAD102", "saisanjay.24ad@kct.ac.in",         "AIML"),
    ("Monika Riya",          "25BCS211", "monikariya.25cs@kct.ac.in",        "AIML"),
    ("Vignesh B",            "25BCS435", "vignesh2.25cs@kct.ac.in",          "AIML"),
    ("Satheesh B",           "24BAD107", "satheesh.24ad@kct.ac.in",          "AIML"),
    ("Prithesa R",           "25BAD083", "prithesa.25ad@kct.ac.in",          "AIML"),
    ("Akshaya B",            "25BAD006", "akshaya.25ad@kct.ac.in",           "AIML"),
    ("Bavesh V",             "25BEC021", "bavesh.25ec@kct.ac.in",            "AIML"),
    ("Adhithyalakshman N",   "24BEC009", "adhithyalakshman.24ec@kct.ac.in",  "AIML"),
    ("Aparna V",             "24BCS025", "aparna.24cs@kct.ac.in",            "AIML"),
    ("Harish Ragavan R P",   "25BAD034", "harishragavan.25ad@kct.ac.in",     "AIML"),
    ("Adithya Ragavan",      "25BIT002", "adithyaragavan.25it@kct.ac.in",    "AIML"),
    ("K Poovarasan",         "25BIT065", "poovarasan.25it@kct.ac.in",        "AIML"),
    ("Gokul S",              "25BCS114", "gokul.25cs@kct.ac.in",             "AIML"),
    ("Nishanth S",           "25BIT060", "nishanth1.25it@kct.ac.in",         "AIML"),
    ("Kishore Kumar R",      "25BAD048", "kishorekumar.25ad@kct.ac.in",      "AIML"),
    ("K K Shanmitha",        "25BCS352", "shanmitha.25cs@kct.ac.in",         "AIML"),
    ("Giridharan R N",       "25BCS110", "giridharan.25cs@kct.ac.in",        "AIML"),
    ("Pranish S",            "25BIT069", "pranish.25it@kct.ac.in",           "AIML"),
    ("Vibusha G",            "24BAD128", "vibusha.24ad@kct.ac.in",           "AIML"),
    ("Pugalendhi M",         "25BCS281", "pugalendhi.25cs@kct.ac.in",        "AIML"),
    ("R Sudharshan",         "24BEI062", "sudharshan.24ei@kct.ac.in",        "AIML"),
    ("Sanjith M",            "24BIT105", "sanjith.24it@kct.ac.in",           "AIML"),
    ("Sastha Jeyasri A",     "24BAD106", "sasthajeyasri.24ad@kct.ac.in",     "AIML"),
    ("Sowrendar B",          "25BCS372", "sowrendar.25cs@kct.ac.in",         "AIML"),
    ("Anish S",              "25BME004", "anish.25me@kct.ac.in",             "AIML"),

    # ── Web & App Development ────────────────────────────────
    ("Kavya M",              "25BIT043", "kavya.25it@kct.ac.in",             "Web & App Development"),
    ("Kavipriya B",          "25BIT042", "kavipriya.25it@kct.ac.in",         "Web & App Development"),
    ("Visagan A C",          "25BCS445", "visagan.25cs@kct.ac.in",           "Web & App Development"),
    ("Loguprasath D",        "25BCS195", "loguprasath.25cs@kct.ac.in",       "Web & App Development"),
    ("Madhusree T G",        "25BIT047", "madhusree.25it@kct.ac.in",         "Web & App Development"),
    ("Lavanya R",            "25BIT046", "lavanya.25it@kct.ac.in",           "Web & App Development"),
    ("Parani Sri P",         "25BCS242", "paranisri.25cs@kct.ac.in",         "Web & App Development"),
    ("Pooja P",              "25BEC131", "pooja.25ec@kct.ac.in",             "Web & App Development"),
    ("Gayathri A",           "25BIT026", "gayathri.25it@kct.ac.in",          "Web & App Development"),
    ("Deeksha A",            "25BIT018", "deeksha.25it@kct.ac.in",           "Web & App Development"),
    ("Navadara P T",         "25BIT056", "navadara.25it@kct.ac.in",          "Web & App Development"),
    ("Rajamanisha P",        "25BCS286", "rajamanisha.25cs@kct.ac.in",       "Web & App Development"),
    ("Vinay Vasanth A A",    "25BCS443", "vinayvasanth.25cs@kct.ac.in",      "Web & App Development"),
    ("Nagul",                "25BCS219", "nagul.25cs@kct.ac.in",             "Web & App Development"),
    ("Raneus Eben L",        "25BCS293", "raneuseben.25cs@kct.ac.in",        "Web & App Development"),
    ("Nandhana D",           "25BCS221", "nandhana.25cs@kct.ac.in",          "Web & App Development"),
    ("Taranya S A",          "25BEE130", "taranya.25ee@kct.ac.in",           "Web & App Development"),
    ("Ranjani L",            "25BEE088", "ranjani.25ee@kct.ac.in",           "Web & App Development"),
    ("Sanjay A",             "24BCS239", "sanjay1.24cs@kct.ac.in",           "Web & App Development"),
    ("Prateepa R",           "25BIT070", "prateepa.25it@kct.ac.in",          "Web & App Development"),
    ("Rahul G",              "25BIT073", "rahul.25it@kct.ac.in",             "Web & App Development"),
    ("Sanjay Riyanth",       "25BAD097", "sanjayriyanth.25ad@kct.ac.in",     "Web & App Development"),
    ("Sanjay Raj G",         "25BCS331", "sanjayraj.25cs@kct.ac.in",         "Web & App Development"),
    ("Aashish Sivaram R",    "25BCS004", "aashishsivaram.25cs@kct.ac.in",    "Web & App Development"),
    ("Bhavan Raj S",         "25BCS059", "bhavanraj.25cs@kct.ac.in",         "Web & App Development"),
    ("Kavin Kumar J",        "25BIT041", "kavinkumar.25it@kct.ac.in",        "Web & App Development"),
    ("Dakshata S P",         "25BAD133", "dakshata.25ad@kct.ac.in",          "Web & App Development"),
]

ADMINS = [
    ("Abinesh B",             "23BCS006", "abinesh.23cs@kct.ac.in"),
    ("Denistan B",            "23BCS030", "denistan.23cs@kct.ac.in"),
    ("Nivetha M",             "23BAD080", "nivetha.23ad@kct.ac.in"),
    ("Sakthi S",              "23BIT091", "sakthi.23it@kct.ac.in"),
    ("Bavin P T",             "23BIT010", "bavin.23it@kct.ac.in"),
    ("Danushika N",           "23BIT013", "danushika.23it@kct.ac.in"),
    ("Nithisha V",            "23BAD079", "nithisha.23ad@kct.ac.in"),
    ("Santhiya Joe Harson J", "23BAD102", "santhiyajoe.23ad@kct.ac.in"),
    ("Yogeshwaran S",         "23BEC213", "yogeshwaran.23ec@kct.ac.in"),
]


class Command(BaseCommand):
    help = 'Seed 57 students (30 AIML + 27 Web) and 9 admins into the database'

    def handle(self, *args, **options):
        event, _ = Event.objects.get_or_create(
            name="KIC Software Engineering Assessment",
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
