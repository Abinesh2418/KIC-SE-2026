# ML Fest

## Project Description
ML Fest is a multi-round machine learning competition platform built with Django. It hosts three progressive rounds of challenges — from ML knowledge quizzes to debugging buggy notebooks to security-focused Capture The Flag (CTF) tasks. The entire platform is containerized with Docker Compose, backed by PostgreSQL, and designed for real-time competitive use with admin dashboards, evaluator workflows, and live leaderboards.

---

## Project Details

### Problem Statement
Running an ML competition requires a platform that can handle timed assessments, anti-cheating measures, manual evaluation workflows, and real-time scoring — all while supporting multiple independent rounds with different challenge formats. ML Fest solves this by providing three specialized Django applications, each tailored to a distinct round format, unified under a single Docker Compose deployment.

### Round 1: MCQ Quiz
- **Format:** Timed multiple-choice questions on ML concepts (30-minute limit).
- **Anti-Cheating:** Tab-switch detection with configurable limits (default 3). Exceeding the limit auto-submits and disqualifies the participant.
- **Scoring:** Number of correct answers, with time taken as a tiebreaker.
- **Admin Controls:** Start/stop events, approve participants, toggle leaderboard visibility, reset quizzes, and export results to XLSX.
- **Questions:** Imported from CSV via a management command.

### Round 2: ML Debugging Challenge
- **Format:** Participants receive buggy Jupyter notebooks (classification with 12 bugs, regression with 6 bugs) and upload corrected versions within a 60-minute time limit.
- **Evaluation:** Assigned evaluators grade each submission bug-by-bug through a dedicated evaluator panel.
- **Scoring:** 1 point per correctly fixed bug (max 18 points total).
- **Features:** Notebook upload with validation (.ipynb only, 10MB limit), evaluator assignment system, and tab-switch detection.

### Round 3: ML Capture The Flag (CTF)
- **Format:** Five security-focused ML challenges of increasing difficulty (Easy to Expert), covering data poisoning, constrained attacks, model repair, model evaluation, and weight recovery.
- **Unique Flags:** Each participant receives deterministically generated unique flags per challenge (SHA-256 based), preventing answer sharing.
- **Dual Scoring:** Separate points for correct flag submission and quality of explanation (evaluated by assigned evaluators).
- **Approval Workflow:** Submissions are pending until an evaluator approves with point allocation.
- **Leaderboard Tiebreaker:** Equal scores are broken by who reached the score first.
- **Jupyter Integration:** JSON login endpoint for notebook-based authentication.

### Shared Architecture
- **Shared Auth Model:** A `CustomUser` model (extending `AbstractUser`) with role-based access (participant, evaluator, admin) and approval gating.
- **Database Isolation:** Each round uses its own PostgreSQL database (`mlfest_r1`, `mlfest_r2`, `mlfest_r3`) on a single PostgreSQL 16 instance.
- **Common Patterns:** Participant approval workflows, live leaderboards with XLSX export, event start/stop controls, and role-based dashboards across all rounds.

### Deployment
- **Containerized:** Each round runs as a separate Docker container with Gunicorn, behind WhiteNoise for static file serving.
- **Database Init:** An `init-db.sh` script auto-creates all three databases on first PostgreSQL startup.
- **Environment Configuration:** All secrets and settings are configurable via environment variables with sensible defaults.

---

