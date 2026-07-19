function formatCurrency(amount) {
    const num = parseFloat(amount);
    if (isNaN(num)) return "0 ج.م";
    return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' ج.م';
}

const ConfirmDialog = {
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
};

const Validator = {
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
};

const StateHelper = {
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
};

const Toast = {
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
};

const getRoleName = (role) => {
    const names = { 'boss': 'المدير العام', 'moneyman': 'المحاسب', 'supervisor': 'مشرف', 'teacher': 'معلم' };
    return names[role] || role;
};

const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
}[char]));
const jsArg = (value) => escapeHtml(JSON.stringify(String(value ?? '')));

document.addEventListener('DOMContentLoaded', async () => {
    const loginView = document.getElementById('login-view');
    const dashboardView = document.getElementById('dashboard-view');

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

    
    // Check auth on load
    try {
        const user = await API.getMe();
        showDashboard(user);
        await loadData();
    } catch (e) {
        showLogin();
    }

    // Login Form
    const loginForm = document.getElementById('login-form');
    
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('login-error');
        
        try {
            errorDiv.textContent = '';
            const data = await API.login(email, password);
            showDashboard(data.user);
            await loadData();
        } catch (err) {
            errorDiv.textContent = err.message;
        }
    });

    // Logout
    document.getElementById('logout-btn').addEventListener('click', async () => {
        await API.logout();
        showLogin();
    });



    // Navigation
    const navBtns = document.querySelectorAll('#main-nav .nav-btn');
    const panels = document.querySelectorAll('.panel');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            navBtns.forEach(b => b.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));
            
            btn.classList.add('active');
            const targetPanel = document.getElementById(btn.dataset.target);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
            
            if (btn.id === 'nav-finance') {
                FinanceUI.showTab('finance-income', document.querySelector('.finance-nav-btn'));
            }
            if (btn.id === 'nav-exams') {
                loadExams();
            }
            
            // Mobile Grid Logic
            if (window.innerWidth <= 768) {
                document.body.classList.add('mobile-panel-active');
                document.body.classList.remove('mobile-grid-active');
            }
        });
    });

    function showLogin() {
        dashboardView.classList.remove('active');
        loginView.classList.add('active');
    }

    function showDashboard(user) {
        loginView.classList.remove('active');
        dashboardView.classList.add('active');
        
        document.getElementById('user-name').textContent = user.name;
        document.getElementById('user-role-label').textContent = getRoleName(user.role);
        
        document.getElementById('user-name').textContent = user.name;
        document.getElementById('user-role-label').textContent = getRoleName(user.role);
        document.getElementById('user-avatar').textContent = user.name.charAt(0);
        
        // Sync mobile welcome card
        const mobileGridName = document.getElementById('mobile-grid-name');
        if (mobileGridName) mobileGridName.textContent = user.name.split(' ')[0]; // First name only
        const mobileGridAvatar = document.getElementById('mobile-grid-avatar');
        if (mobileGridAvatar) mobileGridAvatar.textContent = user.name.charAt(0);

        
        window.currentUser = user; // Store for later access control checks
        
        const role = user.role;
        const isBoss = (role === 'boss');
        const isSupervisor = (role === 'supervisor');
        const isMoneyman = (role === 'moneyman');
        const isTeacher = (role === 'teacher');

        const setDisplay = (id, condition) => {
            const el = document.getElementById(id);
            if(el) el.style.display = condition ? 'block' : 'none';
        };
        const setInlineDisplay = (id, condition) => {
            const el = document.getElementById(id);
            if(el) el.style.display = condition ? 'inline-block' : 'none';
        };

        // Navigation Tabs Visibility
        setDisplay('nav-tree', isBoss || isSupervisor);
        setDisplay('nav-classes', isBoss || isSupervisor || isTeacher);
        setDisplay('nav-students', true);
        setDisplay('nav-exams', isBoss || isSupervisor || isTeacher);
        setDisplay('nav-staff', isBoss);
        setDisplay('nav-promotions', isBoss || isSupervisor);
        setDisplay('nav-finance', isBoss || isMoneyman);
        setDisplay('nav-reports', isBoss || isSupervisor || isMoneyman);
        setDisplay('nav-audit', isBoss);
        setDisplay('nav-settings', isBoss);

        // Action Buttons
        ['btn-add-class', 'btn-add-student', 'btn-add-subject', 'btn-add-level'].forEach(id => {
            setInlineDisplay(id, isBoss || isSupervisor);
        });

        setInlineDisplay('btn-add-exam', isBoss || isSupervisor || isTeacher);
        setInlineDisplay('btn-add-staff', isBoss);
        
        // Settings Cards
        setDisplay('settings-institution-card', isBoss);
        setDisplay('settings-db-card', isBoss);
        setDisplay('settings-fee-templates-card', isBoss);
        
        // Dashboard Stats
        setDisplay('boss-stat-invoices', isBoss);
        setDisplay('boss-stat-promotions', isBoss);
    }


    // --- FORM HANDLERS ---
    document.getElementById('form-subject').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('subj-id').value;
        const payload = {
            name_ar: document.getElementById('subj-name').value,
            description: document.getElementById('subj-desc').value,
            promotion_threshold: parseInt(document.getElementById('subj-promo-threshold').value) || 75
        };
        try {
            if (id) {
                await API.put(`/subjects/${id}`, payload);
                Toast.success('تم التعديل بنجاح');
            } else {
                await API.post('/subjects/', payload);
                Toast.success('تمت الإضافة بنجاح');
            }
            UI.closeModal('modal-subject');
            await loadData();
        } catch (err) {
            Toast.error(err.message || 'حدث خطأ');
        }
    });

    document.getElementById('form-level').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('lvl-id').value;
        const payload = {
            name_ar: document.getElementById('lvl-name').value,
            code: document.getElementById('lvl-code').value,
            order_index: parseInt(document.getElementById('lvl-order').value),
            subject_id: parseInt(document.getElementById('lvl-subject-id').value) || null
        };
        
        try {
            if (id) {
                await API.put(`/levels/${id}`, payload);
                Toast.success('تم التعديل بنجاح');
            } else {
                await API.post('/levels/', payload);
                Toast.success('تمت الإضافة بنجاح');
            }
            UI.closeModal('modal-level');
            await loadData();
        } catch (err) {
            Toast.error(err.message || 'حدث خطأ');
        }
    });

    document.getElementById('form-class').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('cls-id').value;
        const capacityInput = document.getElementById('cls-capacity');
        const statusInput = document.getElementById('cls-status');
        const teacherInput = document.getElementById('cls-teacher');
        const payload = {
            name_ar: document.getElementById('cls-name').value,
            level_id: parseInt(document.getElementById('cls-level').value),
            group_label: document.getElementById('cls-group').value,
            capacity: capacityInput && capacityInput.value ? parseInt(capacityInput.value) : 30,
            status: statusInput ? statusInput.value : 'active',
            teacher_id: teacherInput && teacherInput.value ? parseInt(teacherInput.value) : null
        };
        
        try {
            if (id) {
                await API.put(`/classes/${id}`, payload);
                Toast.success('تم التعديل بنجاح');
            } else {
                await API.post('/classes/', payload);
                Toast.success('تمت الإضافة بنجاح');
            }
            UI.closeModal('modal-class');
            await loadData();
        } catch (err) {
            Toast.error(err.message || 'حدث خطأ');
        }
    });

    document.getElementById('form-student').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('stu-edit-id').value;
        const payload = {
            full_name_ar: document.getElementById('stu-name').value,
            dob: document.getElementById('stu-dob').value || null,
            address: document.getElementById('stu-address').value || null,
            father_phone: document.getElementById('stu-father-phone').value || null,
            mother_phone: document.getElementById('stu-mother-phone').value || null
        };
        
        try {
            if (id) {
                await API.put(`/students/${id}`, payload);
                Toast.success('تم التعديل بنجاح');
            } else {
                await API.post('/students/', payload);
                Toast.success('تمت الإضافة بنجاح');
            }
            UI.closeModal('modal-student');
            await loadData();
        } catch (err) {
            Toast.error(err.message || 'حدث خطأ');
        }
    });

    document.getElementById('form-enroll').addEventListener('submit', async (e) => {
        e.preventDefault();
        const sid = document.getElementById('enroll-student-id').value;
        const cid = document.getElementById('enroll-class-id').value;
        
        // Collect subject levels
        const subjectLevels = [];
        const container = document.getElementById('enroll-subject-levels-list');
        const selects = container.querySelectorAll('select');
        selects.forEach(select => {
            if(select.value) {
                subjectLevels.push({
                    subject_id: parseInt(select.dataset.subjectId),
                    level_id: parseInt(select.value)
                });
            }
        });
        
        try {
            const res = await API.post(`/students/${sid}/enroll`, { 
                class_id: parseInt(cid),
                subject_levels: subjectLevels.length > 0 ? subjectLevels : null
            });
            
            UI.closeModal('modal-enroll');
            await loadData();
            
            // Open the generated certificate in a new tab
            if(res.certificate_id) {
                window.open(`/api/certificates/${res.certificate_id}`, '_blank');
            }
        } catch (err) {
            Toast.error(err.message || 'Error enrolling student');
        }
    });

    // Add/Edit Staff form
    document.getElementById('form-staff').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('staff-id').value;
        const classCheckboxes = document.querySelectorAll('#staff-classes-checkboxes input[type="checkbox"]:checked');
        const class_ids = Array.from(classCheckboxes).map(cb => parseInt(cb.value));
        
        const data = {
            full_name_ar: document.getElementById('staff-name').value,
            email: document.getElementById('staff-email').value,
            role: document.getElementById('staff-role').value,
            phone: document.getElementById('staff-phone').value || null,
            base_salary: parseFloat(document.getElementById('staff-base-salary').value) || 0.0,
            class_ids: class_ids
        };
        try {
            if (id) {
                await StaffAPI.update(id, data);
                Toast.success('تم تحديث بيانات الموظف بنجاح');
            } else {
                data.password = document.getElementById('staff-password').value;
                await StaffAPI.create(data);
                Toast.success('تم إضافة الموظف بنجاح');
            }
            UI.closeModal('modal-staff');
            await loadData();
        } catch (err) {
            Toast.error(err.message);
        }
    });

    // Change password form
    document.getElementById('form-change-password').addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            await StaffAPI.changePassword(
                document.getElementById('cp-staff-id').value,
                document.getElementById('cp-new-password').value
            );
            UI.closeModal('modal-change-password');
            Toast.success('تم تغيير كلمة المرور بنجاح');
        } catch (err) {
            Toast.error(err.message);
        }
    });

    // Settings form
    document.getElementById('form-settings').addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            await SettingsAPI.update({
                institution_name: document.getElementById('setting-institution-name').value
            });
            Toast.success('تم حفظ الإعدادات بنجاح');
        } catch (err) {
            Toast.error(err.message);
        }
    });

    const accountForm = document.getElementById('form-update-account');
    if (accountForm) {
        accountForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                await API.put('/me/update', {
                    current_password: document.getElementById('account-current-password').value,
                    new_email: document.getElementById('account-new-email').value || null,
                    new_password: document.getElementById('account-new-password').value || null
                });
                Toast.success('تم تحديث بيانات الحساب بنجاح');
                accountForm.reset();
            } catch (err) {
                Toast.error(err.message);
            }
        });
    }

    // Manual Level form

});

// Duplicate getRoleName removed
// --- GLOBAL UI HELPERS ---
window.UI = {
    activeModalId: null,
    async onEnrollClassChange() {
        const classId = document.getElementById('enroll-class-id').value;
        const container = document.getElementById('enroll-subject-levels-container');
        const listContainer = document.getElementById('enroll-subject-levels-list');
        
        if (!classId) {
            container.style.display = 'none';
            return;
        }
        
        try {
            const cls = window.allClasses.find(c => c.id == classId);
            if (!cls) return;
            
            let html = '';
            window.allSubjects.forEach(subject => {
                const subjectLevels = window.allLevels.filter(l => l.subject_id === subject.id);
                subjectLevels.sort((a, b) => a.order_index - b.order_index);
                
                let options = '<option value="">المستوى الأول (تلقائي)</option>';
                subjectLevels.forEach(l => {
                    options += `<option value="${l.id}">${escapeHtml(l.name_ar)}</option>`;
                });
                
                html += `
                    <div class="form-group mb-2">
                        <label style="font-size: 0.9rem; margin-bottom: 0.2rem;">${escapeHtml(subject.name_ar)}</label>
                        <select class="enroll-subject-level-select" data-subject-id="${subject.id}" style="padding: 0.4rem;">
                            ${options}
                        </select>
                    </div>
                `;
            });
            
            if (window.allSubjects.length > 0) {
                listContainer.innerHTML = html;
                container.style.display = 'block';
            } else {
                container.style.display = 'none';
            }
            
        } catch (e) {
            console.error('Error fetching subjects for enrollment', e);
        }
    },
    onManualLevelSubjectChange() {
        const subjectId = document.getElementById('manual-lvl-subject-id').value;
        const levelSelect = document.getElementById('manual-lvl-level-id');
        if (!subjectId) {
            levelSelect.innerHTML = '<option value="">اختر المادة أولاً...</option>';
            return;
        }
        
        const subjectLevels = window.allLevels.filter(l => l.subject_id == subjectId);
        subjectLevels.sort((a, b) => a.order_index - b.order_index);
        
        if (subjectLevels.length === 0) {
            levelSelect.innerHTML = '<option value="">لا توجد مستويات لهذه المادة</option>';
            return;
        }
        
        levelSelect.innerHTML = subjectLevels.map(l => `<option value="${l.id}">${escapeHtml(l.name_ar)}</option>`).join('');
    },
    handleEsc(e) {
        if (e.key === 'Escape' && window.UI.activeModalId) {
            window.UI.closeModal(window.UI.activeModalId);
        }
    },
    openModal(id) {
        const modal = document.getElementById(id);
        if (!modal) return;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        window.UI.activeModalId = id;
        
        document.addEventListener('keydown', window.UI.handleEsc);
        
        modal.onclick = (e) => {
            if (e.target === modal) {
                window.UI.closeModal(id);
            }
        };
        
        const focusable = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (focusable.length) {
            setTimeout(() => focusable[0].focus(), 100);
        }
    },
    closeModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.classList.remove('active');
        document.body.style.overflow = '';
        window.UI.activeModalId = null;
        document.removeEventListener('keydown', window.UI.handleEsc);
        
        const form = document.querySelector(`#${id} form`);
        if (form) {
            form.reset();
            form.querySelectorAll('input[type="hidden"]').forEach(input => input.value = '');
            form.querySelectorAll('.field-error').forEach(err => err.remove());
            form.querySelectorAll('.has-error').forEach(el => el.classList.remove('has-error'));
        }
    },
    switchProfileTab(tab, e) {
        document.querySelectorAll('.profile-tab').forEach(el => el.style.display = 'none');
        document.querySelectorAll('#modal-student-profile .nav-btn').forEach(el => el.classList.remove('active'));
        document.getElementById(`ptab-${tab}`).style.display = 'block';
        if (e && e.target) {
            e.target.classList.add('active');
        } else if (window.event && window.event.target) {
            window.event.target.classList.add('active');
        }
        
        const studentId = document.getElementById('profile-student-id').value;
        if (studentId) {
            if (tab === 'finance') {
                loadStudentFinance(studentId);
            } else if (tab === 'certificates') {
                loadStudentCertificates(studentId);
            }
        }
    }
};

