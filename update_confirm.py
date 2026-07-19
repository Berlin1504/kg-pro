import re

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

confirm_obj = '''const ConfirmDialog = {
    show(message, options = {}) {
        return new Promise((resolve) => {
            const type = options.type || 'info';
            const title = options.title || 'تأكيد';
            
            const overlay = document.createElement('div');
            overlay.className = 'confirm-overlay';
            
            const dialog = document.createElement('div');
            dialog.className = confirm-dialog \;
            
            const icon = type === 'danger' ? '⚠️' : '❓';
            
            dialog.innerHTML = 
                <div class="confirm-icon">\</div>
                <h3>\</h3>
                <p>\</p>
                <div class="confirm-actions">
                    <button class="btn-secondary" id="confirm-btn-cancel">إلغاء</button>
                    <button class="btn-\" id="confirm-btn-ok">تأكيد</button>
                </div>
            ;
            
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
};

'''

if 'const ConfirmDialog =' not in content:
    content = content.replace('const Toast = {', confirm_obj + 'const Toast = {')

# Make downloadBackup async
content = content.replace('downloadBackup() {', 'async downloadBackup() {')
content = content.replace('uploadBackup(inputElem) {', 'async uploadBackup(inputElem) {')

# Replace confirms manually
content = re.sub(r"if\s*\(\!confirm\((.*?)\)\)\s*return;", r"if (!(await ConfirmDialog.show(\1, {type: 'danger'}))) return;", content)
content = re.sub(r"if\s*\(\!confirm\((.*?)\)\)\s*\{", r"if (!(await ConfirmDialog.show(\1, {type: 'danger'}))) {", content)

with open('frontend/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
