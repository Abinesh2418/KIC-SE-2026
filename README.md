# KIC Software Engineering 2026

## Project Description
KIC SE is a timed MCQ assessment platform built with Django, designed for the KIC Software Engineering 2026 competition organized by iQube - KIC. It hosts a single competitive round — a branch-aware multiple-choice quiz covering AI/ML, Web, Cybersecurity, DevOps, and DBMS topics. The platform is containerized with Docker Compose, backed by PostgreSQL, and supports real-time competitive use with an admin dashboard, live leaderboard, and XLSX export.

---

## Round 1: MCQ Quiz

### Format
- **75 questions**, MCQ (4 options), timed per participant.
- **Two branches:** AIML and Web & App Dev — each participant registers under their branch.
- **Cross-domain 2x scoring:** Questions from the opposing branch score double, rewarding breadth of knowledge.

### Question Sections & Distribution

| Section | Questions | Q Range |
|---------|-----------|---------|
| Pure AI | 25 | Q1 – Q25 |
| AI + Dev | 5 | Q26 – Q30 |
| AI + Cyber | 5 | Q31 – Q35 |
| Pure Web | 25 | Q36 – Q60 |
| Web + Cyber | 5 | Q61 – Q65 |
| Web + DevOps | 5 | Q66 – Q70 |
| DBMS | 5 | Q71 – Q75 |

### Scoring by Branch

| Section | AIML Max | Web & App Dev Max |
|---------|----------|-------------------|
| Pure AI | 25 (1×) | 50 (2×) |
| AI + Dev | 5 (1×) | 10 (2×) |
| AI + Cyber | 5 (1×) | 10 (2×) |
| Pure Web | 50 (2×) | 25 (1×) |
| Web + Cyber | 10 (2×) | 5 (1×) |
| Web + DevOps | 10 (2×) | 5 (1×) |
| DBMS | 5 (1×) | 5 (1×) |
| **Total Max** | **110** | **110** |

### Features
- **Anti-Cheating:** Tab-switch detection with configurable limit (default 3). Exceeding it auto-submits and disqualifies the participant.
- **Per-Participant Timer:** Each participant's countdown starts when they enter the quiz, not when the event starts.
- **Admin Controls:** Start/stop event, approve/disqualify participants, toggle leaderboard visibility, reset quiz, export results to XLSX.
- **Leaderboard:** Live rankings sorted by score, tiebroken by time taken. Section-wise breakdown visible per participant.
- **Question Import:** Questions loaded from `KIC-SE-MCQ.csv` via a Django management command.

---

## Tech Stack
- Python 3.x
- Django 5.x
- PostgreSQL 16 (Alpine)
- Docker & Docker Compose
- Gunicorn
- WhiteNoise (static files)
- openpyxl (XLSX export)
- django-widget-tweaks (form rendering)
- HTML / CSS / JavaScript (Django templates, Neo-Brutalist design)

---

## Getting Started

### 1. Clone the repository
```bash
git clone <repository-url>
cd KIC-AIML-2026
```

### 2. Configure environment variables (optional)
Override defaults by setting environment variables or editing `docker-compose.yml`:
```
DB_USER=postgres
DB_PASSWORD=iqube@KIC2026
SECRET_KEY=your_secret_key
ADMIN_USERNAME=iqube@kic.ac.in
ADMIN_PASSWORD=iqube@KIC2026
ADMIN_EMAIL=iqube@kic.ac.in
DEBUG=False
ALLOWED_HOSTS=*
```

### 3. Launch with Docker Compose
```bash
docker-compose up --build
```

This starts:
- **PostgreSQL** on port `7737`
- **KIC SE MCQ App** on port `7738`

### 4. Access the application
- Quiz: `http://localhost:7738`
- Admin login: `iqube@kic.ac.in`

### 5. Import questions
```bash
docker exec <app-container> python manage.py import_questions --csv KIC-SE-MCQ.csv
```

---

## Usage
- **Admin:** Log in to start/stop the event, approve participants, and monitor the leaderboard.
- **Participants:** Register with roll number and branch (AIML or Web & App Dev), wait for admin approval, then take the timed quiz.
- **Leaderboard:** Live rankings accessible to all; admins can export full results with section-wise scores to XLSX.

---

## Project Structure
```
KIC-AIML-2026/
│
├── docker-compose.yml              # Docker orchestration (DB + Round 1 app)
├── init-db.sh                      # Creates the kic_aiml_r1 database on first run
├── KIC-SE-MCQ.csv                  # (root reference — actual file inside Round 1/)
│
└── Round 1/                        # MCQ Quiz Application
    ├── Dockerfile.prod
    ├── requirements.txt
    ├── manage.py
    ├── entrypoint.prod.sh
    ├── KIC-SE-MCQ.csv              # 75-question bank (7 sections, tagged)
    ├── mlfest/                     # Django project settings & URLs
    └── quiz/                       # Quiz app
        ├── models.py               # Event, Question, Participant, Answer
        ├── views.py                # Quiz flow, admin dashboard, AJAX, XLSX export
        ├── constants.py            # Section ranges, totals, cross-domain multiplier
        ├── forms.py
        ├── templatetags/
        ├── templates/quiz/         # HTML templates (Neo-Brutalist design)
        ├── static/quiz/            # Static assets (images, CSS)
        └── management/commands/
            └── import_questions.py # CSV import command
```

---

## Contact
- **Organized by:** iQube - KIC
- **Email:** iqubeclaude2@gmail.com
