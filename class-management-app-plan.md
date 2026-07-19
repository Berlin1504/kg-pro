# Class Management App — Final Plan (v6)

> **Scope:** Complete product + technical plan for a multi-role class management application. **No code, no images, no PDFs, no student logins, no parent portals** — staff-only system, Arabic-only RTL UI, text-only architecture, designed to host on a tiny VPS. Three fixed certificate templates (level start, level completion, payment receipt) rendered as styled HTML/CSS from live data. **Level Promotion Engine restored for students**, with approval workflow, level history, and "stuck students" classification.
>
> **Changelog:**
> - v1 → v2: text-only, Notes, Staff Absence, Class Lifecycle.
> - v2 → v3: students are records; Arabic-only RTL; score-only exams; Levels as templates; Boss-centric setup.
> - v3 → v4: removed parent view-link; expanded Certificates to 3 types; all certificates are styled HTML/CSS templates.
> - v4 → v5: **removed the Level Promotion Engine** (misread as a staff feature); Class Profile reduced to 3 questions (no "stuck").
> - v5 → v6 (final): **restored the Level Promotion Engine for students** (propose → approve → level up); **restored Level History**; **restored "stuck students"** in Class Profile (4 questions again); 3 fixed certificate templates confirmed.

---

## 1. Product Vision

A **staff-only**, Arabic-language, text-based web app for an educational institution to run its **classes, students, staff, certificates, and money** under one roof. The Boss is the architect — they set up Levels first, then start Classes from those Levels, assign staff, enroll students, and the system runs from there.

