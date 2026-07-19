from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import os
from .. import models, auth
from ..database import get_db

router = APIRouter(prefix="/api/certificates", tags=["Certificates"])

@router.get("/student/{student_id}")
def get_student_certificates(student_id: int, db: Session = Depends(get_db)):
    certificates = db.query(models.Certificate).filter(models.Certificate.student_id == student_id).order_by(models.Certificate.issued_at.desc()).all()
    res = []
    for cert in certificates:
        res.append({
            "id": cert.id,
            "certificate_id": cert.certificate_id,
            "type": cert.type,
            "template_key": cert.template_key,
            "status": cert.status,
            "issued_at": str(cert.issued_at)
        })
    return res

@router.get("/{cert_id}", response_class=HTMLResponse)
def get_certificate(cert_id: str, db: Session = Depends(get_db)):
    cert = db.query(models.Certificate).filter(models.Certificate.certificate_id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
        
    student = db.query(models.Student).filter(models.Student.id == cert.student_id).first()
    level = db.query(models.Level).filter(models.Level.id == cert.level_id).first()
    cls = db.query(models.Class).filter(models.Class.id == cert.class_id).first()
    
    # Load template
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", f"{cert.template_key}.html.tpl")
    if not os.path.exists(template_path):
        raise HTTPException(status_code=500, detail="Template not found")
        
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    # Get Institution Name and Currency
    institution_name_setting = db.query(models.Setting).filter(models.Setting.key == "institution_name").first()
    institution_name = institution_name_setting.value_text if institution_name_setting else "الروضة"
    
    currency_setting = db.query(models.Setting).filter(models.Setting.key == "currency").first()
    currency = currency_setting.value_text if currency_setting else "ج.م"
        
    # Calculate Age
    age_at_enrollment = "غير محدد"
    if student and student.dob and cert.issued_at:
        age_at_enrollment = str(cert.issued_at.date().year - student.dob.year)
        
    # Replace placeholders
    html = html.replace("{{institution_name}}", institution_name)
    html = html.replace("{{ institution_name }}", institution_name)
    html = html.replace("{{currency}}", currency)
    html = html.replace("{{student_name}}", student.full_name_ar if student else "")
    html = html.replace("{{enroll_date}}", str(student.enrollment_date) if student and student.enrollment_date else "")
    html = html.replace("{{dob}}", str(student.dob) if student and student.dob else "غير محدد")
    html = html.replace("{{address}}", student.address if student and student.address else "غير محدد")
    html = html.replace("{{father_phone}}", student.father_phone if student and student.father_phone else "غير محدد")
    html = html.replace("{{mother_phone}}", student.mother_phone if student and student.mother_phone else "غير محدد")
    html = html.replace("{{level_name}}", level.name_ar if level else "")
    html = html.replace("{{age_at_enrollment}}", age_at_enrollment)
    html = html.replace("{{class_name}}", cls.name_ar if cls else "")
    html = html.replace("{{date}}", str(cert.issued_at.date()))
    html = html.replace("{{ issue_date }}", str(cert.issued_at.date()))
    html = html.replace("{{certificate_id}}", cert.certificate_id)
    
    # Specific for payment_receipt
    if cert.type == "payment_receipt" and cert.payment_id:
        payment = db.query(models.Payment).filter(models.Payment.id == cert.payment_id).first()
        if payment:
            # Get receiver name
            receiver = db.query(models.User).filter(models.User.id == payment.received_by).first()
            receiver_name = receiver.full_name_ar if receiver else "غير معروف"
            
            invoice = None
            if payment.invoice_id:
                invoice = db.query(models.Invoice).filter(models.Invoice.id == payment.invoice_id).first()
            
            method_ar = {"cash": "نقدي", "bank": "حوالة بنكية", "card": "بطاقة"}.get(payment.method, payment.method)
            
            # Determine title
            invoice_title = payment.notes
            if invoice and invoice.title:
                invoice_title = invoice.title
            if not invoice_title:
                invoice_title = "سداد حر"
                
            html = html.replace("{{payment_method}}", method_ar)
            html = html.replace("{{amount}}", str(payment.amount))
            html = html.replace("{{invoice_title}}", invoice_title)
            html = html.replace("{{received_by_name}}", receiver_name)
        else:
            html = html.replace("{{payment_method}}", "").replace("{{amount}}", "").replace("{{invoice_title}}", "").replace("{{received_by_name}}", "غير معروف")
    
    return HTMLResponse(content=html)