## Tech Stack
- Python 3.x
- Django 5.x
- PostgreSQL 16 (Alpine)
- Docker & Docker Compose
- Gunicorn
- WhiteNoise (static files)
- scikit-learn, pandas, numpy (Round 3 challenges)
- openpyxl (XLSX export)
- django-widget-tweaks (form rendering)
- HTML/CSS/JavaScript (Django templates)

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/DCode-v05/ML-Fest.git
cd ML-Fest
```

### 2. Configure environment variables (optional)
Create a `.env` file in the project root to override defaults:
```
DB_USER=postgres
DB_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key
ADMIN_USERNAME=admin@example.com
ADMIN_PASSWORD=your_admin_password
ADMIN_EMAIL=admin@example.com
DEBUG=False
ALLOWED_HOSTS=*
```

### 3. Launch with Docker Compose
```bash
docker-compose up --build
```

This starts:
- **PostgreSQL** on port `7737`
- **Round 1 (MCQ Quiz)** on port `7738`
- **Round 2 (Debug Challenge)** on port `7739`
- **Round 3 (CTF)** on port `7740`

### 4. Access the applications
- Round 1: `http://localhost:7738`
- Round 2: `http://localhost:7739`
- Round 3: `http://localhost:7740`

Admin credentials are shared across all rounds (default: `teamqernels@gmail.com`).

---

## Usage
- **Admins:** Log in to any round's admin dashboard to manage events, approve participants, assign evaluators, and control leaderboard visibility.
- **Participants:** Register, wait for admin approval, then compete in the active round within the time limit.
- **Evaluators (Round 2 & 3):** Review assigned submissions, grade bug fixes or flag explanations, and approve scores.
- **Leaderboards:** View live rankings; admins can export results to XLSX at any time.

---

## Project Structure
```
ML-Fest/
|
├── docker-compose.yml              # Production orchestration (DB + 3 rounds)
├── init-db.sh                      # Creates databases on first PostgreSQL init
├── shared_auth/                    # Shared CustomUser model across rounds
│   ├── models.py
│   ├── admin.py
│   └── migrations/
|
├── Round 1/                        # MCQ Quiz Application
│   ├── Dockerfile.prod
│   ├── requirements.txt
│   ├── manage.py
│   ├── entrypoint.prod.sh
│   ├── mlfest/                     # Django project settings & URLs
│   ├── quiz/                       # Quiz app (models, views, templates)
│   │   ├── models.py               # Event, Question, Participant, Answer
│   │   ├── views.py                # Quiz flow, admin dashboard, AJAX endpoints
│   │   ├── templates/quiz/         # HTML templates
│   │   ├── management/commands/    # import_questions command
│   │   └── static/quiz/            # Static assets
│   └── Final-Mixed_60_MCQ.csv      # Question bank
|
├── Round 2/                        # ML Debugging Challenge
│   ├── Dockerfile.prod
│   ├── requirements.txt
│   ├── manage.py
│   ├── entrypoint.prod.sh
│   ├── mlfest/                     # Django project settings & URLs
│   ├── debugchallenge/             # Debug challenge app
│   │   ├── models.py               # Challenge, Submission, Evaluation
│   │   ├── views.py                # Challenge flow, evaluator panel
│   │   ├── templates/debugchallenge/
│   │   └── management/commands/    # setup_challenges command
│   └── challenge_materials/        # Buggy notebooks & datasets
|
├── Round 3/                        # ML CTF Application
│   ├── Dockerfile.prod
│   ├── requirements.txt
│   ├── manage.py
│   ├── entrypoint.prod.sh
│   ├── mlfest/                     # Django project settings & URLs
│   ├── ctf/                        # CTF app
│   │   ├── models.py               # Challenge, Flag, Score, UserFlag
│   │   ├── views.py                # CTF flow, evaluator dashboard
│   │   ├── challenge_catalog.py    # 5 challenge definitions & seeding
│   │   ├── evaluation.py           # Flag validation logic
│   │   ├── middleware.py           # Approval gate middleware
│   │   ├── templates/ctf/
│   │   └── management/commands/    # seed_challenges, create_admin
│   └── challenge_files/            # Notebooks, datasets, pickled models
|
└── DB Backup/                      # SQL dumps for each round
    ├── round-1.sql
    ├── round-2.sql
    └── round-3.sql
```

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request describing your changes.

---

## Contact
- **GitHub:** [DCode-v05](https://github.com/DCode-v05)
- **Email:** denistanb05@gmail.com
