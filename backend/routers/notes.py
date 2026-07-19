from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from .. import models, auth
from ..database import get_db

router = APIRouter(prefix="/api/notes", tags=["Notes"])

class NoteCreate(BaseModel):
    target_type: str
    target_id: int
    category: Optional[str] = None
    severity: str = "low"
    visibility: str = "private"
    content: str

class NoteResponse(BaseModel):
    id: int
    target_type: str
    target_id: int
    author_id: int
    author_name: str
    category: Optional[str]
    severity: str
    visibility: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=NoteResponse)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if note.target_type not in ["student", "staff"]:
        raise HTTPException(status_code=400, detail="Invalid target type")
    if note.severity not in ["low", "medium", "high"]:
        raise HTTPException(status_code=400, detail="Invalid severity")
    if note.visibility not in ["private", "assigned_staff", "all_staff"]:
        raise HTTPException(status_code=400, detail="Invalid visibility")
        
    db_note = models.Note(
        target_type=note.target_type,
        target_id=note.target_id,
        author_id=current_user["id"],
        category=note.category,
        severity=note.severity,
        visibility=note.visibility,
        content=note.content
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    # We need the author name for the response
    author = db.query(models.User).filter(models.User.id == current_user["id"]).first()
    return {
        **db_note.__dict__,
        "author_name": author.full_name_ar if author else "Unknown"
    }

@router.get("/{target_type}/{target_id}", response_model=List[NoteResponse])
def get_notes(
    target_type: str,
    target_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    if target_type not in ["student", "staff"]:
        raise HTTPException(status_code=400, detail="Invalid target type")

    notes = db.query(models.Note).filter(
        models.Note.target_type == target_type,
        models.Note.target_id == target_id
    ).order_by(models.Note.created_at.desc()).all()
    
    result = []
    for note in notes:
        # Determine visibility
        if note.visibility == "private" and note.author_id != current_user["id"]:
            # Boss can see everything
            if current_user["role"] != "boss":
                continue
        
        author = db.query(models.User).filter(models.User.id == note.author_id).first()
        author_name = author.full_name_ar if author else "Unknown"
        
        result.append({
            **note.__dict__,
            "author_name": author_name
        })
        
    return result

@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if current_user["role"] != "boss" and note.author_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully"}
