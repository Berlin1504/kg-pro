import os
import socket
import subprocess
import sys
import tempfile
import time

import requests


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for_server(base_url, process):
    deadline = time.time() + 20
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError("Server exited before it became ready")
        try:
            response = requests.get(f"{base_url}/api/me", timeout=1)
            if response.status_code in {200, 401}:
                return
        except requests.RequestException:
            time.sleep(0.2)
    raise TimeoutError("Server did not become ready")


def assert_status(response, expected):
    if response.status_code != expected:
        raise AssertionError(f"Expected {expected}, got {response.status_code}: {response.text}")


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    port = free_port()
    base_url = f"http://127.0.0.1:{port}"

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        db_path = os.path.join(tmp, "smoke.db")
        env = os.environ.copy()
        env.update(
            {
                "DATABASE_URL": f"sqlite:///{db_path}",
                "SECRET_KEY": "smoke-test-secret",
                "SEED_ADMIN": "true",
                "SEED_ADMIN_PASSWORD": "smoke-password",
            }
        )
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--log-level",
                "warning",
            ],
            cwd=root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            wait_for_server(base_url, process)
            session = requests.Session()

            health = session.get(f"{base_url}/api/health", timeout=5)
            assert_status(health, 200)
            if health.json().get("status") != "ok":
                raise AssertionError(f"Unexpected health response: {health.text}")
            if health.headers.get("x-content-type-options") != "nosniff":
                raise AssertionError("Missing security headers")

            response = session.post(
                f"{base_url}/api/login",
                json={"email": "admin@local.com", "password": "smoke-password"},
                timeout=5,
            )
            assert_status(response, 200)
            
            csrf_token = session.cookies.get("csrf_token")
            if csrf_token:
                session.headers.update({"x-csrf-token": csrf_token})

            subject = session.post(
                f"{base_url}/api/subjects/",
                json={"name_ar": "Arabic", "default_passing_grade": 60},
                timeout=5,
            )
            assert_status(subject, 200)
            subject_id = subject.json()["id"]

            level = session.post(
                f"{base_url}/api/levels/",
                json={"name_ar": "Level 1", "code": "L1", "order_index": 1, "subject_ids": [subject_id]},
                timeout=5,
            )
            assert_status(level, 200)
            level_id = level.json()["id"]

            class_response = session.post(
                f"{base_url}/api/classes/",
                json={"name_ar": "Class A", "level_id": level_id, "group_label": "A", "capacity": 1},
                timeout=5,
            )
            assert_status(class_response, 200)
            class_id = class_response.json()["id"]

            student = session.post(
                f"{base_url}/api/students/",
                json={"full_name_ar": "Student One", "contact_phone": "01000000000"},
                timeout=5,
            )
            assert_status(student, 200)
            student_id = student.json()["id"]

            enrollment = session.post(
                f"{base_url}/api/students/{student_id}/enroll",
                json={"class_id": class_id},
                timeout=5,
            )
            assert_status(enrollment, 200)

            duplicate_enrollment = session.post(
                f"{base_url}/api/students/{student_id}/enroll",
                json={"class_id": class_id},
                timeout=5,
            )
            assert_status(duplicate_enrollment, 400)

            roster = session.get(f"{base_url}/api/classes/{class_id}/students", timeout=5)
            assert_status(roster, 200)
            if len(roster.json()) != 1 or roster.json()[0]["student"]["id"] != student_id:
                raise AssertionError(f"Unexpected class roster: {roster.text}")

            class_profile = session.get(f"{base_url}/api/classes/{class_id}/profile", timeout=5)
            assert_status(class_profile, 200)

            schedule = session.post(
                f"{base_url}/api/schedules/",
                json={
                    "class_id": class_id,
                    "subject_id": subject_id,
                    "day_of_week": 0,
                    "start_time": "10:00",
                    "end_time": "11:00",
                },
                timeout=5,
            )
            assert_status(schedule, 200)

            generated = session.post(
                f"{base_url}/api/sessions/generate",
                json={"class_id": class_id, "start_date": "2026-07-05", "end_date": "2026-07-05"},
                timeout=5,
            )
            assert_status(generated, 200)

            sessions = session.get(f"{base_url}/api/sessions/?class_id={class_id}", timeout=5)
            assert_status(sessions, 200)
            session_id = sessions.json()[0]["id"]

            bad_attendance = session.post(
                f"{base_url}/api/sessions/{session_id}/attendance",
                json={"records": [{"student_id": 999, "status": "present"}]},
                timeout=5,
            )
            assert_status(bad_attendance, 400)

            attendance = session.post(
                f"{base_url}/api/sessions/{session_id}/attendance",
                json={"records": [{"student_id": student_id, "status": "present"}]},
                timeout=5,
            )
            assert_status(attendance, 200)

            invoice = session.post(
                f"{base_url}/api/finance/invoices",
                json={"student_id": student_id, "class_id": class_id, "amount": 100, "title": "Tuition"},
                timeout=5,
            )
            assert_status(invoice, 200)
            invoice_id = invoice.json()["id"]

            overpayment = session.post(
                f"{base_url}/api/finance/payments",
                json={"invoice_id": invoice_id, "amount": 150, "method": "cash"},
                timeout=5,
            )
            assert_status(overpayment, 400)

            payment = session.post(
                f"{base_url}/api/finance/payments",
                json={"invoice_id": invoice_id, "amount": 100, "method": "cash"},
                timeout=5,
            )
            assert_status(payment, 200)

            exam = session.post(
                f"{base_url}/api/exams/",
                json={
                    "title": "Certification",
                    "subject_id": subject_id,
                    "class_id": class_id,
                    "date": "2026-07-09",
                    "total_points": 100,
                    "passing_grade": 60,
                    "is_certification": True,
                },
                timeout=5,
            )
            assert_status(exam, 200)
            exam_id = exam.json()["id"]

            bad_score = session.post(
                f"{base_url}/api/exams/{exam_id}/scores",
                json={"scores": [{"student_id": student_id, "score": 101}]},
                timeout=5,
            )
            assert_status(bad_score, 400)

            scores = session.post(
                f"{base_url}/api/exams/{exam_id}/scores",
                json={"scores": [{"student_id": student_id, "score": 88}]},
                timeout=5,
            )
            assert_status(scores, 200)

            published = session.post(f"{base_url}/api/exams/{exam_id}/publish", json={}, timeout=5)
            assert_status(published, 200)

            edit_published = session.post(
                f"{base_url}/api/exams/{exam_id}/scores",
                json={"scores": [{"student_id": student_id, "score": 90}]},
                timeout=5,
            )
            assert_status(edit_published, 400)

            note = session.post(
                f"{base_url}/api/notes/",
                json={"target_type": "student", "target_id": student_id, "content": "Follow up"},
                timeout=5,
            )
            assert_status(note, 200)
            note_id = note.json()["id"]

            deleted_note = session.delete(f"{base_url}/api/notes/{note_id}", timeout=5)
            assert_status(deleted_note, 200)

            bad_salary = session.post(
                f"{base_url}/api/finance/salaries",
                json={"user_id": 999, "month": "2026-07", "base_salary": 1000},
                timeout=5,
            )
            assert_status(bad_salary, 404)

            logout = session.post(f"{base_url}/api/logout", timeout=5)
            assert_status(logout, 200)
            if "access_token" in session.cookies or "csrf_token" in session.cookies:
                raise AssertionError("Logout did not clear auth cookies")

            print("smoke api ok")
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    main()
