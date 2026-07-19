from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import datetime
from datetime import timedelta
from .. import models, auth
from ..database import get_db

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/gradebook/{class_id}")
def get_gradebook(class_id: int, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    cls = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
        
    enrollments = db.query(models.ClassEnrollment).filter(models.ClassEnrollment.class_id == class_id, models.ClassEnrollment.status == 'active').all()
    student_ids = [e.student_id for e in enrollments]
    students = db.query(models.Student).filter(models.Student.id.in_(student_ids)).all() if student_ids else []
    
    exams = db.query(models.Exam).filter(models.Exam.class_id == class_id).all()
    exam_ids = [e.id for e in exams]
    scores = db.query(models.ExamScore).filter(models.ExamScore.exam_id.in_(exam_ids)).all() if exam_ids else []
    
    # Map scores: student_id -> exam_id -> score
    score_map = {}
    for s in scores:
        if s.student_id not in score_map:
            score_map[s.student_id] = {}
        score_map[s.student_id][s.exam_id] = s.score

    student_data = []
    for st in students:
        st_scores = score_map.get(st.id, {})
        total_earned = sum(st_scores.values())
        total_possible = sum([e.total_points for e in exams if e.id in st_scores])
        percentage = (total_earned / total_possible * 100) if total_possible > 0 else 0
        
        student_data.append({
            "id": st.id,
            "name": st.full_name_ar,
            "scores": st_scores,
            "total_percentage": round(percentage, 2)
        })
        
    return {
        "class_id": class_id,
        "class_name": cls.name_ar,
        "exams": [{"id": e.id, "title": e.title, "total_points": e.total_points} for e in exams],
        "students": sorted(student_data, key=lambda x: x["total_percentage"], reverse=True)
    }

@router.get("/attendance/{class_id}")
def get_attendance_report(class_id: int, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    cls = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
        
    sessions = db.query(models.Session).filter(models.Session.class_id == class_id).all()
    session_ids = [s.id for s in sessions]
    
    enrollments = db.query(models.ClassEnrollment).filter(models.ClassEnrollment.class_id == class_id, models.ClassEnrollment.status == 'active').all()
    student_ids = [e.student_id for e in enrollments]
    students = db.query(models.Student).filter(models.Student.id.in_(student_ids)).all() if student_ids else []
    
    attendance = db.query(models.StudentAttendance).filter(models.StudentAttendance.session_id.in_(session_ids)).all() if session_ids else []
    
    # student_id -> {present: X, absent: Y, late: Z}
    att_map = {st.id: {"present": 0, "absent": 0, "late": 0, "excused": 0} for st in students}
    
    for a in attendance:
        if a.student_id in att_map and a.status in att_map[a.student_id]:
            att_map[a.student_id][a.status] += 1
            
    student_data = []
    for st in students:
        counts = att_map.get(st.id, {})
        total = sum(counts.values())
        student_data.append({
            "id": st.id,
            "name": st.full_name_ar,
            "attendance": counts,
            "total_sessions_recorded": total,
            "absent_rate": round((counts.get("absent", 0) / total * 100) if total > 0 else 0, 2)
        })
        
    return {
        "class_id": class_id,
        "class_name": cls.name_ar,
        "total_sessions": len(sessions),
        "students": sorted(student_data, key=lambda x: x["absent_rate"], reverse=True)
    }

@router.get("/stuck")
def get_stuck_students(days: int = 90, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    if user["role"] not in ["boss", "supervisor"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    threshold_date = datetime.datetime.utcnow().date() - timedelta(days=days)
    
    active_students = db.query(models.Student).filter(models.Student.status == 'active').all()
    student_ids = [s.id for s in active_students]
    
    all_ssls = db.query(models.StudentSubjectLevel).filter(models.StudentSubjectLevel.student_id.in_(student_ids)).all() if student_ids else []
    
    history_subq = db.query(
        models.LevelHistory.student_id,
        models.LevelHistory.subject_id,
        func.max(models.LevelHistory.created_at).label('max_created_at')
    ).filter(models.LevelHistory.student_id.in_(student_ids)).group_by(
        models.LevelHistory.student_id, models.LevelHistory.subject_id
    ).all() if student_ids else []
    
    latest_promos = {(row.student_id, row.subject_id): row.max_created_at for row in history_subq}
    
    levels = {l.id: l for l in db.query(models.Level).all()}
    subjects = {s.id: s for s in db.query(models.Subject).all()}
    students_map = {s.id: s for s in active_students}
    
    stuck_students = []
    
    for ssl in all_ssls:
        st = students_map.get(ssl.student_id)
        if not st:
            continue
            
        last_promo_date = latest_promos.get((ssl.student_id, ssl.subject_id))
        last_date = last_promo_date.date() if last_promo_date else st.enrollment_date
        
        if last_date and last_date <= threshold_date:
            lvl = levels.get(ssl.current_level_id)
            subj = subjects.get(ssl.subject_id)
            lvl_name = lvl.name_ar if lvl else "غير محدد"
            subj_name = subj.name_ar if subj else ""
            
            stuck_students.append({
                "id": st.id,
                "name": st.full_name_ar,
                "subject": subj_name,
                "current_level": lvl_name,
                "last_movement_date": last_date.isoformat() if last_date else None,
                "days_stuck": (datetime.datetime.utcnow().date() - last_date).days if last_date else 0
            })
            
    return sorted(stuck_students, key=lambda x: x["days_stuck"], reverse=True)
