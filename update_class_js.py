import re

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Update renderClasses to show status
content = content.replace("<td>\</td>", "<td>\</td>\\n                                    <td><span class=\\"badge\\">\</span></td>")
content = content.replace("<th>المجموعة</th>", "<th>المجموعة</th>\\n                                    <th>الحالة</th>")

# Update saveClass
content = content.replace("const capacity = document.getElementById('cls-capacity').value;", "const capacity = document.getElementById('cls-capacity').value;\\n        const status = document.getElementById('cls-status').value;")

content = content.replace("capacity: parseInt(capacity)", "capacity: parseInt(capacity),\\n                status: status")

with open('frontend/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
