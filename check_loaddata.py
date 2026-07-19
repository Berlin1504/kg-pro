import re

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'async function loadData()' in line or 'window.loadData =' in line:
        start = i
        for j in range(i, len(lines)):
            if 'window.TreeUI =' in lines[j] or 'async function renderStudents' in lines[j] or 'async function load' in lines[j]:
                print(''.join(lines[start:j]))
                break
        break
