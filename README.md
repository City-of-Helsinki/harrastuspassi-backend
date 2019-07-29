
# Harrastuspassi

Backend for Harrastuspassi. Built with Django, uses PostgreSQL as a database.

Installation
------------

### 1. Create and activate virtualenv

    python3 -m venv .venv
    source .venv/bin/activate

### 2. Install required packages for development

    pip install -r requirements.txt

### 3. Create `local_settings.py` from existing template

    cp local_settings.py.tpl local_settings.py

### 4. Create PostgreSQL database for Harrastuspassi

    sudo su - postgres
    psql
    CREATE DATABASE <database_name>;
    CREATE USER <user> WITH PASSWORD '<password>';
    GRANT ALL PRIVILEGES ON DATABASE <database_name> TO <user>;

### 5. Configure `local_settings.py`'s `DATABASES` section based on previous step

### 6. Run migrations

    python3 manage.py migrate

### 7. Start server

    python3 manage.py runserver