The system must answer four questions on demand, per class:
1. Who is **leading**?
2. Who is **weak** (and why)?
3. Who is **most absent**?
4. Who is **stuck** at their current level (hasn't been promoted in N months AND grade is low)?

Plus a fifth for the Boss: **Who of my staff is absent today, and how often?**

**Core design rules (locked, final):**
- **No student login. No parent portal.** Students are records. Parents call, staff global-searches, opens the profile, reads the data aloud, prints certificates on demand.
- **Arabic only, RTL.** No language switcher. Strings authored in Arabic. A future `en.json` can be added without refactor.
- **Text only, no images, no PDFs.** Avatars = CSS initials. Certificates = styled HTML/CSS templates. Reports = CSV. QR codes = inline SVG.
- **Exams are just scores.** Teacher records a score per student. That's it.
- **Levels are the foundation.** Boss creates Levels; Classes are concrete instances of those Levels.
- **Level Promotion Engine (for students).** A student starts at a `starting_level` and has a `current_level`. They move up via a propose → approve flow, triggered by passing the certification exam for their current level. Every level change is recorded in `LevelHistory`.
- **3 fixed certificate templates** (level start, level completion, payment receipt) — Boss does not edit templates in v1.
- **Boss is the architect.** Every setup step flows from the Boss.

**Why text-only matters:**
- A 1,000-student institution, 5 years of data, fits in **< 50 MB** of database.
- Hostable on a **$5–$10/month VPS**, backup included.
- No S3, no CDN, no image processing, no PDF library, no file storage.
- Pages load fast on 3G.

---

## 2. Roles & Permission Matrix

There are **four roles**. The Boss is the root.

| Capability | Boss | Supervisor | Money Man | Teacher |
|---|:---:|:---:|:---:|:---:|
| Set up Levels (create/edit/deactivate) | ✅ | ❌ | ❌ | ❌ |
| Create/edit/deactivate Subjects | ✅ | ❌ | ❌ | ❌ |
| Set up Classes from Levels (create/edit/archive) | ✅ | ❌ | ❌ | ❌ |
| Build weekly time table for a class | ✅ | ✅ (assigned classes) | ❌ | ❌ |
| Assign teacher to a class/subject | ✅ | ❌ | ❌ | ❌ |
| Assign supervisor to a class | ✅ | ❌ | ❌ | ❌ |
| Enroll/unenroll students in classes | ✅ | ✅ (assigned classes) | ❌ | ❌ |
| Manage staff users (add/edit/deactivate) | ✅ | ❌ | ❌ | ❌ |
| Grant/revoke individual capabilities to staff | ✅ | ❌ | ❌ | ❌ |
| View all classes' data | ✅ | ✅ (assigned only) | ✅ (financial only) | ✅ (assigned only) |
| Start / grade / publish exams | ✅ | ✅ (oversight) | ❌ | ✅ (own classes) |
| Mark student attendance | ✅ | ✅ | ❌ | ✅ |
| Self check-in (daily presence) | ✅ | ✅ | ✅ | ✅ |
| **View staff absence report** | ✅ | ❌ | ❌ | ❌ |
| **Write notes on a student** | ✅ | ✅ (assigned) | ❌ | ✅ (own students) |
| **Write notes on a staff member** | ✅ | ✅ (assigned) | ✅ (assigned) | ❌ |
| **View notes on a student** | ✅ | ✅ (assigned) | ❌ | ✅ (own) |
| **Propose a student's level-up** | ✅ | ✅ | ❌ | ✅ (own students) |
| **Approve a student's level-up / certification** | ✅ | ✅ (configurable per Level) | ❌ | ❌ |
| **Override a student's level assignment** | ✅ | ❌ | ❌ | ❌ |
| Issue / view **level-start certificate** | ✅ | ✅ (assigned) | ❌ | ✅ (own) |
| Issue / view **level-completion certificate** | ✅ | ✅ (assigned) | ❌ | ✅ (own) |
| Issue / view **payment receipt** | ✅ | ❌ | ✅ | ❌ |
| Manage tuition & payments | ✅ | ❌ | ✅ | ❌ |
| Manage salaries & payroll | ✅ | ❌ | ✅ | ❌ |
| Manage expenses | ✅ | ❌ | ✅ | ❌ |
| Financial reports | ✅ | ❌ | ✅ | ❌ |
| View class profile (lead / weak / absent / stuck) | ✅ | ✅ (assigned) | ❌ | ✅ (own classes) |
| View audit log | ✅ | ❌ | ❌ | ❌ |
| Configure note categories & severity rules | ✅ | ❌ | ❌ | ❌ |
| Configure promotion rules, approval chain, "stuck" thresholds | ✅ | ❌ | ❌ | ❌ |

**Notes on permissions:**
- The Promotion Engine is **student-only** (no staff promotion, no salary-grade progression, no seniority). It's a single engine that handles student level-ups.
- A promotion **proposal** can be created by Teacher, Supervisor, or Boss; the **approver** is configurable per Level (Boss, or Supervisor if Boss allows).
- "Override a student's level assignment" is the Boss's safety valve — for cases where the normal flow doesn't apply (e.g., transfer from another school).
- **Notes** have a separate per-note visibility rule (see §6).
- **Certificates**: issuing is role-gated (per row above); **viewing** any issued certificate is allowed for the issuer and the Boss.

---

## 3. Levels & Classes — The Heart of the System

The Boss is the architect. They set up the academic structure in this order:
1. **Levels** (the abstract curriculum stages — e.g., "Level 1", "Level 2", "A1", "B2")
2. **Subjects** (the teachable units)
3. **Classes** (concrete instances of a Level, with a roster, a time table, a term)
4. **Roster & Time Table** (assign students to classes; build the weekly schedule)
5. **Staff Assignments** (assign teacher per subject, supervisor per class)

### 3.1 Level (the abstract unit)
- `name_ar` — e.g., "المستوى الأول"
- `code` — short identifier, e.g., "L1"
- `description` — free text
- `order_index` — numeric, for sorting and determining the "next level" for promotion
- `default_subjects[]` — default curriculum
- `default_passing_grade` — % required to pass an exam
- `default_promotion_rule` — text: "pass certification exam" / "average ≥ X%" / "manual decision"
- `next_level_id` — optional explicit pointer to the Level students get promoted to (defaults to the next `order_index` Level)
- `status` — active / inactive

### 3.2 Class (a concrete instance of a Level)
```
Class
├── Identity:        name (auto: "<Level name> - <Group>"), manual code
├── Level:           reference to one Level
├── Group:           group label (أ, ب, ج, ...)
├── Status:          Draft | Active | On Hold | Completed | Archived
├── Term:            start date, expected end date
├── Capacity:        max students
├── Supervisor:      1 assigned supervisor
├── Subjects:        1..N subjects (inherited from Level, customizable)
│   └── Each subject has 1 primary teacher (+ optional backup teacher)
├── Roster:          0..N enrolled students (each with a starting_level)
└── Weekly Timetable:0..N session slots per week
```

Key rules:
- **One class = one Level.** A class belongs to exactly one Level.
- **A class has one weekly timetable** (its recurring week schedule).
- **A class can have multiple subjects** (inherited from its Level, Boss can override).
- **One teacher can teach multiple subjects**, in one or more classes.
- **A Level can have many Classes** (e.g., "Level 1" → "Level 1 - Group A", "Level 1 - Group B").

### 3.3 Class Lifecycle
```
   [Draft] ──start──▶ [Active] ──pause──▶ [On Hold]
      │                  │                     │
      │                  │                     └──resume──▶ [Active]
      │                  │
      │                  ├──complete──▶ [Completed] ──archive──▶ [Archived]
      │                  │
      │                  └──cancel──▶ [Archived]
```

State changes are logged in the audit log with a reason.

### 3.4 Weekly Timetable (per class)
- One class = one weekly timetable.
- A **session slot** = (day, start, end, subject, teacher, room).
- The system auto-generates concrete session instances for the current week (and rolling N weeks ahead).
- Conflict checks: teacher can't be in two slots, room can't host two classes, students can't have overlapping slots.
- Views: class view, teacher view, room view.

### 3.5 Term-to-Term Continuity
- A new term → Boss creates a **new Class** from the same Level.
- The previous Class is `Completed` → `Archived`.
- Students who have been promoted (in `LevelHistory`) can be enrolled in a new Class at their new (higher) Level.

---

## 4. Core Modules

### 4.1 Auth & Identity (staff only)
- Email + password login, password reset via email token.
- 2FA for Boss (TOTP).
- Session timeout.
- Role-based routing.
- Avatar = Arabic initials in a colored CSS circle.

### 4.2 User Management (Boss only)
- Add/edit/deactivate staff (Supervisors, Money Man, Teachers).
- Bulk import (CSV/TSV, Arabic headers).
- Search + filter on every list page.

### 4.3 Level Management (Boss only)
- CRUD on Levels, ordering, default curriculum, default promotion rule, `next_level_id` mapping.

### 4.4 Subject Management (Boss only)
- CRUD for subjects: name (Arabic), description, passing grade.
- Reusable across Levels and Classes.

### 4.5 Class Management
- Boss creates a Class by picking a Level + Group + term + capacity + supervisor.
- Subjects inherited from the Level; Boss can override per Class.
- Assign a primary teacher (+ optional backup) per subject.
- Manage roster: enroll, unenroll, transfer.

### 4.6 Weekly Timetable
- Visual week grid per class.
- Drag-to-create session slots (or form-based).
- Conflict warnings on save.
- Editable only by Boss or the assigned Supervisor.

### 4.7 Session Management
- A **session** is a concrete instance of a time-table slot on a specific date.
- Auto-generated; status: `Scheduled → In Progress → Locked → Cancelled`.
- Locks at the end time; corrections require an audit-logged reason.

### 4.8 Student Records
- A **student is a record**, not a user. No login, no portal, no app.
- Boss or Supervisor creates the student record: full name (Arabic), DOB, contact phone, guardian name + phone, address, enrollment date, **starting_level** (set at creation), free-text background notes.
- A student is enrolled in **one or more Classes** (usually one).
- A student is **never visible to themselves**; staff view their record in-app.
- **When a parent calls**, staff searches the student (by name, by phone, by guardian phone), opens the profile, and reads out the data. Nothing is sent to the parent. This is the entire parent-interaction model.

### 4.9 Level Promotion Engine (restored)

The engine that moves students up through Levels. **Student-only** — does not apply to staff.

**Triggers:**
- The primary trigger is **passing a certification exam for the student's current Level**.
- Alternatively, the Boss can manually create a promotion (via "Override a student's level assignment") for edge cases (transfer from another school, special exemption, etc.).

**Flow:**
1. Teacher runs a certification exam for a Class (or for a specific student).
2. Teacher enters scores → publishes the exam.
3. The system flags each `passed = true` score on a certification exam as **eligible for promotion**.
4. For each eligible student, a **promotion proposal** is auto-created with: student, from level, to level (resolved via `next_level_id` of the current level), exam reference, score, timestamp.
5. The proposer is the Teacher who published the exam. The Teacher can also manually create a proposal for a student who has met the criteria even if no exam is tied (e.g., Boss's manual decision with a text reason).
6. The proposal goes to the **approver** for the target Level (configured in Settings — usually Boss, optionally Supervisor for trusted classes).
7. Approver reviews and either:
   - **Approves** → system:
     - Writes a `LevelHistory` row (from → to, reason, exam ref, changed_by, changed_at).
     - Updates `Student.current_level_id`.
     - Issues a **level-completion certificate** (template: `level_completion`).
     - Notifies assigned staff in-app.
     - Updates the student's "developmental timeline" entry.
   - **Rejects** → logs the rejection with a required text reason, notifies the proposer, student stays at current level.
8. After approval, the student is eligible to be enrolled in a new Class at the new Level (the Boss or Supervisor does the enrollment manually — it is not automatic).

**Approval chain config (Boss sets in Settings):**
- Per Level: `approver_role` = `boss` (default) or `supervisor` (Boss can delegate).
- Per Level: `auto_approve_on_cert_pass` = `true | false` (default: false — always require human approval).
- Per Level: `min_cert_passes_to_promote` = `1` (default; can be raised for stricter levels).

**Edge cases:**
- Student has no `next_level_id` for their current level → promotion is not auto-suggested; manual proposal only.
- Student is already at the highest level → promotion engine returns "no next level".
- Student fails a certification exam → no proposal is created. They can retake.
- Student passes but approver rejects (e.g., missing coursework) → no promotion; teacher can re-propose after addressing the issue.

**Audit:**
- Every proposal, approval, and rejection is logged in the audit log with full text of the reason.

### 4.10 Exams & Grading (score-only)
- Teacher **starts an exam**: title, subject, date, type, total points, passing grade, **certification flag**.
- Status: `Scheduled → In Progress → Grading → Published → Archived`.
- Teacher enters scores (one per student). System auto-calculates grade and pass/fail.
- **No per-question scoring, no per-student feedback text, no duration tracking required.**
- On publish, results become visible to the assigned staff and to the student record.
- A **Certification exam** is a special type — passing it (per §4.9) makes the student eligible for promotion and triggers a level-completion certificate on approval.

### 4.11 Certificates (3 fixed templates, data-driven)

Three certificate types, all rendered from **HTML/CSS templates populated with live data**. No PDF engine, no images. The output is a self-contained HTML page (inline CSS) that prints cleanly via the browser.

| Type | Issued when | Issuer | Template key | Visible to |
|---|---|---|---|---|
| **Level-start certificate** (شهادة بداية المستوى) | Student is enrolled in a Class | Auto on enrollment; re-printable by Teacher/Supervisor/Boss | `level_start` | Staff (assigned) + Boss |
| **Level-completion certificate** (شهادة إتمelm المست altogether) — let me redo this: **Level-completion certificate** (شهادة إتمام المستوى) | A promotion is **approved** (not on exam pass alone) | Auto on promotion approval; re-printable | `level_completion` | Staff (assigned) + Boss |
| **Payment receipt** (إيصال دفع) | A payment is recorded | Auto on payment save; re-printable by Money Man/Boss | `payment_receipt` | Money Man + Boss |

> Note: the certificate is issued on **promotion approval**, not on exam pass alone. This matches the real flow (passing alone doesn't promote; an approver does).

**Certificate anatomy (rendered):**
- Header: institution name, logo placeholder (a styled text block — no image), certificate title in Arabic.
- Body: dynamic fields from data (student name, from level, to level, exam, score, amount, date, etc.).
- Footer: certificate ID (public), issued-on date, issued-by name, verification URL.
- Optional decorative border: pure CSS (no image).

**Certificate templates (v1, fixed):**
- 3 hardcoded files in the backend: `level_start.html.tpl`, `level_completion.html.tpl`, `payment_receipt.html.tpl`.
- Each has inline `<style>` CSS and placeholders like `{{student_name}}`, `{{level_name}}`, `{{date}}`, `{{score}}`, `{{certificate_id}}`.
- **Boss does not edit templates in v1.** If customization is needed later, it's a Phase 6 enhancement with an in-app editor.
- A printed/certified feel is achieved with:
  - Centered layout, large Arabic-friendly typography.
  - CSS border (double border, or corner ornaments via pseudo-elements).
  - Signature line (a styled empty block labeled "توقيع المدير" or "توقيع المحاسب").
  - Print stylesheet (`@media print`) to hide nav and force a clean single-page output.

**Certificate lifecycle:**
- `issued` (with verification ID) → `revoked` (only Boss, with reason, audited).
- Verification: public URL `/verify/<certificate_id>` shows: valid / revoked, type, date issued, student name (hidden for payment receipts by default, for privacy).
- Re-print: any authorized staff can re-open the certificate and "Download as HTML" (saves the rendered page as a standalone .html file the user can archive).

**Why this works:**
- No PDF library = no dependencies, no extra CPU, no font embedding issues.
- HTML + inline CSS is portable, printable, and looks polished.
- The browser's "Print → Save as PDF" is good enough if a PDF is ever needed.
- Storage is just a few KB per certificate (the row + the template ref + the verification ID).

### 4.12 Student Attendance
- Marked per session by the teacher (or supervisor).
- States: `Present`, `Absent`, `Late`, `Excused` (with text reason).
- Two mark modes: quick (mark all present, toggle) and per-student.
- Late = present but after the start time.
- Excused absences don't count against attendance %.
- No student dispute flow (students don't have access).

### 4.13 Staff Presence & Absence
- **Daily check-in** by each staff member: one click "أنا موجود" with optional text note.
- States: `Present`, `Absent`, `On Leave`, `Sick`, `Official Duty`.
- **Auto-detected absence** for teachers: session end time passes with no attendance submitted → flagged as `No-Show`.
- **Visible to Boss only.**
- Reports: today's board, monthly count, no-show list, excused vs unexcused breakdown.
- Optional payroll hook: Money Man can apply "deduct X days" in salary module.

### 4.14 Class Profile (4 questions, "stuck" restored)
For any class, an instant text-based dashboard answering **four** questions:
- **Leading students** — top N by weighted score.
- **Weak students** — bottom N, tagged: `LOW SCORE` / `LOW ATTENDANCE` / `BOTH` / `STUCK AT LEVEL`.
- **Most absent** — sorted by absence rate.
- **Stuck students** — students whose **current level hasn't changed in N months AND whose average grade in that level is below threshold M** (or who have failed the certification exam K times). N, M, K are configurable in Settings.

Filters: by subject, by date range. Drill-down: click a student → full profile. No images, no heavy charts — clean tables with text "sparklines" (`▁▂▃▅▆▇`).

> "Stuck students" is a per-class view because students in a class share the same current level; once promoted, they leave the class. So a student appears "stuck" relative to their Class's Level.

### 4.15 Student Profile (staff view)
Each student record contains:
- **Personal info (all text):** Arabic name, DOB, contact phone, guardian name + phone, address, enrollment date, status, background notes.
- **Starting level** — set at first enrollment, immutable.
- **Current level** — auto-updated on promotion approval.
- **Level history** — every level change with date, reason, exam reference, who approved.
- **Certificates** — list of all level-start and level-completion certificates (with "print" buttons).
- **Exam history** — every exam, score, grade, pass/fail, subject, teacher.
- **Class history** — every Class the student has been enrolled in, with term dates and status.
- **Developmental timeline** — chronological milestones: enrollments, class completions, level-ups, certificates, attendance milestones, positive notes, status changes.
- **Attendance history** — per class, %, trend, with text sparkline.
- **Notes from staff** — see §6.
- **Payments status** — visible to Money Man + Boss.
- **Quick search keys:** student name (Arabic), phone, guardian phone. Search is fast because it's the primary parent-interaction workflow.

### 4.16 Notes System (cross-cutting)
See §6 for the full design. Notes are written by staff about students or staff, with categories, severity, and visibility rules. Notes are **internal only** — never shared with parents verbally or otherwise by staff.

### 4.17 Finance Module (Money Man)
- **Tuition:** set tuition per Class or per student; create invoices; mark paid/unpaid/partial.
- **Payment recording:** amount, method, date, receipt number, notes. **On save, system auto-generates a payment receipt certificate** (see §4.11).
- **Discounts & scholarships:** apply per student with reason.
- **Salaries:** staff payroll, monthly. Base + bonuses + deductions = net. Optional days-deducted from staff absence.
- **Expenses:** operational costs, categorized by text labels.
- **Reports:** income, outstanding, P&L, per-class revenue, salary sheet. All exportable as CSV.
- **Money visibility rule:** Money Man sees all money data; Boss sees everything; others see only payment status on a student (if Boss permits).

### 4.18 Notifications
- In-app + email (Arabic templates).
- Triggers: exam scheduled, exam published, promotion proposal created, promotion approved, promotion rejected, certificate issued, payment received, payment due, attendance below threshold, note flagged urgent, staff no-show detected.
- All text in a single template table.

### 4.19 Reporting & Analytics
- Class-level, institution-level, staff-level.
- All exportable as CSV. Text-based sparklines for v1.

### 4.20 Audit Log
- Every add/edit/delete/state-change/promotion/note/certificate-issuance by any user.
- Boss can view & filter.
- Read-only, append-only.

---

## 5. High-Level Data Model

> Entities and relationships — no SQL DDL. ~20 tables.

**User** (staff only)
- id, full_name_ar, full_name_en?, email, phone, role, status, password_hash, totp_secret?, created_at

**Capability Grant**
- id, user_id, capability_key, value (grant/deny), granted_by, granted_at

**Level**
- id, name_ar, code, description, order_index, default_passing_grade, default_promotion_rule, next_level_id?, status, created_at

**Subject**
- id, name_ar, description, default_passing_grade, status

**Level Subject** (default curriculum per level)
- id, level_id, subject_id

**Class**
- id, name_ar, code, level_id, group_label, status, capacity, term_start, term_end, supervisor_id, created_by, created_at

**Class Subject**
- id, class_id, subject_id, primary_teacher_id, backup_teacher_id?

**Class Enrollment**
- id, class_id, student_id, enrolled_at, status, ended_at?, **starting_level_id** (snapshot at enrollment)

**Time Table Slot**
- id, class_id, day_of_week, start_time, end_time, class_subject_id, room_label

**Session**
- id, slot_id, class_id, date, status, started_at, locked_at, cancelled_reason?

**Student**
- id, full_name_ar, dob, contact_phone, guardian_name, guardian_phone, address, enrollment_date, **starting_level_id** (set at creation), **current_level_id** (auto-updated on promotion), status, background_notes, created_at

**Student Attendance**
- id, session_id, student_id, state, reason_text?, marked_by, marked_at

**Staff Daily Presence**
- id, user_id, date, state, note_text?, self_reported, auto_flagged_no_show, source_session_id?

**Exam**
- id, class_id, subject_id, teacher_id, title_ar, type, date, total_points, passing_grade, status, is_certification, published_at

**Exam Score**
- id, exam_id, student_id, score, grade, passed, entered_by, entered_at

**Promotion Proposal** (the engine's work item)
- id, student_id, from_level_id, to_level_id, exam_id?, reason_text, proposed_by, proposed_at, status (pending | approved | rejected), decided_by?, decided_at?, decision_reason_text?

**Level History** (every approved promotion)
- id, student_id, from_level_id, to_level_id, exam_id?, reason, proposal_id?, changed_by, changed_at

**Certificate** (covers all 3 types)
- id, type (level_start | level_completion | payment_receipt), certificate_id (public, unique), issued_at, issued_by, status (issued | revoked), revoked_at?, revoked_reason?
- student_id (for level_start + level_completion)
- level_id? (for level_start + level_completion)
- class_id? (for level_start)
- exam_id? (for level_completion)
- level_history_id? (for level_completion, links to the LevelHistory row that triggered it)
- payment_id? (for payment_receipt)
- template_key (e.g., 'level_start', 'level_completion', 'payment_receipt')
- data_snapshot (JSON, optional — cached at issuance for fast re-render if the source row changes)

**Note** — see §6
- id, author_id, target_type (student/staff/class), target_id, category, severity, body, visibility, parent_note_id?, created_at

**Tuition Plan**
- id, class_id? | student_id?, amount, frequency, currency, terms_text

**Invoice**
- id, student_id, class_id, amount, due_date, status, notes_text

**Payment**
- id, invoice_id, amount, method, paid_at, received_by, receipt_no, notes_text

**Salary**
- id, user_id, month, base, bonuses, deductions, net, status, paid_at, days_deducted?

**Expense**
- id, category, amount, date, description, recorded_by

**Notification**
- id, user_id, type, subject_ar, body_ar, read_at, created_at

**Audit Log**
- id, actor_id, action, entity_type, entity_id, before_text?, after_text?, created_at

**Settings (institution-wide)**
- key, value_text, updated_by, updated_at

**Relationships (short version):**
- A `Level` has many `LevelSubject` rows, many `Class` rows, and an optional `next_level_id` pointer.
- A `Class` belongs to one `Level`, one `Supervisor`, has many `ClassSubject` rows, many `ClassEnrollment`s, many `TimeTableSlot`s.
- A `TimeTableSlot` spawns many `Session`s.
- A `Session` has many `StudentAttendance` rows; may also produce a `StaffDailyPresence` row.
- A `Class` has many `Exam`s; an `Exam` has many `ExamScore`s.
- A `Student` has one `starting_level_id` and one `current_level_id`, many `LevelHistory` rows, many `PromotionProposal` rows, many `Certificate` rows (level_start + level_completion), many `ClassEnrollment`s, many `Note` rows.
- A `PromotionProposal` resolves to a `LevelHistory` row on approval.
- A `LevelHistory` row triggers a `Certificate` (level_completion) on creation.
- A `Payment` has one `Certificate` (payment_receipt) auto-issued on save.
- A `Note` targets a `Student`, a `User` (staff), or a `Class`; may be a reply to a parent note.
- A `Certificate` row references the source entity and uses a `template_key` to look up the right HTML/CSS template at render time.

---

## 6. Notes System (detailed)

Captures soft signals like *"علي كسلان هذا الأسبوع"*, *"مريم تبدو حزينة، مشكلة عائلية محتملة"*.

### 6.1 What a Note Looks Like
```
author:    [اسم + دور]
target:    [اسم الطالب/الموظف/الفصل]
category:  [من قائمة قابلة للتخصيص]
severity:  info | attention | urgent
body:      "علي كسلان هذا الأسبوع، لم يسلم الواجب مرتين."
visible to: [قائمة الأدوار/المستخدمين]
created:   [التاريخ + الوقت]
replies:   [0..N ردود]
```

### 6.2 Configurable Categories (Boss sets them up in Settings)

Default Arabic categories (Boss can edit/add/remove):
- **سلوكي:** كسلان، مشاغب، وقح، تنمر، متعاون، مساعد
- **عاطفي:** حزين، غاضب، قلق، سعيد، متحمس
- **أداء:** يتحسن، يتراجع، عالق، متفوق
- **رفاهية:** مريض، متعب، مشكلة عائلية، صعوبة مالية
- **أخرى:** ملاحظة إيجابية، ملاحظة عامة

### 6.3 Severity
- `info` — neutral observation.
- `attention` — worth following up.
- `urgent` — Boss gets an instant notification + dashboard widget.

### 6.4 Visibility Rules
- Notes written by **Teacher** about a **Student**: visible to Teacher, Supervisor of that class, Boss. **Never to the student.**
- Notes written by **Supervisor** about a **Student**: visible to Supervisor, Boss, Teachers of that class.
- Notes written by **Money Man** about a **Student**: visible to Money Man, Boss. Not to teachers.
- Notes written by **Boss** about a **Student**: visible to Boss only by default. Boss can extend per note.
- Notes about **Staff**: visible to Boss, the author, the target staff. Supervisor of that staff can be added.
- Notes about a **Class**: visible to all assigned staff + Boss.

Per-note override: `private_to_author` | `default` | `custom_list`.

### 6.5 Workflow
1. Staff opens a student's profile.
2. Clicks "إضافة ملاحظة" → picks category, sets severity, types body, optionally adjusts visibility, saves.
3. Note is **append-only** — author cannot edit or delete. They can add a "correction" follow-up note.
4. If `severity = urgent`, Boss is notified instantly.
5. Notes appear on the student's profile in a chronological list, filterable by category and author.
6. On the Class Profile dashboard, a "Flagged Students" widget shows students with `urgent` or recent `attention` notes.

### 6.6 Why This Matters
- Notes turn a database of grades and attendance into a **human record** of each student.
- Replaces the "we know who's struggling but it's all in our heads" problem.
- All text — ~100 bytes per note. Negligible storage.

---

## 7. Key User Journeys

### 7.1 Boss setup (the architect's flow)
1. Boss creates the institution profile (name, currency, default passing grades, note categories, severity rules, default promotion rules, "stuck" thresholds, approval-chain config).
2. Boss creates **Levels** (Level 1, Level 2, ...) with default subjects and `next_level_id` pointers.
3. Boss creates **Subjects**.
4. Boss adds **staff**: Supervisors, Money Man, Teachers.
5. Boss creates **Classes** by picking a Level + Group + term + supervisor.
6. Boss assigns **teachers per subject** in each class.
7. Boss builds the **weekly time table** for each class.
8. Boss bulk-imports **Students** and enrolls them into classes.
   - **On each enrollment, a level-start certificate is auto-issued** and visible on the student's profile.
9. Boss grants any extra capabilities to staff (e.g., allow a Supervisor to approve promotions for a specific Level).

### 7.2 Daily teacher flow
1. Teacher logs in → "أنا موجود" check-in.
2. Lands on dashboard: today's classes, pending exams, pending promotion proposals, urgent notes.
3. Opens a class → marks attendance for the current session.
4. Writes a quick note on a student who seemed off today.
5. Starts a scheduled exam → marks it "In Progress" → enters scores → publishes.
6. Reviews class profile (leading / weak / absent / stuck).
7. (Optional) prints a certificate for a parent who came in person.

### 7.3 Supervisor flow
1. Self check-in.
2. Dashboard: assigned classes, urgent notes, pending promotion proposals (if configured as approver).
3. Reviews teacher's attendance and grading quality.
4. Reads notes flagged urgent.
5. Sees class profile for assigned classes.
6. Approves/rejects promotion proposals for assigned classes (if configured).
7. Adjusts the weekly timetable for assigned classes if needed.

### 7.4 Money Man flow
1. Self check-in.
2. Creates tuition plans for the term.
3. Generates monthly invoices.
4. Records a payment → **system auto-issues a payment receipt certificate**; Money Man prints it for the parent.
5. Marks salary payments (with optional days-deducted from staff absence).
6. Closes the month → runs reports → exports to Boss.

### 7.5 Parent inquiry flow (call-in)
1. A parent calls asking about their child.
2. Staff opens the system, types the student's name (or guardian phone) in the global search.
3. Student profile opens — staff reads out: current level, attendance summary, recent exam results, certificates earned.
4. **No link is generated. Nothing is sent to the parent.** The conversation is verbal.
5. If the parent needs a written proof (e.g., for a school transfer), staff prints a **level-completion certificate** or **level-start certificate** directly from the profile and hands it over (or the parent picks it up).

### 7.6 Promotion flow (the engine's happy path)
1. Teacher creates and publishes a **certification exam** for a Class.
2. Teacher enters scores → some students pass.
3. On publish, the system **auto-creates a Promotion Proposal** for each passing student:
   - `from_level` = student's `current_level_id`
   - `to_level` = resolved via the from-level's `next_level_id` (or "no next level" if undefined)
   - `exam_id` = the exam
   - `proposed_by` = the Teacher
   - `status` = `pending`
4. The proposal goes to the approver configured for the target Level (Boss, or Supervisor if Boss delegated).
5. Approver reviews the proposal (with the student's full profile in context) and either:
   - **Approves** → system:
     - Writes a `LevelHistory` row.
     - Updates `Student.current_level_id`.
     - Issues a **level-completion certificate** (template: `level_completion`).
     - Notifies assigned staff in-app.
     - Adds a "level-up" entry to the student's developmental timeline.
   - **Rejects** → logs the rejection with a required text reason, notifies the proposer, student stays at current level.
6. After approval, the student is **eligible to be enrolled in a new Class at the new Level** (Boss or Supervisor does the enrollment manually — not automatic).

### 7.7 Promotion flow (manual override)
1. Boss opens a student's profile → clicks "Override level".
2. Selects new level, types a required text reason, saves.
3. System writes a `LevelHistory` row (with `proposal_id = null`, `reason = "manual override: <text>"`).
4. Updates `Student.current_level_id`.
5. Issues a **level-completion certificate** (same as the engine's path).

### 7.8 Certificate issuance flow (payment receipt)
1. Money Man records a payment on an invoice.
2. System saves the payment, generates a receipt number, and **auto-issues a payment receipt certificate** (template: `payment_receipt`) with a verification ID.
3. Money Man clicks "Print receipt" → opens the rendered HTML certificate → prints via browser.
4. The receipt is stored on the student's profile under "Payments".

### 7.9 Staff absence flow
1. Teacher is scheduled for Class 1-A at 10:00. Doesn't show. Doesn't mark attendance by 10:30.
2. System flags the session as `incomplete` and creates a `StaffDailyPresence` row with `state = absent`, `auto_flagged_no_show = true`.
3. Boss sees it on the "Staff presence today" board within minutes.
4. If teacher was actually sick, they (or their supervisor) update the row with `state = sick` and a text reason.
5. Boss's monthly absence report shows the no-show counted or not counted depending on the final state.

### 7.10 Notes flow
1. Teacher notices Ali is distracted for the third day. Opens Ali's profile → clicks "إضافة ملاحظة".
2. Selects category: `قلق`. Severity: `attention`. Body: "منشغل ثلاثة أيام متوالية، لم يسلم واجبين."
3. Saves. Supervisor and Boss can now see this note.
4. Two days later, Supervisor writes a reply: "تحدثت معه، مشكلة عائلية في البيت، أتابع الموضوع."

---

## 8. UI / Screen Inventory (by role)

**Boss**
- Dashboard (KPI text cards + urgent notes + staff presence board + promotion queue).
- Levels (CRUD, reorder, default curriculum, `next_level_id`).
- Subjects.
- Classes (CRUD, time tables, roster, class profile).
- Staff presence (today's board, monthly reports, no-show list).
- Notes (inbox of urgent notes, search across all notes).
- **Promotion queue** (pending proposals awaiting Boss approval).
- Users (add/edit/deactivate, grant capabilities).
- Reports.
- Audit log.
- Settings (institution, note categories, severity rules, promotion rules, approval chain, "stuck" thresholds).

**Supervisor**
- Dashboard (assigned classes, urgent notes, promotion queue if configured as approver).
- Class detail (tabs: roster, attendance, exams, class profile, notes, time table).
- Teacher oversight (assigned teachers' recent activity, notes they wrote).
- **Promotion queue** (pending proposals for assigned classes, if configured as approver).
- My daily presence.

**Money Man**
- Dashboard (outstanding payments, monthly income, salary due).
- Tuition plans / Invoices / Payments.
- Salaries / Expenses.
- Reports (income, P&L, exports).
- My daily presence.

**Teacher**
- Dashboard (today's classes, pending exams, pending promotion proposals, urgent notes on my students).
- Class detail (roster, attendance, exams, class profile, time table).
- Attendance (live, per session).
- Exams (create, enter scores, publish).
- Class profile view.
- **My promotion proposals** (proposals I created and their status).
- My daily presence.

**No student UI. No parent UI.** All interactions happen on the staff screens, in person or over the phone.

**Certificate screens (cross-role):**
- Certificate viewer (`/certificates/<id>`) — renders the HTML/CSS template with live data. Has "Print" and "Download as HTML" buttons.
- Public verification (`/verify/<certificate_id>`) — minimal page: valid / revoked, type, date issued, student name (hidden for payment receipts by default).

**Global search (top of every page):**
- A single search bar that resolves to: students (by name/phone/guardian phone), staff (by name/email/phone), classes (by name/code), certificates (by certificate ID), proposals (by student name).
- This is the **primary tool for parent inquiries** and for the Boss to jump to anything fast.

---

## 9. Tech Stack Recommendations

Tuned for **Arabic-only, staff-only, text-only, low-cost hosting**.

- **Frontend:** React (Vite) or Next.js, TailwindCSS with **RTL plugin**, TanStack Query for data, FullCalendar (text/HTML, no images) for timetables, CSS-only sparklines.
- **Backend:** Node.js + NestJS (or Django REST, or Laravel). Strict typing. JWT + refresh tokens. **CASL** for RBAC + per-row visibility.
- **Database:** **PostgreSQL** for v1. **SQLite** for very small single-server deployments.
- **No file storage service** — all data in the DB. Avatar = CSS initials. QR code = inline SVG.
- **No PDF library** — certificates and receipts are printable HTML pages with inline CSS.
- **Email:** Resend or Postmark. Optional for v1; in-app notifications cover the core flow.
- **Hosting:** Single $5–$10/month VPS (Hetzner, DigitalOcean). Dockerized. Nginx + Caddy (auto-HTTPS).
- **Backups:** Cron `pg_dump` → Backblaze B2 ($0.005/GB/month). Daily, 30-day retention.
- **CI/CD:** GitHub Actions, deploy via SSH pull.
- **Observability:** Sentry (free tier) for errors. Simple text log for everything else.
- **Total monthly cost estimate:** **$5–$15** for a 1,000-student institution.

> **No-code shortcut for fastest MVP:** Supabase + Retool/Appsmith/Budibase. Trade-off: less control over the certificate template rendering, the promotion engine, and the note visibility logic.

---

## 10. Non-Functional Requirements

- **Language & layout:** **Arabic only, RTL**. Strings in Arabic. Future `en.json` is possible without refactor.
- **Security:** argon2/bcrypt passwords, HTTPS, RBAC + per-row visibility on every endpoint, audit log for all sensitive actions, 2FA for Boss, rate-limiting on login.
- **Performance:** dashboards < 1s on 4G. List pages paginated (50/page). Global search returns results in < 200ms.
- **Storage budget:** **< 50 MB** total DB for a 1,000-student institution, 5 years of data. Hard constraint.
- **Reliability:** daily DB backups with 30-day retention; restore tested monthly; 99.5% uptime target.
- **Data export:** Boss can export entire DB as SQL or CSV.
- **Privacy:** soft-delete by default; hard-delete requires Boss + reason. **Notes are internal — never shared with parents.** Payment receipts hide the student name in public verification by default.
- **Accessibility:** WCAG 2.1 AA. All forms keyboard-navigable. RTL-correct focus order. No color-only signals.

---

## 11. Phased Build Roadmap

### Phase 0 — Foundations (1–2 weeks)
- Project skeleton (RTL by default), Auth, roles, capability-grant system.
- User CRUD (Boss only).
- Settings (institution, note categories, severity rules, promotion rules, approval chain, "stuck" thresholds).
- Audit log plumbing.
- Global search infrastructure (trigram index on Arabic names + phone).

### Phase 1 — Levels, Subjects, Classes (2–3 weeks)
- Level CRUD + ordering + `next_level_id`.
- Subject CRUD.
- Class creation from Level (with subject inheritance + override).
- Weekly time table.
- Class Enrollment (with `starting_level_id` snapshot).
- Student records CRUD.
- **Level-start certificate auto-issuance on enrollment** (first certificate template live).

### Phase 2 — Attendance & Sessions (2 weeks)
- Auto-generation of sessions from the weekly timetable.
- Student attendance (mark + lock).
- Staff auto no-show detection + Boss's staff presence board.

### Phase 3 — Student Records & Notes (2 weeks)
- Student profile (text fields, level history, developmental timeline).
- **Global search on students** (the parent-inquiry workflow depends on this).
- Notes System (categories, severity, visibility, replies, urgent widget).
- Class Profile dashboard (leading / weak / absent / stuck — **4 questions**).
- **Payment receipt certificate plumbing** (third template defined; exercised in Phase 5).

### Phase 4 — Exams, Promotion, Certificates (3 weeks)
- Exams (create, enter scores, publish).
- Exam history on student profile.
- **Level Promotion Engine**: proposal creation, approval workflow, LevelHistory, current_level update, notification.
- **Level-completion certificate auto-issuance on promotion approval** (second certificate template live).
- Certificate template polish (3 templates refined with print stylesheet).

### Phase 5 — Money & Polish (2–3 weeks)
- Finance module (tuition, invoices, payments, salaries, expenses, reports).
- Payment → auto-issues payment receipt (plumbed in Phase 3, now exercised end-to-end).
- Notifications (in-app + email).
- Staff monthly absence reports.
- Performance pass + security audit + backup test.

### Phase 6 — Optional Extras (post-v1)
- Bulk import UX polish.
- Advanced reports.
- Optional in-app certificate template editor (Boss can edit HTML/CSS templates).
- Optional lightweight mobile shell (Capacitor/PWA) — still staff-only.

> **Total v1 estimate: 13–17 weeks** with a small team (1 frontend, 1 backend, 1 designer part-time). Faster with the no-code shortcut.

---

## 12. Open Questions to Lock Before Build

1. **Bulk import format** — do you have existing student/staff data in Excel/CSV to migrate in?
2. **Currency & tuition model** — single currency? Fixed tuition per Level or per Class?
3. **Promotion approval chain** — Boss only (default), or Boss can delegate to Supervisor per Level? Auto-approve on cert pass (default: off)?
4. **"Stuck" thresholds** — defaults: 6 months at same level + average < 50% OR 2 failed cert attempts. Boss-configurable per institution?
5. **Note retention** — keep all notes forever, or auto-archive after N years?
6. **Email necessity** — required in v1, or in-app only is enough for v1?
7. **Hosting preference** — your own server, or managed cloud? Any data-residency requirement?
8. **Multi-branch / multi-institution** — single institution, or multi-tenant from the start?
9. **Salary module complexity** — simple base + bonus + deduction, or tax rules, hourly, etc.?
10. **Search language** — Arabic trigram full-text, or also match Latin transliteration of names?

---

## 13. Definition of Done for v1

The app is "done" when:
- A Boss can run a full academic term end-to-end: set up Levels → create Classes → enroll students (level-start cert auto-issued) → schedule classes → mark attendance → run exams (score-only) → publish a certification exam (promotion proposals auto-created for passers) → approve/reject proposals (level-completion cert auto-issued on approval, LevelHistory recorded) → manually enroll promoted students in a new Class at the new Level → record payments (payment receipt auto-issued) → answer the **four** class-profile questions (lead / weak / absent / stuck) for any class.
- All four staff roles can log in and complete their core journeys.
- A teacher can write a note on a student, tag it with a category and severity, and the Boss sees urgent notes instantly.
- A Boss can see which staff are present, absent, or on leave today, and the monthly absence report.
- A Boss can grant or revoke any individual capability to any staff member.
- A teacher can propose a level-up; an approver can approve/reject; on approval the system updates the student's level, writes LevelHistory, and issues a level-completion certificate.
- When a parent calls, staff can global-search the student, open the profile, read out the data, and print any certificate the parent needs — all within 30 seconds.
- All three certificate types (level start, level completion, payment receipt) are rendered as styled HTML/CSS from fixed templates, printable, downloadable as standalone HTML, and have a public verification page.
- **No staff promotion engine** (only student promotion). No parent portal, no student login, no link sent to parents. Parents receive information verbally and certificates on paper.
- The 3 certificate templates are **fixed in v1** (Boss does not edit them in-app).
- Audit log captures all sensitive actions, including every promotion proposal/approval/rejection.
- Backups run daily and can be restored.
- 2FA is enabled for the Boss.
- UI is Arabic-only, RTL, fully accessible.
- Total monthly hosting cost is under $20.

---

## 14. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Scope creep (especially finance + promotion complexity) | Delays v1 | Phase 4 promotion is minimal (propose → approve → write history → issue cert); advanced promotion rules deferred. |
| Permission model + note visibility getting messy | Security/privacy bugs | Use CASL; tests for every role × capability × note-visibility combination. |
| Promotion engine creating "stuck" feedback loops (e.g., student stuck → Boss manually promotes → no learning) | Bad outcomes | The "stuck" widget surfaces the issue; Boss can choose to give extra time, propose a remedial class, or override. Audit log captures overrides. |
| Staff no-show detection false positives | Unfair to staff | Only auto-flag if end time passed AND no attendance marked; staff can update state with reason. |
| Notes becoming a gossip channel | HR issue | Append-only, strict visibility rules, Boss can audit, internal only. |
| Certificate forgery | Reputation | Public verification page by certificate ID; revocation is audited. |
| Certificate template bugs (e.g., missing data, broken RTL) | Looks unprofessional | Render-and-screenshot test in CI; print stylesheet QA; Phase 4 polish pass. |
| Global search slow on Arabic | Slow parent-call workflow | Trigram index on Arabic name + phone; benchmark with 10k students before launch. |
| Data loss | Catastrophic | Daily automated backups, restore tested monthly. |
| Single-VPS hosting going down | Service outage | Auto-restart via systemd; optional backup VPS. |
| RTL layout bugs in third-party libs | UX issues | Choose RTL-friendly libs; test every screen in RTL. |
| Arabic text input issues (diacritics, RTL in forms) | Data quality | Use well-tested form libs; test Arabic IME and mixed Arabic/English content. |
| Boss wanting template edits before launch | Scope creep on certificates | 3 fixed templates are the v1 contract. Customization is explicitly Phase 6. |

---

## 15. Summary (TL;DR — final)

- **Four staff roles** (no student role). Boss is the root architect.
- **Levels are the foundation.** Boss creates Levels; Classes are concrete instances with one weekly timetable, one supervisor, many subjects, many students.
- **Students are records, not users.** No student login, no parent portal. Parents call, staff global-searches, opens the profile, reads the data, prints certificates as needed.
- **Level Promotion Engine (student-only, restored).** Students have a `starting_level` and a `current_level`. They move up via a propose → approve flow, triggered by passing the certification exam for their current Level. Every level change is recorded in `LevelHistory`. Boss can also override manually. The "stuck students" classification is back: a student is stuck if they've been at the same level for N months AND their average grade is below threshold (configurable).
- **Class Profile is 4 questions again:** leading / weak / most absent / stuck.
- **3 fixed certificate types** (level start, level completion, payment receipt), all rendered as **styled HTML/CSS templates populated with live data** — no PDF engine, no images, print-ready. Auto-issued at the right moments; printable on demand; publicly verifiable by ID. **Templates are fixed in v1** — no in-app editor.
- **Notes System** captures soft signals with categories, severity, and strict visibility. Append-only, internal-only, audited, never shared with parents.
- **Exams = scores only.** A certification exam, if passed, triggers a promotion proposal (not a direct promotion).
- **Staff absence** is tracked separately from student attendance, auto-detected for teacher no-shows, visible only to the Boss.
- **Text-only architecture:** < 50 MB for 1,000 students, 5 years. Hostable on $5–$15/month VPS.
- **Arabic-only, RTL** by default.
- **Global search** is the parent-inquiry tool — must be fast and forgiving of Arabic name variations.
- **Phased build:** v1 in **13–17 weeks** with a small team.
- **10 open questions** to lock before coding (most can be deferred, but #2, #3, and #4 affect the schema and the promotion engine).

---

*End of final plan v6.*
