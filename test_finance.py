import requests

base_url = "http://127.0.0.1:8000/api"

session = requests.Session()
# Login
res = session.post(f"{base_url}/login", json={"email": "admin@local.com", "password": "password123"})
if res.status_code != 200:
    print("Login failed", res.text)
    exit(1)

# Get students to find an ID
res = session.get(f"{base_url}/students/")
if res.status_code != 200 or not res.json():
    print("Failed to get students", res.text)
    exit(1)
    
student_id = res.json()[0]["id"]

# Create Invoice
inv_data = {
    "student_id": student_id,
    "amount": 1000,
    "title": "Test Tuition"
}
res = session.post(f"{base_url}/finance/invoices", json=inv_data)
if res.status_code != 200:
    print("Failed to create invoice", res.text)
    exit(1)
    
inv_id = res.json()["id"]
print("Created invoice:", inv_id)

# Record Payment
pay_data = {
    "invoice_id": inv_id,
    "amount": 400,
    "method": "cash"
}
res = session.post(f"{base_url}/finance/payments", json=pay_data)
if res.status_code != 200:
    print("Failed to record payment", res.text)
    exit(1)

print("Payment response:", res.json())

# Get Receipts/Reports
res = session.get(f"{base_url}/finance/reports")
print("Reports:", res.json())