window.RoadmapUI = {
    showPanel() {
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        document.getElementById('panel-roadmaps').classList.add('active');
        this.render();
    },
    hidePanel() {
        document.getElementById('panel-roadmaps').classList.remove('active');
        document.getElementById('panel-settings').classList.add('active');
    },
    render() {
        const container = document.getElementById('roadmap-container');
        if (!window.allLevels || !window.allSubjects) {
            StateHelper.loading(container);
            return;
        }
        
        if (window.allSubjects.length === 0) {
            StateHelper.empty(container, 'لم يتم إضافة أي مواد بعد');
            return;
        }
        
        let html = '<div class="roadmaps-wrapper">';
        
        window.allSubjects.forEach(subject => {
            const subjectLevels = window.allLevels.filter(l => l.subject_id === subject.id);
            if (subjectLevels.length === 0) return;
            
            // Sort levels by order_index, or by looking at next_level_id chains
            subjectLevels.sort((a, b) => (a.order_index || 0) - (b.order_index || 0));
            
            html += `
            <div class="roadmap-subject-row">
                <div class="roadmap-subject-title">
                    <h4>${escapeHtml(subject.name_ar)}</h4>
                </div>
                <div class="roadmap-nodes" dir="ltr" style="justify-content: flex-start;">
            `;
            
            subjectLevels.forEach((level, index) => {
                html += `
                    <div class="roadmap-node">
                        <div class="roadmap-node-circle">${index + 1}</div>
                        <div class="roadmap-node-label">${escapeHtml(level.name_ar)}</div>
                        <div class="roadmap-node-code">${escapeHtml(level.code || '')}</div>
                    </div>
                `;
                
                if (index < subjectLevels.length - 1) {
                    html += `<div class="roadmap-arrow">&#10230;</div>`;
                }
            });
            
            html += `
                </div>
            </div>
            `;
        });
        
        html += '</div>';
        
        if (html === '<div class="roadmaps-wrapper"></div>') {
            StateHelper.empty(container, 'لا توجد مستويات مرتبطة بالمواد حتى الآن');
        } else {
            container.innerHTML = html;
        }
    }
};

window.TreeUI = {
    async loadSchoolTree() {
        const container = document.getElementById('school-tree-container');
        if (!window.allLevels || !window.allClasses) {
            StateHelper.loading(container);
            return;
        }
        if (window.allLevels.length === 0) {
            StateHelper.empty(container, 'لم يتم إعداد الهيكل الدراسي بعد');
            return;
        }
        
        // Render tree
        container.innerHTML = window.allLevels.map(level => {
            const levelClasses = window.allClasses.filter(c => c.level_id === level.id);
            return `
                <div class="tree-level-card">
                    <div class="tree-header flex-between" onclick="TreeUI.toggleLevel(${level.id})">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
                            <h3 style="margin:0;">${escapeHtml(level.name_ar)}</h3>
                        </div>
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <span class="text-muted" style="font-size: 0.9rem;">${levelClasses.length} فصول</span>
                            <svg class="chevron chevron-level-${level.id}" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="transition: transform 0.3s ease;"><polyline points="6 9 12 15 18 9"></polyline></svg>
                        </div>
                    </div>
                    <div class="tree-content" id="tree-level-content-${level.id}" style="display: none;">
                        ${levelClasses.length === 0 ? '<p class="text-muted" style="padding: 1rem;">لا توجد فصول في هذا المستوى</p>' : ''}
                        ${levelClasses.map(cls => `
                            <div class="tree-class-card">
                                <div class="tree-header flex-between" onclick="TreeUI.toggleClass(${cls.id})">
                                    <div style="display: flex; align-items: center; gap: 10px;">
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                                        <strong style="font-size: 1.05rem;">${escapeHtml(cls.name_ar)} (${escapeHtml(cls.group_label)})</strong>
                                    </div>
                                    <div style="display: flex; align-items: center; gap: 15px;">
                                        <span class="text-muted" style="font-size: 0.85rem;">${cls.roster_count || 0}/${cls.capacity}</span>
                                        <svg class="chevron chevron-class-${cls.id}" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="transition: transform 0.3s ease;"><polyline points="6 9 12 15 18 9"></polyline></svg>
                                    </div>
                                </div>
                                <div class="tree-content" id="tree-class-content-${cls.id}" style="display: none;">
                                    <div class="loader-spinner" id="loader-class-${cls.id}" style="display: none; padding: 1rem; text-align: center; color: var(--primary-color);">جاري التحميل...</div>
                                    <div class="tree-students-list" id="students-list-${cls.id}"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }).join('');
    },
    
    toggleLevel(levelId) {
        const content = document.getElementById(`tree-level-content-${levelId}`);
        const chevron = document.querySelector(`.chevron-level-${levelId}`);
        if (content.style.display === 'none') {
            content.style.display = 'block';
            chevron.style.transform = 'rotate(180deg)';
        } else {
            content.style.display = 'none';
            chevron.style.transform = 'rotate(0deg)';
        }
    },
    
    async toggleClass(classId) {
        const content = document.getElementById(`tree-class-content-${classId}`);
        const chevron = document.querySelector(`.chevron-class-${classId}`);
        const studentsList = document.getElementById(`students-list-${classId}`);
        const loader = document.getElementById(`loader-class-${classId}`);
        
        if (content.style.display === 'none') {
            content.style.display = 'block';
            chevron.style.transform = 'rotate(180deg)';
            
            // Lazy load students if empty
            if (studentsList.innerHTML === '') {
                loader.style.display = 'block';
                try {
                    const roster = await ProfileAPI.getClassRoster(classId);
                    if (roster.length === 0) {
                        studentsList.innerHTML = '<p class="text-muted" style="padding: 1rem;">لا يوجد طلاب في هذا الفصل</p>';
                    } else {
                        studentsList.innerHTML = roster.map(item => {
                            const sJson = JSON.stringify(item.student).replace(/"/g, '&quot;');
                            return `
                                <div class="tree-student-card flex-between" onclick="window.openStudentProfile(event, ${sJson})">
                                    <div style="display: flex; align-items: center; gap: 10px;">
                                        <div class="avatar" style="width: 32px; height: 32px; font-size: 0.9rem; line-height: 32px;">
                                            ${item.student.full_name_ar.charAt(0)}
                                        </div>
                                        <span>${escapeHtml(item.student.full_name_ar)}</span>
                                    </div>
                                    <span class="text-muted" style="font-size: 0.8rem;">رقم: ${item.student.id}</span>
                                </div>
                            `;
                        }).join('');
                    }
                } catch (e) {
                    studentsList.innerHTML = '<p class="text-danger" style="padding: 1rem;">فشل تحميل بيانات الطلاب</p>';
                } finally {
                    loader.style.display = 'none';
                }
            }
        } else {
            content.style.display = 'none';
            chevron.style.transform = 'rotate(0deg)';
        }
    }
};

window.deactivateStaff = async (id, name) => {
    if (!(await ConfirmDialog.show(`هل تريد إلغاء تفعيل حساب ${name}؟`, {type: 'danger'}))) return;
    try {
        await StaffAPI.deactivate(id);
        Toast.success('تم إلغاء تفعيل الموظف');
        await loadData();
    } catch (err) {
        Toast.error(err.message);
    }
};

async function populateStaffClasses(selectedIds = []) {
    const container = document.getElementById('staff-classes-checkboxes');
    container.innerHTML = 'جاري التحميل...';
    try {
        const classes = await API.get('/classes/');
        if (!classes || classes.length === 0) {
            container.innerHTML = 'لا توجد فصول متاحة.';
            return;
        }
        container.innerHTML = classes.map(cls => `
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                <input type="checkbox" id="scb-${cls.id}" value="${cls.id}" ${selectedIds.includes(cls.id) ? 'checked' : ''}>
                <label for="scb-${cls.id}" style="margin: 0;">${cls.name_ar} ${cls.group_label ? `(${cls.group_label})` : ''}</label>
            </div>
        `).join('');
    } catch(err) {
        container.innerHTML = 'خطأ في تحميل الفصول.';
        console.error('Failed to load classes for staff form', err);
    }
}

document.getElementById('staff-role').addEventListener('change', (e) => {
    const group = document.getElementById('staff-classes-group');
    if (e.target.value === 'teacher') {
        group.style.display = 'block';
    } else {
        group.style.display = 'none';
    }
});



window.PairingCard = {
    render: () => {
        const card = document.getElementById('card-pair-classes');
        if (!window.currentUser || window.currentUser.role !== 'boss') {
            card.style.display = 'none';
            return;
        }
        card.style.display = 'block';

        const teacherSelect = document.getElementById('pair-card-teacher-select');
        const teachers = (window.StaffList || []).filter(s => s.role === 'teacher' && s.status === 'active');
        teacherSelect.innerHTML = '<option value="">اختر معلماً...</option>' + 
            teachers.map(t => `<option value="${t.id}">${escapeHtml(t.full_name_ar)}</option>`).join('');

        const classesContainer = document.getElementById('pair-card-classes-container');
        const classes = window.ClassesList || [];
        if (classes.length === 0) {
            classesContainer.innerHTML = '<div class="text-muted">لا توجد فصول متاحة.</div>';
        } else {
            classesContainer.innerHTML = classes.map(cls => `
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <input type="checkbox" id="pair-cb-${cls.id}" value="${cls.id}" class="pair-class-checkbox">
                    <label for="pair-cb-${cls.id}" style="margin: 0;">${escapeHtml(cls.name_ar)} ${cls.group_label ? `(${escapeHtml(cls.group_label)})` : ''}</label>
                </div>
            `).join('');
        }
        
        document.getElementById('pair-card-classes-group').style.display = 'none';
        document.getElementById('btn-save-pairing').disabled = true;
    },
    onTeacherSelect: () => {
        const teacherId = parseInt(document.getElementById('pair-card-teacher-select').value);
        const classesGroup = document.getElementById('pair-card-classes-group');
        const saveBtn = document.getElementById('btn-save-pairing');
        
        if (!teacherId) {
            classesGroup.style.display = 'none';
            saveBtn.disabled = true;
            return;
        }

        const teacher = window.StaffList.find(s => s.id === teacherId);
        const selectedIds = teacher ? (teacher.class_ids || []) : [];

        document.querySelectorAll('.pair-class-checkbox').forEach(cb => {
            cb.checked = selectedIds.includes(parseInt(cb.value));
        });

        classesGroup.style.display = 'block';
        saveBtn.disabled = false;
    },
    save: async (e) => {
        e.preventDefault();
        const teacherId = parseInt(document.getElementById('pair-card-teacher-select').value);
        if (!teacherId) return;

        const checkboxes = document.querySelectorAll('.pair-class-checkbox:checked');
        const class_ids = Array.from(checkboxes).map(cb => parseInt(cb.value));
        
        const saveBtn = document.getElementById('btn-save-pairing');
        saveBtn.disabled = true;
        saveBtn.innerText = 'جاري الحفظ...';

        try {
            await API.put(`/staff/${teacherId}/classes`, { class_ids });
            loadData();
            alert('تم حفظ الإقران بنجاح');
            // The table and staff list will be re-fetched by loadData(),
            // and PairingCard.render() will be called again to reset the form.
        } catch (err) {
            console.error('Failed to save pairing', err);
            alert('حدث خطأ أثناء حفظ الإقران');
        } finally {
            saveBtn.disabled = false;
            saveBtn.innerText = 'حفظ الإقران';
        }
    }
};

window.openEditStaffModal = async (staff) => {
    document.getElementById('staff-id').value = staff.id;
    document.getElementById('staff-name').value = staff.full_name_ar;
    document.getElementById('staff-email').value = staff.email;
    document.getElementById('staff-phone').value = staff.phone || '';
    document.getElementById('staff-role').value = staff.role;
    document.getElementById('staff-base-salary').value = staff.base_salary || 0.0;
    document.getElementById('staff-password-group').style.display = 'none';
    
    const roleGroup = document.getElementById('staff-classes-group');
    if (staff.role === 'teacher') {
        roleGroup.style.display = 'block';
    } else {
        roleGroup.style.display = 'none';
    }
    
    document.getElementById('modal-staff-title').innerText = 'تعديل موظف';
    UI.openModal('modal-staff');
    await populateStaffClasses(staff.class_ids || []);
};

window.openAddStaffModal = async () => {
    document.getElementById('staff-id').value = '';
    document.getElementById('form-staff').reset();
    document.getElementById('staff-base-salary').value = '0';
    document.getElementById('staff-password-group').style.display = 'block';
    document.getElementById('staff-classes-group').style.display = 'none';
    document.getElementById('modal-staff-title').innerText = 'إضافة موظف';
    UI.openModal('modal-staff');
    await populateStaffClasses([]);
};

window.app = window.app || {};
window.app.quickPayment = (e) => {
    e.preventDefault();
    const studentId = document.getElementById('profile-student-id').value;
    const studentName = document.getElementById('profile-name').textContent;
    UI.closeModal('modal-student-profile');
    document.getElementById('pay-student-id').value = studentId;
    document.getElementById('pay-invoice-id').value = '';
    document.getElementById('pay-notes').value = ''; // clear notes
    document.getElementById('payment-invoice-title').textContent = `(سداد حر لـ ${studentName})`;
    UI.openModal('modal-payment');
};
window.app.quickPrint = (e) => {
    e.preventDefault();
    window.print();
};


window.openStudentProfileById = async (studentId, tab = 'info') => {
    try {
        Toast.info('جاري التحميل...');
        const profileData = await ProfileAPI.getStudentProfile(studentId);
        if (!profileData || !profileData.student) {
            Toast.error('لم يتم العثور على الطالب');
            return;
        }
        await window.openStudentProfile(null, profileData.student);
        if (tab !== 'info') {
            window.UI.switchProfileTab(tab, { target: document.querySelector(`.nav-btn[onclick*="switchProfileTab('${tab}'"]`) });
        }
    } catch(e) {
        console.error(e);
        Toast.error('حدث خطأ أثناء تحميل الملف');
    }
};

window.openStudentProfile = async (e, student) => {
    if (e) e.preventDefault();
    document.getElementById('profile-student-id').value = student.id;
    document.getElementById('profile-name').textContent = student.full_name_ar;
    
    // Set Avatar initials
    const initials = student.full_name_ar ? student.full_name_ar.substring(0, 1) : '?';
    document.getElementById('profile-avatar-display').textContent = initials;
    
    document.getElementById('profile-dob').textContent = student.dob || 'غير محدد';
    document.getElementById('profile-address').textContent = student.address || 'غير محدد';
    document.getElementById('profile-father-phone').textContent = student.father_phone || 'غير محدد';
    document.getElementById('profile-mother-phone').textContent = student.mother_phone || 'غير محدد';
    
    const statusBadge = document.getElementById('profile-status-badge');
    if (student.status === 'inactive') {
        statusBadge.textContent = 'مؤرشف';
        statusBadge.style.background = '#9ca3af';
    } else {
        statusBadge.textContent = 'نشط';
        statusBadge.style.background = 'var(--success-color)';
    }
    
    // Switch to info tab by default
    const infoTabBtn = document.querySelector('.profile-nav .nav-btn');
    if (infoTabBtn) infoTabBtn.click();
    
    try {
        const profileData = await ProfileAPI.getStudentProfile(student.id);
        
        document.getElementById('profile-enroll-date').textContent = profileData.student.enrollment_date || 'غير محدد';
        
        // Current Classes
        const classesContainer = document.getElementById('profile-current-classes');
        if (profileData.current_classes && profileData.current_classes.length > 0) {
            classesContainer.innerHTML = 'الفصول الحالية: ' + profileData.current_classes.map(c => `<span style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px; margin-left: 4px; color: #1a202c; font-weight: bold;">${escapeHtml(c.class_name_ar)} (${escapeHtml(c.level_name_ar)})</span>`).join('');
        } else {
            classesContainer.innerHTML = 'غير مسجل في أي فصل حالياً';
        }

        // Subject Levels
        const slContainer = document.getElementById('profile-subject-levels-content');
        if (profileData.student_subject_levels && profileData.student_subject_levels.length > 0) {
            slContainer.innerHTML = profileData.student_subject_levels.map(sl => {
                let currentLvl = sl.level_name_ar || 'غير محدد';
                if (sl.current_level && sl.current_level.name_ar) currentLvl = sl.current_level.name_ar;
                let subjName = sl.subject_name_ar || 'غير محدد';
                if (sl.subject && sl.subject.name_ar) subjName = sl.subject.name_ar;
                
                let upd = sl.updated_at ? new Date(sl.updated_at).toLocaleDateString('ar-SA') : '-';
                return `<tr>
                    <td>${escapeHtml(subjName)}</td>
                    <td>${escapeHtml(currentLvl)}</td>
                    <td>${upd}</td>
                    <td><button class="btn-secondary btn-sm" onclick="window.app.openManualPromotion(event, ${sl.subject_id}, ${sl.level_id || sl.current_level_id})">تغيير يدوي</button></td>
                </tr>`;
            }).join('');
        } else {
            slContainer.innerHTML = '<tr><td colspan="4" class="text-center text-muted">لا توجد مستويات مسجلة</td></tr>';
        }
        
        // Financial Logic
        const billed = parseFloat(profileData.student.total_billed) || 0;
        const paid = parseFloat(profileData.student.total_paid) || 0;
        const balance = parseFloat(profileData.student.balance) || 0;
        
        document.getElementById('profile-total-billed').textContent = formatCurrency(billed);
        document.getElementById('profile-total-paid').textContent = formatCurrency(paid);
        document.getElementById('profile-balance').textContent = formatCurrency(balance);
        
        // Add WhatsApp reminder button if balance > 0
        const profileBalanceEl = document.getElementById('profile-balance');
        const phone = profileData.student.contact_phone || profileData.student.father_phone || '';
        if (balance > 0 && phone) {
            let msg = encodeURIComponent(`مرحباً ${profileData.student.full_name_ar}، نذكركم بوجود مستحقات مالية متأخرة بقيمة ${balance} ج.م. يرجى المبادرة بالسداد.`);
            let waBtn = document.createElement('a');
            waBtn.href = `https://wa.me/${phone}?text=${msg}`;
            waBtn.target = '_blank';
            waBtn.className = 'btn-success btn-sm';
            waBtn.style.marginLeft = '10px';
            waBtn.style.textDecoration = 'none';
            waBtn.style.display = 'inline-block';
            waBtn.style.padding = '2px 8px';
            waBtn.style.borderRadius = '4px';
            waBtn.innerHTML = '📱 واتساب';
            waBtn.id = 'profile-wa-reminder-btn';
            
            // Remove old button if exists
            const oldBtn = document.getElementById('profile-wa-reminder-btn');
            if (oldBtn) oldBtn.remove();
            
            profileBalanceEl.parentNode.appendChild(waBtn);
        } else {
            const oldBtn = document.getElementById('profile-wa-reminder-btn');
            if (oldBtn) oldBtn.remove();
        }

        // Wallet Progress Bar
        const walletBar = document.getElementById('wallet-paid-bar');
        if (billed > 0) {
            let percentage = Math.min((paid / billed) * 100, 100);
            walletBar.style.width = `${percentage}%`;
        } else {
            walletBar.style.width = '0%';
        }
        
        // Timeline Logic
        const timelineContainer = document.getElementById('profile-timeline-content');
        if (profileData.timeline && profileData.timeline.length > 0) {
            timelineContainer.innerHTML = profileData.timeline.map(item => `
                <div class="timeline-item">
                    <div class="date">${item.date ? new Date(item.date).toLocaleDateString('ar-SA') : ''}</div>
                    <div class="desc">${escapeHtml(item.description)}</div>
                </div>
            `).join('');
        } else {
            timelineContainer.innerHTML = '<div class="text-center text-muted">لا توجد نشاطات مسجلة</div>';
        }
        
        // Set rings
        document.getElementById('profile-score').textContent = profileData.average_score || '-';
        document.getElementById('profile-absences').textContent = profileData.absences || '0';
        document.getElementById('profile-lates').textContent = profileData.lates || '0';
        
        const attContainer = document.getElementById('profile-attendance-content');
        if (!profileData.attendance_details || profileData.attendance_details.length === 0) {
            attContainer.innerHTML = '<tr><td colspan="3" class="text-center text-muted">لا توجد سجلات حضور</td></tr>';
        } else {
            const statusMap = {
                'absent': 'غائب',
                'late': 'متأخر',
                'excused': 'عذر',
                'present': 'حاضر'
            };
            
            attContainer.innerHTML = profileData.attendance_details.map(att => `
                <tr>
                    <td>${att.date}</td>
                    <td>${att.subject}</td>
                    <td>${statusMap[att.status] || att.status}</td>
                </tr>
            `).join('');
        }
        
        // Render detailed exams
        const examsContainer = document.getElementById('profile-exams-content');
        if (!profileData.exam_details || profileData.exam_details.length === 0) {
            examsContainer.innerHTML = '<tr><td colspan="4" class="text-center text-muted">لا يوجد درجات مسجلة</td></tr>';
        } else {
            examsContainer.innerHTML = profileData.exam_details.map(ex => {
                const pct = ((ex.score / ex.total_points) * 100).toFixed(1);
                return `<tr>
                    <td>${ex.date}</td>
                    <td>${ex.title}</td>
                    <td>${ex.score} / ${ex.total_points}</td>
                    <td>
                        <div style="display:flex; align-items:center; gap:0.5rem;">
                            <div style="width: 50px; background: #e2e8f0; border-radius: 4px; overflow: hidden; height: 8px;">
                                <div style="width: ${pct}%; background: ${pct >= 50 ? 'var(--success-color)' : 'var(--danger-color)'}; height: 100%;"></div>
                            </div>
                            <span>${pct}%</span>
                        </div>
                    </td>
                </tr>`;
            }).join('');
        }
    } catch(err) {
        console.error(err);
    }

    UI.openModal('modal-student-profile');
};

async function loadStudentNotes(studentId) {
    try {
        const notes = await NotesAPI.getNotes('student', studentId);
        const notesContainer = document.getElementById('profile-notes-content');
        if (notes.length === 0) {
            notesContainer.innerHTML = '<div style="text-align:center; padding: 2rem; background: #f8fafc; border-radius: 8px; margin-top: 1rem;"><p class="text-muted" style="margin:0; font-size: 1.1rem;">لا توجد ملاحظات.</p></div>';
        } else {
            notesContainer.innerHTML = notes.map(note => `
                <div style="margin-top: 1rem; padding: 1rem; background: ${note.severity === 'high' ? '#fee2e2' : (note.severity === 'medium' ? '#fef3c7' : '#f3f4f6')}; border-radius: 4px;">
                    <div class="flex-between mb-2">
                        <strong>${note.author_name}</strong>
                        <small class="text-muted">${new Date(note.created_at).toLocaleString('ar-SA')}</small>
                    </div>
                    <p style="white-space: pre-wrap; margin: 0;">${note.content}</p>
                </div>
            `).join('');
        }
    } catch(err) {
        console.error(err);
    }
}

async function loadStudentFinance(studentId) {
    try {
        const data = await API.get('/finance/student/' + studentId);
        
        const invTbody = document.getElementById('profile-invoices-content');
        if(data.invoices.length === 0) {
            invTbody.innerHTML = '<tr><td colspan="6" class="text-center">لا توجد فواتير</td></tr>';
        } else {
            invTbody.innerHTML = data.invoices.map(inv => `
                <tr>
                    <td>${inv.title}</td>
                    <td>${inv.amount}</td>
                    <td>${inv.paid_amount}</td>
                    <td>${inv.remaining}</td>
                    <td>${inv.due_date || '-'}</td>
                    <td><span class="status-badge status-${inv.status}">${inv.status === 'paid' ? 'مدفوعة' : (inv.status === 'partial' ? 'جزئي' : 'غير مدفوعة')}</span></td>
                </tr>
            `).join('');
            
            const totalAmount = data.invoices.reduce((sum, d) => sum + (parseFloat(d.amount) || 0), 0);
            const totalPaid = data.invoices.reduce((sum, d) => sum + (parseFloat(d.paid_amount) || 0), 0);
            const totalRemaining = data.invoices.reduce((sum, d) => sum + (parseFloat(d.remaining) || 0), 0);
            
            if (document.getElementById('profile-sum-amount')) document.getElementById('profile-sum-amount').textContent = totalAmount;
            if (document.getElementById('profile-sum-paid')) document.getElementById('profile-sum-paid').textContent = totalPaid;
            if (document.getElementById('profile-sum-remaining')) document.getElementById('profile-sum-remaining').textContent = totalRemaining;
        }
        
        const payTbody = document.getElementById('profile-payments-content');
        if(data.payments.length === 0) {
            payTbody.innerHTML = '<tr><td colspan="4" class="text-center">لا توجد مدفوعات</td></tr>';
        } else {
            const methodNames = { 'cash': 'نقدي', 'bank': 'حوالة بنكية', 'card': 'بطاقة' };
            payTbody.innerHTML = data.payments.map(pay => `
                <tr>
                    <td>${pay.amount}</td>
                    <td>${methodNames[pay.method] || pay.method}</td>
                    <td>${pay.receipt_no || '-'}</td>
                    <td>${new Date(pay.paid_at).toLocaleString('ar-SA')}</td>
                </tr>
            `).join('');
        }
    } catch(err) {
        console.error(err);
    }
}

async function loadStudentCertificates(studentId) {
    try {
        const certs = await API.get('/certificates/student/' + studentId);
        
        const tbody = document.getElementById('profile-certificates-content');
        if(certs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">لا توجد شهادات</td></tr>';
        } else {
            const typeNames = { 'payment_receipt': 'إيصال دفع', 'level_completion': 'اجتياز مستوى', 'level_start': 'تسجيل مستوى' };
            tbody.innerHTML = certs.map(cert => `
                <tr>
                    <td>${typeNames[cert.type] || cert.type}</td>
                    <td>${new Date(cert.issued_at).toLocaleDateString('ar-SA')}</td>
                    <td><span class="status-badge status-active">مُصدرة</span></td>
                    <td>
                        <button class="btn-secondary" onclick="window.open('/api/certificates/${cert.certificate_id}', '_blank')">عرض / طباعة</button>
                    </td>
                </tr>
            `).join('');
        }
    } catch(err) {
        console.error(err);
    }
}



window.openClassProfile = async (event, classData) => {
    if (event && event.target && event.target.tagName === 'BUTTON') return;
    await ClassroomView.open(classData.id, classData.name_ar);
};

window.toggleSubjectAccordion = function(id) {
    const content = document.getElementById('accordion-content-' + id);
    const icon = document.getElementById('accordion-icon-' + id);
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.style.transform = 'rotate(180deg)';
    } else {
        content.style.display = 'none';
        icon.style.transform = 'rotate(0deg)';
    }
};

