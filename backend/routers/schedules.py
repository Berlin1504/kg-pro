from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..database import get_db
from .. import models, auth

router = APIRouter(prefix="/api/schedules", tags=["schedules"])

class ScheduleCreate(BaseModel):
    class_id: int
    subject_id: int
    teacher_id: Optional[int] = None
    day_of_week: int
    start_time: str
    end_time: str

@router.get("/")
def get_schedules(class_id: Optional[int] = None, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    query = db.query(models.ClassSchedule)
    if class_id:
        query = query.filter(models.ClassSchedule.class_id == class_id)
    return query.all()

@router.post("/")
def create_schedule(sched: ScheduleCreate, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
        
    # Check for teacher conflict
    if sched.teacher_id:
        teacher_conflicts = db.query(models.ClassSchedule).filter(
            models.ClassSchedule.teacher_id == sched.teacher_id,
            models.ClassSchedule.day_of_week == sched.day_of_week,
            models.ClassSchedule.start_time < sched.end_time,
            models.ClassSchedule.end_time > sched.start_time
        ).first()
        if teacher_conflicts:
            raise HTTPException(status_code=400, detail="تعارض: المعلم لديه حصة أخرى في هذا الوقت.")
            
    # Check for class conflict
    class_conflicts = db.query(models.ClassSchedule).filter(
        models.ClassSchedule.class_id == sched.class_id,
        models.ClassSchedule.day_of_week == sched.day_of_week,
        models.ClassSchedule.start_time < sched.end_time,
        models.ClassSchedule.end_time > sched.start_time
    ).first()
    if class_conflicts:
        raise HTTPException(status_code=400, detail="تعارض: الفصل لديه حصة أخرى في هذا الوقت.")
    
    new_sched = models.ClassSchedule(**sched.dict())
    db.add(new_sched)
    db.commit()
    db.refresh(new_sched)
    return new_sched

@router.delete("/{sched_id}")
def delete_schedule(sched_id: int, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
        
    sched = db.query(models.ClassSchedule).filter(models.ClassSchedule.id == sched_id).first()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")
        
    db.delete(sched)
    db.commit()
    return {"message": "Deleted successfully"}
