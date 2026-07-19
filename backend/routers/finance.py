from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime
from .. import models, auth
from .audit import log_audit
from ..database import get_db

router = APIRouter(prefix="/api/finance", tags=["Finance"])

def require_finance_role(user: dict = Depends(auth.require_finance_access)):
    return user

# Pydantic Schemas

class FeeTemplateCreate(BaseModel):
    name_ar: str
    amount: float
    level_id: Optional[int] = None
    is_recurring: bool = True
    recurrence_type: str = "monthly"
    recurrence_label: Optional[str] = None

class BulkInvoiceCreate(BaseModel):
    fee_template_id: int
    class_id: int
    month_label: Optional[str] = None

class BulkSalaryCreate(BaseModel):
    month: str

class InvoiceCreate(BaseModel):
    student_id: int
    class_id: Optional[int] = None
    amount: float
    title: str
    due_date: Optional[date] = None
    notes: Optional[str] = None
    discount: Optional[float] = 0.0
    discount_type: Optional[str] = "fixed"
    paid_amount: Optional[float] = 0.0

class PaymentCreate(BaseModel):
    student_id: Optional[int] = None
    invoice_id: Optional[int] = None
    amount: float
    method: str
    receipt_no: Optional[str] = None
    notes: Optional[str] = None

def reconcile_financials(student_id: int, db: Session):
    # 1. Get all fees and payments
    all_fees = db.query(models.Invoice).filter(models.Invoice.student_id == student_id).all()
    all_payments = db.query(models.Payment).filter(models.Payment.student_id == student_id).all()
    
    # 2. Global Totals
    total_billed = sum(fee.net_total for fee in all_fees)
    total_paid = sum(payment.amount for payment in all_payments)
    
    # 3. Update Student Profile
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student:
        student.total_billed = total_billed
        student.total_paid = total_paid
        student.balance = total_billed - total_paid
        
    # 4. FIFO Distribution
    remaining_to_allot = total_paid
    
    # Sort fees oldest to newest based on created_at
    sorted_fees = sorted(all_fees, key=lambda f: f.created_at)
    
    for fee in sorted_fees:
        amount_to_apply = min(remaining_to_allot, fee.net_total)
        remaining_to_allot -= amount_to_apply
        
        fee.paid_amount = amount_to_apply
        fee.remaining = max(0.0, fee.net_total - amount_to_apply)
        
        if fee.remaining <= 0:
            fee.status = 'paid'
        elif fee.paid_amount > 0:
            fee.status = 'partial'
        else:
            fee.status = 'unpaid'
            
    db.commit()

class SalaryCreate(BaseModel):
    user_id: int
    month: str
    base_salary: float
    bonuses: Optional[float] = 0.0
    deductions: Optional[float] = 0.0
    days_deducted: Optional[int] = 0

class SalaryPay(BaseModel):
    status: str # "paid"

class ExpenseCreate(BaseModel):
    category: str
    amount: float
    description: Optional[str] = None
    date: date

# ----------------- FEE TEMPLATES -----------------

@router.get("/fee-templates")
def get_fee_templates(db: Session = Depends(get_db), user: dict = Depends(require_finance_role)):
    templates = db.query(models.FeeTemplate).filter(models.FeeTemplate.status == "active").all()
    level_ids = [t.level_id for t in templates if t.level_id]
    levels = {l.id: l for l in db.query(models.Level).filter(models.Level.id.in_(level_ids)).all()} if level_ids else {}
    
    res = []
    for t in templates:
        level = levels.get(t.level_id)
        res.append({
            "id": t.id,
            "name_ar": t.name_ar,
            "amount": t.amount,
            "level_id": t.level_id,
            "level_name": level.name_ar if level else "عام",
            "is_recurring": t.is_recurring,
            "recurrence_type": getattr(t, 'recurrence_type', 'monthly'),
            "recurrence_label": getattr(t, 'recurrence_label', None)
        })
    return res

