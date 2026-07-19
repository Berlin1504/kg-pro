import requests

BASE_URL = 'http://localhost:8000/api'

# 1. Login
r = requests.post(f'{BASE_URL}/auth/login', data={'username': 'admin@classify.local', 'password': 'admin'})
if r.status_code != 200:
    print('Login failed:', r.text)
    exit(1)
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# 2. Create Subject
r = requests.post(f'{BASE_URL}/subjects/', json={'name_ar': 'English Test', 'description': 'desc', 'promotion_threshold': 75}, headers=headers)
if r.status_code != 200:
    print('Failed to create subject:', r.text)
    exit(1)
subject = r.json()
print('Created subject:', subject)

# 3. Create Levels
r = requests.post(f'{BASE_URL}/levels/', json={'name_ar': 'L1', 'code': 'L1', 'order_index': 1, 'subject_id': subject['id']}, headers=headers)
level1 = r.json()
print('Created Level 1:', level1)
r = requests.post(f'{BASE_URL}/levels/', json={'name_ar': 'L2', 'code': 'L2', 'order_index': 2, 'subject_id': subject['id']}, headers=headers)
level2 = r.json()
print('Created Level 2:', level2)

# 4. Create Class
r = requests.post(f'{BASE_URL}/classes/', json={'name_ar': 'Class 1', 'level_id': level1['id'], 'capacity': 10}, headers=headers)
cls = r.json()
print('Created Class:', cls)

# 5. Create Student
r = requests.post(f'{BASE_URL}/students/', json={'full_name_ar': 'John Doe', 'gender': 'male'}, headers=headers)
student = r.json()
print('Created Student:', student)

# 6. Enroll Student
r = requests.post(f'{BASE_URL}/students/{student["id"]}/enroll', json={'class_id': cls['id']}, headers=headers)
print('Enrolled Student:', r.json())

# 7. Check Profile (initial)
r = requests.get(f'{BASE_URL}/profiles/student/{student["id"]}', headers=headers)
profile = r.json()
print('Initial profile subject levels:', profile['student_subject_levels'])

# 8. Manual Level Override
r = requests.put(f'{BASE_URL}/students/{student["id"]}/subject-level', json={'subject_id': subject['id'], 'level_id': level2['id']}, headers=headers)
print('Manual override response:', r.json())

# 9. Check Profile (after override)
r = requests.get(f'{BASE_URL}/profiles/student/{student["id"]}', headers=headers)
profile = r.json()
print('After override profile subject levels:', profile['student_subject_levels'])

