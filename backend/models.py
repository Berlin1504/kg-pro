from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Date, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name_ar = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    role = Column(String, nullable=False) # 'boss', 'supervisor', 'moneyman', 'teacher'
    status = Column(String, default='active')
    password_hash = Column(String, nullable=False)
    base_salary = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Setting(Base):
    __tablename__ = "settings"
    
    key = Column(String, primary_key=True, index=True)
    value_text = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    before_text = Column(JSON, nullable=True)
    after_text = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name_ar = Column(String, nullable=False)
    description = Column(String, nullable=True)
    default_passing_grade = Column(Integer, default=50)
    promotion_threshold = Column(Integer, default=75)
    status = Column(String, default='active')

class Level(Base):
    __tablename__ = "levels"
    id = Column(Integer, primary_key=True, index=True)
    name_ar = Column(String, nullable=False)
    code = Column(String, nullable=False)
    description = Column(String, nullable=True)
    order_index = Column(Integer, default=0)
    default_passing_grade = Column(Integer, default=50)
    default_promotion_rule = Column(String, nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    next_level_id = Column(Integer, ForeignKey("levels.id"), nullable=True)
    status = Column(String, default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())



class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name_ar = Column(String, nullable=False)
    code = Column(String, nullable=True)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
    group_label = Column(String, nullable=True)
    status = Column(String, default='active')
    capacity = Column(Integer, default=20)
    term_start = Column(Date, nullable=True)
    term_end = Column(Date, nullable=True)
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ClassTeacher(Base):
    __tablename__ = "class_teachers"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    full_name_ar = Column(String, nullable=False)
    dob = Column(Date, nullable=True)
    contact_phone = Column(String, nullable=True)
    father_phone = Column(String, nullable=True)
    mother_phone = Column(String, nullable=True)
    guardian_name = Column(String, nullable=True)
    guardian_phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    enrollment_date = Column(Date, nullable=True)
    starting_level_id = Column(Integer, ForeignKey("levels.id"), nullable=True)
    current_level_id = Column(Integer, ForeignKey("levels.id"), nullable=True)
    status = Column(String, default='active')
    background_notes = Column(String, nullable=True)
    total_billed = Column(Float, default=0.0)
    total_paid = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ClassEnrollment(Base):
    __tablename__ = "class_enrollments"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default='active', index=True)
    starting_level_id = Column(Integer, ForeignKey("levels.id"), nullable=True)

class StudentSubjectLevel(Base):
    __tablename__ = "student_subject_levels"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    current_level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
class ClassSchedule(Base):
    __tablename__ = "class_schedules"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    day_of_week = Column(Integer, nullable=False) # 0=Sunday, 1=Monday, ..., 6=Saturday
    start_time = Column(String, nullable=False) # format "HH:MM"
    end_time = Column(String, nullable=False) # format "HH:MM"

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, index=True)
    schedule_id = Column(Integer, ForeignKey("class_schedules.id"), nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    date = Column(Date, nullable=False, index=True)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    status = Column(String, default='scheduled') # scheduled, completed, cancelled

class StudentAttendance(Base):
    __tablename__ = "student_attendance"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    status = Column(String, nullable=False, index=True) # present, absent, late, excused
    notes = Column(String, nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

class Exam(Base):
    __tablename__ = "exams"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    class_id = Column(Integer, ForeignKey('classes.id'))
    date = Column(Date)
    total_points = Column(Integer, default=100)
    passing_grade = Column(Integer, default=50)
    is_certification = Column(Boolean, default=False)
    status = Column(String, default='scheduled') # scheduled, grading, published
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ExamScore(Base):
    __tablename__ = "exam_scores"
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey('exams.id'), index=True)
    student_id = Column(Integer, ForeignKey('students.id'), index=True)
    score = Column(Float)
    passed = Column(Boolean)
    notes = Column(Text, nullable=True)



class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    target_type = Column(String, nullable=False, index=True) # 'student' or 'staff'
    target_id = Column(Integer, nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=True)
    severity = Column(String, default="low") # low, medium, high
    visibility = Column(String, default="private") # private, assigned_staff, all_staff
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class LevelHistory(Base):
    __tablename__ = "level_history"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True, index=True)
    from_level_id = Column(Integer, ForeignKey("levels.id"), nullable=True)
    to_level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
    reason = Column(String, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    exam_ref = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Certificate(Base):
    __tablename__ = "certificates"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False) # level_start, level_completion, payment_receipt
    certificate_id = Column(String, unique=True, index=True, nullable=False)
    issued_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True, index=True)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    template_key = Column(String, nullable=False)
    status = Column(String, default="issued") # issued, revoked
    issued_at = Column(DateTime(timezone=True), server_default=func.now())

class FeeTemplate(Base):
    __tablename__ = "fee_templates"
    id = Column(Integer, primary_key=True, index=True)
    name_ar = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=True)
    is_recurring = Column(Boolean, default=True)
    recurrence_type = Column(String, default="monthly") # monthly, weekly, per_term, one_time, custom
    recurrence_label = Column(String, nullable=True) # e.g. "يوليو 2026"
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    amount = Column(Float, nullable=False)
    title = Column(String, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String, default="unpaid", index=True) # unpaid, partial, paid
    notes = Column(Text, nullable=True)
    discount = Column(Float, default=0.0)
    discount_type = Column(String, default="fixed") # fixed, percent
    net_total = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0)
    remaining = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    method = Column(String, nullable=False) # cash, bank, card
    receipt_no = Column(String, nullable=True)
    received_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)
    paid_at = Column(DateTime(timezone=True), server_default=func.now())

class Salary(Base):
    __tablename__ = "salaries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month = Column(String, nullable=False) # "YYYY-MM"
    base_salary = Column(Float, nullable=False)
    bonuses = Column(Float, default=0.0)
    deductions = Column(Float, default=0.0)
    days_deducted = Column(Integer, default=0)
    net_salary = Column(Float, nullable=False)
    status = Column(String, default="draft") # draft, paid
    paid_at = Column(DateTime(timezone=True), nullable=True)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=False)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    date = Column(Date, nullable=False)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
