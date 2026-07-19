import re

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# loadData injections
content = content.replace('async function loadData() {\n    try {', '''async function loadData() {
    StateHelper.loading(document.querySelector('#table-subjects tbody'));
    StateHelper.loading(document.querySelector('#table-levels tbody'));
    StateHelper.loading(document.querySelector('#table-classes tbody'));
    StateHelper.loading(document.querySelector('#table-students tbody'));
    try {''')

content = content.replace('''const subjBody = document.querySelector('#table-subjects tbody');
        subjBody.innerHTML = subjects.map(s => {''', '''const subjBody = document.querySelector('#table-subjects tbody');
        if (subjects.length === 0) StateHelper.empty(subjBody, 'لا توجد مواد مضافة');
        else subjBody.innerHTML = subjects.map(s => {''')

content = content.replace('''const lvlBody = document.querySelector('#table-levels tbody');
        lvlBody.innerHTML = levels.map(l => {''', '''const lvlBody = document.querySelector('#table-levels tbody');
        if (levels.length === 0) StateHelper.empty(lvlBody, 'لا توجد مستويات مضافة');
        else lvlBody.innerHTML = levels.map(l => {''')

content = content.replace('''const clsBody = document.querySelector('#table-classes tbody');
        clsBody.innerHTML = classes.map(c => {''', '''const clsBody = document.querySelector('#table-classes tbody');
        if (classes.length === 0) StateHelper.empty(clsBody, 'لا توجد فصول مضافة');
        else clsBody.innerHTML = classes.map(c => {''')

# students is rendered by renderStudents(students, classes) but loadData calls it
content = content.replace('''window.renderStudents(students, classes);''', '''if (students.length === 0) StateHelper.empty(document.querySelector('#table-students tbody'), 'لا يوجد طلاب مسجلين');
        else window.renderStudents(students, classes);''')


# TreeUI
content = content.replace('''window.TreeUI = {
    async loadSchoolTree() {
        const container = document.getElementById('school-tree-container');
        if (!window.allLevels || !window.allClasses) {
            container.innerHTML = '<p class="text-muted" style="padding: 1rem;">جاري التحميل...</p>';
            return;
        }''', '''window.TreeUI = {
    async loadSchoolTree() {
        const container = document.getElementById('school-tree-container');
        if (!window.allLevels || !window.allClasses) {
            StateHelper.loading(container);
            return;
        }
        if (window.allLevels.length === 0) {
            StateHelper.empty(container, 'لم يتم إعداد الهيكل الدراسي بعد');
            return;
        }''')

# Sessions
content = content.replace('''const container = document.getElementById('sessions-list');
        try {
            const sessions = await API.get('/sessions/');''', '''const container = document.getElementById('sessions-list');
        StateHelper.loading(container);
        try {
            const sessions = await API.get('/sessions/');
            if (sessions.length === 0) {
                StateHelper.empty(container, 'لا توجد جلسات لهذا اليوم');
                return;
            }''')

with open('frontend/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
