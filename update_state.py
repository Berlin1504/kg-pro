import re

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

state_obj = '''const StateHelper = {
    loading(container) {
        if (typeof container === 'string') container = document.getElementById(container);
        if (!container) return;
        if (container.tagName === 'TBODY') {
            const cols = container.closest('table').querySelectorAll('th').length || 1;
            container.innerHTML = <tr><td colspan="\"><div class="state-loading"><div class="spinner"></div><p>جاري التحميل...</p></div></td></tr>;
        } else {
            container.innerHTML = <div class="state-loading"><div class="spinner"></div><p>جاري التحميل...</p></div>;
        }
    },
    empty(container, message = 'لا توجد بيانات', ctaText = null, ctaAction = null) {
        if (typeof container === 'string') container = document.getElementById(container);
        if (!container) return;
        
        let html = <div class="state-empty"><div class="state-icon">📋</div><p>\</p>;
        if (ctaText && ctaAction) {
            html += <button class="btn-primary" style="margin-top:1rem;" onclick="\">\</button>;
        }
        html += </div>;
        
        if (container.tagName === 'TBODY') {
            const cols = container.closest('table').querySelectorAll('th').length || 1;
            container.innerHTML = <tr><td colspan="\">\</td></tr>;
        } else {
            container.innerHTML = html;
        }
    },
    error(container, message = 'حدث خطأ', retryAction = null) {
        if (typeof container === 'string') container = document.getElementById(container);
        if (!container) return;
        
        let html = <div class="state-error"><div class="state-icon">⚠️</div><p>\</p>;
        if (retryAction) {
            html += <button class="btn-secondary" style="margin-top:1rem;" onclick="\">إعادة المحاولة</button>;
        }
        html += </div>;
        
        if (container.tagName === 'TBODY') {
            const cols = container.closest('table').querySelectorAll('th').length || 1;
            container.innerHTML = <tr><td colspan="\">\</td></tr>;
        } else {
            container.innerHTML = html;
        }
    },
    clear(container) {
        if (typeof container === 'string') container = document.getElementById(container);
        if (!container) return;
        container.innerHTML = '';
    }
};

'''

if 'const StateHelper =' not in content:
    content = content.replace('const Toast = {', state_obj + 'const Toast = {')

with open('frontend/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
