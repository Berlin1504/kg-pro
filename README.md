# Class Management App

## Run locally

```powershell
venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Or double-click/run:

```powershell
.\run_app.bat
```

Open `http://127.0.0.1:8000`.

## Required configuration

Copy `.env.example` to your environment and set:

- `SECRET_KEY`: required for production. Do not use the example value.
- `DATABASE_URL`: defaults to `sqlite:///./class_app.db`.
- `COOKIE_SECURE`: use `false` for local HTTP; use `true` behind production HTTPS.
- `SEED_ADMIN`: set to `true` only for first setup, then set it back to `false`.
- `SEED_ADMIN_PASSWORD`: set a strong password before first setup. Weak defaults are rejected.

When `APP_ENV=production`, the app refuses to start with the development secret.

The first seeded admin account is `admin@local.com` with the password you provide in `SEED_ADMIN_PASSWORD`.
After the first login, create named staff accounts and disable seeding.

## Operational checks

Use the health endpoint for local smoke checks or uptime monitors:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/api/health
```

It returns `{"status":"ok"}` only after the app can open a database session.

## Smoke test

The smoke test starts the app against a temporary SQLite database and checks auth, setup data, enrollment, class profiles, notes, finance validation, logout, and security headers.

```powershell
venv\Scripts\python.exe tests\smoke_api.py
```

Expected output:

```text
smoke api ok
```
