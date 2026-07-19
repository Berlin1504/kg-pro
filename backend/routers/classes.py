from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from .. import models, auth
from ..database import get_db
from .audit import log_audit

router = APIRouter(prefix="/api/classes", tags=["Classes"])

class ClassCreate(BaseModel):
    name_ar: str
    code: Optional[str] = None
    level_id: int
    group_label: str
    capacity: int = 20
    status: Optional[str] = 'active'
    teacher_id: Optional[int] = None

def build_roster(db: Session, class_id: int):
    enrollments = db.query(models.ClassEnrollment).filter(
        models.ClassEnrollment.class_id == class_id,
        models.ClassEnrollment.status == "active"
    ).all()
    student_ids = [e.student_id for e in enrollments]
    if not student_ids:
        return []
        
    students = {s.id: s for s in db.query(models.Student).filter(models.Student.id.in_(student_ids)).all()}
    
    roster = []
    for enrollment in enrollments:
        student = students.get(enrollment.student_id)
        if not student:
            continue
        roster.append({
            "enrollment_id": enrollment.id,
            "student": {
                "id": student.id,
                "full_name_ar": student.full_name_ar,
                "dob": student.dob,
                "contact_phone": student.contact_phone,
                "father_phone": student.father_phone,
                "mother_phone": student.mother_phone,
                "guardian_name": student.guardian_name,
                "guardian_phone": student.guardian_phone,
                "address": student.address,
                "enrollment_date": student.enrollment_date,
                "current_level_id": student.current_level_id,
                "status": student.status,
            }
        })
    return roster