window.openEnrollModal = (id, name) => {
    document.getElementById('enroll-student-id').value = id;
    document.getElementById('enroll-student-name').value = name;
    UI.openModal('modal-enroll');
};

async function loadData() {
    // Subjects now rendered as accordion tree
    // Levels now nested inside subjects accordion
    StateHelper.loading(document.querySelector('#table-students tbody'));
    try {
        const [subjects, levels, classes, students, summary] = await Promise.all([
            API.get('/subjects/'),
            API.get('/levels/'),
            API.get('/classes/'),
            API.get('/students/'),
            API.get('/dashboard/summary').catch(e => { console.error("Dashboard summary error", e); return null; })
        ]);
        
        window.allSubjects = subjects;
        window.allLevels = levels;
        window.allClasses = classes;
        
        if (window.currentUser && window.currentUser.role === 'boss') {
            loadStaffNotes().catch(e=>{});
            Audit.loadLogs().catch(e=>{});
            FinanceUI.loadFeeTemplates().catch(e=>{});
            document.getElementById('nav-audit').style.display = 'block';
        }

        if (summary) {
            document.getElementById('stat-students').textContent = summary.stats.students;
            document.getElementById('stat-classes').textContent = summary.stats.classes;
            document.getElementById('stat-levels').textContent = summary.stats.levels;
            document.getElementById('stat-sessions').textContent = summary.stats.sessions_today;
            
            const sessionsCompletedEl = document.getElementById('stat-sessions-completed');
            if (sessionsCompletedEl) sessionsCompletedEl.textContent = `مكتملة: ${summary.stats.sessions_completed}`;
            
            const statInvoices = document.getElementById('stat-invoices');
            if (statInvoices) statInvoices.textContent = summary.stats.overdue_invoices;
            
            const statPromotions = document.getElementById('stat-promotions');
            if (statPromotions) statPromotions.textContent = summary.stats.pending_promotions;
            
            const feedContainer = document.getElementById('dashboard-activity-feed');
            if (feedContainer) {
                if (summary.activity_feed.length === 0) {
                    feedContainer.innerHTML = '<div class="text-muted text-center p-4">لا توجد نشاطات حديثة</div>';
                } else {
                    feedContainer.innerHTML = summary.activity_feed.map(act => {
                        const icon = act.type === 'note' ? '📝' : (act.type === 'payment' ? '💰' : '📈');
                        const date = act.date ? new Date(act.date).toLocaleDateString('ar-SA', {hour: '2-digit', minute:'2-digit'}) : '';
                        return `
                        <div style="display: flex; gap: 1rem; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color);">
                            <div style="font-size: 1.5rem;">${icon}</div>
                            <div>
                                <div style="font-weight: 500;">${escapeHtml(act.description)}</div>
                                <div class="text-sm text-muted">${date}</div>
                            </div>
                        </div>`;
                    }).join('');
                }
            }
        }
        // Render Subjects & Levels Tree
        const treeContainer = document.getElementById('subjects-levels-tree');
        if (treeContainer) {
            if (subjects.length === 0) {
                StateHelper.empty(treeContainer, 'لا توجد مواد مضافة');
            } else {
                treeContainer.innerHTML = subjects.map(s => {
                    const sJson = JSON.stringify(s).replace(/"/g, '&quot;');
                    let subjectActions = '';
                    if (window.currentUser && window.currentUser.role === 'boss') {
                        subjectActions = `<button class="btn-secondary btn-sm" onclick="event.stopPropagation(); CRUDApi.editSubject(${sJson})">تعديل المادة</button> 
                                          <button class="btn-danger btn-sm" onclick="event.stopPropagation(); CRUDApi.deleteSubject(${s.id})">حذف المادة</button>`;
                    }
                    
                    const subjLevels = s.levels || [];
                    const levelsHtml = subjLevels.map(l => {
                        const lJson = JSON.stringify(l).replace(/"/g, '&quot;');
                        let levelActions = '';
                        if (window.currentUser && window.currentUser.role === 'boss') {
                            levelActions = `<button class="btn-secondary btn-sm" onclick="CRUDApi.editLevel(${lJson})">تعديل</button> 
                                            <button class="btn-danger btn-sm" onclick="CRUDApi.deleteLevel(${l.id})">حذف</button>`;
                        }
                        return `
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 1rem; border-bottom: 1px solid var(--border-color);">
                            <div>
                                <span class="badge" style="background: var(--primary-color); color: white;">${l.order_index}</span>
                                <span style="font-weight: 500; margin: 0 0.5rem;">${escapeHtml(l.name_ar)}</span>
                                <span class="text-sm text-muted">(${escapeHtml(l.code)})</span>
                            </div>
                            <div>${levelActions}</div>
                        </div>`;
                    }).join('');

                    return `
                    <div class="accordion-subject card" style="margin-bottom: 1rem; padding: 0; overflow: hidden;">
                        <div class="accordion-header" style="padding: 1rem; background: #f8f9fa; display: flex; justify-content: space-between; align-items: center; cursor: pointer;" onclick="toggleSubjectAccordion(${s.id})">
                            <h4 style="margin: 0; color: var(--primary-color);">
                                📘 ${escapeHtml(s.name_ar)} 
                                <span class="badge" style="background: var(--secondary-color); color: white;">${subjLevels.length} مستويات</span>
                            </h4>
                            <div style="display: flex; gap: 0.5rem;">
                                ${subjectActions}
                                <span id="accordion-icon-${s.id}" style="font-size: 1.2rem; transition: transform 0.3s;">▾</span>
                            </div>
                        </div>
                        <div id="accordion-content-${s.id}" class="accordion-content" style="display: none; border-top: 1px solid var(--border-color);">
                            ${levelsHtml}
                            <div style="padding: 1rem; text-align: center; background: #fafafa;">
                                <button class="btn-secondary btn-sm" onclick="UI.openModal('modal-level'); document.getElementById('lvl-subject-id').value = ${s.id};">
                                    + إضافة مستوى لهذه المادة
                                </button>
                            </div>
                        </div>
                    </div>`;
                }).join('');
            }
        }
        
        const lvlSubjSelect = document.getElementById('lvl-subject-id');
        if (lvlSubjSelect) {
            lvlSubjSelect.innerHTML = '<option value="">بدون مادة</option>' + subjects.map(s => `<option value="${s.id}">${escapeHtml(s.name_ar)}</option>`).join('');
        }
        
        const reportClassSelect = document.getElementById('report-class-select');
        const reportAttClassSelect = document.getElementById('report-attendance-class-select');
        reportClassSelect.innerHTML = '<option value="">اختر الفصل...</option>' + classes.map(c => `<option value="${c.id}">${escapeHtml(c.name_ar)} (${escapeHtml(c.group_label||'')})</option>`).join('');
        reportAttClassSelect.innerHTML = reportClassSelect.innerHTML;
        
        const clsLevelSelect = document.getElementById('cls-level');
        clsLevelSelect.innerHTML = levels.map(l => `<option value="${l.id}">${escapeHtml(l.name_ar)}</option>`).join('');

        try {
            const staff = await API.get('/staff/');
            const teachers = staff.filter(s => s.role === 'teacher' || s.role === 'supervisor' || s.role === 'boss');
            const clsTeacherSelect = document.getElementById('cls-teacher');
            if (clsTeacherSelect) {
                clsTeacherSelect.innerHTML = '<option value="">-- بدون معلم --</option>' + 
                    teachers.map(t => `<option value="${t.id}">${escapeHtml(t.full_name_ar)}</option>`).join('');
            }
        } catch(e) { console.error("Error loading staff for teachers dropdown", e); }

        // Render Classes
        const clsGrid = document.querySelector('#grid-classes');
        if (classes.length === 0) StateHelper.empty(clsGrid, 'لا توجد فصول مضافة');
        else clsGrid.innerHTML = classes.map(c => {
            const cJson = JSON.stringify(c).replace(/"/g, '&quot;');
            let actions = '';
            if (window.currentUser && window.currentUser.role === 'boss') {
                actions = `
                <div class="flex-between mt-3 pt-3" style="border-top: 1px solid var(--border-color)">
                    <button class="btn-secondary btn-sm" onclick="CRUDApi.editClass(${cJson})">تعديل</button> 
                    <button class="btn-danger btn-sm" onclick="CRUDApi.deleteClass(${c.id})">حذف</button>
                </div>`;
            }
            
            const capacity = c.capacity || 20;
            const enrolled = c.roster_count || 0;
            const progress = capacity > 0 ? Math.min((enrolled / capacity) * 100, 100) : 0;
            let progressColor = 'var(--primary-color)';
            if (progress >= 100) progressColor = 'var(--danger-color)';
            else if (progress >= 80) progressColor = 'var(--warning-color)';
            
            return `
            <div class="card" style="display: flex; flex-direction: column; cursor: pointer;" onclick="openClassProfile(event, ${cJson})">
                <div class="flex-between mb-2">
                    <h3 style="margin: 0; color: var(--text-color);">${escapeHtml(c.name_ar)}</h3>
                    <span class="status-pill ${c.status === 'active' ? 'active-present' : 'active-late'}">${c.status === 'active' ? 'نشط' : 'مغلق'}</span>
                </div>
                <div class="text-sm text-muted mb-3">
                    ${escapeHtml(c.level_name || '-')} • ${escapeHtml(c.group_label || '-')}
                </div>
                
                <div class="mb-2 flex-between text-sm">
                    <span>الطلاب: ${enrolled} / ${capacity}</span>
                    <span style="color: ${progressColor}; font-weight: 600;">${Math.round(progress)}%</span>
                </div>
                <div class="progress-bar mb-3">
                    <div class="progress-fill" style="width: ${progress}%; background-color: ${progressColor};"></div>
                </div>
                
                <div class="text-sm mt-auto" style="color: var(--text-muted);">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: text-bottom; margin-left: 4px;"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                    المشرف: ${c.supervisor ? escapeHtml(c.supervisor.full_name_ar) : 'غير محدد'}
                </div>
                
                ${actions}
            </div>`;
        }).join('');
        const enrollClsSelect = document.getElementById('enroll-class-id');
        enrollClsSelect.innerHTML = '<option value="">اختر الفصل...</option>' + classes.map(c => `<option value="${c.id}">${escapeHtml(c.name_ar)}</option>`).join('');
        
        const filterClsSelect = document.getElementById('filter-student-class');
        if(filterClsSelect) {
            filterClsSelect.innerHTML = '<option value="">جميع الفصول</option>' + classes.map(c => `<option value="${c.id}">${escapeHtml(c.name_ar)}</option>`).join('');
        }

        const stuBody = document.querySelector('#table-students tbody');
        stuBody.innerHTML = students.map(s => {
            const sJson = JSON.stringify(s).replace(/"/g, '&quot;');
            let actions = `<button class="btn-secondary" onclick="openEnrollModal(${s.id}, ${jsArg(s.full_name_ar)})">تسجيل بفصل</button>`;
            if (window.currentUser && window.currentUser.role === 'boss') {
                actions += ` <button class="btn-secondary btn-sm" onclick="CRUDApi.editStudent(${sJson})">تعديل</button>`;
                if (s.status === 'inactive') {
                    actions += ` <button class="btn-primary btn-sm" onclick="CRUDApi.enableStudent(${s.id})">إعادة تنشيط</button>`;
                } else {
                    actions += ` <button class="btn-warning btn-sm" onclick="CRUDApi.disableStudent(${s.id})">أرشفة</button>`;
                }
                actions += ` <button class="btn-danger btn-sm" onclick="CRUDApi.deleteStudent(${s.id})">حذف</button>`;
            }
            const rowStyle = s.status === 'inactive' ? 'opacity: 0.6; background-color: #f9f9f9;' : '';
            const statusBadge = s.status === 'inactive' ? `<span class="status-pill" style="background:#e5e7eb; color:#374151; margin-right:5px;">مؤرشف</span>` : '';
            return `<tr style="${rowStyle}">
                <td>${s.id}</td>
                <td><a href="#" onclick="openStudentProfile(event, ${sJson})">${escapeHtml(s.full_name_ar)}</a> ${statusBadge}</td>
                <td>${s.enrollment_date || ''}</td>
                <td><span class="status-pill" style="color:var(--danger-color); background:#fef2f2; border-color:#fca5a5; padding: 2px 8px;">${s.absences || 0}</span></td>
                <td><span style="font-weight:600; color:${s.balance > 0 ? 'var(--danger-color)' : 'var(--success-color)'};">${s.balance || 0} EGP</span></td>
                <td>${actions}</td>
            </tr>`;
        }).join('');

        if (window.currentUser && window.currentUser.role === 'boss') {
            // Fetch Staff, Classes, and Settings in parallel without blocking
            Promise.all([
                StaffAPI.getAll().catch(e => { console.error('Failed to load staff list', e); return null; }),
                API.get('/classes/').catch(e => { console.error('Failed to load classes', e); return []; }),
                SettingsAPI.get().catch(e => { console.error('Failed to load settings', e); return null; })
            ]).then(([allStaff, classes, settings]) => {
                window.ClassesList = classes || [];
                window.StaffList = allStaff || [];
                PairingCard.render();
                if (allStaff) {
                    const staffListBody = document.querySelector('#table-staff-list tbody');
                    if (staffListBody) {
                        staffListBody.innerHTML = allStaff.map(s => {
                            const sJson = JSON.stringify(s).replace(/"/g, '&quot;');
                            return `<tr>
                                <td>${escapeHtml(s.full_name_ar)}</td>
                                <td>${escapeHtml(s.email)}</td>
                                <td><span class="role-badge">${getRoleName(s.role)}</span></td>
                                <td>${escapeHtml(s.phone || '-')}</td>
                                <td>${s.base_salary || 0}</td>
                                <td>
                                    ${(s.class_ids || []).map(cid => {
                                        const c = window.ClassesList.find(x => x.id === cid);
                                        return `<span class="badge" style="background:var(--primary-light); color:var(--primary-hover); margin:2px;">${c ? escapeHtml(c.name_ar) : 'فصل ' + cid}</span>`;
                                    }).join('')}
                                </td>
                                <td>
                                    ${s.role !== 'boss' ? `
                                        <button class="btn-secondary btn-sm" onclick="openEditStaffModal(${sJson})">تعديل</button>
                                        <button class="btn-secondary btn-sm" onclick="openChangePasswordModal(${s.id}, ${jsArg(s.full_name_ar)})">كلمة المرور</button>
                                        <button class="btn-danger btn-sm" onclick="deactivateStaff(${s.id}, ${jsArg(s.full_name_ar)})">إلغاء التفعيل</button>
                                    ` : ''}
                                </td>
                            </tr>`;
                        }).join('');
                    }
                }
                
                if (settings) {
                    const iName = document.getElementById('setting-institution-name');
                    if (iName) iName.value = settings.institution_name || '';
                    const iCurr = document.getElementById('setting-currency');
                    if (iCurr) iCurr.value = settings.currency || '';
                    const iStuckM = document.getElementById('setting-stuck-months');
                    if (iStuckM) iStuckM.value = settings.stuck_threshold_months || '6';
                    const iStuckG = document.getElementById('setting-stuck-grade');
                    if (iStuckG) iStuckG.value = settings.stuck_threshold_grade || '50';
                    const iPass = document.getElementById('setting-passing-grade');
                    if (iPass) iPass.value = settings.default_passing_grade || '50';
                }
            });
        }
        
        if (window.TreeUI) {
            window.TreeUI.loadSchoolTree();
        }
        if (window.RoadmapUI) {
            window.RoadmapUI.render();
        }

        // Populate class dropdown for exams filter and create modal
        const classFilter = document.getElementById('exam-class-filter');
        const classSelect = document.getElementById('exam-class-id');
        const options = classes.map(c => `<option value="${c.id}">${escapeHtml(c.name_ar)}</option>`).join('');
        if (classFilter) classFilter.innerHTML = '<option value="">جميع الفصول</option>' + options;
        if (classSelect) classSelect.innerHTML = options;
        
        // Load subjects for exam modal
        const subjSelect = document.getElementById('exam-subject-id');
        if (subjSelect) subjSelect.innerHTML = subjects.map(s => `<option value="${s.id}">${escapeHtml(s.name_ar)}</option>`).join('');
    } catch (error) {
        console.error('Failed to load data', error);
    }
}

// --- SESSIONS & ATTENDANCE ---
window.Sessions = {
    async openClassSessions(classId, className) {
        document.getElementById('current-sessions-class-id').value = classId;
        document.getElementById('sessions-modal-title').textContent = `الجلسات (الجدول والحضور) - ${className}`;
        
        // Populate subject select for schedule form
        const schedSubjSelect = document.getElementById('sched-subject');
        schedSubjSelect.innerHTML = window.allSubjects.map(s => `<option value="${s.id}">${s.name_ar}</option>`).join('');
        
        await this.loadSchedules(classId);
        
        // Silently generate upcoming sessions for 30 days based on the schedule
        await this.generateSessions(true);
        
        await this.loadSessions(classId);
        UI.openModal('modal-sessions');
    },
    
    async loadSchedules(classId) {
        try {
            const schedules = await API.get(`/schedules/?class_id=${classId}`);
            const tbody = document.querySelector('#table-schedules tbody');
            const days = ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'];
            
            tbody.innerHTML = schedules.map(s => {
                const subject = window.allSubjects.find(sub => sub.id === s.subject_id);
                const subjName = subject ? subject.name_ar : 'مجهول';
                return `<tr>
                    <td>${days[s.day_of_week]}</td>
                    <td>${subjName}</td>
                    <td>${s.start_time} - ${s.end_time}</td>
                    <td>
                        <button class="btn-danger" onclick="Sessions.deleteSchedule(${s.id}, ${classId})">حذف</button>
                    </td>
                </tr>`;
            }).join('');
        } catch(e) {
            console.error('Error loading schedules', e);
        }
    },
    
    async deleteSchedule(schedId, classId) {
        if (!(await ConfirmDialog.show('هل أنت متأكد من حذف هذا الموعد من الجدول؟', {type: 'danger'}))) return;
        try {
            await fetch(`/api/schedules/${schedId}`, { method: 'DELETE' });
            await this.loadSchedules(classId);
        } catch(e) {
            Toast.error('Error deleting schedule');
        }
    },
    
    async loadSessions(classId) {
        try {
            const sessions = await API.get(`/sessions/?class_id=${classId}`);
            const listContainer = document.getElementById('sessions-list');
            
            const todayStr = new Date().toISOString().split('T')[0];
            const tomorrowDate = new Date();
            tomorrowDate.setDate(tomorrowDate.getDate() + 1);
            const tomorrowStr = tomorrowDate.toISOString().split('T')[0];
            
            const groups = { overdue: [], today: [], tomorrow: [], upcoming: [], completed: [] };
            
            sessions.forEach(s => {
                const subject = window.allSubjects.find(sub => sub.id === s.subject_id);
                s.subjectName = subject ? subject.name_ar : 'مجهول';
                
                if (s.status === 'completed') {
                    groups.completed.push(s);
                } else if (s.date < todayStr) {
                    groups.overdue.push(s);
                } else if (s.date === todayStr) {
                    groups.today.push(s);
                } else if (s.date === tomorrowStr) {
                    groups.tomorrow.push(s);
                } else {
                    groups.upcoming.push(s);
                }
            });
            
            const renderCard = (s, isOverdue) => {
                const isCompleted = s.status === 'completed';
                return `
                <div class="task-card ${isCompleted ? 'completed' : ''}" onclick="Sessions.openAttendance(${s.id}, ${classId})">
                    <div class="task-left">
                        <div class="task-checkbox"></div>
                        <div class="task-details">
                            <div class="task-title">${escapeHtml(s.subjectName)}</div>
                            <div class="task-meta ${isOverdue && !isCompleted ? 'overdue' : ''}">
                                <span>${s.start_time} - ${s.end_time}</span>
                                <span>${s.date}</span>
                            </div>
                        </div>
                    </div>
                </div>`;
            };
            
            let html = '';
            if (groups.overdue.length > 0) {
                html += `
                <div class="task-group">
                    <div class="task-group-title overdue">متأخرة</div>
                    ${groups.overdue.map(s => renderCard(s, true)).join('')}
                </div>`;
            }
            if (groups.today.length > 0) {
                html += `
                <div class="task-group">
                    <div class="task-group-title">اليوم</div>
                    ${groups.today.map(s => renderCard(s, false)).join('')}
                </div>`;
            }
            if (groups.tomorrow.length > 0) {
                html += `
                <div class="task-group">
                    <div class="task-group-title">غداً</div>
                    ${groups.tomorrow.map(s => renderCard(s, false)).join('')}
                </div>`;
            }
            if (groups.upcoming.length > 0) {
                html += `
                <div class="task-group">
                    <div class="task-group-title">لاحقاً</div>
                    ${groups.upcoming.map(s => renderCard(s, false)).join('')}
                </div>`;
            }
            if (groups.completed.length > 0) {
                html += `
                <div class="task-group mt-4">
                    <div class="task-group-title text-muted">مكتملة</div>
                    ${groups.completed.map(s => renderCard(s, false)).join('')}
                </div>`;
            }
            
            if (!html) {
                html = '<div class="text-center text-muted p-4">لا توجد جلسات</div>';
            }
            
            listContainer.innerHTML = html;
        } catch(e) {
            Toast.error('Error loading sessions');
        }
    },
    
    async generateSessions(silent = false) {
        const classId = document.getElementById('current-sessions-class-id').value;
        const start = new Date();
        const end = new Date();
        // Generate sessions for the next 30 days to make it repetitive
        end.setDate(end.getDate() + 30);
        
        try {
            await API.post('/sessions/generate', {
                class_id: parseInt(classId),
                start_date: start.toISOString().split('T')[0],
                end_date: end.toISOString().split('T')[0]
            });
            if (!silent) {
                Toast.success('تم توليد الجلسات بناء على الجدول الأسبوعي لمدة شهر قادم');
            }
            await this.loadSessions(classId);
        } catch(e) {
            if (!silent) {
                Toast.error(e.message || 'Error generating sessions');
            }
        }
    },
    
    async openAttendance(sessionId, classId) {
        document.getElementById('att-session-id').value = sessionId;
        
        const roster = await ProfileAPI.getClassRoster(classId);
        
        const listContainer = document.getElementById('attendance-list');
        if (roster.length === 0) {
            listContainer.innerHTML = '<div class="text-center text-muted p-4">لا يوجد طلاب في هذا الفصل</div>';
            UI.openModal('modal-attendance');
            return;
        }
        
        listContainer.innerHTML = roster.map(enroll => {
            const stu = enroll.student;
            return `
            <div class="checklist-item" id="att-item-${stu.id}" data-student-id="${stu.id}" data-status="absent">
                <div class="checklist-left" onclick="Sessions.toggleAttendance(${stu.id})">
                    <div class="check-toggle"></div>
                    <div class="student-name">${escapeHtml(stu.full_name_ar)}</div>
                </div>
                <div class="checklist-actions">
                    <button type="button" class="status-pill" id="pill-late-${stu.id}" onclick="Sessions.setAttendanceStatus(${stu.id}, 'late')">متأخر</button>
                    <button type="button" class="status-pill" id="pill-excused-${stu.id}" onclick="Sessions.setAttendanceStatus(${stu.id}, 'excused')">عذر</button>
                </div>
            </div>`;
        }).join('');
        
        UI.openModal('modal-attendance');
    },
    
    toggleAttendance(studentId) {
        const item = document.getElementById(`att-item-${studentId}`);
        const currentStatus = item.getAttribute('data-status');
        
        if (currentStatus === 'present') {
            this.setAttendanceStatus(studentId, 'absent');
        } else {
            this.setAttendanceStatus(studentId, 'present');
        }
    },
    
    setAttendanceStatus(studentId, status) {
        const item = document.getElementById(`att-item-${studentId}`);
        const pillLate = document.getElementById(`pill-late-${studentId}`);
        const pillExcused = document.getElementById(`pill-excused-${studentId}`);
        
        item.classList.remove('present');
        pillLate.classList.remove('active-late');
        pillExcused.classList.remove('active-excused');
        
        item.setAttribute('data-status', status);
        
        if (status === 'present') {
            item.classList.add('present');
        } else if (status === 'late') {
            pillLate.classList.add('active-late');
        } else if (status === 'excused') {
            pillExcused.classList.add('active-excused');
        }
    },
    
    markAllPresent() {
        const items = document.querySelectorAll('#attendance-list .checklist-item');
        items.forEach(item => {
            const studentId = item.getAttribute('data-student-id');
            this.setAttendanceStatus(studentId, 'present');
        });
    }
};

document.getElementById('form-schedule').addEventListener('submit', async (e) => {
    e.preventDefault();
    const classId = document.getElementById('current-sessions-class-id').value;
    
    try {
        await API.post('/schedules/', {
            class_id: parseInt(classId),
            day_of_week: parseInt(document.getElementById('sched-day').value),
            subject_id: parseInt(document.getElementById('sched-subject').value),
            start_time: document.getElementById('sched-start').value,
            end_time: document.getElementById('sched-end').value
        });
        document.getElementById('form-schedule').reset();
        await Sessions.loadSchedules(classId);
    } catch(e) {
        Toast.error('Error adding schedule');
    }
});

document.getElementById('form-attendance').addEventListener('submit', async (e) => {
    e.preventDefault();
    const sessionId = document.getElementById('att-session-id').value;
    const items = document.querySelectorAll('#attendance-list .checklist-item');
    
    const records = Array.from(items).map(item => ({
        student_id: parseInt(item.getAttribute('data-student-id')),
        status: item.getAttribute('data-status')
    }));
    
    try {
        await API.post(`/sessions/${sessionId}/attendance`, { records });
        Toast.success('تم حفظ الحضور');
        UI.closeModal('modal-attendance');
        const classId = document.getElementById('current-sessions-class-id').value;
        await Sessions.loadSessions(classId);
    } catch(e) {
        Toast.error('Error saving attendance');
    }
});

document.getElementById('form-add-note').addEventListener('submit', async (e) => {
    e.preventDefault();
    const studentId = document.getElementById('profile-student-id').value;
    
    try {
        await NotesAPI.createNote({
            target_type: 'student',
            target_id: parseInt(studentId),
            category: 'general',
            severity: document.getElementById('note-severity').value,
            visibility: 'all_staff',
            content: document.getElementById('note-content').value
        });
        document.getElementById('form-add-note').reset();
        await loadStudentNotes(studentId);
    } catch(e) {
        Toast.error('Error adding note');
    }
});

async function loadStaffNotes() {
    try {
        const notes = await NotesAPI.getNotes('staff', window.currentUser.id); // For global, we can just use a target_id=0 or 1. Let's say target_id=0 means global board.
        const notesContainer = document.getElementById('staff-notes-content');
        if (notes.length === 0) {
            notesContainer.innerHTML = '<div style="text-align:center; padding: 2rem; background: #f8fafc; border-radius: 8px; margin-top: 1rem;"><p class="text-muted" style="margin:0; font-size: 1.1rem;">لا توجد ملاحظات.</p></div>';
        } else {
            notesContainer.innerHTML = notes.map(note => `
                <div style="margin-top: 1rem; padding: 1rem; background: ${note.severity === 'high' ? '#fee2e2' : (note.severity === 'medium' ? '#fef3c7' : '#f3f4f6')}; border-radius: 4px;">
                    <div class="flex-between mb-2">
                        <strong>${note.author_name}</strong>
                        <small class="text-muted">${new Date(note.created_at).toLocaleString('ar-SA')}</small>
                    </div>
                    <p style="white-space: pre-wrap; margin: 0;">${note.content}</p>
                </div>
            `).join('');
        }
    } catch(err) {
        console.error(err);
    }
}

document.getElementById('form-staff-note')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        await NotesAPI.createNote({
            target_type: 'staff',
            target_id: 0, // 0 for global staff board
            category: 'general',
            severity: document.getElementById('staff-note-severity').value,
            visibility: 'all_staff',
            content: document.getElementById('staff-note-content').value
        });
        document.getElementById('form-staff-note').reset();
        await loadStaffNotes();
    } catch(e) {
        Toast.error('Error adding note');
    }
});

/* ====================================================
   EXAMS LOGIC
==================================================== */

async function loadExams() {
    const classId = document.getElementById('exam-class-filter').value;

    
    try {
        const exams = await ExamsAPI.getExams(classId || null);
        const tbody = document.querySelector('#table-exams tbody');
        if (exams.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">لا يوجد اختبارات لهذا الفصل</td></tr>';
            return;
        }
        
        tbody.innerHTML = exams.map(e => `
            <tr>
                <td>${e.title}</td>
                <td>${e.date}</td>
                <td>${e.total_points} (النجاح: ${e.passing_grade})</td>
                <td>${e.status === 'scheduled' ? 'مجدول' : (e.status === 'grading' ? 'رصد الدرجات' : 'تم النشر')}</td>
                <td>${e.is_certification ? 'شهادة 🏆' : 'عادي'}</td>
                <td>
                    ${e.status !== 'published' ? `<button class="btn-primary" onclick="openGradeExamModal(${e.id}, ${e.class_id}, ${jsArg(e.title)})">رصد الدرجات</button>` : `<button class="btn-secondary" onclick="openGradeExamModal(${e.id}, ${e.class_id}, ${jsArg(e.title)})">عرض النتائج</button>`}
                </td>
            </tr>
        `).join('');
    } catch (e) {
        console.error("Error loading exams:", e);
    }
}

document.getElementById('form-create-exam')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        await ExamsAPI.createExam({
            title: document.getElementById('exam-title').value,
            class_id: parseInt(document.getElementById('exam-class-id').value),
            subject_id: parseInt(document.getElementById('exam-subject-id').value),
            date: document.getElementById('exam-date').value,
            total_points: parseInt(document.getElementById('exam-total').value),
            passing_grade: parseInt(document.getElementById('exam-passing').value),
            is_certification: document.getElementById('exam-is-certification').checked
        });
        UI.closeModal('modal-create-exam');
        loadExams();
    } catch(err) {
        Toast.error('خطأ في إضافة الاختبار');
        console.error(err);
    }
});

