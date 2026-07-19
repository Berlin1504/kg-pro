const API = {
    getCSRFToken() {
        const match = document.cookie.match(new RegExp('(^| )csrf_token=([^;]+)'));
        return match ? match[2] : '';
    },

    async parseError(res) {
        try {
            const data = await res.json();
            return data.detail || data.message || 'API Error';
        } catch (e) {
            return 'API Error';
        }
    },

    async login(email, password) {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
            credentials: 'same-origin'
        });
        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || 'Login failed');
        }
        return res.json();
    },

    async logout() {
        await fetch('/api/logout', { method: 'POST', credentials: 'same-origin' });
    },

    async getMe() {
        const res = await fetch('/api/me', { credentials: 'same-origin' });
        if (!res.ok) {
            throw new Error('Not authenticated');
        }
        return res.json();
    },

    async get(path) {
        const res = await fetch(`/api${path}`, { credentials: 'same-origin' });
        if (!res.ok) throw new Error(await this.parseError(res));
        return res.json();
    },

    async post(path, data) {
        const res = await fetch(`/api${path}`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRF-Token': this.getCSRFToken()
            },
            body: JSON.stringify(data),
            credentials: 'same-origin'
        });
        if (!res.ok) throw new Error(await this.parseError(res));
        return res.json();
    },

    async delete(path) {
        const res = await fetch(`/api${path}`, {
            method: 'DELETE',
            headers: { 'X-CSRF-Token': this.getCSRFToken() },
            credentials: 'same-origin'
        });
        if (!res.ok) throw new Error(await this.parseError(res));
        return res.json();
    },

    async put(path, data) {
        const res = await fetch(`/api${path}`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRF-Token': this.getCSRFToken()
            },
            body: JSON.stringify(data),
            credentials: 'same-origin'
        });
        if (!res.ok) throw new Error(await this.parseError(res));
        return res.json();
    }
};

const FinanceAPI = {
    getFeeTemplates: async () => API.get('/finance/fee-templates'),
    addFeeTemplate: async (data) => API.post('/finance/fee-templates', data),
    deleteFeeTemplate: async (id) => API.delete(`/finance/fee-templates/${id}`),
    
    getInvoices: async (status, from, to) => {
        let q = [];
        if(status) q.push(`status=${status}`);
        if(from) q.push(`from_date=${from}`);
        if(to) q.push(`to_date=${to}`);
        let qs = q.length ? '?' + q.join('&') : '';
        return API.get('/finance/invoices' + qs);
    },
    addInvoice: async (data) => API.post('/finance/invoices', data),
    bulkInvoice: async (data) => API.post('/finance/invoices/bulk', data),
    deleteInvoice: async (id) => API.delete(`/finance/invoices/${id}`),
    
    getPayments: async (from, to) => {
        let q = [];
        if(from) q.push(`from_date=${from}`);
        if(to) q.push(`to_date=${to}`);
        let qs = q.length ? '?' + q.join('&') : '';
        return API.get('/finance/payments' + qs);
    },
    addPayment: async (data) => API.post('/finance/payments', data),
    deletePayment: async (id) => API.delete(`/finance/payments/${id}`),
    
    getSalaries: async (month = "") => {
        const url = month ? `/finance/salaries?month=${month}` : `/finance/salaries`;
        return API.get(url);
    },
    addSalary: async (data) => API.post('/finance/salaries', data),
    generateSalaries: async (data) => API.post('/finance/salaries/bulk', data),
    paySalary: async (id) => API.post(`/finance/salaries/${id}/pay`, { status: 'paid' }),
    
    getExpenses: async () => API.get('/finance/expenses'),
    addExpense: async (data) => API.post('/finance/expenses', data),
    
    getReports: async (from, to) => {
        let q = [];
        if(from) q.push(`from_date=${from}`);
        if(to) q.push(`to_date=${to}`);
        let qs = q.length ? '?' + q.join('&') : '';
        return API.get('/finance/reports' + qs);
    },
    getSummary: async () => API.get('/finance/summary'),
    getDebts: async () => API.get('/finance/debts'),
    payDebt: async (invoiceId, data) => API.post(`/finance/debts/${invoiceId}/pay`, data),
    autoGenerateInvoices: async () => API.post('/finance/auto-generate-invoices')
};

const NotesAPI = {
    createNote: function(data) {
        return API.post('/notes/', data);
    },
    getNotes: function(targetType, targetId) {
        return API.get(`/notes/${targetType}/${targetId}`);
    },
    deleteNote: async (noteId) => API.delete(`/notes/${noteId}`)
};

const ExamsAPI = {
    getExams: async (classId) => API.get(classId ? `/exams/?class_id=${classId}` : '/exams/'),
    createExam: async (examData) => API.post('/exams/', examData),
    getExamDetails: async (examId) => API.get(`/exams/${examId}`),
    submitScores: async (examId, scoresData) => API.post(`/exams/${examId}/scores`, scoresData),
    publishExam: async (examId) => API.post(`/exams/${examId}/publish`, {})
};

const PromotionsAPI = {
    getPendingProposals: async () => API.get('/promotions/'),
    makeDecision: async (proposalId, decisionData) => API.post(`/promotions/${proposalId}/decision`, decisionData)
};

const ProfileAPI = {
    getStudentProfile: function(id) {
        return API.get(`/students/${id}/profile`);
    },
    getClassProfile: function(id) {
        return API.get(`/classes/${id}/profile`);
    },
    getClassRoster: function(id) {
        return API.get(`/classes/${id}/students`);
    }
};

const StaffAPI = {
    getAll: async () => API.get('/staff/'),
    create: async (data) => API.post('/staff/', data),
    update: async (id, data) => {
        const res = await fetch(`/api/staff/${id}`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRF-Token': API.getCSRFToken()
            },
            body: JSON.stringify(data),
            credentials: 'same-origin'
        });
        if (!res.ok) throw new Error(await API.parseError(res));
        return res.json();
    },
    changePassword: async (id, password) => {
        const res = await fetch(`/api/staff/${id}/password`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRF-Token': API.getCSRFToken()
            },
            body: JSON.stringify({ password }),
            credentials: 'same-origin'
        });
        if (!res.ok) throw new Error(await API.parseError(res));
        return res.json();
    },
    deactivate: async (id) => API.delete(`/staff/${id}`)
};

const SettingsAPI = {
    get: async () => API.get('/settings/'),
    update: async (settingsObj) => {
        const res = await fetch('/api/settings/', {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRF-Token': API.getCSRFToken()
            },
            body: JSON.stringify({ settings: settingsObj }),
            credentials: 'same-origin'
        });
        if (!res.ok) throw new Error(await API.parseError(res));
        return res.json();
    }
};

const DatabaseAPI = {
    wipe: async (password) => API.post('/db/wipe', { password }),
    upload: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch('/api/db/upload', {
            method: 'POST',
            headers: { 'X-CSRF-Token': API.getCSRFToken() },
            body: formData,
            credentials: 'same-origin'
        });
        if (!res.ok) throw new Error(await API.parseError(res));
        return res.json();
    }
};
