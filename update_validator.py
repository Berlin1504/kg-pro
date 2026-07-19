import re

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Validator object
validator_obj = '''const Validator = {
    checkRequired(form, fields) {
        let valid = true;
        fields.forEach(f => {
            const el = form.querySelector([id="\"]);
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
};

'''

if 'const Validator =' not in content:
    content = content.replace('const StateHelper = {', validator_obj + 'const StateHelper = {')


# Dark Mode toggle logic
dark_mode_logic = '''
    const darkToggle = document.getElementById('dark-toggle');
    if (localStorage.getItem('theme') === 'dark') {
        document.documentElement.classList.add('dark');
        darkToggle.textContent = '☀️';
    }
    darkToggle.addEventListener('click', () => {
        document.documentElement.classList.toggle('dark');
        if (document.documentElement.classList.contains('dark')) {
            localStorage.setItem('theme', 'dark');
            darkToggle.textContent = '☀️';
        } else {
            localStorage.setItem('theme', 'light');
            darkToggle.textContent = '🌙';
        }
    });
'''

if "localStorage.getItem('theme')" not in content:
    content = content.replace("const dashboardView = document.getElementById('dashboard-view');", "const dashboardView = document.getElementById('dashboard-view');\n" + dark_mode_logic)


# Populate new stats in loadData
stat_logic = '''
        try {
            const res = await fetch('/sessions/');
            const sessions = await res.json();
            const today = new Date().toISOString().split('T')[0];
            const todaySessions = Array.isArray(sessions) ? sessions.filter(s => s.date.startsWith(today)) : [];
            document.getElementById('stat-sessions').textContent = todaySessions.length;
        } catch(e) {}
        
        try {
            const res = await fetch('/finance/dashboard');
            const data = await res.json();
            document.getElementById('stat-invoices').textContent = (data.overdue_invoices_count || 0);
        } catch(e) {}
        
        try {
            const res = await fetch('/promotions/');
            const data = await res.json();
            const pending = Array.isArray(data) ? data.filter(p => p.status === 'pending') : [];
            document.getElementById('stat-promotions').textContent = pending.length;
        } catch(e) {}
'''

# insert before '// Render Subjects'
content = content.replace('// Render Subjects', stat_logic + '\n        // Render Subjects')

with open('frontend/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