function updateExamPercentage(inputElem, maxScore) {
    const val = parseFloat(inputElem.value);
    const tdPercent = inputElem.closest('tr').querySelector('.score-percentage');
    if (isNaN(val)) {
        tdPercent.textContent = '-';
    } else {
        tdPercent.textContent = ((val / maxScore) * 100).toFixed(1) + '%';
    }
}

async function openGradeExamModal(examId, classId, title) {
    document.getElementById('grade-exam-title').textContent = title;
    document.getElementById('grade-exam-id').value = examId;
    
    try {
        const examDetails = await ExamsAPI.getExamDetails(examId);
        const exam = examDetails.exam;
        const scores = examDetails.scores || [];
        
        const roster = await ProfileAPI.getClassRoster(classId);
        
        const tbody = document.querySelector('#table-grade-exam tbody');
        if (roster.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">لا يوجد طلاب في هذا الفصل</td></tr>';
        } else {
            const maxScore = exam.total_points || 100;
            tbody.innerHTML = roster.map(enroll => {
                const s = enroll.student;
                const existingScore = scores.find(sc => sc.student_id === s.id);
                const scoreValue = existingScore ? existingScore.score : '';
                const percentValue = scoreValue !== '' ? ((scoreValue / maxScore) * 100).toFixed(1) + '%' : '-';
                return `
                    <tr>
                        <td>${s.full_name_ar}</td>
                        <td>
                            <input type="number" step="0.5" class="form-control score-input" data-sid="${s.id}" value="${scoreValue}" oninput="updateExamPercentage(this, ${maxScore})" ${exam.status === 'published' ? 'disabled' : ''}>
                        </td>
                        <td class="score-percentage" style="vertical-align: middle; font-weight: bold; color: var(--primary-color); text-align: left;" dir="ltr">${percentValue}</td>
                    </tr>
                `;
            }).join('');
        }
        
        const publishBtn = document.getElementById('btn-publish-exam');
        if (exam.status === 'published') {
            publishBtn.style.display = 'none';
        } else {
            publishBtn.style.display = 'block';
        }
        
        UI.openModal('modal-grade-exam');
    } catch(err) {
        console.error(err);
    }
}

