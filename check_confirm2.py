import re

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'confirm(' in line:
        print('---')
        start = max(0, i-5)
        for j in range(start, i+1):
            print(f'{j+1}: {lines[j].strip()}')
