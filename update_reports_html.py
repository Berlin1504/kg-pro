import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add navigation button
content = content.replace('<button class="nav-btn" data-target="panel-settings">الإعدادات</button>', '<button class="nav-btn" data-target="panel-reports">التقارير</button>\n                <button class="nav-btn" data-target="panel-settings">الإعدادات</button>')

# Add Reports Panel before panel-settings
reports_panel = '''
                <div id="panel-reports" class="panel">
                    <div class="flex-between mb-4">
                        <h2>التقارير والإحصائيات</h2>
                    </div>
                    
                    <div class="card mb-4">
                        <div style="display: flex; gap: 1rem; margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
                            <button class="btn-primary report-tab-btn" onclick="Reports.switchTab('gradebook')">سجل الدرجات</button>
                            <button class="btn-secondary report-tab-btn" onclick="Reports.switchTab('attendance')">تقرير الغياب</button>
                            <button class="btn-secondary report-tab-btn" onclick="Reports.switchTab('stuck')">الطلاب المتعثرين</button>
                        </div>
                        
                        <div id="report-view-gradebook" class="report-view">
                            <div class="flex-between mb-4">
                                <div class="form-group" style="max-width: 300px; flex: 1;">
                                    <label>اختر الفصل</label>
                                    <select id="report-class-select" class="form-control" onchange="Reports.loadGradebook()">
                                        <option value="">اختر الفصل...</option>
                                    </select>
                                </div>
                                <button class="btn-secondary" onclick="Reports.exportCSV('table-report-gradebook', 'سجل_الدرجات.csv')">تصدير CSV</button>
                            </div>
                            <div class="table-responsive">
                                <table class="data-table" id="table-report-gradebook">
                                    <thead><tr><th>الطالب</th><th>النسبة الإجمالية</th></tr></thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                        </div>
                        
                        <div id="report-view-attendance" class="report-view" style="display:none;">
                            <div class="flex-between mb-4">
                                <div class="form-group" style="max-width: 300px; flex: 1;">
                                    <label>اختر الفصل</label>
                                    <select id="report-attendance-class-select" class="form-control" onchange="Reports.loadAttendance()">
                                        <option value="">اختر الفصل...</option>
                                    </select>
                                </div>
                                <button class="btn-secondary" onclick="Reports.exportCSV('table-report-attendance', 'تقرير_الغياب.csv')">تصدير CSV</button>
                            </div>
                            <div class="table-responsive">
                                <table class="data-table" id="table-report-attendance">
                                    <thead><tr><th>الطالب</th><th>حضور</th><th>غياب</th><th>تأخر</th><th>عذر</th><th>نسبة الغياب</th></tr></thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                        </div>
                        
                        <div id="report-view-stuck" class="report-view" style="display:none;">
                            <div class="flex-between mb-4">
                                <p>الطلاب الذين لم يتم ترفيعهم لأكثر من 90 يوم</p>
                                <button class="btn-secondary" onclick="Reports.exportCSV('table-report-stuck', 'الطلاب_المتعثرين.csv')">تصدير CSV</button>
                            </div>
                            <div class="table-responsive">
                                <table class="data-table" id="table-report-stuck">
                                    <thead><tr><th>الطالب</th><th>المستوى الحالي</th><th>تاريخ آخر تحرك</th><th>أيام التعثر</th></tr></thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                        </div>
                        
                    </div>
                </div>
'''

content = content.replace('<div id="panel-settings" class="panel">', reports_panel + '\n                <div id="panel-settings" class="panel">')

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
