import re

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

audit_js = '''
window.Audit = {
    async loadLogs() {
        const tbody = document.querySelector('#table-audit tbody');
        StateHelper.loading(tbody);
        try {
            const data = await API.get('/audit/');
            if (data.length === 0) {
                StateHelper.empty(tbody, 'لا توجد سجلات');
                return;
            }
            tbody.innerHTML = data.map(log => {
                const dateObj = new Date(log.created_at);
                const dateStr = dateObj.toLocaleDateString('ar-SA') + ' ' + dateObj.toLocaleTimeString('ar-SA');
                return <tr>
                    <td dir="ltr" style="text-align:right;">\</td>
                    <td>\</td>
                    <td><span class="badge" style="background:var(--primary-light); color:var(--primary-hover);">\</span></td>
                    <td>\</td>
                    <td>\</td>
                </tr>;
            }).join('');
        } catch(e) {
            StateHelper.error(tbody, 'خطأ في جلب السجلات');
        }
    }
};
'''

content = content + '\n' + audit_js

# update showDashboard to show nav-audit if boss
content = content.replace("document.getElementById('nav-promotions').style.display = 'block';", "document.getElementById('nav-promotions').style.display = 'block';\n        if (user.role === 'boss') document.getElementById('nav-audit').style.display = 'block';")

# Call Audit.loadLogs in loadData if boss
content = content.replace("try { await loadPromotions(); } catch(e){}", "try { await loadPromotions(); } catch(e){}\n            try { await Audit.loadLogs(); } catch(e){}")

with open('frontend/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