@router.get("/")
def get_classes(db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    query = db.query(models.Class)
    
    if user['role'] == 'teacher':
        # Filter classes to those the teacher is assigned to
        teacher_class_ids = [ct.class_id for ct in db.query(models.ClassTeacher).filter(models.ClassTeacher.teacher_id == user['id']).all()]
        query = query.filter(
            (models.Class.teacher_id == user['id']) | 
            (models.Class.id.in_(teacher_class_ids))
        )
        
    classes = query.all()
    levels = {l.id: l for l in db.query(models.Level).all()}
    
    # Get all active enrollments grouped by class_id to avoid N+1 count() queries
    from sqlalchemy import func
    counts_query = db.query(models.ClassEnrollment.class_id, func.count(models.ClassEnrollment.id)).filter(models.ClassEnrollment.status == "active").group_by(models.ClassEnrollment.class_id).all()
    roster_counts = {class_id: count for class_id, count in counts_query}
    
    # Get supervisors and teachers
    staff_users = db.query(models.User).filter(models.User.role.in_(['supervisor', 'teacher'])).all()
    staff_map = {u.id: u for u in staff_users}
    
    # Get all class_teachers assignments
    class_teachers = db.query(models.ClassTeacher).all()
    ct_map = {}
    for ct in class_teachers:
        if ct.class_id not in ct_map:
            ct_map[ct.class_id] = []
        ct_map[ct.class_id].append(ct.teacher_id)
    
    res = []
    for cls in classes:
        level = levels.get(cls.level_id)
        sup = staff_map.get(cls.supervisor_id)
        teacher = staff_map.get(cls.teacher_id)
        
        # Build assigned teachers list
        assigned_teachers = []
        if teacher:
            assigned_teachers.append({"id": teacher.id, "full_name_ar": teacher.full_name_ar})
        for tid in ct_map.get(cls.id, []):
            if tid != getattr(teacher, 'id', None) and tid in staff_map:
                t = staff_map[tid]
                assigned_teachers.append({"id": t.id, "full_name_ar": t.full_name_ar})
                
        res.append({
            "id": cls.id,
            "name_ar": cls.name_ar,
            "level_id": cls.level_id,
            "level_name": level.name_ar if level else "",
            "group_label": cls.group_label,
            "capacity": cls.capacity,
            "roster_count": roster_counts.get(cls.id, 0),
            "status": cls.status,
            "supervisor": {"id": sup.id, "full_name_ar": sup.full_name_ar} if sup else None,
            "teacher": {"id": teacher.id, "full_name_ar": teacher.full_name_ar} if teacher else None,
            "assigned_teachers": assigned_teachers
        })
    return res

@router.post("/")
def create_class(cls_data: ClassCreate, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    if cls_data.capacity <= 0:
        raise HTTPException(status_code=400, detail="Class capacity must be greater than zero")
    level = db.query(models.Level).filter(models.Level.id == cls_data.level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    db_cls = models.Class(**cls_data.dict())
    db.add(db_cls)
    db.commit()
    db.refresh(db_cls)
    log_audit(db, user['id'], "إضافة فصل", "Class", db_cls.id, None, {"name": db_cls.name_ar})
    return db_cls

@router.get("/{id}")
def get_class(id: int, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    cls = db.query(models.Class).filter(models.Class.id == id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
        
    return {
        "id": cls.id,
        "name_ar": cls.name_ar,
        "capacity": cls.capacity,
        "roster": build_roster(db, id)
    }

@router.get("/{id}/students")
def get_class_students(id: int, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    cls = db.query(models.Class).filter(models.Class.id == id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    return build_roster(db, id)

@router.get("/{id}/profile")
def get_class_profile(id: int, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    cls = db.query(models.Class).filter(models.Class.id == id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
        
    enrollments = db.query(models.ClassEnrollment).filter(models.ClassEnrollment.class_id == id, models.ClassEnrollment.status == 'active').all()
    student_ids = [e.student_id for e in enrollments]
    
    students = db.query(models.Student).filter(models.Student.id.in_(student_ids)).all()
    
    absences_by_student = {}
    scores_by_student = {sid: [] for sid in student_ids}
    stuck_students = []
    
    import datetime
    six_months_ago = datetime.datetime.utcnow() - datetime.timedelta(days=180)

    def as_naive_datetime(value):
        if isinstance(value, datetime.datetime):
            return value.replace(tzinfo=None)
        if isinstance(value, datetime.date):
            return datetime.datetime.combine(value, datetime.time.min)
        return None
    
    if student_ids:
        # Bulk fetch absences
        from sqlalchemy import func
        absence_counts = db.query(models.StudentAttendance.student_id, func.count(models.StudentAttendance.id))\
            .filter(models.StudentAttendance.student_id.in_(student_ids), models.StudentAttendance.status == 'absent')\
            .group_by(models.StudentAttendance.student_id).all()
        absences_by_student = {sid: count for sid, count in absence_counts}
        
        # Bulk fetch scores
        all_scores = db.query(models.ExamScore.student_id, models.ExamScore.score)\
            .join(models.Exam)\
            .filter(models.ExamScore.student_id.in_(student_ids), models.Exam.class_id == id)\
            .all()
        for sid, score in all_scores:
            scores_by_student[sid].append(score)
            
        # Bulk fetch level history (latest per student)
        history_subq = db.query(
            models.LevelHistory.student_id,
            func.max(models.LevelHistory.created_at).label('max_created_at')
        ).filter(models.LevelHistory.student_id.in_(student_ids))\
         .group_by(models.LevelHistory.student_id).subquery()
         
        last_histories = {row.student_id: row.max_created_at for row in db.query(history_subq).all()}
        
        for sid in student_ids:
            # Ensure 0 if no absences
            if sid not in absences_by_student:
                absences_by_student[sid] = 0
                
            student = next((s for s in students if s.id == sid), None)
            if student:
                last_change = as_naive_datetime(last_histories.get(sid) or student.enrollment_date)
                if last_change and last_change < six_months_ago:
                    stuck_students.append({
                        "student_id": sid,
                        "name": student.full_name_ar,
                        "months": (datetime.datetime.utcnow() - last_change).days // 30
                    })

    most_absent_ids = sorted(absences_by_student, key=absences_by_student.get, reverse=True)
    
    avg_scores = {}
    for sid, scores in scores_by_student.items():
        if scores:
            avg_scores[sid] = sum(scores) / len(scores)
        else:
            avg_scores[sid] = 0
            
    sorted_by_score = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
    
    profile = {
        "class_id": id,
        "total_students": len(students),
        "leading": [], 
        "weak": [], 
        "most_absent": [],
        "stuck": stuck_students
    }
    
    for sid in most_absent_ids[:3]:
        if absences_by_student[sid] > 0:
            student = next((s for s in students if s.id == sid), None)
            profile["most_absent"].append({
                "student_id": sid,
                "name": student.full_name_ar if student else "",
                "count": absences_by_student[sid]
            })
            
    # Leading (top 3)
    for sid, score in sorted_by_score[:3]:
        if score > 0:
            student = next((s for s in students if s.id == sid), None)
            profile["leading"].append({
                "student_id": sid,
                "name": student.full_name_ar if student else "",
                "score": round(score, 1)
            })
            
    # Weak (bottom 3) - reversed logic
    sorted_weak = sorted(avg_scores.items(), key=lambda x: x[1])
    for sid, score in sorted_weak[:3]:
        # Only consider weak if they have scores and it's below some threshold (e.g. 60)
        # Or if we just take bottom 3 anyway:
        if len(scores_by_student[sid]) > 0 and score < 60:
            student = next((s for s in students if s.id == sid), None)
            profile["weak"].append({
                "student_id": sid,
                "name": student.full_name_ar if student else "",
                "score": round(score, 1)
            })
                
    return profile

@router.put("/{id}")
def update_class(id: int, cls_data: ClassCreate, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    db_cls = db.query(models.Class).filter(models.Class.id == id).first()
    if not db_cls:
        raise HTTPException(status_code=404, detail="Class not found")
        
    db_cls.name_ar = cls_data.name_ar
    db_cls.code = cls_data.code
    db_cls.level_id = cls_data.level_id
    db_cls.group_label = cls_data.group_label
    db_cls.capacity = cls_data.capacity
    db_cls.teacher_id = cls_data.teacher_id
    db.commit()
    db.refresh(db_cls)
    log_audit(db, user['id'], "تحديث بيانات الفصل", "Class", id, None, {"name": db_cls.name_ar})
    return db_cls

@router.delete("/{id}")
def delete_class(id: int, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    db_cls = db.query(models.Class).filter(models.Class.id == id).first()
    if not db_cls:
        raise HTTPException(status_code=404, detail="Class not found")
        
    # Check for dependent students in roster
    enrolled = db.query(models.ClassEnrollment).filter(models.ClassEnrollment.class_id == id).first()
    if enrolled:
        raise HTTPException(status_code=400, detail="Cannot delete class with enrolled students. Unenroll them first.")
    if db.query(models.Session).filter(models.Session.class_id == id).first():
        raise HTTPException(status_code=400, detail="لا يمكن حذف الفصل لوجود حصص مسجلة مرتبطة به.")
    if db.query(models.Exam).filter(models.Exam.class_id == id).first():
        raise HTTPException(status_code=400, detail="لا يمكن حذف الفصل لوجود اختبارات مرتبطة به.")
        
    db.query(models.ClassTeacher).filter(models.ClassTeacher.class_id == id).delete()
    db.query(models.ClassSchedule).filter(models.ClassSchedule.class_id == id).delete()
    
    # Reconcile financials for students whose invoices are deleted
    invoices_to_delete = db.query(models.Invoice).filter(models.Invoice.class_id == id).all()
    affected_students = list(set([inv.student_id for inv in invoices_to_delete]))
    db.query(models.Invoice).filter(models.Invoice.class_id == id).delete()
    
    db.delete(db_cls)
    db.commit()
    
    from .finance import reconcile_financials
    for st_id in affected_students:
        reconcile_financials(st_id, db)
        
    log_audit(db, user['id'], "حذف فصل", "Class", id, {"name": db_cls.name_ar}, None)
    return {"message": "Class deleted successfully"}
