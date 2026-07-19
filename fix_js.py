import re

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix ConfirmDialog
confirm_broken = r"""const ConfirmDialog = \{.*?\n\};"""
confirm_fixed = """const ConfirmDialog = {
    show(message, options = {}) {
        return new Promise((resolve) => {
            const type = options.type || 'info';
            const title = options.title || 'تأكيد';
            
            const overlay = document.createElement('div');
            overlay.className = 'confirm-overlay';
            
            const dialog = document.createElement('div');
            dialog.className = `confirm-dialog ${type}`;
            
            const icon = type === 'danger' ? '⚠️' : '❓';
            
            dialog.innerHTML = `
                <div class="confirm-icon">${icon}</div>
                <h3>${title}</h3>
                <p>${message}</p>
                <div class="confirm-actions">
                    <button class="btn-secondary" id="confirm-btn-cancel">إلغاء</button>
                    <button class="btn-${type}" id="confirm-btn-ok">تأكيد</button>
                </div>
            `;
            
            overlay.appendChild(dialog);
            document.body.appendChild(overlay);
            
            // Trigger animation
            setTimeout(() => overlay.classList.add('active'), 10);
            
            const close = (result) => {
                overlay.classList.remove('active');
                setTimeout(() => document.body.removeChild(overlay), 200);
                resolve(result);
            };
            
            dialog.querySelector('#confirm-btn-ok').onclick = () => close(true);
            dialog.querySelector('#confirm-btn-cancel').onclick = () => close(false);
            overlay.onclick = (e) => { if (e.target === overlay) close(false); };
            
            // Esc key
            const escHandler = (e) => {
                if (e.key === 'Escape') {
                    document.removeEventListener('keydown', escHandler);
                    close(false);
                }
            };
            document.addEventListener('keydown', escHandler);
            
            // Focus trap (simple)
            dialog.querySelector('#confirm-btn-cancel').focus();
        });
    }
};"""

content = re.sub(confirm_broken, lambda _: confirm_fixed, content, flags=re.DOTALL)

# Fix Validator
val_broken = r"""const Validator = \{.*?checkRequired.*?return valid;\n    \}\n\};"""
val_fixed = """const Validator = {
    checkRequired(form, fields) {
        let valid = true;
        fields.forEach(f => {
            const el = form.querySelector(`[id="${f}"]`);
            const group = el.closest('.form-group');
            if (group) group.classList.remove('has-error');
            const existErr = el.parentNode.querySelector('.field-error');
            if (existErr) existErr.remove();
            
            if (!el.value.trim()) {
                if (group) group.classList.add('has-error');
                el.insertAdjacentHTML('afterend', '<span class="field-error">هذا الحقل مطلوب</span>');
                valid = false;
            }
        });
        return valid;
    }
};"""

content = re.sub(val_broken, lambda _: val_fixed, content, flags=re.DOTALL)

# Fix StateHelper
sh_broken = r"""const StateHelper = \{.*?\}\n\};"""
sh_fixed = """const StateHelper = {
    loading(container) {
        if (typeof container === 'string') container = document.getElementById(container);
        if (!container) return;
        if (container.tagName === 'TBODY') {
            const cols = container.closest('table').querySelectorAll('th').length || 1;
            container.innerHTML = `<tr><td colspan="${cols}"><div class="state-loading"><div class="spinner"></div><p>جاري التحميل...</p></div></td></tr>`;
        } else {
            container.innerHTML = `<div class="state-loading"><div class="spinner"></div><p>جاري التحميل...</p></div>`;
        }
    },
    empty(container, message = 'لا توجد بيانات', ctaText = null, ctaAction = null) {
        if (typeof container === 'string') container = document.getElementById(container);
        if (!container) return;
        
        let html = `<div class="state-empty"><div class="state-icon">📋</div><p>${message}</p>`;
        if (ctaText && ctaAction) {
            html += `<button class="btn-primary" style="margin-top:1rem;" onclick="${ctaAction}">${ctaText}</button>`;
        }
        html += `</div>`;
        
        if (container.tagName === 'TBODY') {
            const cols = container.closest('table').querySelectorAll('th').length || 1;
            container.innerHTML = `<tr><td colspan="${cols}">${html}</td></tr>`;
        } else {
            container.innerHTML = html;
        }
    },
    error(container, message = 'حدث خطأ', retryAction = null) {
        if (typeof container === 'string') container = document.getElementById(container);
        if (!container) return;
        
        let html = `<div class="state-error"><div class="state-icon">⚠️</div><p>${message}</p>`;
        if (retryAction) {
            html += `<button class="btn-secondary" style="margin-top:1rem;" onclick="${retryAction}">إعادة المحاولة</button>`;
        }
        html += `</div>`;
        
        if (container.tagName === 'TBODY') {
            const cols = container.closest('table').querySelectorAll('th').length || 1;
            container.innerHTML = `<tr><td colspan="${cols}">${html}</td></tr>`;
        } else {
            container.innerHTML = html;
        }
    },
    clear(container) {
        if (typeof container === 'string') container = document.getElementById(container);
        if (!container) return;
        container.innerHTML = '';
    }
};"""