async function submitExamScores() {
    const examId = document.getElementById('grade-exam-id').value;
    const inputs = document.querySelectorAll('.score-input');
    const scores = [];
    inputs.forEach(input => {
        if (input.value !== '') {
            scores.push({
                student_id: parseInt(input.getAttribute('data-sid')),
                score: parseFloat(input.value)
            });
        }
    });
    
    try {
        await ExamsAPI.submitScores(examId, { scores });
        Toast.success('تم حفظ الدرجات');
        loadExams();
    } catch(err) {
        console.error(err);
        Toast.error('خطأ في حفظ الدرجات');
    }
}

async function publishExam() {
    if (!(await ConfirmDialog.show('هل أنت متأكد من نشر الاختبار؟ (لا يمكن التعديل بعد النشر وسيتم إنشاء طلبات ترفيع للناجحين إذا كان اختبار شهادة)', {type: 'danger'}))) return;
    
    const examId = document.getElementById('grade-exam-id').value;
    try {
        await ExamsAPI.publishExam(examId);
        Toast.success('تم النشر بنجاح');
        UI.closeModal('modal-grade-exam');
        loadExams();
        if (window.currentUser && window.currentUser.role === 'boss') {
            loadPromotions();
        }
    } catch(err) {
        console.error(err);
        Toast.error('خطأ في النشر');
    }
}



/* ====================================================
   FINANCE LOGIC
==================================================== */

