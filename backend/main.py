from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
import os
import uuid
import time
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware

from . import models, database, auth
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
if auth.SECRET_KEY == auth.DEFAULT_DEV_SECRET:
    logger.warning("WARNING: Using default development SECRET_KEY. This is highly insecure for production!")

app = FastAPI(title="Class Management App API")

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ["POST", "PUT", "DELETE"]:
            if not request.url.path.startswith("/api/login") and not request.url.path.startswith("/api/logout"):
                csrf_cookie = request.cookies.get("csrf_token")
                csrf_header = request.headers.get("x-csrf-token")
                if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
                    return Response(content="CSRF token missing or incorrect", status_code=403)
        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        return response

app.add_middleware(CSRFMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

from .routers import classes, students, levels, subjects, schedules, sessions, staff, notes, exams, certificates, finance, settings, database_admin, reports, audit

app.include_router(classes.router)
app.include_router(students.router)
app.include_router(levels.router)
app.include_router(subjects.router)
app.include_router(schedules.router)
app.include_router(sessions.router)
app.include_router(staff.router)
app.include_router(notes.router)
app.include_router(exams.router)
app.include_router(certificates.router)
app.include_router(finance.router)
app.include_router(settings.router)
app.include_router(database_admin.router)
app.include_router(reports.router)
app.include_router(audit.router)

# Seed initial boss user
def seed_initial_user():
    if os.environ.get("SEED_ADMIN", "false").lower() not in {"1", "true", "yes"}:
        return
    db = database.SessionLocal()
    try:
        if db.query(models.User).count() == 0:
            password = os.environ.get("SEED_ADMIN_PASSWORD", "")
            if len(password) < 8 or password in {"change-me-now", "password", "password123"}:
                raise RuntimeError("SEED_ADMIN_PASSWORD must be set to a strong first-run password")
            boss = models.User(
                full_name_ar="المدير العام",
                email="admin@local.com",
                role="boss",
                password_hash=auth.get_password_hash(password)
            )
            db.add(boss)
            db.commit()
    finally:
        db.close()

def seed_default_settings():
    db = database.SessionLocal()
    settings.seed_default_settings(db)
    db.close()

seed_initial_user()
seed_default_settings()

from pydantic import BaseModel

login_attempts = defaultdict(list)

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/login")
def login(login_data: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{client_ip}:{login_data.email}"
    
    current_time = time.time()
    login_attempts[rate_key] = [t for t in login_attempts[rate_key] if current_time - t < 900]
    
    if len(login_attempts[rate_key]) >= 5:
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again later.")
        
    login_attempts[rate_key].append(current_time)

    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or not auth.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="البريد الإلكتروني أو كلمة المرور غير صحيحة",
        )
    
    login_attempts[rate_key] = []
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": str(user.id), "role": user.role}, expires_delta=access_token_expires
    )
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        path="/",
        secure=auth.COOKIE_SECURE
    )
    
    csrf_token = str(uuid.uuid4())
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        path="/",
        secure=auth.COOKIE_SECURE
    )
    return {"message": "تم تسجيل الدخول بنجاح", "user": {"id": user.id, "name": user.full_name_ar, "role": user.role}}

@app.post("/api/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("csrf_token", path="/")
    return {"message": "تم تسجيل الخروج"}

@app.get("/api/me")
def get_me(current_user: dict = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == current_user["id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.full_name_ar, "email": user.email, "role": user.role}

class UpdateMeRequest(BaseModel):
    current_password: str
    new_email: Optional[str] = None
    new_password: Optional[str] = None

@app.put("/api/me/update")
def update_me(req: UpdateMeRequest, current_user: dict = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == current_user["id"]).first()
    if not user or not auth.verify_password(req.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="كلمة المرور الحالية غير صحيحة")
    
    if req.new_email:
        # Check if email is used by someone else
        existing = db.query(models.User).filter(models.User.email == req.new_email, models.User.id != user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="هذا البريد مستخدم بالفعل")
        user.email = req.new_email
        
    if req.new_password:
        user.password_hash = auth.get_password_hash(req.new_password)
        
    db.commit()
    return {"message": "تم تحديث البيانات بنجاح"}

@app.get("/api/dashboard/summary")
def get_dashboard_summary(current_user: dict = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    from datetime import date
    today = date.today()
    
    student_count = db.query(models.Student).filter(models.Student.status == 'active').count()
    class_count = db.query(models.Class).filter(models.Class.status == 'active').count()
    level_count = db.query(models.Level).count()
    
    sessions_count = db.query(models.Session).filter(models.Session.date == today).count()
    completed_sessions = db.query(models.Session).filter(
        models.Session.date == today, 
        models.Session.status == 'completed'
    ).count()
    
    overdue_invoices = db.query(models.Invoice).filter(
        models.Invoice.status != 'paid',
        models.Invoice.due_date < today
    ).count()
    

    
    activities = []
    
    recent_notes = db.query(models.Note).order_by(models.Note.created_at.desc()).limit(5).all()
    for n in recent_notes:
        activities.append({
            "type": "note",
            "date": n.created_at.isoformat() if n.created_at else "",
            "description": f"ملاحظة جديدة: {n.content[:50]}"
        })
        
    recent_history = db.query(models.LevelHistory).order_by(models.LevelHistory.created_at.desc()).limit(5).all()
    for h in recent_history:
        activities.append({
            "type": "level_change",
            "date": h.created_at.isoformat() if h.created_at else "",
            "description": f"تغيير مستوى (سبب: {h.reason})"
        })
        
    recent_payments = db.query(models.Payment).order_by(models.Payment.paid_at.desc()).limit(5).all()
    for p in recent_payments:
        activities.append({
            "type": "payment",
            "date": p.paid_at.isoformat() if p.paid_at else "",
            "description": f"دفعة مالية بقيمة {p.amount}"
        })
        
    activities.sort(key=lambda x: x["date"], reverse=True)
    
    return {
        "stats": {
            "students": student_count,
            "classes": class_count,
            "levels": level_count,
            "sessions_today": sessions_count,
            "sessions_completed": completed_sessions,
            "overdue_invoices": overdue_invoices
        },
        "activity_feed": activities[:10]
    }

@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(models.User.__table__.select().limit(1))
    return {"status": "ok"}

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/{full_path:path}")
def serve_index_and_assets(full_path: str):
    file_path = os.path.join(frontend_dir, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(frontend_dir, "index.html"))