@router.post("/fee-templates")
def create_fee_template(template: FeeTemplateCreate, db: Session = Depends(get_db), user: dict = Depends(auth.require_boss)):
    if template.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")
    new_template = models.FeeTemplate(**template.dict())
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    log_audit(db, user['id'], "إنشاء قالب رسوم", "FeeTemplate", new_template.id, None, {"name": new_template.name_ar})
    return new_template

@router.delete("/fee-templates/{id}")
def delete_fee_template(id: int, db: Session = Depends(get_db), user: dict = Depends(auth.require_boss)):
    t = db.query(models.FeeTemplate).filter(models.FeeTemplate.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    t.status = "archived"
    db.commit()
    log_audit(db, user['id'], "أرشفة قالب رسوم", "FeeTemplate", id, None, None)
    return {"message": "Template archived"}


# ----------------- INVOICES -----------------

@router.get("/invoices")
def get_invoices(
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db), 
    user: dict = Depends(require_finance_role)
):
    query = db.query(models.Invoice)
    
    if status:
        query = query.filter(models.Invoice.status == status)
    if from_date:
        query = query.filter(func.date(models.Invoice.created_at) >= from_date)
    if to_date:
        query = query.filter(func.date(models.Invoice.created_at) <= to_date)
        
    invoices = query.order_by(models.Invoice.created_at.desc()).all()
    student_ids = list(set(inv.student_id for inv in invoices))
    class_ids = list(set(inv.class_id for inv in invoices if inv.class_id))
    
    students_map = {s.id: s for s in db.query(models.Student).filter(models.Student.id.in_(student_ids)).all()} if student_ids else {}
    classes_map = {c.id: c for c in db.query(models.Class).filter(models.Class.id.in_(class_ids)).all()} if class_ids else {}
    
    res = []
    for inv in invoices:
        student = students_map.get(inv.student_id)
        cls = classes_map.get(inv.class_id)
        
        res.append({
            "id": inv.id,
            "student_id": inv.student_id,
            "student_name": student.full_name_ar if student else "Unknown",
            "class_name": cls.name_ar if cls else "N/A",
            "title": inv.title,
            "amount": inv.amount,
            "discount": inv.discount,
            "discount_type": inv.discount_type,
            "net_total": inv.net_total,
            "paid_amount": inv.paid_amount,
            "remaining": inv.remaining,
            "due_date": inv.due_date,
            "status": inv.status,
            "created_at": inv.created_at
        })
    return res

