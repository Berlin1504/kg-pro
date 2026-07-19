from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import shutil

from .. import models, auth
from ..database import get_db, engine, DEFAULT_DB_PATH

router = APIRouter(prefix="/api/db", tags=["Database Management"])

@router.get("/download")
def download_database(user: dict = Depends(auth.require_boss)):
    if not os.path.exists(DEFAULT_DB_PATH):
        raise HTTPException(status_code=404, detail="Database file not found.")
        
    return FileResponse(path=DEFAULT_DB_PATH, filename="school_backup.db", media_type="application/octet-stream")

@router.post("/upload")
def upload_database(file: UploadFile = File(...), user: dict = Depends(auth.require_boss)):
    if not file.filename.endswith(".db"):
        raise HTTPException(status_code=400, detail="Invalid file type. Must be a .db file.")
        
    try:
        with open(DEFAULT_DB_PATH, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to overwrite database: {str(e)}")
        
    return {"message": "Database uploaded successfully."}

class WipeRequest(BaseModel):
    password: str

@router.post("/wipe")
def wipe_database(req: WipeRequest, user: dict = Depends(auth.require_boss)):
    if req.password != "112233**":
        raise HTTPException(status_code=401, detail="كلمة المرور غير صحيحة")
    try:
        db = next(get_db())
        current_boss = db.query(models.User).filter(models.User.id == user["id"]).first()
        if not current_boss:
            raise HTTPException(status_code=404, detail="Current boss user not found.")
            
        boss_dict = {
            "full_name_ar": current_boss.full_name_ar,
            "email": current_boss.email,
            "phone": current_boss.phone,
            "role": current_boss.role,
            "status": current_boss.status,
            "password_hash": current_boss.password_hash
        }
        
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)
        
        new_db = next(get_db())
        restored_boss = models.User(**boss_dict)
        new_db.add(restored_boss)
        new_db.commit()
        
        from .settings import seed_default_settings
        seed_default_settings(new_db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to wipe database: {str(e)}")
        
    return {"message": "Database wiped and reset successfully. Your boss account has been restored."}
