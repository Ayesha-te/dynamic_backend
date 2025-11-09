# Backend (Django)

This folder contains the Django backend for the project.

Quick start (development):

1. Create a virtual environment and install dependencies:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Configure the database. This project uses `DATABASE_URL` env var. For local testing you can use the provided Postgres URL (example shown by user), or use sqlite by setting the env or modifying `core/settings.py`.

Example (PowerShell):

```powershell
$env:DATABASE_URL = "postgresql://user:pass@host:5432/dbname"
```

3. Run migrations and seed database:

```powershell
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

Security note: Do not commit credentials to version control. If you use the remote DB URL for development, be aware this contains secrets.
\"# d_backend\"  
