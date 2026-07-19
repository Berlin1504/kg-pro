import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add navigation button for Audit Log (Boss only initially visible, or handled by JS)
content = content.replace('<button class="nav-btn" data-target="panel-reports">التقارير</button>', '<button class="nav-btn" data-target="panel-reports">التقارير</button>\n                <button class="nav-btn" id="nav-audit" data-target="panel-audit" style="display:none;">سجل النظام</button>')

# Add Audit Log Panel before panel-settings
audit_panel = '''
                <div id="panel-audit" class="panel">
                    <div class="flex-between mb-4">
                        <h2>سجل النظام (Audit Log)</h2>
                        <button class="btn-secondary" onclick="Audit.loadLogs()">تحديث</button>
                    </div>
                    <div class="table-responsive">
                        <table class="data-table" id="table-audit">
                            <thead>
                                <tr>
                                    <th>التاريخ والوقت</th>
                                    <th>المستخدم</th>
                                    <th>الحدث</th>
                                    <th>الكيان</th>
                                    <th>المعرف</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
'''

content = content.replace('<div id="panel-settings" class="panel">', audit_panel + '\n                <div id="panel-settings" class="panel">')

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
