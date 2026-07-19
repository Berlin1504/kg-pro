function formatCurrency(amount) {
    const num = parseFloat(amount);
    if (isNaN(num)) return "0 ج.م";
    return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' ج.م';
}

const invoices = [
    { student_name: "Ahmed", title: "Test", amount: 1200, paid_amount: 0, remaining: 1200, status: "unpaid", student_id: 1, id: 1 }
];

const window = { currentUser: { role: 'boss' } };

try {
    const html = invoices.map(i => `
                <tr>
                    <td>${i.student_name}</td>
                    <td>${i.title}</td>
                    <td>${formatCurrency(i.amount)}</td>
                    <td class="text-success">${formatCurrency(i.paid_amount)}</td>
                    <td class="text-danger">${formatCurrency(i.remaining)}</td>
                    <td>${i.status === 'paid' ? 'مدفوعة' : i.status === 'partial' ? 'مدفوعة جزئياً' : 'غير مدفوعة'}</td>
                    <td>
                        ${i.remaining > 0 ? `<button class="btn-primary" onclick="FinanceUI.openPaymentModal(${i.student_id}, ${i.id}, ${i.remaining})">تسجيل دفعة</button>` : ''}
                        ${(i.paid_amount == 0 && window.currentUser && window.currentUser.role === 'boss') ? `<button class="btn-danger" onclick="FinanceUI.deleteInvoice(${i.id})">حذف</button>` : ''}
                    </td>
                </tr>
            `).join('');
    print("Success:");
    print(html);
} catch (e) {
    print("Error:");
    print(e);
}