const FinanceUI = {
    showTab: async function(tabId, btnElement) {
        document.querySelectorAll('.finance-tab').forEach(t => t.style.display = 'none');
        document.getElementById(tabId).style.display = 'block';
        
        if (btnElement) {
            document.querySelectorAll('.finance-nav-btn').forEach(b => {
                b.classList.remove('btn-primary', 'active-tab');
                b.classList.add('btn-secondary');
            });
            btnElement.classList.remove('btn-secondary');
            btnElement.classList.add('btn-primary', 'active-tab');
        }
        
        // Auto-generate missing invoices first
        try {
            const result = await FinanceAPI.autoGenerateInvoices();
            if (result && result.created > 0) {
                Toast.success(`تم توليد ${result.created} فاتورة مستحقة تلقائياً`);
            }
        } catch(e) {
            console.error('Error auto-generating invoices:', e);
        }
        
        if (tabId === 'finance-income') { this.loadSummary(); this.loadInvoices(); }
        else if (tabId === 'finance-debts') this.loadDebts();
        else if (tabId === 'finance-salaries') this.loadSalaries();
        else if (tabId === 'finance-expenses') this.loadExpenses();
        else if (tabId === 'finance-reports') this.loadReports();
    },
    
    loadSummary: async function() {
        try {
            const summary = await FinanceAPI.getSummary();
            if (document.getElementById('summary-billed')) {
                document.getElementById('summary-billed').textContent = formatCurrency(summary.total_billed);
                document.getElementById('summary-collected').textContent = formatCurrency(summary.total_collected);
                document.getElementById('summary-outstanding').textContent = formatCurrency(summary.total_outstanding);
                document.getElementById('summary-overdue').textContent = summary.overdue_count;
            }
        } catch(e) { console.error('Error loading finance summary:', e); }
    },
    
    loadInvoices: async function() {
        try {
            const status = document.getElementById('filter-invoice-status') ? document.getElementById('filter-invoice-status').value : '';
            const from = document.getElementById('filter-invoice-from') ? document.getElementById('filter-invoice-from').value : '';
            const to = document.getElementById('filter-invoice-to') ? document.getElementById('filter-invoice-to').value : '';
            
            const invoices = await FinanceAPI.getInvoices(status, from, to);
            
            // Populate class filter if needed
            const classSelect = document.getElementById('filter-invoice-class');
            if (classSelect && classSelect.options.length <= 1) {
                const classes = await API.get('/classes/');
                classes.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c.name_ar; // API returns class_name
                    opt.textContent = c.name_ar;
                    classSelect.appendChild(opt);
                });
            }

            let filteredInvoices = invoices;
            
            const searchInput = document.getElementById('filter-invoice-search');
            if (searchInput && searchInput.value) {
                const q = searchInput.value.toLowerCase();
                filteredInvoices = filteredInvoices.filter(i => 
                    (i.student_name && i.student_name.toLowerCase().includes(q)) || 
                    (i.title && i.title.toLowerCase().includes(q))
                );
            }
            
            if (classSelect && classSelect.value) {
                filteredInvoices = filteredInvoices.filter(i => i.class_name === classSelect.value);
            }
            
            const tbody = document.querySelector('#table-invoices tbody');
            if (tbody) {
                tbody.innerHTML = filteredInvoices.map(i => `
                    <tr>
                        <td>${i.student_name}</td>
                        <td>${i.title}</td>
                        <td>${formatCurrency(i.amount)}</td>
                        <td class="text-success">${formatCurrency(i.paid_amount)}</td>
                        <td class="text-danger">${formatCurrency(i.remaining)}</td>
                        <td>${i.status === 'paid' ? 'مدفوعة' : i.status === 'partial' ? 'مدفوعة جزئياً' : 'غير مدفوعة'}</td>
                        <td>
                            ${(i.status !== 'paid') ? `<button class="btn-success btn-sm" onclick="FinanceUI.openPaymentModal(${i.student_id}, ${i.id}, ${i.remaining}, '${i.title}')">تسديد</button>` : ''}
                            ${(i.paid_amount == 0 && window.currentUser && window.currentUser.role === 'boss') ? `<button class="btn-danger btn-sm" onclick="FinanceUI.deleteInvoice(${i.id})">حذف</button>` : ''}
                        </td>
                    </tr>
                `).join('');
            }
        } catch(e) { console.error('Error in loadInvoices:', e); }
    },
    
    loadDebts: async function() {
        try {
            const debts = await FinanceAPI.getDebts();
            
            // Group by student
            const studentDebts = {};
            debts.forEach(d => {
                if (!studentDebts[d.student_id]) {
                    studentDebts[d.student_id] = {
                        student_id: d.student_id,
                        student_name: d.student_name,
                        student_phone: d.student_phone || "",
                        invoices: [],
                        total_net: 0,
                        total_paid: 0,
                        total_remaining: 0
                    };
                }
                studentDebts[d.student_id].invoices.push(d);
                studentDebts[d.student_id].total_net += (parseFloat(d.net_total) || 0);
                studentDebts[d.student_id].total_paid += (parseFloat(d.paid_amount) || 0);
                studentDebts[d.student_id].total_remaining += (parseFloat(d.remaining) || 0);
            });

            const tbody = document.querySelector('#table-debts tbody');
            if (tbody) {
                tbody.innerHTML = Object.values(studentDebts).map(s => {
                    const invoicesTitles = s.invoices.map(i => i.title).join('، ');
                    
                    let whatsappBtn = '';
                    if (s.student_phone) {
                        let msg = encodeURIComponent(`مرحباً ${s.student_name}، نذكركم بوجود مستحقات مالية متأخرة بقيمة ${s.total_remaining} ج.م. يرجى المبادرة بالسداد.`);
                        whatsappBtn = `<a href="https://wa.me/${s.student_phone}?text=${msg}" target="_blank" class="btn-success btn-sm" style="text-decoration: none; display: inline-block; padding: 2px 8px; border-radius: 4px;">📱 واتساب</a>`;
                    }

                    return `
                    <tr>
                        <td><a href="#" onclick="UI.openStudentProfile(${s.student_id}); return false;" style="color: var(--primary-color); font-weight: bold; text-decoration: none;">${s.student_name}</a></td>
                        <td><small>${invoicesTitles}</small></td>
                        <td>${formatCurrency(s.total_net)}</td>
                        <td class="text-success">${formatCurrency(s.total_paid)}</td>
                        <td class="text-danger" style="font-weight: bold;">${formatCurrency(s.total_remaining)}</td>
                        <td>${s.total_remaining > 0 ? 'غير مسدد بالكامل' : 'مدفوع'}</td>
                        <td>
                            <div style="display: flex; gap: 5px;">
                                <button class="btn-primary btn-sm" onclick="FinanceUI.openPaymentModal(${s.student_id}, '', ${s.total_remaining}, '(سداد حر)')">+ تسجيل دفعة حرة</button>
                                ${whatsappBtn}
                            </div>
                        </td>
                    </tr>
                `}).join('');
                
                const totalAmount = debts.reduce((sum, d) => sum + (parseFloat(d.net_total) || 0), 0);
                const totalPaid = debts.reduce((sum, d) => sum + (parseFloat(d.paid_amount) || 0), 0);
                const totalRemaining = debts.reduce((sum, d) => sum + (parseFloat(d.remaining) || 0), 0);
                
                if (document.getElementById('total-debts-amount')) document.getElementById('total-debts-amount').textContent = formatCurrency(totalAmount);
                if (document.getElementById('total-debts-paid')) document.getElementById('total-debts-paid').textContent = formatCurrency(totalPaid);
                if (document.getElementById('total-debts-remaining')) document.getElementById('total-debts-remaining').textContent = formatCurrency(totalRemaining);
            }
        } catch(e) { console.error('Error in loadDebts:', e); }
    },
    
    deleteInvoice: async function(id) {
        if (!(await ConfirmDialog.show('هل أنت متأكد من حذف هذه الفاتورة؟', {type: 'danger'}))) return;
        try {
            await FinanceAPI.deleteInvoice(id);
            Toast.success('تم الحذف');
            this.loadInvoices();
        } catch(e) {
            Toast.error(e.detail || 'خطأ في الحذف');
        }
    },
    
    openInvoiceModal: async function() {
        try {
            const students = await API.get('/students/');
            const select = document.getElementById('invoice-student-id');
            select.innerHTML = students.map(s => `<option value="${s.id}">${s.full_name_ar}</option>`).join('');
            
            const templates = await FinanceAPI.getFeeTemplates();
            const tSelect = document.getElementById('invoice-template-id');
            tSelect.innerHTML = '<option value="">-- إدخال يدوي --</option>' + templates.map(t => `<option value="${t.id}" data-amount="${t.amount}" data-name="${t.name_ar}">${t.name_ar} (${t.amount})</option>`).join('');
            
            // Reset fields
            document.getElementById('invoice-title').value = '';
            document.getElementById('invoice-amount').value = '';
            document.getElementById('invoice-discount-value').value = '';
            document.getElementById('invoice-paid-amount').value = '';
            document.getElementById('invoice-due-date').value = '';
            
            if (select.options.length > 0) {
                this.onStudentSelectForInvoice(select);
            } else {
                this.calculateInvoiceTotals();
            }
            
            UI.openModal('modal-invoice');
        } catch(e) { console.error(e); }
    },
    
    onStudentSelectForInvoice: async function(selectElem) {
        if (!selectElem.value) return;
        try {
            const studentId = selectElem.value;
            const fetched = await API.get(`/students/${studentId}`);
            const balance = fetched.balance || 0;
            document.getElementById('invoice-calc-previous').dataset.val = balance;
            this.calculateInvoiceTotals();
        } catch (e) { console.error(e); }
    },
    
    calculateInvoiceTotals: function() {
        const amount = parseFloat(document.getElementById('invoice-amount').value) || 0;
        const discountType = document.getElementById('invoice-discount-type').value;
        const discountValue = parseFloat(document.getElementById('invoice-discount-value').value) || 0;
        
        let currentTotal = amount;
        if (discountValue > 0) {
            if (discountType === 'percent') {
                currentTotal = amount - (amount * discountValue / 100);
            } else {
                currentTotal = amount - discountValue;
            }
        }
        currentTotal = Math.max(0, currentTotal);
        
        const previousDebt = parseFloat(document.getElementById('invoice-calc-previous').dataset.val) || 0;
        const totalDue = currentTotal + previousDebt;
        
        document.getElementById('invoice-calc-current').textContent = currentTotal.toFixed(2) + ' ج.م';
        document.getElementById('invoice-calc-previous').textContent = previousDebt.toFixed(2) + ' ج.م';
        document.getElementById('invoice-calc-total-due').textContent = totalDue.toFixed(2) + ' ج.م';
        document.getElementById('invoice-calc-total-due').dataset.val = totalDue;
        
        const paidAmount = parseFloat(document.getElementById('invoice-paid-amount').value) || 0;
        const remaining = totalDue - paidAmount;
        document.getElementById('invoice-calc-remaining').textContent = remaining.toFixed(2) + ' ج.م';
    },
    
    payFullInvoiceAccount: function() {
        const totalDue = parseFloat(document.getElementById('invoice-calc-total-due').dataset.val) || 0;
        document.getElementById('invoice-paid-amount').value = totalDue.toFixed(2);
        this.calculateInvoiceTotals();
    },
    
    onTemplateSelect: function(selectElem) {
        if (!selectElem.value) return;
        const selected = selectElem.options[selectElem.selectedIndex];
        document.getElementById('invoice-amount').value = selected.getAttribute('data-amount');
        document.getElementById('invoice-title').value = selected.getAttribute('data-name');
        this.calculateInvoiceTotals();
    },

    openBulkInvoiceModal: async function() {
        try {
            const classes = await API.get('/classes/');
            const cSelect = document.getElementById('bulk-class-id');
            cSelect.innerHTML = classes.map(c => `<option value="${c.id}">${c.name_ar}</option>`).join('');
            
            const templates = await FinanceAPI.getFeeTemplates();
            const tSelect = document.getElementById('bulk-template-id');
            tSelect.innerHTML = templates.map(t => `<option value="${t.id}">${t.name_ar} (${t.amount})</option>`).join('');
            
            UI.openModal('modal-bulk-invoice');
        } catch(e) { console.error(e); }
    },

    openFeeTemplateModal: async function() {
        try {
            const levels = await API.get('/levels/');
            const select = document.getElementById('fee-template-level');
            select.innerHTML = '<option value="">عام (لجميع المستويات)</option>' + levels.map(l => `<option value="${l.id}">${l.name_ar}</option>`).join('');
            UI.openModal('modal-fee-template');
        } catch(e) { console.error(e); }
    },

    loadFeeTemplates: async function() {
        try {
            const templates = await FinanceAPI.getFeeTemplates();
            const tbody = document.querySelector('#table-fee-templates tbody');
            tbody.innerHTML = templates.map(t => `
                <tr>
                    <td>${t.name_ar}</td>
                    <td>${formatCurrency(t.amount)}</td>
                    <td>${t.level_name}</td>
                    <td>${t.is_recurring ? 'دورية' : 'لمرة واحدة'}</td>
                    <td><button class="btn-danger" onclick="FinanceUI.deleteFeeTemplate(${t.id})">حذف</button></td>
                </tr>
            `).join('');
            
            const totalAmount = templates.reduce((sum, t) => sum + (parseFloat(t.amount) || 0), 0);
            if (document.getElementById('total-fee-templates-amount')) {
                document.getElementById('total-fee-templates-amount').textContent = formatCurrency(totalAmount);
            }
        } catch(e) { console.error(e); }
    },

    deleteFeeTemplate: async function(id) {
        if (!(await ConfirmDialog.show('هل أنت متأكد من حذف هذا القالب؟', {type: 'danger'}))) return;
        try {
            await FinanceAPI.deleteFeeTemplate(id);
            Toast.success('تم الحذف');
            this.loadFeeTemplates();
        } catch(e) { Toast.error('خطأ'); }
    },
    
    openPaymentModal: function(studentId, invoiceId, remaining, title) {
        document.getElementById('pay-student-id').value = studentId;
        document.getElementById('pay-invoice-id').value = invoiceId || '';
        document.getElementById('payment-invoice-title').innerText = invoiceId ? `للفاتورة #${invoiceId}` : 'للطالب';
        
        const itemGroup = document.getElementById('pay-item-group');
        const itemTitle = document.getElementById('pay-item-title');
        
        let invoiceTitle = title || '';
        if (!invoiceTitle && invoiceId) {
            const row = document.querySelector(`button[onclick*="FinanceUI.openPaymentModal(${studentId}, ${invoiceId}"]`)?.closest('tr');
            if (row) {
                invoiceTitle = row.children[0]?.innerText || row.children[3]?.innerText || '';
            }
        }
        
        if (invoiceId) {
            itemTitle.value = invoiceTitle;
            itemGroup.style.display = 'block';
        } else {
            itemGroup.style.display = 'none';
        }
        
        document.getElementById('pay-notes').value = '';
        
        const amountInput = document.getElementById('pay-amount');
        amountInput.value = remaining || '';
        amountInput.min = '0.01';
        amountInput.step = '0.01';
        if (invoiceId && remaining) {
            amountInput.max = String(remaining);
        } else {
            amountInput.removeAttribute('max');
        }
        UI.openModal('modal-payment');
    },

    loadSalaries: async function() {
        const month = document.getElementById('salary-month-filter').value;
        try {
            const salaries = await FinanceAPI.getSalaries(month);
            const tbody = document.querySelector('#table-salaries tbody');
            tbody.innerHTML = salaries.map(s => `
                <tr>
                    <td>${s.staff_name}</td>
                    <td>${s.month}</td>
                    <td>${formatCurrency(s.base_salary)}</td>
                    <td class="text-success">${formatCurrency(s.bonuses)}</td>
                    <td class="text-danger">${formatCurrency(s.deductions)}</td>
                    <td><strong>${formatCurrency(s.net_salary)}</strong></td>
                    <td>${s.status === 'paid' ? 'مدفوع' : 'مسودة'}</td>
                    <td>
                        ${s.status !== 'paid' ? `<button class="btn-primary" onclick="FinanceUI.paySalary(${s.id})">تأكيد الدفع</button>` : ''}
                    </td>
                </tr>
            `).join('');
        } catch(e) { console.error(e); }
    },
    
    generateBulkSalaries: async function() {
        const month = document.getElementById('salary-month-filter').value;
        if (!month) {
            Toast.error('الرجاء اختيار الشهر أولاً من الفلتر');
            return;
        }
        if (!(await ConfirmDialog.show(`هل أنت متأكد من توليد رواتب شهر ${month} لجميع الموظفين؟`))) return;
        
        try {
            const res = await FinanceAPI.generateSalaries({ month });
            Toast.success(res.message);
            this.loadSalaries();
        } catch(e) { Toast.error('خطأ في التنفيذ'); }
    },
    
    openSalaryModal: async function() {
        try {
            const staff = await StaffAPI.getAll();
            const select = document.getElementById('salary-user-id');
            select.innerHTML = staff.map(s => `<option value="${s.id}">${s.full_name_ar}</option>`).join('');
            UI.openModal('modal-salary');
        } catch(e) { console.error(e); }
    },
    
    paySalary: async function(id) {
        if (!(await ConfirmDialog.show('هل أنت متأكد من دفع هذا الراتب؟', {type: 'danger'}))) return;
        try {
            await FinanceAPI.paySalary(id);
            Toast.success('تم تأكيد الدفع');
            this.loadSalaries();
        } catch(e) { Toast.error('خطأ في التنفيذ'); }
    },

    loadExpenses: async function() {
        try {
            const expenses = await FinanceAPI.getExpenses();
            const tbody = document.querySelector('#table-expenses tbody');
            tbody.innerHTML = expenses.map(e => `
                <tr>
                    <td>${e.date}</td>
                    <td>${e.category}</td>
                    <td>${formatCurrency(e.amount)}</td>
                    <td>${e.description || ''}</td>
                    <td>${e.recorded_by_name}</td>
                </tr>
            `).join('');
        } catch(e) { console.error(e); }
    },

    loadReports: async function() {
        try {
            const r = await FinanceAPI.getReports();
            document.getElementById('report-income').innerText = formatCurrency(r.total_income);
            document.getElementById('report-outstanding').innerText = formatCurrency(r.total_outstanding);
            document.getElementById('report-salaries').innerText = formatCurrency(r.salaries_paid);
            document.getElementById('report-expenses').innerText = formatCurrency(r.total_expenses);
            document.getElementById('report-net').innerText = formatCurrency(r.net_profit);
            
            if (r.net_profit < 0) {
                document.getElementById('report-net').className = 'stat-value text-danger';
            } else {
                document.getElementById('report-net').className = 'stat-value text-success';
            }
        } catch(e) { console.error(e); }
    },
    
    triggerAutoGenerate: async function() {
        try {
            const result = await FinanceAPI.autoGenerateInvoices();
            if (result && result.created > 0) {
                Toast.success(`تم توليد ${result.created} فاتورة جديدة بنجاح`);
                this.loadFeeTemplates(); // Optionally refresh if needed
            } else {
                Toast.info('لا توجد فواتير جديدة مستحقة التوليد في الوقت الحالي');
            }
        } catch(e) {
            console.error(e);
            Toast.error('حدث خطأ أثناء محاولة توليد الرسوم');
        }
    }
};

