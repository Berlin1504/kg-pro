import sqlite3

def migrate():
    conn = sqlite3.connect('class_app.db')
    c = conn.cursor()
    
    # 1. Update students table
    try:
        c.execute("ALTER TABLE students ADD COLUMN total_billed FLOAT DEFAULT 0.0")
        c.execute("ALTER TABLE students ADD COLUMN total_paid FLOAT DEFAULT 0.0")
        c.execute("ALTER TABLE students ADD COLUMN balance FLOAT DEFAULT 0.0")
        print("Updated students table.")
    except Exception as e:
        print(f"Students table might already be updated: {e}")

    # 2. Update invoices table
    try:
        c.execute("ALTER TABLE invoices ADD COLUMN paid_amount FLOAT DEFAULT 0.0")
        c.execute("ALTER TABLE invoices ADD COLUMN remaining FLOAT DEFAULT 0.0")
        print("Updated invoices table.")
    except Exception as e:
        print(f"Invoices table might already be updated: {e}")

    # 3. Update payments table
    try:
        c.execute("ALTER TABLE payments ADD COLUMN student_id INTEGER NULL")
        print("Updated payments table (student_id added).")
    except Exception as e:
        print(f"Payments table might already be updated: {e}")

    # For existing payments, we should populate student_id based on invoice_id
    try:
        c.execute("""
            UPDATE payments 
            SET student_id = (
                SELECT student_id FROM invoices WHERE invoices.id = payments.invoice_id
            )
            WHERE student_id IS NULL AND invoice_id IS NOT NULL
        """)
        print("Backfilled student_id on payments.")
    except Exception as e:
        print(f"Error backfilling student_id: {e}")

    conn.commit()
    conn.close()
    print("Migration finished successfully.")

if __name__ == "__main__":
    migrate()
