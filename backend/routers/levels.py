from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from .. import models, auth
from ..database import get_db

router = APIRouter(prefix="/api/levels", tags=["Levels"])

class LevelCreate(BaseModel):
    name_ar: str
    code: str
    description: Optional[str] = None
    order_index: int = 0
    subject_id: Optional[int] = None
    next_level_id: Optional[int] = None

@router.get("/")
def get_levels(subject_id: Optional[int] = None, db: Session = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    query = db.query(models.Level).order_by(models.Level.order_index)
    if subject_id:
        query = query.filter(models.Level.subject_id == subject_id)
    levels = query.all()
    
    subjects = {s.id: s for s in db.query(models.Subject).all()}
    
    res = []
    for level in levels:
        subj_name = subjects[level.subject_id].name_ar if level.subject_id and level.subject_id in subjects else None
        res.append({
            "id": level.id,
            "name_ar": level.name_ar,
            "code": level.code,
            "order_index": level.order_index,
            "subject_id": level.subject_id,
            "subject_name_ar": subj_name,
            "next_level_id": level.next_level_id
        })
    return res

@router.post("/")
def create_level(level: LevelCreate, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    db_level = models.Level(
        name_ar=level.name_ar,
        code=level.code,
        description=level.description,
        order_index=level.order_index,
        subject_id=level.subject_id
    )
    db.add(db_level)
    db.commit()
    db.refresh(db_level)
    
    # Auto-link the previous level's next_level_id to this one if it's the newest in the subject
    if level.subject_id:
        prev_level = db.query(models.Level).filter(
            models.Level.subject_id == level.subject_id,
            models.Level.id != db_level.id
        ).order_by(models.Level.order_index.desc()).first()
        if prev_level and not prev_level.next_level_id:
            prev_level.next_level_id = db_level.id
            db.commit()
            
    return {"id": db_level.id, "name_ar": db_level.name_ar}

@router.put("/{id}")
def update_level(id: int, level: LevelCreate, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    db_level = db.query(models.Level).filter(models.Level.id == id).first()
    if not db_level:
        raise HTTPException(status_code=404, detail="Level not found")
        
    db_level.name_ar = level.name_ar
    db_level.code = level.code
    db_level.description = level.description
    db_level.order_index = level.order_index
    if level.subject_id is not None:
        db_level.subject_id = level.subject_id
    if level.next_level_id is not None:
        db_level.next_level_id = level.next_level_id
    db.commit()
    return {"id": db_level.id, "name_ar": db_level.name_ar}

@router.delete("/{id}")
def delete_level(id: int, db: Session = Depends(get_db), user: dict = Depends(auth.require_academic_admin)):
    db_level = db.query(models.Level).filter(models.Level.id == id).first()
    if not db_level:
        raise HTTPException(status_code=404, detail="Level not found")
        
    # Check for dependent classes
    dependent_classes = db.query(models.Class).filter(models.Class.level_id == id).first()
    if dependent_classes:
        raise HTTPException(status_code=400, detail="Cannot delete level because it has classes. Delete or move classes first.")
        
    if db.query(models.StudentSubjectLevel).filter(models.StudentSubjectLevel.current_level_id == id).first():
        raise HTTPException(status_code=400, detail="لا يمكن حذف المستوى لوجود طلاب مرتبطين به.")
        
    if db.query(models.FeeTemplate).filter(models.FeeTemplate.level_id == id).first():
        raise HTTPException(status_code=400, detail="لا يمكن حذف المستوى لوجود قوالب رسوم مرتبطة به.")
    db.delete(db_level)
    db.commit()
    return {"message": "Level deleted successfully"}
