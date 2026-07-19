import re

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

reports_js = '''
window.Reports = {
    switchTab(tab) {
        document.querySelectorAll('.report-tab-btn').forEach(btn => {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-secondary');
        });
        event.target.classList.remove('btn-secondary');
        event.target.classList.add('btn-primary');
        
        document.querySelectorAll('.report-view').forEach(view => view.style.display = 'none');
        document.getElementById(eport-view-\).style.display = 'block';
        
        if (tab === 'stuck') this.loadStuck();
    },
    
    async loadGradebook() {
        const classId = document.getElementById('report-class-select').value;
        const tbody = document.querySelector('#table-report-gradebook tbody');
        const thead = document.querySelector('#table-report-gradebook.data-table thead tr');
        
        if (!classId) {
            StateHelper.empty(tbody, 'الرجاء اختيار فصل');
            return;
        }
        
        StateHelper.loading(tbody);
        try {
            const data = await API.get(/reports/gradebook/\);
            
            // Rebuild header
            let headers = <th>الطالب</th>;
            data.exams.forEach(e => {
                headers += <th>\ (\)</th>;
            });
            headers += <th>النسبة الإجمالية</th>;
            thead.innerHTML = headers;
            
            if (data.students.length === 0) {
                StateHelper.empty(tbody, 'لا يوجد طلاب في هذا الفصل');
                return;
            }
            
            tbody.innerHTML = data.students.map(st => {
                let row = <td>\</td>;
                data.exams.forEach(e => {
                    const score = st.scores[e.id] !== undefined ? st.scores[e.id] : '-';
                    row += <td>\</td>;
                });
                row += <td style="font-weight:bold; color: \">\%</td>;
                return <tr>\</tr>;
            }).join('');
            
        } catch(e) {
            StateHelper.error(tbody, 'خطأ في جلب السجل');
        }
    },
    
    async loadAttendance() {
        const classId = document.getElementById('report-attendance-class-select').value;
        const tbody = document.querySelector('#table-report-attendance tbody');
        
        if (!classId) {
            StateHelper.empty(tbody, 'الرجاء اختيار فصل');
            return;
        }
        
        StateHelper.loading(tbody);
        try {
            const data = await API.get(/reports/attendance/\);
            
            if (data.students.length === 0) {
                StateHelper.empty(tbody, 'لا يوجد طلاب في هذا الفصل');
                return;
            }
            
            tbody.innerHTML = data.students.map(st => {
                const att = st.attendance;
                const danger = st.absent_rate > 20 ? 'color: var(--danger-color); font-weight: bold;' : '';
                return <tr>
                    <td>\</td>
                    <td>\</td>
                    <td>\</td>
                    <td>\</td>
                    <td>\</td>
                    <td style="\">\%</td>
                </tr>;
            }).join('');
        } catch(e) {
            StateHelper.error(tbody, 'خطأ في جلب التقرير');
        }
    },
    
    async loadStuck() {
        const tbody = document.querySelector('#table-report-stuck tbody');
        StateHelper.loading(tbody);
        try {
            const data = await API.get('/reports/stuck');
            if (data.length === 0) {
                StateHelper.empty(tbody, 'لا يوجد طلاب متعثرين', null, null);
                return;
            }
            tbody.innerHTML = data.map(st => 
                <tr>
                    <td>\</td>
                    <td>\</td>
                    <td>\</td>
                    <td style="color:var(--danger-color); font-weight:bold;">\</td>
                </tr>
            ).join('');
        } catch(e) {
            StateHelper.error(tbody, 'خطأ في جلب التقرير');
        }
    },
    
    exportCSV(tableId, filename) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        let csv = [];
        const rows = table.querySelectorAll('tr');
        
        for (let i = 0; i < rows.length; i++) {
            let row = [], cols = rows[i].querySelectorAll('td, th');
            for (let j = 0; j < cols.length; j++) {
                let data = cols[j].innerText.replace(/(\\r\\n|\\n|\\r)/gm, '').replace(/"/g, '""');
                row.push('"' + data + '"');
            }
            csv.push(row.join(','));
        }
        
        const csvFile = new Blob(["\\ufeff" + csv.join('\\n')], {type: "text/csv;charset=utf-8;"});
        const downloadLink = document.createElement("a");
        downloadLink.download = filename;
        downloadLink.href = window.URL.createObjectURL(csvFile);
        downloadLink.style.display = "none";
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
    }
};

'''

content = content + '\n' + reports_js

# update loadData to populate class dropdowns
content = content.replace('''const clsLevelSelect = document.getElementById('cls-level');''', '''
        const reportClassSelect = document.getElementById('report-class-select');
        const reportAttClassSelect = document.getElementById('report-attendance-class-select');
        reportClassSelect.innerHTML = '<option value="">اختر الفصل...</option>' + classes.map(c => <option value="\">\ (\)</option>).join('');
        reportAttClassSelect.innerHTML = reportClassSelect.innerHTML;
        
        const clsLevelSelect = document.getElementById('cls-level');''')

with open('frontend/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
