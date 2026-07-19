from backend.database import engine, Base
from backend.models import ClassTeacher

def main():
    print("Creating class_teachers table...")
    ClassTeacher.__table__.create(bind=engine, checkfirst=True)
    print("Done!")

if __name__ == "__main__":
    main()
