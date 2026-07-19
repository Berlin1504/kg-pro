from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, timedelta, datetime
from ..database import get_db
from .. import models, auth

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

class GenerateSessionsReq(BaseModel):
    class_id: int
    start_date: date
    end_date: date

class AttendanceMark(BaseModel):
    student_id: int
    status: str # present, absent, late, excused
    notes: Optional[str] = None

class SessionAttendanceUpdate(BaseModel):
    records: List[AttendanceMark]

@router.get("/")
def get_sessions(class_id: Optional[int] = None, teacher_id: Optional[int] = None, date_from: Optional[date] = None, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    query = db.query(models.Session)
    if class_id:
        query = query.filter(models.Session.class_id == class_id)
    if teacher_id:
        query = query.filter(models.Session.teacher_id == teacher_id)
    if date_from:
        query = query.filter(models.Session.date >= date_from)
    return query.order_by(models.Session.date, models.Session.start_time).all()

@router.post("/generate")
def generate_sessions(req: GenerateSessionsReq, db: Session = Depends(get_db), user: dict = Depends(auth.require_teacher_access)):
        
    schedules = db.query(models.ClassSchedule).filter(models.ClassSchedule.class_id == req.class_id).all()
    if not schedules:
        raise HTTPException(status_code=400, detail="No schedule defined for this class")

    current_date = req.start_date
    created_count = 0
    
    while current_date <= req.end_date:
        day_of_week = current_date.weekday() # Monday=0, Sunday=6
        # In Python, Sunday is 6. In our app, we might want Sunday=0. Let's assume Sunday=0, Monday=1...
        # Let's map python weekday to our weekday (0=Sun, 1=Mon, ..., 6=Sat)
        app_weekday = (day_of_week + 1) % 7
        
        for sched in schedules:
            if sched.day_of_week == app_weekday:
                # Check if session already exists
                exists = db.query(models.Session).filter(
                    models.Session.class_id == req.class_id,
                    models.Session.date == current_date,
                    models.Session.schedule_id == sched.id
                ).first()
                
                if not exists:
                    sess = models.Session(
                        class_id=req.class_id,
                        schedule_id=sched.id,
                        subject_id=sched.subject_id,
                        teacher_id=sched.teacher_id,
                        date=current_date,
                        start_time=sched.start_time,
                        end_time=sched.end_time,
                        status='scheduled'
                    )
                    db.add(sess)
                    created_count += 1
        current_date += timedelta(days=1)
        
    db.commit()
    return {"message": f"Generated {created_count} sessions"}

@router.get("/{session_id}/attendance")
def get_attendance(session_id: int, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db.query(models.StudentAttendance).filter(models.StudentAttendance.session_id == session_id).all()

@router.post("/{session_id}/attendance")
def mark_attendance(session_id: int, data: SessionAttendanceUpdate, db: Session = Depends(get_db), user: dict = Depends(auth.require_teacher_access)):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    enrolled_ids = {
        enrollment.student_id
        for enrollment in db.query(models.ClassEnrollment).filter(
            models.ClassEnrollment.class_id == session.class_id,
            models.ClassEnrollment.status == "active"
        ).all()
    }
    submitted_ids = {record.student_id for record in data.records}
    if not submitted_ids.issubset(enrolled_ids):
        raise HTTPException(status_code=400, detail="Attendance includes students outside this class")
    allowed_statuses = {"present", "absent", "late", "excused"}
    if any(record.status not in allowed_statuses for record in data.records):
        raise HTTPException(status_code=400, detail="Invalid attendance status")
        
    # Optional: check if user is the teacher for this session, or a boss/supervisor
    
    # Delete existing attendance for this session to overwrite
    db.query(models.StudentAttendance).filter(models.StudentAttendance.session_id == session_id).delete()
    
    for record in data.records:
        att = models.StudentAttendance(
            session_id=session_id,
            student_id=record.student_id,
            status=record.status,
            notes=record.notes
        )
        db.add(att)
        
    session.status = 'completed'
    db.commit()
    return {"message": "Attendance saved successfully"}


class QuickAttendanceRecord(BaseModel):
    student_id: int
    status: str
    
class QuickAttendanceRequest(BaseModel):
    class_id: int
    subject_id: Optional[int] = None
    date: date
    records: List[QuickAttendanceRecord]

@router.post("/quick-attendance")
def quick_attendance(data: QuickAttendanceRequest, db: Session = Depends(get_db)):
    # 1. Find or create session for this date/class/subject
    subj_id = data.subject_id
    if not subj_id:
        first_subj = db.query(models.Subject).first()
        if first_subj:
            subj_id = first_subj.id
        else:
            raise HTTPException(status_code=400, detail="لا يوجد مواد")
            
    session = db.query(models.Session).filter(
        models.Session.class_id == data.class_id,
        models.Session.subject_id == subj_id,
        models.Session.date == data.date
    ).first()
    
    if not session:
        session = models.Session(
            class_id=data.class_id,
            subject_id=subj_id,
            date=data.date,
            start_time='00:00',
            end_time='00:00',
            status='completed'
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
    # 2. Add attendance records (overwrite existing)
    db.query(models.StudentAttendance).filter(models.StudentAttendance.session_id == session.id).delete()
    
    for record in data.records:
        att = models.StudentAttendance(
            session_id=session.id,
            student_id=record.student_id,
            status=record.status
        )
        db.add(att)
        
    session.status = 'completed'
    db.commit()
    return {"message": "Quick attendance saved", "session_id": session.id}
