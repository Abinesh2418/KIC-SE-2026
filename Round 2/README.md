# ML Fest — Round 2: ML Debugging Challenge

A Django-based live proctored challenge platform for **Yugam 2026**, organized by **Team Qernels**.

Participants download buggy Jupyter notebooks (Classification + Regression), find & fix the bugs locally, then upload their corrected notebooks — all within a timed, fullscreen-proctored environment.

---

## Features

- **2 Debugging Challenges**: Titanic Classification (11 bugs) + California Housing Regression (8 bugs)
- **Notebook Download & Upload**: Participants download buggy notebooks, fix them locally, upload solutions
- **Two-ZIP Download System**: Challenge Notebooks ZIP (notebooks + dataset) + Environment Setup ZIP (requirements, scripts)
- **Downloads Available on Approval**: Participants can download & set up their environment *before* the event starts
- **Fullscreen Proctoring**: Enforced fullscreen mode with tab-switch detection
- **Per-Participant Timer**: Individual countdown timer starts when each participant enters the challenge
- **Admin Dashboard**: Approve/disqualify participants, grade submissions, manage event settings
- **Live Leaderboard**: Real-time scores with auto-refresh
- **Neo-Brutalist UI**: Dark/light theme support with clean, modern design

---

## Tech Stack

- **Backend**: Django 5.x + PostgreSQL
- **Frontend**: Vanilla HTML/CSS/JS (no build tools needed)
- **Deployment**: Render-ready (Gunicorn + WhiteNoise)

---

## Quick Start (Local Development)

### Prerequisites

- Python 3.12+
- PostgreSQL installed and running (or use SQLite for quick testing)

### 1. Clone & Install Dependencies

```bash
cd ML_Fest-Round-2
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

pip install -r requirements.txt
```

### 2. Database Setup

**Option A: PostgreSQL (Recommended)**

Make sure PostgreSQL is running, then create the database:

```bash
# In psql:
CREATE DATABASE mlfest_db;
```

The default settings expect:
- Database: `mlfest_db`
- User: `postgres`
- Password: (empty)
- Host: `localhost`
- Port: `5432`

You can override these with environment variables: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

**Option B: SQLite (Quick Testing)**

Set the `DATABASE_URL` environment variable:

```bash
# Windows PowerShell:
$env:DATABASE_URL = "sqlite:///db.sqlite3"

# Linux/Mac:
export DATABASE_URL="sqlite:///db.sqlite3"
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Set Up Challenges

```bash
python manage.py setup_challenges
```

This creates the event and the two debugging challenges (Classification + Regression).

### 5. Create Admin User

```bash
python manage.py createsuperuser
```

### 6. Run the Server

```bash
python manage.py runserver 0.0.0.0:7741
```

Visit: **http://127.0.0.1:7741/**

---

## How It Works

### For Participants

1. **Register** at the home page and wait for admin approval
2. Once **approved** → download the two ZIP files (available immediately)
3. **Set up local environment**:
   - Extract **ML_Challenge_Setup.zip**
   - **Windows**: Double-click `setup.bat` — creates `Task_2_venv`, installs packages, and auto-activates the environment
   - **Linux/Mac**: Run `source setup.sh` — same as above
   - Or manually:
     ```bash
     python -m venv Task_2_venv
     # Windows:
     Task_2_venv\Scripts\activate
     # Linux/Mac:
     source Task_2_venv/bin/activate
     pip install -r participant_requirements.txt
     ```
4. Extract **ML_Challenge_Notebooks.zip** — contains 2 buggy notebooks + `titanic_data.csv`
5. When event starts → enter **fullscreen challenge mode**
6. **Fix bugs** locally in Jupyter (`jupyter notebook`) or any IDE
7. **Upload** the corrected `.ipynb` files
8. **Submit** when done (or auto-submit when timer expires)

### For Admins

1. Log in with superuser credentials → **Admin Dashboard**
2. **Approve** registered participants (individually or all at once)
3. **Configure** event settings (duration, tab switch limit, leaderboard visibility)
4. **Start** the event → participants can now enter the challenge
5. **Stop** the event → auto-finalizes all pending submissions
6. **Grade** submissions: download participant notebooks, review fixes, assign scores
7. **View Leaderboard** for rankings

---

## Admin Dashboard URLs

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/admin-dashboard/` | Admin dashboard |
| `/leaderboard/` | Public leaderboard |
| `/admin/` | Django admin (model management) |

