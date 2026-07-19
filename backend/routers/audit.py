from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .. import models, auth
from ..database import get_db

router = APIRouter(prefix="/api/audit", tags=["audit"])

def log_audit(db: Session, actor_id: int, action: str, entity_type: str, entity_id: int, before_text: dict = None, after_text: dict = None):
    try:
        log = models.AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_text=before_text,
            after_text=after_text
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"Failed to write audit log: {e}")
        db.rollback()

@router.get("/")
def get_audit_logs(limit: int = 200, db: Session = Depends(get_db), user: dict = Depends(auth.require_boss)):
        
    logs = db.query(models.AuditLog).order_by(desc(models.AuditLog.created_at)).limit(limit).all()
    
    actor_ids = list(set([l.actor_id for l in logs]))
    users = db.query(models.User).filter(models.User.id.in_(actor_ids)).all() if actor_ids else []
    user_map = {u.id: u.full_name_ar for u in users}
    
    result = []
    for l in logs:
        result.append({
            "id": l.id,
            "actor": user_map.get(l.actor_id, "مجهول"),
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "created_at": l.created_at.isoformat(),
            "details": f"Before: {l.before_text} | After: {l.after_text}" if (l.before_text or l.after_text) else ""
        })
        
    return result