document.getElementById('form-invoice').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        const payload = {
            student_id: parseInt(document.getElementById('invoice-student-id').value),
            title: document.getElementById('invoice-title').value,
            amount: parseFloat(document.getElementById('invoice-amount').value),
            discount_type: document.getElementById('invoice-discount-type').value,
            discount: parseFloat(document.getElementById('invoice-discount-value').value) || 0,
            paid_amount: parseFloat(document.getElementById('invoice-paid-amount').value) || 0
        };
        const dueDate = document.getElementById('invoice-due-date').value;
        if (dueDate) payload.due_date = dueDate;
        
        await FinanceAPI.addInvoice(payload);
        Toast.success('تم إضافة الفاتورة');
        UI.closeModal('modal-invoice');
        FinanceUI.loadInvoices();
    } catch(err) { Toast.error('خطأ في إضافة الفاتورة'); }
});

document.getElementById('form-bulk-invoice').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        const res = await FinanceAPI.bulkInvoice({
            class_id: parseInt(document.getElementById('bulk-class-id').value),
            fee_template_id: parseInt(document.getElementById('bulk-template-id').value),
            month_label: document.getElementById('bulk-month-label').value
        });
        Toast.success(res.message);
        UI.closeModal('modal-bulk-invoice');
        FinanceUI.loadInvoices();
    } catch(err) { Toast.error('خطأ في فوترة الفصل'); }
});

document.getElementById('form-fee-template').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        const levelId = document.getElementById('fee-template-level').value;
        await FinanceAPI.addFeeTemplate({
            name_ar: document.getElementById('fee-template-name').value,
            amount: parseFloat(document.getElementById('fee-template-amount').value),
            level_id: levelId ? parseInt(levelId) : null,
            is_recurring: document.getElementById('fee-template-recurring').checked
        });
        Toast.success('تم إضافة قالب الرسوم');
        UI.closeModal('modal-fee-template');
        FinanceUI.loadFeeTemplates();
    } catch(err) { Toast.error('خطأ في إضافة القالب'); }
});

document.getElementById('form-payment').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        const res = await FinanceAPI.addPayment({
            student_id: parseInt(document.getElementById('pay-student-id').value) || null,
            invoice_id: parseInt(document.getElementById('pay-invoice-id').value) || null,
            method: document.getElementById('pay-method').value,
            amount: parseFloat(document.getElementById('pay-amount').value),
            notes: document.getElementById('pay-notes').value || null
        });
        Toast.success('تم تسجيل الدفعة بنجاح');
        UI.closeModal('modal-payment');
        FinanceUI.loadInvoices();
        
        if (res.certificate_id) {
            window.open('/api/certificates/' + res.certificate_id, '_blank');
        }
    } catch(err) { Toast.error(err.message || 'خطأ في التسجيل'); }
});

document.getElementById('form-salary').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        await FinanceAPI.addSalary({
            user_id: parseInt(document.getElementById('salary-user-id').value),
            month: document.getElementById('salary-month').value,
            base_salary: parseFloat(document.getElementById('salary-base').value),
            bonuses: parseFloat(document.getElementById('salary-bonus').value || 0),
            deductions: parseFloat(document.getElementById('salary-deduction').value || 0)
        });
        Toast.success('تم رصد مسودة الراتب');
        UI.closeModal('modal-salary');
        FinanceUI.loadSalaries();
    } catch(err) { Toast.error('خطأ في الرصد'); }
});

document.getElementById('form-expense').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        await FinanceAPI.addExpense({
            date: document.getElementById('expense-date').value,
            category: document.getElementById('expense-category').value,
            amount: parseFloat(document.getElementById('expense-amount').value),
            description: document.getElementById('expense-desc').value
        });
        Toast.success('تم تسجيل المصروف');
        UI.closeModal('modal-expense');
        FinanceUI.loadExpenses();
    } catch(err) { Toast.error('خطأ في التسجيل'); }
});



// --- DB ADMINISTRATION ---
window.DBAdmin = {
    async downloadBackup() {
        if (!(await ConfirmDialog.show('هل أنت متأكد أنك تريد تحميل نسخة من قاعدة البيانات؟', {type: 'danger'}))) return;
        window.open('/api/db/download', '_blank');
    },
    
    async uploadBackup(inputElem) {
        const file = inputElem.files[0];
        if (!file) return;
        if (!file.name.endsWith('.db')) {
            Toast.success('يجب أن يكون الملف بامتداد .db');
            inputElem.value = '';
            return;
        }
        
        if (!(await ConfirmDialog.show('تنبيه خطير! رفع قاعدة بيانات جديدة سيؤدي إلى استبدال البيانات الحالية بالكامل. هل أنت متأكد جداً من هذه الخطوة؟', {type: 'danger'}))) {
            inputElem.value = '';
            return;
        }
        
        try {
            await DatabaseAPI.upload(file);
            Toast.success('تم رفع قاعدة البيانات بنجاح. سيتم إعادة تحميل الصفحة.');
            window.location.reload();
        } catch (e) {
            Toast.error('حدث خطأ أثناء رفع قاعدة البيانات: ' + e.message);
        }
        inputElem.value = '';
    },
    
    async wipeDatabase() {
        const password = prompt('تنبيه خطير جداً! سيتم مسح جميع بيانات النظام بلا رجعة (الطلاب، المالية، الفصول، الجلسات... كل شيء).\nيرجى إدخال كلمة المرور الخاصة بمسح البيانات لتأكيد العملية:');
        if (!password) {
            Toast.success('تم إلغاء العملية.');
            return;
        }
        
        try {
            const res = await DatabaseAPI.wipe(password);
            Toast.success(res.message);
            await API.logout();
            window.location.reload();
        } catch (e) {
            Toast.error('حدث خطأ أثناء مسح قاعدة البيانات: ' + e.message);
        }
    }
};

// --- CRUD API ---
window.CRUDApi = {
    editSubject(s) {
        document.getElementById('subj-id').value = s.id;
        document.getElementById('subj-name').value = s.name_ar;
        document.getElementById('subj-desc').value = s.description || '';
        document.getElementById('subj-promo-threshold').value = s.promotion_threshold || 75;
        UI.openModal('modal-subject');
    },
    async deleteSubject(id) {
        if (!(await ConfirmDialog.show('هل أنت متأكد من حذف هذه المادة؟', {type: 'danger'}))) return;
        try {
            await API.delete(`/subjects/${id}`);
            Toast.success('تم الحذف بنجاح');
            await loadData();
        } catch (e) { Toast.error(e.message); }
    },
    
    editLevel(l) {
        document.getElementById('lvl-id').value = l.id;
        document.getElementById('lvl-name').value = l.name_ar;
        document.getElementById('lvl-code').value = l.code;
        document.getElementById('lvl-order').value = l.order_index;
        
        const select = document.getElementById('lvl-subject-id');
        select.innerHTML = '<option value="">بدون مادة</option>';
        window.allSubjects.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.id;
            opt.textContent = s.name_ar;
            if(l.subject_id === s.id) opt.selected = true;
            select.appendChild(opt);
        });
        
        UI.openModal('modal-level');
    },
    async deleteLevel(id) {
        if (!(await ConfirmDialog.show('هل أنت متأكد من حذف هذا المستوى؟', {type: 'danger'}))) return;
        try {
            await API.delete(`/levels/${id}`);
            Toast.success('تم الحذف بنجاح');
            await loadData();
        } catch (e) { Toast.success(e.message); }
    },
    
    editClass(c) {
        document.getElementById('cls-id').value = c.id;
        document.getElementById('cls-name').value = c.name_ar;
        document.getElementById('cls-level').value = c.level_id;
        document.getElementById('cls-group').value = c.group_label || '';
        document.getElementById('cls-capacity').value = c.capacity || 30;
        const teacherInput = document.getElementById('cls-teacher');
        if (teacherInput) {
            teacherInput.value = c.teacher ? c.teacher.id : '';
        }
        UI.openModal('modal-class');
    },
    async deleteClass(id) {
        if (!(await ConfirmDialog.show('هل أنت متأكد من حذف هذا الفصل؟', {type: 'danger'}))) return;
        try {
            await API.delete(`/classes/${id}`);
            Toast.success('تم الحذف بنجاح');
            await loadData();
        } catch (e) { Toast.success(e.message); }
    },
    
    editStudent(s) {
        document.getElementById('stu-edit-id').value = s.id;
        document.getElementById('stu-name').value = s.full_name_ar;
        document.getElementById('stu-dob').value = s.dob || '';
        document.getElementById('stu-address').value = s.address || '';
        document.getElementById('stu-father-phone').value = s.father_phone || '';
        document.getElementById('stu-mother-phone').value = s.mother_phone || '';
        UI.openModal('modal-student');
    },
    async deleteStudent(id) {
        if (!(await ConfirmDialog.show('هل أنت متأكد من حذف هذا الطالب؟', {type: 'danger'}))) return;
        try {
            await API.delete(`/students/${id}`);
            Toast.success('تم الحذف بنجاح');
            await loadData();
            if(window.refreshStudentsTable) await window.refreshStudentsTable();
        } catch (e) { Toast.error(e.message); }
    },
    async disableStudent(id) {
        if (!(await ConfirmDialog.show('هل أنت متأكد من أرشفة/تعطيل هذا الطالب؟ سيتم إلغاء فواتيره غير المدفوعة وإزالته من الفصول.', {type: 'warning'}))) return;
        try {
            await API.put(`/students/${id}/disable`);
            Toast.success('تم أرشفة الطالب بنجاح');
            await loadData();
            if(window.refreshStudentsTable) await window.refreshStudentsTable();
        } catch (e) { Toast.error(e.message); }
    },
    async enableStudent(id) {
        if (!(await ConfirmDialog.show('هل أنت متأكد من إعادة تنشيط هذا الطالب؟', {type: 'info'}))) return;
        try {
            await API.put(`/students/${id}/enable`);
            Toast.success('تم تنشيط الطالب بنجاح');
            await loadData();
            if(window.refreshStudentsTable) await window.refreshStudentsTable();
        } catch (e) { Toast.error(e.message); }
    }
};


window.Reports = {
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
                let data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/"/g, '""');
                row.push('"' + data + '"');
            }
            csv.push(row.join(','));
        }
        
        const csvFile = new Blob(["\ufeff" + csv.join('\n')], {type: "text/csv;charset=utf-8;"});
        const downloadLink = document.createElement("a");
        downloadLink.download = filename;
        downloadLink.href = window.URL.createObjectURL(csvFile);
        downloadLink.style.display = "none";
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
    }
};



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
};


// --- MOBILE UX/UI LOGIC ---
document.addEventListener('DOMContentLoaded', () => {
    // Mobile Drawer Navigation
    
    
    // Set default mobile state
    if (window.innerWidth <= 768) {
        document.body.classList.add('mobile-grid-active');
    }
    
    const mobileBackBtn = document.getElementById('mobile-back-btn');
    if (mobileBackBtn) {
        mobileBackBtn.addEventListener('click', () => {
            document.body.classList.remove('mobile-panel-active');
            if (window.innerWidth <= 768) {
        document.body.classList.add('mobile-grid-active');
    }
        });
    }
    
    // Dynamic Data Labels for Mobile Tables

    const applyDataLabels = () => {
        document.querySelectorAll('table.data-table').forEach(table => {
            const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
            table.querySelectorAll('tbody tr').forEach(row => {
                // Skip empty state rows
                if (row.children.length === 1 && row.children[0].colSpan > 1) return;
                
                Array.from(row.children).forEach((cell, index) => {
                    if (headers[index] && !cell.hasAttribute('data-label')) {
                        cell.setAttribute('data-label', headers[index]);
                    }
                });
            });
        });
    };
    
    applyDataLabels();
    
    const observer = new MutationObserver((mutations) => {
        let shouldApply = false;
        mutations.forEach(m => {
            if (m.addedNodes.length > 0) shouldApply = true;
        });
        if (shouldApply) applyDataLabels();
    });
    
    // Re-observe periodically or when tabs change since tables might be dynamically generated
    document.querySelectorAll('table.data-table').forEach(table => {
        const tbody = table.querySelector('tbody');
        if(tbody) observer.observe(tbody, { childList: true });
    });
    
    // Since content loads dynamically, we can also bind applyDataLabels to nav button clicks
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            setTimeout(applyDataLabels, 500);
            setTimeout(applyDataLabels, 1500);
        });
    });
});



