from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from .. import models, auth
from ..database import get_db
from .audit import log_audit

router = APIRouter(prefix="/api/exams", tags=["Exams"])

class ExamCreate(BaseModel):
    title: str
    subject_id: int
    class_id: int
    date: date
    total_points: int = 100
    passing_grade: int = 50
    is_certification: bool = False

class ScoreInput(BaseModel):
    student_id: int
    score: float

class ExamScoresSubmit(BaseModel):
    scores: List[ScoreInput]

@router.get("/")
def get_exams(class_id: Optional[int] = None, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    query = db.query(models.Exam)
    
    if user['role'] == 'teacher':
        teacher_class_ids = [ct.class_id for ct in db.query(models.ClassTeacher).filter(models.ClassTeacher.teacher_id == user['id']).all()]
        query = query.filter(models.Exam.class_id.in_(teacher_class_ids))
        
    if class_id:
        query = query.filter(models.Exam.class_id == class_id)
        
    return query.all()

@router.post("/")
def create_exam(exam: ExamCreate, db: Session = Depends(get_db), user: dict = Depends(auth.require_teacher_access)):
    if exam.total_points <= 0:
        raise HTTPException(status_code=400, detail="Total points must be greater than zero")
    if exam.passing_grade < 0 or exam.passing_grade > exam.total_points:
        raise HTTPException(status_code=400, detail="Passing grade must be between zero and total points")
    cls = db.query(models.Class).filter(models.Class.id == exam.class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    subject = db.query(models.Subject).filter(models.Subject.id == exam.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db_exam = models.Exam(**exam.dict(), created_by=user["id"])
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    log_audit(db, user['id'], "إنشاء اختبار", "Exam", db_exam.id, None, {"title": db_exam.title})
    return db_exam

@router.delete("/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db), user: dict = Depends(auth.require_teacher_access)):
    exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    exam_title = exam.title
    db.query(models.ExamScore).filter(models.ExamScore.exam_id == exam_id).delete()
    db.query(models.Certificate).filter(models.Certificate.exam_id == exam_id).delete()
    db.delete(exam)
    db.commit()
    log_audit(db, user['id'], "حذف اختبار", "Exam", exam_id, {"title": exam_title}, None)
    return {"message": "Exam deleted"}

@router.get("/{exam_id}")
def get_exam(exam_id: int, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    # get scores
    scores = db.query(models.ExamScore).filter(models.ExamScore.exam_id == exam_id).all()
    
    return {"exam": exam, "scores": scores}

@router.post("/{exam_id}/scores")
def record_scores(exam_id: int, data: ExamScoresSubmit, db: Session = Depends(get_db), user: dict = Depends(auth.require_teacher_access)):
    exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    if exam.status == "published":
        raise HTTPException(status_code=400, detail="Cannot edit scores after publishing")
    enrolled_ids = {
        enrollment.student_id
        for enrollment in db.query(models.ClassEnrollment).filter(
            models.ClassEnrollment.class_id == exam.class_id,
            models.ClassEnrollment.status == "active"
        ).all()
    }
        
    for item in data.scores:
        if item.student_id not in enrolled_ids:
            raise HTTPException(status_code=400, detail="Score includes a student outside this class")
        if item.score < 0 or item.score > exam.total_points:
            raise HTTPException(status_code=400, detail="Score must be between zero and total points")
        score_record = db.query(models.ExamScore).filter(models.ExamScore.exam_id == exam_id, models.ExamScore.student_id == item.student_id).first()
        passed = item.score >= exam.passing_grade
        if score_record:
            score_record.score = item.score
            score_record.passed = passed
        else:
            db.add(models.ExamScore(
                exam_id=exam_id,
                student_id=item.student_id,
                score=item.score,
                passed=passed
            ))
            
    exam.status = 'grading'
    db.commit()
    log_audit(db, user['id'], "إدخال درجات", "Exam", exam_id, None, {"exam_title": exam.title})
    return {"message": "Scores saved successfully"}

@router.post("/{exam_id}/publish")
def publish_exam(exam_id: int, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    if exam.status == 'published':
        raise HTTPException(status_code=400, detail="Exam already published")
        
    exam.status = 'published'
    db.commit()
    
    # If certification, check for passing students and auto-promote
    if exam.is_certification:
        subject = db.query(models.Subject).filter(models.Subject.id == exam.subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        import uuid
        
        scores = db.query(models.ExamScore).filter(models.ExamScore.exam_id == exam_id).all()
        for s in scores:
            if not exam.total_points:
                continue
            perc = (s.score / exam.total_points) * 100
            
            if perc >= subject.promotion_threshold:
                # Find current level in this subject
                ssl = db.query(models.StudentSubjectLevel).filter(
                    models.StudentSubjectLevel.student_id == s.student_id,
                    models.StudentSubjectLevel.subject_id == subject.id
                ).first()
                
                if not ssl:
                    continue
                    
                current_level = db.query(models.Level).filter(models.Level.id == ssl.current_level_id).first()
                if current_level and current_level.next_level_id:
                    # Promote Automatically!
                    ssl.current_level_id = current_level.next_level_id
                    
                    student = db.query(models.Student).filter(models.Student.id == s.student_id).first()
                    if student:
                        student.current_level_id = current_level.next_level_id
                    
                    history = models.LevelHistory(
                        student_id=s.student_id,
                        subject_id=subject.id,
                        from_level_id=current_level.id,
                        to_level_id=current_level.next_level_id,
                        reason=f"اجتاز اختبار ({exam.title}) بنسبة {perc:.1f}%",
                        approved_by=user["id"],
                        exam_ref=str(exam.id)
                    )
                    db.add(history)
                    
                    # Issue level completion certificate
                    cert_id = str(uuid.uuid4())[:8].upper()
                    cert = models.Certificate(
                        type="level_completion",
                        certificate_id=cert_id,
                        issued_by=user["id"],
                        student_id=s.student_id,
                        level_id=current_level.id,
                        class_id=exam.class_id,
                        template_key="level_completion"
                    )
                    db.add(cert)
                    
        db.commit()
        
    return {"message": "Exam published successfully"}


@router.get("/{exam_id}/gradebook")
def get_exam_gradebook(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    # Get all students in the class
    class_students = db.query(models.Student).join(models.ClassEnrollment).filter(
        models.ClassEnrollment.class_id == exam.class_id,
        models.ClassEnrollment.status == "active"
    ).all()
    
    # Get existing scores
    scores = {s.student_id: s for s in db.query(models.ExamScore).filter(models.ExamScore.exam_id == exam_id).all()}
    
    results = []
    for student in class_students:
        s = scores.get(student.id)
        results.append({
            "student_id": student.id,
            "student_name": student.full_name_ar,
            "score": s.score if s else None,
            "passed": s.passed if s else None
        })
        
    return {
        "exam": {
            "id": exam.id,
            "title": exam.title,
            "date": exam.date.isoformat() if exam.date else None,
            "total_points": exam.total_points
        },
        "grades": results
    }
