# Harrastuspassi

Backend for Harrastuspassi. Built with Django, uses PostgreSQL as a database.

## Installation

### 1. Create and activate virtualenv

    python3 -m venv <venv_name>
    source <venv_name>/bin/activate

### 2. Install required packages

    pip install -r requirements.txt

### 3. Create `local_settings.py` from existing template

    cp local_settings.py.tpl local_settings.py

### 4. Create PostgreSQL database for Harrastuspassi

    sudo su - postgres
    psql
    CREATE DATABASE <database_name>;
    \c <database_name>
    CREATE EXTENSION postgis;
    CREATE USER <user> WITH PASSWORD '<password>';
    GRANT ALL PRIVILEGES ON DATABASE <database_name> TO <user>;

### 5. Configure `local_settings.py`'s `DATABASES` section based on previous step

### 6. Run migrations

    python3 manage.py migrate

### 7. Start server

    python3 manage.py runserver

### 8. Run tests

    pytest

## API authentication

Two kinds of token authentication are supported:

- Long-lived API token which can be created from Django admin and does not automatically invalidate.
  This is supposed to be used for automation and server-to-server authentication. It should used in a
  request header: `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`
  - Tokens are managed in `/sysadmin/authtoken/token/`.
- Short-lived JWT token. Token can be fetched from `/auth/token` via GET request if you have a valid
  session cookie or by POST request with username and password payload. The endpoint returns 2 tokens,
  access token and refresh token. Access token can be used to authenticate requests via header
  `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`. Refresh token can be used to obtain a new short-lived access token.

### Example: obtaining JWT tokens

```
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "davidattenborough", "password": "boatymcboatface"}' \
  http://localhost:8000/auth/token/

...
{
  "access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU",
  "refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImNvbGRfc3R1ZmYiOiLimIMiLCJleHAiOjIzNDU2NywianRpIjoiZGUxMmY0ZTY3MDY4NDI3ODg5ZjE1YWMyNzcwZGEwNTEifQ.aEoAYkSJjoWH1boshQAaTkf8G3yn0kapko6HFRt7Rh4"
}
```

### Example: refreshing access token using refresh token

```
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImNvbGRfc3R1ZmYiOiLimIMiLCJleHAiOjIzNDU2NywianRpIjoiZGUxMmY0ZTY3MDY4NDI3ODg5ZjE1YWMyNzcwZGEwNTEifQ.aEoAYkSJjoWH1boshQAaTkf8G3yn0kapko6HFRt7Rh4"}' \
  http://localhost:8000/auth/token/refresh/

...
{"access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNTY3LCJqdGkiOiJjNzE4ZTVkNjgzZWQ0NTQyYTU0NWJkM2VmMGI0ZGQ0ZSJ9.ekxRxgb9OKmHkfy-zs1Ro_xs1eMLXiR17dIDBVxeT-w"}
```