window.ClassroomView = {
    currentClassId: null,
    currentClassName: null,
    currentSubjectId: null, // assumed from class schedules later, but for now we'll pick first subject if needed

    async open(classId, className) {
        this.currentClassId = classId;
        this.currentClassName = className;
        document.getElementById('classroom-title').textContent = `الفصل: ${className}`;
        
        // Find subject from class or levels, for simplicity here we just need subject_id for exams/attendance
        // Let's get class details
        try {
            const cls = classes.find(c => c.id === classId);
            if (cls) {
                const lvl = levels.find(l => l.id === cls.level_id);
                if (lvl) this.currentSubjectId = lvl.subject_id;
            }
        } catch(e) {}

        this.switchTab('students');
        document.getElementById('classroom-attendance-date').value = new Date().toISOString().split('T')[0];
        
        UI.openModal('modal-classroom');
        await this.loadStudents();
    },

    switchTab(tabId, btnElem) {
        document.querySelectorAll('#modal-classroom .finance-tab').forEach(t => t.style.display = 'none');
        document.getElementById(`classroom-tab-${tabId}`).style.display = 'block';
        
        if (btnElem) {
            document.querySelectorAll('#modal-classroom .finance-nav-btn').forEach(b => {
                b.classList.remove('btn-primary', 'active-tab');
                b.classList.add('btn-secondary');
            });
            btnElem.classList.remove('btn-secondary');
            btnElem.classList.add('btn-primary', 'active-tab');
        } else {
            // programmatically clicked
            const btn = document.getElementById(`tab-btn-${tabId}`);
            if (btn) {
                document.querySelectorAll('#modal-classroom .finance-nav-btn').forEach(b => {
                    b.classList.remove('btn-primary', 'active-tab');
                    b.classList.add('btn-secondary');
                });
                btn.classList.remove('btn-secondary');
                btn.classList.add('btn-primary', 'active-tab');
            }
        }
        
        if (tabId === 'students') this.loadStudents();
        if (tabId === 'attendance') this.loadAttendance();
        if (tabId === 'exams') this.loadExams();
    },

    async loadStudents() {
        try {
            const res = await API.get(`/students/?class_id=${this.currentClassId}`);
            const tbody = document.querySelector('#table-classroom-students tbody');
            if (res.length === 0) {
                StateHelper.empty(tbody, 'لا يوجد طلاب في هذا الفصل');
            } else {
                tbody.innerHTML = res.map(s => {
                    return `<tr>
                        <td>${escapeHtml(s.full_name_ar)}</td>
                        <td><span class="badge" style="background:var(--warning-color); color:white;">الغيابات: ${s.absences || 0}</span></td>
                    </tr>`;
                }).join('');
            }
        } catch (e) {
            console.error(e);
            alert('حدث خطأ أثناء تحميل الطلاب');
        }
    },

    async loadAttendance() {
        try {
            const date = document.getElementById('classroom-attendance-date').value;
            if (!date) return;
            const res = await API.get(`/students/?class_id=${this.currentClassId}`);
            const tbody = document.querySelector('#table-classroom-attendance tbody');
            
            if (res.length === 0) {
                StateHelper.empty(tbody, 'لا يوجد طلاب');
                return;
            }
            
            // Note: we can't easily fetch today's attendance if session isn't created yet, so we default to present
            tbody.innerHTML = res.map(s => {
                return `<tr data-student-id="${s.id}">
                    <td>${escapeHtml(s.full_name_ar)}</td>
                    <td><input type="radio" name="att_${s.id}" value="present" checked></td>
                    <td><input type="radio" name="att_${s.id}" value="absent"></td>
                    <td><input type="radio" name="att_${s.id}" value="late"></td>
                    <td><input type="radio" name="att_${s.id}" value="excused"></td>
                </tr>`;
            }).join('');
        } catch (e) {
            console.error(e);
        }
    },

    async saveAttendance() {
        try {
            const date = document.getElementById('classroom-attendance-date').value;
            const rows = document.querySelectorAll('#table-classroom-attendance tbody tr');
            const records = [];
            rows.forEach(row => {
                const sId = row.getAttribute('data-student-id');
                const val = document.querySelector(`input[name="att_${sId}"]:checked`);
                if (val) {
                    records.push({ student_id: parseInt(sId), status: val.value });
                }
            });
            
            if (records.length === 0) return alert('لم يتم العثور على طلاب');
            
            await API.post('/sessions/quick-attendance', {
                class_id: this.currentClassId,
                subject_id: this.currentSubjectId,
                date: date,
                records: records
            });
            alert('تم حفظ سجل الغياب بنجاح');
            
        } catch (e) {
            alert('حدث خطأ: ' + e.message);
        }
    },

    async loadExams() {
        try {
            const select = document.getElementById('classroom-exam-select');
            const res = await API.get(`/exams/?class_id=${this.currentClassId}`);
            select.innerHTML = '<option value="">-- اختر اختبار --</option>' + res.map(e => {
                return `<option value="${e.id}">${escapeHtml(e.title)} (${e.date})</option>`;
            }).join('');
            document.getElementById('classroom-exam-grades-container').innerHTML = '<div class="text-center text-muted p-4">اختر اختباراً من القائمة</div>';
        } catch (e) {
            console.error(e);
        }
    },

    async loadGrades(examId) {
        if (!examId) {
            document.getElementById('classroom-exam-grades-container').innerHTML = '<div class="text-center text-muted p-4">اختر اختباراً من القائمة</div>';
            return;
        }
        try {
            const res = await API.get(`/exams/${examId}/gradebook`);
            // res should be { exam: {...}, grades: [...] }
            let html = `
            <div class="table-responsive mt-3">
                <table class="data-table" id="table-classroom-grades">
                    <thead>
                        <tr>
                            <th>الطالب</th>
                            <th>التاريخ</th>
                            <th>الدرجة (من ${res.exam.total_points})</th>
                            <th>الحالة</th>
                            <th>إجراء</th>
                        </tr>
                    </thead>
                    <tbody>`;
            if (res.grades.length === 0) {
                html += `<tr><td colspan="5" class="text-center text-muted">لا يوجد طلاب</td></tr>`;
            } else {
                res.grades.forEach(g => {
                    const statusHtml = g.score !== null ? 
                        (g.passed ? '<span class="badge" style="background:var(--success-color); color:white;">ناجح</span>' : '<span class="badge" style="background:var(--danger-color); color:white;">راسب</span>') : 
                        '<span class="badge" style="background:var(--warning-color); color:white;">لم تُرصد</span>';
                        
                    html += `<tr data-student-id="${g.student_id}">
                        <td>${escapeHtml(g.student_name)}</td>
                        <td>${res.exam.date}</td>
                        <td><input type="number" class="grade-input form-control" style="width: 80px;" value="${g.score !== null ? g.score : ''}" max="${res.exam.total_points}" min="0"></td>
                        <td class="grade-status">${statusHtml}</td>
                        <td><button class="btn-secondary btn-sm" onclick="ClassroomView.saveSingleGrade(${examId}, ${g.student_id}, this)">حفظ</button></td>
                    </tr>`;
                });
            }
            html += `</tbody></table></div>`;
            document.getElementById('classroom-exam-grades-container').innerHTML = html;
        } catch(e) {
            console.error(e);
            alert('حدث خطأ');
        }
    },
    
    async saveSingleGrade(examId, studentId, btnElem) {
        try {
            const row = btnElem.closest('tr');
            const input = row.querySelector('.grade-input');
            const score = parseFloat(input.value);
            if (isNaN(score)) return alert('الرجاء إدخال رقم صحيح');
            
            await API.post(`/exams/${examId}/scores`, {
                scores: [ { student_id: studentId, score: score } ]
            });
            // Update status pill visually
            const maxScore = parseFloat(input.getAttribute('max'));
            const passed = score >= (maxScore / 2); // Assuming passing is 50% for quick view
            const statusCell = row.querySelector('.grade-status');
            statusCell.innerHTML = passed ? '<span class="badge" style="background:var(--success-color); color:white;">ناجح</span>' : '<span class="badge" style="background:var(--danger-color); color:white;">راسب</span>';
            
            alert('تم الحفظ');
        } catch(e) {
            alert('خطأ: ' + e.message);
        }
    },

    async quickCreateExam() {
        const title = prompt("عنوان الاختبار:");
        if (!title) return;
        
        try {
            await API.post('/exams/', {
                title: title,
                subject_id: this.currentSubjectId || 1,
                class_id: this.currentClassId,
                date: new Date().toISOString().split('T')[0],
                total_points: 100,
                passing_grade: 50,
                is_certification: false
            });
            alert('تم إنشاء الاختبار');
            this.loadExams();
        } catch (e) {
            alert('خطأ: ' + e.message);
        }
    }
};


function filterStudents(query) {
    const q = query.toLowerCase().trim();
    const rows = document.querySelectorAll('#table-students tbody tr');
    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        if (text.includes(q)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

async function refreshStudentsTable() {
    const classId = document.getElementById('filter-student-class').value;
    try {
        StateHelper.loading(document.querySelector('#table-students tbody'));
        const url = classId ? `/students/?class_id=${classId}` : '/students/';
        const students = await API.get(url);
        window.allStudents = students; // Update global state if used elsewhere
        
        const stuBody = document.querySelector('#table-students tbody');
        stuBody.innerHTML = students.map(s => {
            const sJson = JSON.stringify(s).replace(/"/g, '&quot;');
            let actions = `<button class="btn-secondary" onclick="openEnrollModal(${s.id}, ${jsArg(s.full_name_ar)})">تسجيل بفصل</button>`;
            if (window.currentUser && window.currentUser.role === 'boss') {
                actions += ` <button class="btn-secondary btn-sm" onclick="CRUDApi.editStudent(${sJson})">تعديل</button>`;
                if (s.status === 'inactive') {
                    actions += ` <button class="btn-primary btn-sm" onclick="CRUDApi.enableStudent(${s.id})">إعادة تنشيط</button>`;
                } else {
                    actions += ` <button class="btn-warning btn-sm" onclick="CRUDApi.disableStudent(${s.id})">أرشفة</button>`;
                }
                actions += ` <button class="btn-danger btn-sm" onclick="CRUDApi.deleteStudent(${s.id})">حذف</button>`;
            }
            const rowStyle = s.status === 'inactive' ? 'opacity: 0.6; background-color: #f9f9f9;' : '';
            const statusBadge = s.status === 'inactive' ? `<span class="status-pill" style="background:#e5e7eb; color:#374151; margin-right:5px;">مؤرشف</span>` : '';
            return `<tr style="${rowStyle}">
                <td>${s.id}</td>
                <td><a href="#" onclick="openStudentProfile(event, ${sJson})">${escapeHtml(s.full_name_ar)}</a> ${statusBadge}</td>
                <td>${s.enrollment_date || ''}</td>
                <td><span class="status-pill" style="color:var(--danger-color); background:#fef2f2; border-color:#fca5a5; padding: 2px 8px;">${s.absences || 0}</span></td>
                <td><span style="font-weight:600; color:${s.balance > 0 ? 'var(--danger-color)' : 'var(--success-color)'};">${s.balance || 0} EGP</span></td>
                <td>${actions}</td>
            </tr>`;
        }).join('');
        
        // Re-apply text filter if there's any
        const q = document.getElementById('search-student').value;
        if(q) filterStudents(q);
        
    } catch(e) {
        console.error(e);
        Toast.error('فشل في جلب الطلاب');
    }
}

window.app = window.app || {};

window.app.exportClassReportPDF = async () => {
    const classId = document.getElementById('class-profile-id')?.value;
    const className = document.getElementById('class-profile-name')?.textContent;
    if (!classId) return;

    try {
        const [gradesData, attendanceData] = await Promise.all([
            API.get(`/reports/gradebook/${classId}`),
            API.get(`/reports/attendance/${classId}`)
        ]);

        const container = document.getElementById('pdf-report-container');
        
        let html = `
            <div style="text-align: center; margin-bottom: 20px;">
                <h1>تقرير الفصل الدراسي</h1>
                <h2>الفصل: ${className}</h2>
                <p>تاريخ الإصدار: ${new Date().toLocaleDateString('ar-EG')}</p>
            </div>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;" border="1">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 8px;">اسم الطالب</th>
                        <th style="padding: 8px;">النسبة المئوية (الدرجات)</th>
                        <th style="padding: 8px;">نسبة الغياب</th>
                    </tr>
                </thead>
                <tbody>
        `;

        gradesData.students.forEach(st => {
            const attStudent = attendanceData.students.find(a => a.id === st.id);
            const absentRate = attStudent ? attStudent.absent_rate : 0;
            html += `
                <tr>
                    <td style="padding: 8px;">${st.name}</td>
                    <td style="padding: 8px; text-align: center;" dir="ltr">${st.total_percentage}%</td>
                    <td style="padding: 8px; text-align: center;" dir="ltr">${absentRate}%</td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
        `;

        container.innerHTML = html;
        container.parentElement.style.display = 'block';

        const opt = {
            margin:       10,
            filename:     `تقرير_فصل_${className}.pdf`,
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2 },
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };

        await html2pdf().set(opt).from(container).save();
        container.parentElement.style.display = 'none';

    } catch(e) {
        Toast.error('فشل في إنشاء التقرير');
        console.error(e);
    }
};

window.app.exportStudentReportPDF = async () => {
    const studentId = document.getElementById('profile-student-id').value;
    const studentName = document.getElementById('profile-name').textContent;
    if (!studentId) return;

    try {
        const [student, enrollments, finance, notes, levels] = await Promise.all([
            API.get(`/students/${studentId}`),
            API.get(`/students/${studentId}/enrollments`),
            API.get(`/students/${studentId}/finance`),
            API.get(`/students/${studentId}/notes`),
            API.get(`/students/${studentId}/levels`)
        ]);

        const container = document.getElementById('pdf-report-container');
        
        let html = `
            <div style="text-align: center; margin-bottom: 20px;">
                <h1>تقرير أداء الطالب</h1>
                <h2>الطالب: ${studentName}</h2>
                <p>رقم الهاتف: ${student.contact_phone || 'غير مسجل'}</p>
                <p>تاريخ الإصدار: ${new Date().toLocaleDateString('ar-EG')}</p>
            </div>
            
            <h3>الفصول المسجلة</h3>
            <ul>
                ${enrollments.map(e => `<li>${e.class_name} (تاريخ التسجيل: ${e.enrolled_at.split('T')[0]})</li>`).join('') || '<li>لا يوجد</li>'}
            </ul>

            <h3>مستويات المواد</h3>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;" border="1">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 8px;">المادة</th>
                        <th style="padding: 8px;">المستوى الحالي</th>
                    </tr>
                </thead>
                <tbody>
                    ${levels.map(l => `
                        <tr>
                            <td style="padding: 8px;">${l.subject_name}</td>
                            <td style="padding: 8px;">${l.current_level_name}</td>
                        </tr>
                    `).join('') || '<tr><td colspan="2" style="text-align:center;">لا يوجد بيانات</td></tr>'}
                </tbody>
            </table>

            <h3>الوضع المالي</h3>
            <p>إجمالي الفواتير: ${finance.summary.total_amount}</p>
            <p>المدفوع: ${finance.summary.total_paid}</p>
            <p>المتبقي: <span style="color:red;">${finance.summary.total_remaining}</span></p>
        `;

        container.innerHTML = html;
        container.parentElement.style.display = 'block';

        const opt = {
            margin:       10,
            filename:     `تقرير_طالب_${studentName}.pdf`,
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2 },
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };

        await html2pdf().set(opt).from(container).save();
        container.parentElement.style.display = 'none';

    } catch(e) {
        Toast.error('فشل في إنشاء التقرير');
        console.error(e);
    }
};
