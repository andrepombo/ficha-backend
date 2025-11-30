# Ficha Backend

A Django-based backend application.

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Development Server

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## Initial Setup

Run migrations to set up the database:
```bash
python manage.py migrate
```

Create a superuser for the admin panel:
```bash
python manage.py createsuperuser
```

## Project Structure

- `core/` - Main project configuration directory
- `manage.py` - Django management script
- `venv/` - Virtual environment (not tracked in git)
