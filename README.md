# Test Scrape Project

A Django web application for test project.

## 📋 Requirements

- Python >= 3.12
- Django 5.2.11
- Redis (for Celery)
- pip or uv (package manager)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository_url>
cd test_scrape_proj
```

### 2. Install Dependencies

Using `uv` (recommended):
```bash
uv sync
```

Or using `pip`:
```bash
pip install -r requirements.txt
```

### 3. Apply Database Migrations

```bash
python manage.py migrate
```

### 4. Create a Superuser

```bash
python manage.py createsuperuser
```

### 5. Start Redis

```bash
redis-server
```

### 6. Start Celery Worker

In a separate terminal:
```bash
celery -A test_scrape_proj worker -l info
```

### 7. Start Celery Beat (Scheduler)

In a separate terminal:
```bash
celery -A test_scrape_proj beat -l info
```

### 8. Run the Development Server

```bash
python manage.py runserver
```



