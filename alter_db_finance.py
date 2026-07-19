import sqlite3

db_path = "class_app.db"

def migrate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Create fee_templates table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fee_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_ar VARCHAR NOT NULL,
        amount FLOAT NOT NULL,
        level_id INTEGER,
        is_recurring BOOLEAN DEFAULT 1,
        status VARCHAR DEFAULT 'active',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(level_id) REFERENCES levels(id)
    );
    """)
    
    # 2. Add base_salary to users table
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN base_salary FLOAT DEFAULT 0.0;")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            pass # Column already exists
        else:
            raise e
            
    conn.commit()
    conn.close()
    print("Finance migration complete.")

if __name__ == "__main__":
    migrate()