---

## Downloads

| ZIP File | Contents | Available When |
|----------|----------|----------------|
| **ML_Challenge_Notebooks.zip** | 2 buggy notebooks + titanic_data.csv | After approval |
| **ML_Challenge_Setup.zip** | participant_requirements.txt, setup.bat/sh, README | After approval |

**Dependencies installed** (via `participant_requirements.txt`): numpy, pandas, matplotlib, seaborn, scikit-learn

**Virtual environment name**: `Task_2_venv` (auto-created and activated by setup scripts)

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (dev key) | Django secret key |
| `DEBUG` | `True` | Debug mode |
| `ALLOWED_HOSTS` | `*` | Comma-separated hosts |
| `DB_NAME` | `mlfest_db` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL user |
| `DB_PASSWORD` | (empty) | PostgreSQL password |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `7743` | PostgreSQL port |
| `DATABASE_URL` | (none) | Full database URL (overrides above) |

---

## Project Structure

```
ML_Fest-Round-2/
├── mlfest/                # Django project settings
├── debugchallenge/        # Main app
│   ├── models.py          # Event, Challenge, Participant, Submission
│   ├── views.py           # All views (auth, challenge, admin, grading, downloads)
│   ├── urls.py            # URL routing
│   ├── admin.py           # Django admin registration
│   ├── templates/debugchallenge/  # HTML templates
│   ├── static/debugchallenge/     # Static assets
│   └── management/        # Management commands (setup_challenges)
├── challenge_materials/   # Participant-facing challenge files
│   ├── ML_Challenge_Notebooks.zip   # Pre-built: notebooks + CSV
│   ├── ML_Challenge_Setup.zip       # Pre-built: env setup + scripts
│   ├── ml_debug_classification_final.ipynb
│   ├── ml_debug_regression_final.ipynb
│   ├── titanic_data.csv
│   ├── participant_requirements.txt
│   ├── setup.bat          # Windows env setup
│   └── setup.sh           # Linux/Mac env setup
├── cleanup_db.py          # Truncate all tables
├── requirements.txt       # Server dependencies
├── manage.py
└── README.md
```

---

## About the `pgdata/` Folder

The `pgdata/` folder contains a **local PostgreSQL data directory**. This is used during development when PostgreSQL is initialized with a custom data directory.

### Should I keep it?

- **Local development**: You *can* keep it if you want a portable data directory, but it's typically better to use the system-installed PostgreSQL and just create a database (`CREATE DATABASE mlfest_db`).
- **Production**: **Never** ship `pgdata/` to production. Use a managed PostgreSQL service (e.g., Render PostgreSQL, AWS RDS, Supabase) or Docker.
- **Version control**: Add `pgdata/` to `.gitignore` — it should never be committed.

### Docker Alternative (Recommended for Production)

For a clean, reproducible PostgreSQL setup, use Docker:

```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: mlfest_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_secure_password
    ports:
      - "7743:7743"
    volumes:
      - pgdata:/var/lib/postgresql/data

  web:
    build: .
    command: gunicorn mlfest.wsgi:application --bind 0.0.0.0:7741
    environment:
      DATABASE_URL: postgres://postgres:your_secure_password@db:7743/mlfest_db
      SECRET_KEY: your-production-secret-key
      DEBUG: "False"
    ports:
      - "7741:7741"
    depends_on:
      - db

volumes:
  pgdata:
```

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 7741
CMD ["gunicorn", "mlfest.wsgi:application", "--bind", "0.0.0.0:7741"]
```

Then run: `docker-compose up -d`

---

## Deployment (Render)

The project includes `render.yaml`, `Procfile`, and `build.sh` for Render deployment:

```bash
# build.sh runs:
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py setup_challenges
```

---

**Team Qernels | Yugam 2026**
