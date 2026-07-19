import re

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all lines with confirm
for i, line in enumerate(content.split('\n')):
    if 'confirm(' in line:
        print(f'Line {i+1}: {line.strip()}')
