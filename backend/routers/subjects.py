from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from .. import models, auth
from ..database import get_db
from .audit import log_audit

router = APIRouter(prefix="/api/subjects", tags=["Subjects"])

class SubjectCreate(BaseModel):
    name_ar: str
    description: Optional[str] = None
    default_passing_grade: int = 50
    promotion_threshold: Optional[int] = 75

@router.get("/")
def get_subjects(db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    subjects = db.query(models.Subject).all()
    levels = db.query(models.Level).order_by(models.Level.order_index).all()
    
    res = []
    for s in subjects:
        s_levels = [{"id": l.id, "name_ar": l.name_ar, "code": l.code, "order_index": l.order_index} for l in levels if l.subject_id == s.id]
        res.append({
            "id": s.id,
            "name_ar": s.name_ar,
            "description": s.description,
            "default_passing_grade": s.default_passing_grade,
            "promotion_threshold": s.promotion_threshold,
            "level_count": len(s_levels),
            "levels": s_levels
        })
    return res

@router.post("/")
def create_subject(subject: SubjectCreate, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    db_subject = models.Subject(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    log_audit(db, user['id'], "إضافة مادة", "Subject", db_subject.id, None, {"name": db_subject.name_ar})
    return db_subject

@router.put("/{id}")
def update_subject(id: int, subject: SubjectCreate, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    db_subject = db.query(models.Subject).filter(models.Subject.id == id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db_subject.name_ar = subject.name_ar
    db_subject.description = subject.description
    db_subject.default_passing_grade = subject.default_passing_grade
    if subject.promotion_threshold is not None:
        db_subject.promotion_threshold = subject.promotion_threshold
    
    db.commit()
    db.refresh(db_subject)
    log_audit(db, user['id'], "تحديث بيانات مادة", "Subject", id, None, {"name": db_subject.name_ar})
    return db_subject

@router.delete("/{id}")
def delete_subject(id: int, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    db_subject = db.query(models.Subject).filter(models.Subject.id == id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    # Check dependencies
    if db.query(models.Level).filter(models.Level.subject_id == id).first():
        raise HTTPException(status_code=400, detail="لا يمكن حذف المادة لوجود مستويات مرتبطة بها. قم بحذف المستويات أولاً.")
    if db.query(models.ClassSchedule).filter(models.ClassSchedule.subject_id == id).first():
        raise HTTPException(status_code=400, detail="لا يمكن حذف المادة لوجود جداول حصص مرتبطة بها.")
    if db.query(models.Session).filter(models.Session.subject_id == id).first():
        raise HTTPException(status_code=400, detail="لا يمكن حذف المادة لوجود حصص مسجلة مرتبطة بها.")
    if db.query(models.Exam).filter(models.Exam.subject_id == id).first():
        raise HTTPException(status_code=400, detail="لا يمكن حذف المادة لوجود اختبارات مرتبطة بها.")
    if db.query(models.StudentSubjectLevel).filter(models.StudentSubjectLevel.subject_id == id).first():
        raise HTTPException(status_code=400, detail="لا يمكن حذف المادة لوجود مستويات طلاب مرتبطة بها.")
        
    db.delete(db_subject)
    db.commit()
    log_audit(db, user['id'], "حذف مادة", "Subject", id, {"name": db_subject.name_ar}, None)
    return {"message": "Subject deleted successfully"}
