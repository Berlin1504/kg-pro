import re

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'window.UI = {' in line:
        start = i
        for j in range(i, len(lines)):
            if '};' in lines[j] and 'closeModal' in ''.join(lines[i:j]):
                print(''.join(lines[start:j+20]))
                break
        break