content = re.sub(sh_broken, lambda _: sh_fixed, content, flags=re.DOTALL)

# Fix Toast
toast_broken = r"""const Toast = \{.*?init\(\).*?show.*?\}\n\};"""
toast_fixed = """const Toast = {
    container: null,
    init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    },
    show(message, type = 'success', duration = 3000) {
        this.init();
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            'success': '✓',
            'error': '✕',
            'warning': '⚠',
            'info': 'ℹ'
        };
        
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message">${message}</span>
        `;
        
        this.container.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 10);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },
    success(msg) { this.show(msg, 'success'); },
    error(msg) { this.show(msg, 'error'); },
    warning(msg) { this.show(msg, 'warning'); },
    info(msg) { this.show(msg, 'info'); }
};"""

content = re.sub(toast_broken, lambda _: toast_fixed, content, flags=re.DOTALL)

# Fix Reports
reports_broken = r"""window\.Reports = \{.*?exportCSV.*?\}\n\};"""
reports_fixed = """window.Reports = {
    switchTab(tab) {
        document.querySelectorAll('.report-tab-btn').forEach(btn => {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-secondary');
        });
        event.target.classList.remove('btn-secondary');
        event.target.classList.add('btn-primary');
        
        document.querySelectorAll('.report-view').forEach(view => view.style.display = 'none');
        document.getElementById(`report-view-${tab}`).style.display = 'block';
        
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
            const data = await API.get(`/reports/gradebook/${classId}`);
            
            // Rebuild header
            let headers = `<th>الطالب</th>`;
            data.exams.forEach(e => {
                headers += `<th>${escapeHtml(e.title)} (${e.total_points})</th>`;
            });
            headers += `<th>النسبة الإجمالية</th>`;
            thead.innerHTML = headers;
            
            if (data.students.length === 0) {
                StateHelper.empty(tbody, 'لا يوجد طلاب في هذا الفصل');
                return;
            }
            
            tbody.innerHTML = data.students.map(st => {
                let row = `<td>${escapeHtml(st.name)}</td>`;
                data.exams.forEach(e => {
                    const score = st.scores[e.id] !== undefined ? st.scores[e.id] : '-';
                    row += `<td>${score}</td>`;
                });
                row += `<td style="font-weight:bold; color: ${st.total_percentage < 50 ? 'var(--danger-color)' : 'inherit'}">${st.total_percentage}%</td>`;
                return `<tr>${row}</tr>`;
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
            const data = await API.get(`/reports/attendance/${classId}`);
            
            if (data.students.length === 0) {
                StateHelper.empty(tbody, 'لا يوجد طلاب في هذا الفصل');
                return;
            }
            
            tbody.innerHTML = data.students.map(st => {
                const att = st.attendance;
                const danger = st.absent_rate > 20 ? 'color: var(--danger-color); font-weight: bold;' : '';
                return `<tr>
                    <td>${escapeHtml(st.name)}</td>
                    <td>${att.present}</td>
                    <td>${att.absent}</td>
                    <td>${att.late}</td>
                    <td>${att.excused}</td>
                    <td style="${danger}">${st.absent_rate}%</td>
                </tr>`;
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
            tbody.innerHTML = data.map(st => `
                <tr>
                    <td>${escapeHtml(st.name)}</td>
                    <td>${escapeHtml(st.current_level)}</td>
                    <td>${st.last_movement_date ? escapeHtml(st.last_movement_date.split('T')[0]) : '-'}</td>
                    <td style="color:var(--danger-color); font-weight:bold;">${st.days_stuck}</td>
                </tr>
            `).join('');
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
};"""

content = re.sub(reports_broken, lambda _: reports_fixed, content, flags=re.DOTALL)

# Fix Audit
audit_broken = r"""window\.Audit = \{.*?loadLogs.*?\}\n\};"""
audit_fixed = """window.Audit = {
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
                return `<tr>
                    <td dir="ltr" style="text-align:right;">${dateStr}</td>
                    <td>${escapeHtml(log.actor)}</td>
                    <td><span class="badge" style="background:var(--primary-light); color:var(--primary-hover);">${escapeHtml(log.action)}</span></td>
                    <td>${escapeHtml(log.entity_type)}</td>
                    <td>${log.entity_id}</td>
                </tr>`;
            }).join('');
        } catch(e) {
            StateHelper.error(tbody, 'خطأ في جلب السجلات');
        }
    }
};"""

content = re.sub(audit_broken, lambda _: audit_fixed, content, flags=re.DOTALL)

with open('frontend/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
