import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add status dropdown to class modal
status_html = '''
                        <div class="form-group">
                            <label>الحالة</label>
                            <select id="cls-status" class="form-control" required>
                                <option value="draft">مسودة</option>
                                <option value="active" selected>نشط</option>
                                <option value="on_hold">معلق</option>
                                <option value="completed">مكتمل</option>
                                <option value="archived">مؤرشف</option>
                            </select>
                        </div>
'''

content = content.replace('<div class="form-group">\n                            <label>السعة (عدد الطلاب)</label>', status_html + '\n                        <div class="form-group">\n                            <label>السعة (عدد الطلاب)</label>')

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
