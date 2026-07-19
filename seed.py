import os
import sys
sys.path.insert(0, os.path.abspath("backend"))
from backend import database, models, auth

def force_seed():
    db = database.SessionLocal()
    try:
        # Check if user exists
        boss = db.query(models.User).filter(models.User.email == "admin@local.com").first()
        if not boss:
            boss = models.User(
                full_name_ar="المدير العام",
                email="admin@local.com",
                role="boss",
                password_hash=auth.get_password_hash("admin123")
            )
            db.add(boss)
            db.commit()
            print("Seeded admin@local.com with password 'admin123'")
        else:
            boss.password_hash = auth.get_password_hash("admin123")
            db.commit()
            print("Reset admin@local.com password to 'admin123'")
    finally:
        db.close()

if __name__ == "__main__":
    force_seed()
