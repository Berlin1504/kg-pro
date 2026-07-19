from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from ..database import get_db
from .. import models, auth
from .audit import log_audit

router = APIRouter(prefix="/api/staff", tags=["staff"])


# --- Schemas ---

class StaffCreate(BaseModel):
    full_name_ar: str
    email: str
    password: str
    role: str  # 'teacher', 'supervisor', 'moneyman'
    phone: Optional[str] = None
    base_salary: Optional[float] = 0.0
    class_ids: List[int] = []

class StaffUpdate(BaseModel):
    full_name_ar: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    base_salary: Optional[float] = None
    class_ids: Optional[List[int]] = None



# --- Staff CRUD (Boss only) ---

@router.get("/")
def get_all_staff(
    db: Session = Depends(get_db),
    user: dict = Depends(auth.get_current_user),
):
    staff = db.query(models.User).filter(models.User.status == "active").all()
    class_teachers = db.query(models.ClassTeacher).all()
    ct_map = {}
    for ct in class_teachers:
        if ct.teacher_id not in ct_map:
            ct_map[ct.teacher_id] = []
        ct_map[ct.teacher_id].append(ct.class_id)
        
    return [
        {
            "id": s.id,
            "full_name_ar": s.full_name_ar,
            "email": s.email,
            "phone": s.phone,
            "role": s.role,
            "status": s.status,
            "base_salary": s.base_salary,
            "class_ids": ct_map.get(s.id, [])
        }
        for s in staff
    ]


@router.post("/")
def create_staff(
    data: StaffCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(auth.require_boss),
):
    if data.role not in ("teacher", "supervisor", "moneyman"):
        raise HTTPException(status_code=400, detail="الدور يجب أن يكون: teacher أو supervisor أو moneyman")
    existing = db.query(models.User).filter(models.User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="البريد الإلكتروني مستخدم بالفعل")
    new_user = models.User(
        full_name_ar=data.full_name_ar,
        email=data.email,
        phone=data.phone,
        role=data.role,
        base_salary=data.base_salary,
        password_hash=auth.get_password_hash(data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    if data.class_ids:
        for cid in data.class_ids:
            db.add(models.ClassTeacher(class_id=cid, teacher_id=new_user.id))
        db.commit()
        
    log_audit(db, user['id'], "إضافة موظف", "User", new_user.id, None, {"name": new_user.full_name_ar, "role": new_user.role})
        
    return {
        "id": new_user.id,
        "full_name_ar": new_user.full_name_ar,
        "email": new_user.email,
        "role": new_user.role,
        "class_ids": data.class_ids
    }


@router.put("/{staff_id}")
def update_staff(
    staff_id: int,
    data: StaffUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(auth.require_boss),
):
    staff_user = db.query(models.User).filter(models.User.id == staff_id).first()
    if not staff_user:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
    if data.full_name_ar is not None:
        staff_user.full_name_ar = data.full_name_ar
    if data.email is not None:
        dup = db.query(models.User).filter(
            models.User.email == data.email,
            models.User.id != staff_id,
        ).first()
        if dup:
            raise HTTPException(status_code=400, detail="البريد الإلكتروني مستخدم بالفعل")
        staff_user.email = data.email
    if data.phone is not None:
        staff_user.phone = data.phone
    if data.role is not None:
        if data.role not in ("teacher", "supervisor", "moneyman", "boss"):
            raise HTTPException(status_code=400, detail="دور غير صالح")
        staff_user.role = data.role
    if data.base_salary is not None:
        staff_user.base_salary = data.base_salary
        
    if data.class_ids is not None:
        db.query(models.ClassTeacher).filter(models.ClassTeacher.teacher_id == staff_id).delete()
        for cid in data.class_ids:
            db.add(models.ClassTeacher(class_id=cid, teacher_id=staff_id))
            
    db.commit()
    log_audit(db, user['id'], "تحديث بيانات الموظف", "User", staff_id, None, data.dict(exclude_unset=True))
    
    return {"message": "تم تحديث بيانات الموظف"}


class StaffClassesUpdate(BaseModel):
    class_ids: List[int]

@router.put("/{staff_id}/classes")
def update_staff_classes(
    staff_id: int,
    data: StaffClassesUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(auth.require_boss)
):
    staff_user = db.query(models.User).filter(models.User.id == staff_id).first()
    if not staff_user:
        raise HTTPException(status_code=404, detail="Staff not found")
        
    db.query(models.ClassTeacher).filter(models.ClassTeacher.teacher_id == staff_id).delete()
    for cid in data.class_ids:
        db.add(models.ClassTeacher(class_id=cid, teacher_id=staff_id))
        
    db.commit()
    log_audit(db, user['id'], "تحديث فصول المعلم", "User", staff_id, None, {"class_ids": data.class_ids})
    
    return {"message": "تم تحديث فصول الموظف بنجاح"}


@router.delete("/{staff_id}")
def deactivate_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(auth.require_boss),
):
    staff_user = db.query(models.User).filter(models.User.id == staff_id).first()
    if not staff_user:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
    if staff_user.id == user["id"]:
        raise HTTPException(status_code=400, detail="لا يمكنك إلغاء تفعيل حسابك")
    staff_user.status = "inactive"
    db.commit()
    
    log_audit(db, user['id'], "إلغاء تفعيل موظف", "User", staff_id, {"status": "active"}, {"status": "inactive"})
    
    return {"message": "تم إلغاء تفعيل الموظف"}


class StaffPasswordUpdate(BaseModel):
    password: str


@router.put("/{staff_id}/password")
def update_staff_password(
    staff_id: int,
    data: StaffPasswordUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(auth.get_current_user),
):
    staff_user = db.query(models.User).filter(models.User.id == staff_id).first()
    if not staff_user:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
        
    # Only boss can change others' passwords, or the user can change their own
    if user["role"] != "boss" and user["id"] != staff_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    staff_user.password_hash = auth.get_password_hash(data.password)
    db.commit()
    
    log_audit(db, user['id'], "تغيير كلمة المرور", "User", staff_id)
    
    return {"message": "تم تغيير كلمة المرور بنجاح"}



