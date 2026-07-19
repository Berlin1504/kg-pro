from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime
import uuid
from .. import models, auth
from .audit import log_audit
from ..database import get_db

router = APIRouter(prefix="/api/students", tags=["Students"])

class StudentCreate(BaseModel):
    full_name_ar: str
    dob: Optional[date] = None
    address: Optional[str] = None
    father_phone: Optional[str] = None
    mother_phone: Optional[str] = None
    contact_phone: Optional[str] = None
    guardian_phone: Optional[str] = None

class SubjectLevelInput(BaseModel):
    subject_id: int
    level_id: int

class ClassEnroll(BaseModel):
    class_id: int
    subject_levels: Optional[List[SubjectLevelInput]] = None

@router.get("/")
def get_students(class_id: Optional[int] = None, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    query = db.query(models.Student)
    if class_id is not None:
        query = query.join(models.ClassEnrollment).filter(
            models.ClassEnrollment.class_id == class_id,
            models.ClassEnrollment.status == 'active'
        )
    students = query.all()
    res = []
    
    from sqlalchemy import func
    student_ids = [s.id for s in students]
    absence_counts = {}
    if student_ids:
        absence_query = db.query(
            models.StudentAttendance.student_id, 
            func.count(models.StudentAttendance.id)
        ).filter(
            models.StudentAttendance.student_id.in_(student_ids),
            models.StudentAttendance.status == 'absent'
        ).group_by(models.StudentAttendance.student_id).all()
        absence_counts = {student_id: count for student_id, count in absence_query}
        
    for s in students:
        s_dict = {c.name: getattr(s, c.name) for c in s.__table__.columns}
        s_dict["absences"] = absence_counts.get(s.id, 0)
        res.append(s_dict)
    return res

@router.get("/{student_id}")
def get_single_student(student_id: int, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    from .finance import reconcile_financials
    reconcile_financials(student_id, db)
    
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {c.name: getattr(student, c.name) for c in student.__table__.columns}

@router.post("/")
def create_student(student: StudentCreate, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    db_student = models.Student(**student.dict(), enrollment_date=date.today())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    
    log_audit(db, user['id'], "إضافة طالب", "Student", db_student.id, None, {"name": db_student.full_name_ar})
    
    return db_student

@router.post("/{student_id}/enroll")
def enroll_student(student_id: int, enroll: ClassEnroll, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    cls = db.query(models.Class).filter(models.Class.id == enroll.class_id).first()
    if not student or not cls:
        raise HTTPException(status_code=404, detail="Student or Class not found")
    existing = db.query(models.ClassEnrollment).filter(
        models.ClassEnrollment.student_id == student_id,
        models.ClassEnrollment.class_id == enroll.class_id,
        models.ClassEnrollment.status == "active"
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student is already enrolled in this class")
    active_count = db.query(models.ClassEnrollment).filter(
        models.ClassEnrollment.class_id == enroll.class_id,
        models.ClassEnrollment.status == "active"
    ).count()
    if cls.capacity and active_count >= cls.capacity:
        raise HTTPException(status_code=400, detail="Class capacity has been reached")
    
    # Enroll
    enrollment = models.ClassEnrollment(
        class_id=cls.id,
        student_id=student.id,
        starting_level_id=cls.level_id
    )
    db.add(enrollment)
    
    # Update student starting level if not set
    if not student.starting_level_id:
        student.starting_level_id = cls.level_id
        student.current_level_id = cls.level_id
        
    cls_level = db.query(models.Level).filter(models.Level.id == cls.level_id).first()
    if cls_level and cls_level.subject_id:
        ssl = db.query(models.StudentSubjectLevel).filter(
            models.StudentSubjectLevel.student_id == student.id,
            models.StudentSubjectLevel.subject_id == cls_level.subject_id
        ).first()
        if not ssl:
            db.add(models.StudentSubjectLevel(
                student_id=student.id,
                subject_id=cls_level.subject_id,
                current_level_id=cls_level.id
            ))
    
    # Issue Certificate
    cert_id = str(uuid.uuid4())[:8].upper()
    cert = models.Certificate(
        type="level_start",
        certificate_id=cert_id,
        issued_by=user["id"],
        student_id=student.id,
        level_id=cls.level_id,
        class_id=cls.id,
        template_key="level_start"
    )
    db.add(cert)
    
    # Save subject levels if provided
    if enroll.subject_levels:
        for sl in enroll.subject_levels:
            ssl = db.query(models.StudentSubjectLevel).filter(
                models.StudentSubjectLevel.student_id == student.id,
                models.StudentSubjectLevel.subject_id == sl.subject_id
            ).first()
            if ssl:
                ssl.current_level_id = sl.level_id
            else:
                db.add(models.StudentSubjectLevel(
                    student_id=student.id,
                    subject_id=sl.subject_id,
                    current_level_id=sl.level_id
                ))
                
    db.commit()
    log_audit(db, user['id'], "تسجيل طالب في فصل", "Student", student_id, None, {"class_id": enroll.class_id})
    return {"message": "Enrolled successfully", "certificate_id": cert.certificate_id}

class ManualLevelUpdate(BaseModel):
    subject_id: int
    level_id: int
    class_id: Optional[int] = None
    reason: Optional[str] = None

@router.put("/{student_id}/subject-level")
def update_student_subject_level(student_id: int, data: ManualLevelUpdate, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    ssl = db.query(models.StudentSubjectLevel).filter(
        models.StudentSubjectLevel.student_id == student_id,
        models.StudentSubjectLevel.subject_id == data.subject_id
    ).first()
    
    from_level_id = ssl.current_level_id if ssl else None
    
    if ssl:
        ssl.current_level_id = data.level_id
        ssl.updated_at = datetime.utcnow()
    else:
        db.add(models.StudentSubjectLevel(
            student_id=student_id,
            subject_id=data.subject_id,
            current_level_id=data.level_id
        ))
        
    # Handle Class Enrollment if provided
    if data.class_id:
        # Check if class exists
        cls = db.query(models.Class).filter(models.Class.id == data.class_id).first()
        if cls:
            # Unenroll from old classes for the same subject/level
            old_enrollments = db.query(models.ClassEnrollment).filter(
                models.ClassEnrollment.student_id == student_id,
                models.ClassEnrollment.status == 'active'
            ).all()
            for e in old_enrollments:
                e_cls = db.query(models.Class).filter(models.Class.id == e.class_id).first()
                if e_cls and (e_cls.level_id == from_level_id or e_cls.level_id == data.level_id):
                    e.status = 'transferred'
                    
            # Enroll in new class
            db.add(models.ClassEnrollment(
                student_id=student_id,
                class_id=data.class_id,
                status='active'
            ))
            
            # Update student's primary level id if it was set
            student.current_level_id = data.level_id

    # Record history
    history = models.LevelHistory(
        student_id=student_id,
        subject_id=data.subject_id,
        from_level_id=from_level_id,
        to_level_id=data.level_id,
        reason=data.reason or "تغيير يدوي",
        approved_by=user["id"]
    )
    db.add(history)
    db.commit()
    log_audit(db, user['id'], "تحديث مستوى الطالب", "Student", student_id, None, {
        "subject_id": data.subject_id,
        "new_level_id": data.level_id,
        "reason": data.reason
    })
    return {"message": "Updated successfully"}

@router.get("/{id}/profile")
def get_student_profile(id: int, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    from .finance import reconcile_financials
    reconcile_financials(id, db)
    
    student = db.query(models.Student).filter(models.Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Get enrollments
    enrollments = db.query(models.ClassEnrollment).filter(models.ClassEnrollment.student_id == id).all()
    
    # Get subject levels
    subject_levels_db = db.query(models.StudentSubjectLevel).filter(models.StudentSubjectLevel.student_id == id).all()
    subjects = {s.id: s for s in db.query(models.Subject).all()}
    levels = {l.id: l for l in db.query(models.Level).all()}
    classes_map = {c.id: c for c in db.query(models.Class).all()}
    
    current_classes = []
    for en in enrollments:
        if en.status == 'active':
            c = classes_map.get(en.class_id)
            if c:
                lvl = levels.get(c.level_id)
                current_classes.append({
                    "class_id": c.id,
                    "class_name_ar": c.name_ar,
                    "level_name_ar": lvl.name_ar if lvl else "Unknown"
                })

    subject_levels = []
    for sl in subject_levels_db:
        subj = subjects.get(sl.subject_id)
        lvl = levels.get(sl.current_level_id)
        subject_levels.append({
            "subject_id": sl.subject_id,
            "subject_name_ar": subj.name_ar if subj else "Unknown",
            "level_id": sl.current_level_id,
            "level_name_ar": lvl.name_ar if lvl else "Unknown",
            "updated_at": sl.updated_at.isoformat() if sl.updated_at else None
        })
    
    # Get level history
    level_history = db.query(models.LevelHistory).filter(models.LevelHistory.student_id == id).order_by(models.LevelHistory.created_at.desc()).all()
    
    # Get certificates
    certificates = db.query(models.Certificate).filter(models.Certificate.student_id == id).all()
    
    # Get notes
    notes = db.query(models.Note).filter(models.Note.target_type == "student", models.Note.target_id == id).order_by(models.Note.created_at.desc()).all()
    
    # Compile timeline
    timeline = []
    
    # Add enrollment date
    timeline.append({
        "date": student.enrollment_date.isoformat() if student.enrollment_date else None,
        "type": "enrollment",
        "description": "تم تسجيل الطالب في المركز"
    })
    
    for h in level_history:
        to_level = levels.get(h.to_level_id)
        subj = subjects.get(h.subject_id)
        subj_name = f" في مادة {subj.name_ar}" if subj else ""
        timeline.append({
            "date": h.created_at.isoformat(),
            "type": "level_change",
            "description": f"انتقل إلى مستوى: {to_level.name_ar if to_level else 'غير معروف'}{subj_name} ({h.reason or ''})"
        })
        
    for c in certificates:
        timeline.append({
            "date": c.issued_at.isoformat() if c.issued_at else None,
            "type": "certificate",
            "description": f"إصدار شهادة: {c.type} ({c.certificate_id})"
        })
        
    for n in notes:
        timeline.append({
            "date": n.created_at.isoformat() if n.created_at else None,
            "type": "note",
            "severity": n.severity,
            "description": f"ملاحظة: {n.content}"
        })
        
    exam_records = db.query(models.ExamScore, models.Exam)\
        .join(models.Exam, models.ExamScore.exam_id == models.Exam.id)\
        .filter(models.ExamScore.student_id == id)\
        .order_by(models.Exam.date.desc()).all()
        
    exam_details = []
    total_score_percentage = 0
    exams_count = 0
    for score, exam in exam_records:
        subj = subjects.get(exam.subject_id)
        subj_name = subj.name_ar if subj else "Unknown"
        exam_details.append({
            "date": exam.date.isoformat() if exam.date else "",
            "title": exam.title,
            "subject": subj_name,
            "score": score.score,
            "total_points": exam.total_points
        })
        if score.score is not None and exam.total_points:
            perc = (score.score / exam.total_points) * 100
            total_score_percentage += perc
            exams_count += 1
            timeline.append({
                "date": exam.date.isoformat() if exam.date else None,
                "type": "exam",
                "description": f"أجرى اختبار {exam.title} ({subj_name}) وحصل على {score.score}/{exam.total_points} ({perc:.1f}%)"
            })
            
    # Sort timeline by date
    timeline.sort(key=lambda x: x["date"] or "", reverse=True)
    
    attendance_records = db.query(models.StudentAttendance, models.Session, models.Subject, models.Class)\
        .join(models.Session, models.StudentAttendance.session_id == models.Session.id)\
        .outerjoin(models.Subject, models.Session.subject_id == models.Subject.id)\
        .outerjoin(models.Class, models.Session.class_id == models.Class.id)\
        .filter(models.StudentAttendance.student_id == id)\
        .order_by(models.Session.date.desc()).all()
        
    attendance_details = []
    absent_count = 0
    late_count = 0
    for att, sess, subj, cls in attendance_records:
        if att.status == 'absent':
            absent_count += 1
        elif att.status == 'late':
            late_count += 1
            
        subj_name = subj.name_ar if subj else ""
        if cls:
            subj_name += f" ({cls.name_ar})"
            
        attendance_details.append({
            "date": sess.date.isoformat() if sess.date else "",
            "subject": subj_name,
            "status": att.status
        })
            
    average_score = (total_score_percentage / exams_count) if exams_count > 0 else 0
    
    return {
        "student": student,
        "student_subject_levels": subject_levels,
        "current_classes": current_classes,
        "timeline": timeline,
        "certificates": certificates,
        "absences": absent_count,
        "lates": late_count,
        "average_score": round(average_score, 1),
        "attendance_details": attendance_details,
        "exam_details": exam_details
    }

@router.put("/{student_id}")
def update_student(student_id: int, student_data: StudentCreate, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    db_student.full_name_ar = student_data.full_name_ar
    db_student.dob = student_data.dob
    db_student.address = student_data.address
    db_student.father_phone = student_data.father_phone
    db_student.mother_phone = student_data.mother_phone
    if student_data.contact_phone is not None:
        db_student.contact_phone = student_data.contact_phone
    if student_data.guardian_phone is not None:
        db_student.guardian_phone = student_data.guardian_phone
    if student_data.background_notes is not None:
        db_student.background_notes = student_data.background_notes
    
    db.commit()
    db.refresh(db_student)
    log_audit(db, user['id'], "تحديث بيانات الطالب", "Student", student_id, None, {"name": db_student.full_name_ar})
    return db_student

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # We allow deleting the student, and we can either cascade or delete dependencies.
    # Because of foreign keys in ClassEnrollment, StudentAttendance, Payment, etc, we should clean up if not cascaded.
    db.query(models.ClassEnrollment).filter(models.ClassEnrollment.student_id == student_id).delete()
    db.query(models.StudentAttendance).filter(models.StudentAttendance.student_id == student_id).delete()
    db.query(models.Payment).filter(models.Payment.student_id == student_id).delete()
    db.query(models.Invoice).filter(models.Invoice.student_id == student_id).delete()
    db.query(models.Certificate).filter(models.Certificate.student_id == student_id).delete()
    db.query(models.StudentSubjectLevel).filter(models.StudentSubjectLevel.student_id == student_id).delete()
    db.query(models.Note).filter(models.Note.target_type == 'student', models.Note.target_id == student_id).delete()
    db.query(models.ExamScore).filter(models.ExamScore.student_id == student_id).delete()
    db.query(models.LevelHistory).filter(models.LevelHistory.student_id == student_id).delete()
    
    db.delete(db_student)
    db.commit()
    log_audit(db, user['id'], "حذف طالب", "Student", student_id, {"name": db_student.full_name_ar}, None)
    return {"message": "Student deleted successfully"}

@router.put("/{student_id}/disable")
def disable_student(student_id: int, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    db_student.status = 'inactive'
    
    # Mark active enrollments as inactive
    enrollments = db.query(models.ClassEnrollment).filter(
        models.ClassEnrollment.student_id == student_id,
        models.ClassEnrollment.status == 'active'
    ).all()
    for e in enrollments:
        e.status = 'inactive'
        
    # Delete unpaid invoices
    db.query(models.Invoice).filter(
        models.Invoice.student_id == student_id,
        models.Invoice.paid_amount == 0
    ).delete()
    
    db.commit()
    
    # Recalculate financials
    from .finance import reconcile_financials
    reconcile_financials(student_id, db)
    
    log_audit(db, user['id'], "تعطيل طالب", "Student", student_id, {"name": db_student.full_name_ar}, None)
    return {"message": "تم أرشفة الطالب بنجاح"}

@router.put("/{student_id}/enable")
def enable_student(student_id: int, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    db_student.status = 'active'
    db.commit()
    
    log_audit(db, user['id'], "تنشيط طالب", "Student", student_id, {"name": db_student.full_name_ar}, None)
    return {"message": "تم إعادة تنشيط الطالب بنجاح"}
