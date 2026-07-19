import sqlite3

conn = sqlite3.connect('d:/Apps/classify/class_app.db')
c = conn.cursor()

try:
    c.execute('ALTER TABLE certificates ADD COLUMN exam_id INTEGER')
except Exception as e:
    print(e)
    
try:
    c.execute('ALTER TABLE certificates ADD COLUMN payment_id INTEGER')
except Exception as e:
    print(e)

conn.commit()
conn.close()
