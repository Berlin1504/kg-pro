import re

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Toast object
toast_obj = '''const Toast = {
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
        toast.className = 	oast toast-\;
        
        const icons = {
            'success': '✓',
            'error': '✕',
            'warning': '⚠',
            'info': 'ℹ'
        };
        
        toast.innerHTML = 
            <span class="toast-icon">\</span>
            <span class="toast-message">\</span>
            <button class="toast-close">&times;</button>
            <div class="toast-progress" style="animation-duration: \ms"></div>
        ;
        
        toast.querySelector('.toast-close').onclick = () => this.dismiss(toast);
        this.container.appendChild(toast);
        
        setTimeout(() => this.dismiss(toast), duration);
    },
    dismiss(toast) {
        toast.style.animation = 'toast-slide-out 0.3s forwards';
        setTimeout(() => { if (toast.parentNode) toast.parentNode.removeChild(toast); }, 300);
    },
    success(msg, duration) { this.show(msg, 'success', duration); },
    error(msg, duration) { this.show(msg, 'error', duration); },
    warning(msg, duration) { this.show(msg, 'warning', duration); },
    info(msg, duration) { this.show(msg, 'info', duration); }
};

'''

if 'const Toast =' not in content:
    content = toast_obj + content

# Replace alerts
def replace_alert(match):
    msg = match.group(1)
    # Heuristic: if message contains 'خطأ' or 'Error' or 'failed', it's an error
    if 'خطأ' in msg or 'Error' in msg or 'failed' in msg.lower() or 'err.' in msg.lower():
        return f"Toast.error({msg})"
    else:
        return f"Toast.success({msg})"

# regex to find alert(...)
content = re.sub(r'alert\((.*?)\)', replace_alert, content)

with open('frontend/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
