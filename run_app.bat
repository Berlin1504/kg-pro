@echo off
cd /d "%~dp0"
set SEED_ADMIN=true
if "%SEED_ADMIN_PASSWORD%"=="" (
    echo First run setup: if no admin exists yet, this password will be used for admin@local.com.
    set /p SEED_ADMIN_PASSWORD=Create initial admin password: 
)
venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