@router.post("/invoices")
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db), user: dict = Depends(require_finance_role)):
    if invoice.amount <= 0:
        raise HTTPException(status_code=400, detail="Invoice amount must be greater than zero")
    student = db.query(models.Student).filter(models.Student.id == invoice.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if invoice.class_id:
        cls = db.query(models.Class).filter(models.Class.id == invoice.class_id).first()
        if not cls:
            raise HTTPException(status_code=404, detail="Class not found")
    net_total = invoice.amount
    if invoice.discount > 0:
        if invoice.discount_type == "percent":
            net_total = invoice.amount - (invoice.amount * invoice.discount / 100)
        else:
            net_total = invoice.amount - invoice.discount
    
    new_invoice = models.Invoice(
        student_id=invoice.student_id,
        class_id=invoice.class_id,
        amount=invoice.amount,
        title=invoice.title,
        due_date=invoice.due_date,
        notes=invoice.notes,
        discount=invoice.discount,
        discount_type=invoice.discount_type,
        net_total=max(0.0, net_total)
    )
    db.add(new_invoice)
    db.commit()
    
    if getattr(invoice, 'paid_amount', 0) > 0:
        new_payment = models.Payment(
            student_id=invoice.student_id,
            invoice_id=new_invoice.id,
            amount=invoice.paid_amount,
            method="cash", # Default method, can be enhanced later
            notes="دفعة محصلة فور إنشاء الفاتورة",
            received_by=user['id']
        )
        db.add(new_payment)
        db.commit()
        
    reconcile_financials(new_invoice.student_id, db)
    db.refresh(new_invoice)
    log_audit(db, user['id'], "إصدار فاتورة", "Invoice", new_invoice.id, None, {"amount": new_invoice.net_total})
    return new_invoice

@router.post("/invoices/bulk")
def generate_bulk_invoices(data: BulkInvoiceCreate, db: Session = Depends(get_db), user: dict = Depends(require_finance_role)):
    template = db.query(models.FeeTemplate).filter(models.FeeTemplate.id == data.fee_template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
        
    enrollments = db.query(models.ClassEnrollment).filter(models.ClassEnrollment.class_id == data.class_id, models.ClassEnrollment.status == 'active').all()
    student_ids = [e.student_id for e in enrollments]
    if not student_ids:
        return {"created": 0, "skipped": 0, "message": "لا يوجد طلاب في هذا الفصل"}
        
    period_label = data.month_label or getattr(template, 'recurrence_label', None)
    title = f"{template.name_ar} - {period_label}" if period_label else template.name_ar
    
    # Check existing invoices
    existing = db.query(models.Invoice.student_id).filter(
        models.Invoice.student_id.in_(student_ids),
        models.Invoice.title == title
    ).all()
    existing_sids = {e.student_id for e in existing}
    
    created = 0
    skipped = 0
    for sid in student_ids:
        if sid in existing_sids:
            skipped += 1
            continue
            
        inv = models.Invoice(
            student_id=sid,
            class_id=data.class_id,
            amount=template.amount,
            net_total=template.amount,
            title=title,
            notes=f"تم التوليد تلقائياً من قالب: {template.name_ar}"
        )
        db.add(inv)
        created += 1
        
    db.commit()
    for sid in student_ids:
        if sid not in existing_sids:
            reconcile_financials(sid, db)
            
    log_audit(db, user['id'], "توليد فواتير جماعية", "Invoice", None, None, {"count": created})
    return {"created": created, "skipped": skipped, "message": f"تم توليد {created} فاتورة بنجاح"}

@router.delete("/invoices/{id}")
def delete_invoice(id: int, db: Session = Depends(get_db), user: dict = Depends(auth.require_boss)):
    inv = db.query(models.Invoice).filter(models.Invoice.id == id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    if inv.paid_amount > 0:
        raise HTTPException(status_code=400, detail="لا يمكن حذف فاتورة مدفوعة أو مدفوعة جزئياً. قم بحذف الدفعات أولاً.")
        
    student_id = inv.student_id
    db.query(models.Payment).filter(models.Payment.invoice_id == id).update({"invoice_id": None})
    db.delete(inv)
    db.commit()
    reconcile_financials(student_id, db)
    log_audit(db, user['id'], "حذف فاتورة", "Invoice", id, None, None)
    return {"message": "تم حذف الفاتورة بنجاح"}

# ----------------- PAYMENTS -----------------

@router.post("/payments")
def record_payment(payment: PaymentCreate, db: Session = Depends(get_db), user: dict = Depends(require_finance_role)):
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be greater than zero")
        
    student_id = payment.student_id
    if payment.invoice_id:
        invoice = db.query(models.Invoice).filter(models.Invoice.id == payment.invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        if payment.amount > (invoice.remaining or invoice.amount):
            raise HTTPException(status_code=400, detail="Payment cannot exceed invoice remaining balance")
        student_id = invoice.student_id
        
    if not student_id:
        raise HTTPException(status_code=400, detail="Either student_id or invoice_id must be provided")

    new_payment = models.Payment(
        student_id=student_id,
        invoice_id=payment.invoice_id,
        amount=payment.amount,
        method=payment.method,
        receipt_no=payment.receipt_no,
        notes=payment.notes,
        received_by=user["id"]
    )
    db.add(new_payment)
    db.flush() # flush to get ID
    
    # Generate Receipt Certificate
    cert = models.Certificate(
        type="payment_receipt",
        certificate_id=f"RCPT-{student_id}-{new_payment.id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}",
        issued_by=user["id"],
        student_id=student_id,
        payment_id=new_payment.id,
        template_key="payment_receipt"
    )
    db.add(cert)
    
    db.commit()
    
    # Run reconciliation
    reconcile_financials(student_id, db)
    log_audit(db, user['id'], "تسجيل دفعة", "Payment", new_payment.id, None, {"amount": new_payment.amount})
    return {"message": "Payment recorded", "payment_id": new_payment.id, "certificate_id": cert.certificate_id}

# ----------------- SALARIES -----------------

@router.get("/salaries")
def get_salaries(month: Optional[str] = None, db: Session = Depends(get_db), user: dict = Depends(require_finance_role)):
    query = db.query(models.Salary)
    if month:
        query = query.filter(models.Salary.month == month)
    salaries = query.order_by(models.Salary.id.desc()).all()
    
    user_ids = list(set(s.user_id for s in salaries))
    staff_map = {u.id: u for u in db.query(models.User).filter(models.User.id.in_(user_ids)).all()} if user_ids else {}
    
    res = []
    for s in salaries:
        staff = staff_map.get(s.user_id)
        res.append({
            "id": s.id,
            "user_id": s.user_id,
            "staff_name": staff.full_name_ar if staff else "Unknown",
            "role": staff.role if staff else "",
            "month": s.month,
            "base_salary": s.base_salary,
            "bonuses": s.bonuses,
            "deductions": s.deductions,
            "days_deducted": s.days_deducted,
            "net_salary": s.net_salary,
            "status": s.status,
            "paid_at": s.paid_at
        })
    return res

@router.post("/salaries/bulk")
def generate_bulk_salaries(data: BulkSalaryCreate, db: Session = Depends(get_db), user: dict = Depends(require_finance_role)):
    staff_members = db.query(models.User).filter(
        models.User.status == "active",
        models.User.base_salary > 0
    ).all()
    
    if not staff_members:
        return {"created": 0, "skipped": 0, "message": "لا يوجد موظفين براتب أساسي محدد"}
        
    existing = db.query(models.Salary.user_id).filter(models.Salary.month == data.month).all()
    existing_uids = {e.user_id for e in existing}
    
    created = 0
    skipped = 0
    for staff in staff_members:
        if staff.id in existing_uids:
            skipped += 1
            continue
            
        new_salary = models.Salary(
            user_id=staff.id,
            month=data.month,
            base_salary=staff.base_salary,
            bonuses=0.0,
            deductions=0.0,
            days_deducted=0,
            net_salary=staff.base_salary,
            recorded_by=user["id"]
        )
        db.add(new_salary)
        created += 1
        
    db.commit()
    log_audit(db, user['id'], "توليد مسيرات رواتب جماعية", "Salary", None, None, {"count": created})
    return {"created": created, "skipped": skipped, "message": f"تم توليد {created} مسودة راتب بنجاح"}

@router.post("/salaries")
def create_salary(salary: SalaryCreate, db: Session = Depends(get_db), user: dict = Depends(require_finance_role)):
    if salary.base_salary < 0 or salary.bonuses < 0 or salary.deductions < 0:
        raise HTTPException(status_code=400, detail="Salary values cannot be negative")
    staff = db.query(models.User).filter(models.User.id == salary.user_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff user not found")
    net = salary.base_salary + salary.bonuses - salary.deductions
    new_salary = models.Salary(
        user_id=salary.user_id,
        month=salary.month,
        base_salary=salary.base_salary,
        bonuses=salary.bonuses,
        deductions=salary.deductions,
        days_deducted=salary.days_deducted,
        net_salary=net,
        recorded_by=user["id"]
    )
    db.add(new_salary)
    db.commit()
    db.refresh(new_salary)
    log_audit(db, user['id'], "إنشاء سجل راتب", "Salary", new_salary.id, None, {"user_id": new_salary.user_id})
    return new_salary

@router.post("/salaries/{id}/pay")
def pay_salary(id: int, db: Session = Depends(get_db), user: dict = Depends(require_finance_role)):
    salary = db.query(models.Salary).filter(models.Salary.id == id).first()
    if not salary:
        raise HTTPException(status_code=404, detail="Salary record not found")
    salary.status = "paid"
    salary.paid_at = datetime.utcnow()
    db.commit()
    log_audit(db, user['id'], "صرف راتب", "Salary", id, {"status": "draft"}, {"status": "paid"})
    return {"message": "Salary marked as paid"}

# ----------------- EXPENSES -----------------

@router.get("/expenses")
def get_expenses(db: Session = Depends(get_db), user: dict = Depends(require_finance_role)):
    expenses = db.query(models.Expense).order_by(models.Expense.date.desc()).all()
    
    recorded_by_ids = list(set(e.recorded_by for e in expenses))
    staff_map = {u.id: u for u in db.query(models.User).filter(models.User.id.in_(recorded_by_ids)).all()} if recorded_by_ids else {}
    
    res = []
    for e in expenses:
        staff = staff_map.get(e.recorded_by)
        res.append({
            "id": e.id,
            "category": e.category,
            "amount": e.amount,
            "description": e.description,
            "date": e.date,
            "recorded_by_name": staff.full_name_ar if staff else "System"
        })
    return res

@router.post("/expenses")
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db), user: dict = Depends(require_finance_role)):
    if expense.amount <= 0:
        raise HTTPException(status_code=400, detail="Expense amount must be greater than zero")
    new_exp = models.Expense(
        category=expense.category,
        amount=expense.amount,
        description=expense.description,
        date=expense.date,
        recorded_by=user["id"]
    )
    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)
    log_audit(db, user['id'], "تسجيل مصروف", "Expense", new_exp.id, None, {"amount": new_exp.amount, "category": new_exp.category})
    return new_exp

# ----------------- REPORTS -----------------

@router.get("/reports")
def get_financial_reports(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db), 
    user: dict = Depends(require_finance_role)
):
    payment_query = db.query(func.sum(models.Payment.amount))
    if from_date: payment_query = payment_query.filter(func.date(models.Payment.paid_at) >= from_date)
    if to_date: payment_query = payment_query.filter(func.date(models.Payment.paid_at) <= to_date)
    total_income = payment_query.scalar() or 0.0
    
    invoice_query = db.query(models.Invoice).filter(models.Invoice.status != "paid")
    if from_date: invoice_query = invoice_query.filter(func.date(models.Invoice.created_at) >= from_date)
    if to_date: invoice_query = invoice_query.filter(func.date(models.Invoice.created_at) <= to_date)
    
    outstanding = 0.0
    for inv in invoice_query.all():
        outstanding += inv.remaining
        
    salary_query = db.query(func.sum(models.Salary.net_salary)).filter(models.Salary.status == "paid")
    if from_date: salary_query = salary_query.filter(func.date(models.Salary.paid_at) >= from_date)
    if to_date: salary_query = salary_query.filter(func.date(models.Salary.paid_at) <= to_date)
    salaries_paid = salary_query.scalar() or 0.0
    
    expense_query = db.query(func.sum(models.Expense.amount))
    if from_date: expense_query = expense_query.filter(func.date(models.Expense.date) >= from_date)
    if to_date: expense_query = expense_query.filter(func.date(models.Expense.date) <= to_date)
    total_expenses = expense_query.scalar() or 0.0
    
    net_profit = total_income - salaries_paid - total_expenses
    
    return {
        "total_income": total_income,
        "total_outstanding": outstanding,
        "salaries_paid": salaries_paid,
        "total_expenses": total_expenses,
        "net_profit": net_profit
    }

@router.get("/student/{student_id}")
def get_student_finance_history(student_id: int, db: Session = Depends(get_db)):
    invoices = db.query(models.Invoice).filter(models.Invoice.student_id == student_id).order_by(models.Invoice.created_at.desc()).all()
    payments = db.query(models.Payment).filter(models.Payment.student_id == student_id).order_by(models.Payment.paid_at.desc()).all()
    
    inv_list = []
    for inv in invoices:
        inv_list.append({
            "id": inv.id,
            "title": inv.title,
            "amount": inv.amount,
            "paid_amount": inv.paid_amount,
            "remaining": inv.remaining,
            "due_date": str(inv.due_date) if inv.due_date else None,
            "status": inv.status,
            "created_at": str(inv.created_at)
        })
        
    pay_list = []
    for pay in payments:
        pay_list.append({
            "id": pay.id,
            "amount": pay.amount,
            "method": pay.method,
            "receipt_no": pay.receipt_no,
            "paid_at": str(pay.paid_at),
            "invoice_id": pay.invoice_id
        })
        
    return {
        "invoices": inv_list,
        "payments": pay_list
    }

@router.post("/auto-generate-invoices")
def auto_generate_invoices(db: Session = Depends(get_db), user: dict = Depends(require_finance_role)):
    # Get active templates that are recurring monthly
    templates = db.query(models.FeeTemplate).filter(
        models.FeeTemplate.status == "active",
        models.FeeTemplate.is_recurring == True,
        models.FeeTemplate.recurrence_type == "monthly"
    ).all()
    
    if not templates:
        return {"created": 0, "message": "No active recurring templates found."}
        
    # Get all active enrollments
    enrollments = db.query(models.ClassEnrollment).filter(models.ClassEnrollment.status == 'active').all()
    
    # We will need the students' enrollment dates (from Student table)
    student_ids = list(set(e.student_id for e in enrollments))
    students = db.query(models.Student).filter(models.Student.id.in_(student_ids)).all()
    student_map = {s.id: s for s in students}
    
    import datetime
    from dateutil.relativedelta import relativedelta
    today = datetime.date.today()
    
    arabic_months = ['', 'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
    
    created_count = 0
    affected_students = set()
    
    # Batch create list
    invoices_to_create = []
    
    # Check all existing invoices for these templates to avoid duplicates
    existing_invoices = db.query(models.Invoice.student_id, models.Invoice.title).filter(
        models.Invoice.student_id.in_(student_ids)
    ).all()
    existing_set = set((inv.student_id, inv.title) for inv in existing_invoices)
    
    for template in templates:
        template_date = template.created_at.date() if template.created_at else today
        
        for e in enrollments:
            student = student_map.get(e.student_id)
            if not student:
                continue
                
            # If template has a specific level, check if class level matches
            if template.level_id:
                cls = db.query(models.Class).filter(models.Class.id == e.class_id).first()
                if not cls or cls.level_id != template.level_id:
                    continue
            
            # Start date: max(student enrollment date, template creation date)
            start_date = student.enrollment_date if student.enrollment_date else template_date
            start_date = max(start_date, template_date)
            
            # Start from the 1st of the month
            current = datetime.date(start_date.year, start_date.month, 1)
            end = datetime.date(today.year, today.month, 1)
            
            while current <= end:
                month_label = f"{arabic_months[current.month]} {current.year}"
                title = f"{template.name_ar} - {month_label}"
                
                # Check if this invoice already exists
                if (student.id, title) not in existing_set:
                    inv = models.Invoice(
                        student_id=student.id,
                        class_id=e.class_id,
                        amount=template.amount,
                        net_total=template.amount,
                        title=title,
                        notes=f"تم التوليد تلقائياً من قالب: {template.name_ar}"
                    )
                    db.add(inv) # Add immediately so it gets an ID or wait until commit
                    existing_set.add((student.id, title))
                    affected_students.add(student.id)
                    created_count += 1
                
                current += relativedelta(months=1)
                
    if created_count > 0:
        db.commit()
        for sid in affected_students:
            reconcile_financials(sid, db)
            
    return {"created": created_count, "message": f"تم توليد {created_count} فاتورة جديدة بنجاح"}

@router.get("/summary")
def get_finance_summary(db: Session = Depends(get_db), user: dict = Depends(require_finance_role)):
    # Total billed (all invoices net_total)
    total_billed = db.query(func.sum(models.Invoice.net_total)).scalar() or 0.0
    
    # Total collected (all payments amount)
    total_collected = db.query(func.sum(models.Payment.amount)).scalar() or 0.0
    
    # Total outstanding (all unpaid/partial invoices remaining)
    total_outstanding = db.query(func.sum(models.Invoice.remaining)).filter(models.Invoice.status != "paid").scalar() or 0.0
    
    # Overdue invoices count (status != paid and due_date < today)
    import datetime
    today = datetime.date.today()
    overdue_count = db.query(models.Invoice).filter(
        models.Invoice.status != "paid",
        models.Invoice.due_date < today
    ).count()
    
    return {
        "total_billed": total_billed,
        "total_collected": total_collected,
        "total_outstanding": total_outstanding,
        "overdue_count": overdue_count
    }

@router.get("/debts")
def get_debts(db: Session = Depends(get_db), user: dict = Depends(require_finance_role)):
    debts = db.query(models.Invoice).filter(models.Invoice.status != "paid").order_by(models.Invoice.created_at.desc()).all()
    
    student_ids = list(set(inv.student_id for inv in debts))
    invoice_ids = [inv.id for inv in debts]
    
    students_map = {s.id: s for s in db.query(models.Student).filter(models.Student.id.in_(student_ids)).all()} if student_ids else {}
    
    all_payments = db.query(models.Payment).filter(models.Payment.invoice_id.in_(invoice_ids)).order_by(models.Payment.paid_at.desc()).all() if invoice_ids else []
    payments_by_invoice = {}
    for p in all_payments:
        if p.invoice_id not in payments_by_invoice:
            payments_by_invoice[p.invoice_id] = []
        payments_by_invoice[p.invoice_id].append(p)
    
    res = []
    for inv in debts:
        student = students_map.get(inv.student_id)
        payments = payments_by_invoice.get(inv.id, [])
        
        pay_history = [{
            "id": p.id,
            "amount": p.amount,
            "date": p.paid_at,
            "method": p.method
        } for p in payments]
        
        res.append({
            "id": inv.id,
            "student_id": student.id if student else None,
            "student_name": student.full_name_ar if student else "Unknown",
            "student_phone": student.contact_phone if student and student.contact_phone else (student.father_phone if student and student.father_phone else ""),
            "title": inv.title,
            "net_total": inv.net_total,
            "paid_amount": inv.paid_amount,
            "remaining": inv.remaining,
            "due_date": inv.due_date,
            "status": inv.status,
            "payment_history": pay_history
        })
    return res

class DebtPaymentCreate(BaseModel):
    amount: float
    method: str = 'cash'
    receipt_no: Optional[str] = None
    notes: Optional[str] = None

@router.post("/debts/{invoice_id}/pay")
def pay_debt(invoice_id: int, payment: DebtPaymentCreate, db: Session = Depends(get_db), user: dict = Depends(require_finance_role)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be > 0")
        
    if payment.amount > invoice.remaining:
        raise HTTPException(status_code=400, detail="المبلغ المدخل أكبر من المتبقي")
        
    new_payment = models.Payment(
        student_id=invoice.student_id,
        invoice_id=invoice_id,
        amount=payment.amount,
        method=payment.method,
        receipt_no=payment.receipt_no,
        notes=payment.notes
    )
    db.add(new_payment)
    db.commit()
    
    reconcile_financials(invoice.student_id, db)
    log_audit(db, user['id'], "تسجيل دفعة دين", "Payment", new_payment.id, None, {"amount": new_payment.amount})
    return {"message": "تم تسجيل الدفعة بنجاح"}
