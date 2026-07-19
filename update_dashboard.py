import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Dark mode toggle
content = content.replace('<div class="user-info">', '<div class="user-info">\n                <button id="dark-toggle" class="btn-secondary btn-sm dark-toggle" style="margin-left: 10px; padding: 0.5rem; font-size: 1.2rem;">🌙</button>')

# Add new stat cards
new_cards = '''
            <div class="stat-card">
                <h3>جلسات اليوم</h3>
                <div class="value" id="stat-sessions">0</div>
            </div>
            <div class="stat-card">
                <h3>ترفيعات قيد الانتظار</h3>
                <div class="value" id="stat-promotions">0</div>
            </div>
            <div class="stat-card">
                <h3>فواتير متأخرة</h3>
                <div class="value" id="stat-invoices">0</div>
            </div>
'''
content = content.replace('<div class="value" id="stat-levels">0</div>\n            </div>', '<div class="value" id="stat-levels">0</div>\n            </div>' + new_cards)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
