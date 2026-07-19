from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from pydantic import BaseModel
from .. import models, auth
from ..database import get_db

router = APIRouter(prefix="/api/settings", tags=["Settings"])

# Default settings seeded on first run
DEFAULT_SETTINGS = {
    "institution_name": "الروضة",
    "currency": "ج.م",
    "stuck_threshold_months": "6",
    "stuck_threshold_grade": "50",
    "default_passing_grade": "50",
}


def seed_default_settings(db: Session):
    """Insert default settings if they don't exist yet."""
    for key, value in DEFAULT_SETTINGS.items():
        existing = db.query(models.Setting).filter(models.Setting.key == key).first()
        if not existing:
            db.add(models.Setting(key=key, value_text=value))
    db.commit()


class SettingsUpdate(BaseModel):
    settings: Dict[str, str]


@router.get("/")
def get_settings(
    db: Session = Depends(get_db),
    user: dict = Depends(auth.get_current_user),
):
    rows = db.query(models.Setting).all()
    return {row.key: row.value_text for row in rows}


@router.put("/")
def update_settings(
    data: SettingsUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(auth.require_boss),
):
    for key, value in data.settings.items():
        row = db.query(models.Setting).filter(models.Setting.key == key).first()
        if row:
            row.value_text = value
        else:
            db.add(models.Setting(key=key, value_text=value))
    db.commit()
    return {"message": "تم حفظ الإعدادات بنجاح"}
