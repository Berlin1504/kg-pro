<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إيصال دفع</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Amiri:ital,wght@0,400;0,700;1,400&display=swap');
        
        body {
            font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f1f5f9;
            margin: 0;
            padding: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .receipt-wrapper {
            background-color: white;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .receipt {
            border: 2px solid #0f172a;
            padding: 40px;
            position: relative;
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        }
        .header {
            text-align: center;
            border-bottom: 2px dashed #cbd5e1;
            padding-bottom: 20px;
            margin-bottom: 40px;
            position: relative;
        }
        .header h1 {
            color: #0f172a;
            font-family: 'Amiri', serif;
            font-size: 2.8em;
            margin: 0 0 5px 0;
            font-weight: 700;
        }
        .header h2 {
            color: #1e40af;
            font-size: 1.5em;
            margin: 0;
            letter-spacing: 1px;
        }
        .receipt-number {
            position: absolute;
            left: 0;
            top: 0;
            background: #f1f5f9;
            padding: 5px 15px;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            font-family: monospace;
            font-weight: bold;
            color: #475569;
        }
        .content {
            font-size: 1.25em;
            line-height: 2.2;
        }
        .content strong {
            display: inline-block;
            width: 160px;
            color: #475569;
            font-weight: 600;
        }
        .amount-highlight {
            font-size: 1.4em;
            font-weight: bold;
            color: #b91c1c;
            background: #fef2f2;
            padding: 0 10px;
            border-radius: 4px;
            border: 1px dashed #f87171;
        }
        .footer {
            margin-top: 60px;
            display: flex;
            justify-content: space-between;
            border-top: 1px solid #e2e8f0;
            padding-top: 20px;
            font-size: 0.95em;
            color: #64748b;
        }
        .signature {
            text-align: center;
            margin-top: 50px;
            width: 250px;
        }
        .signature-line {
            display: inline-block;
            width: 100%;
            border-bottom: 2px solid #0f172a;
            margin-bottom: 10px;
        }
        .watermark {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-30deg);
            font-size: 8rem;
            color: rgba(30, 64, 175, 0.03);
            font-weight: 800;
            white-space: nowrap;
            pointer-events: none;
            user-select: none;
            z-index: 0;
        }
        @media print {
            body { background: white; padding: 0; }
            .receipt-wrapper { box-shadow: none; padding: 0; max-width: 100%; margin: 0; }
            .amount-highlight { border: 1px solid #000; background: none; color: #000; }
            button { display: none !important; }
        }
    </style>
</head>
<body>
    <div class="receipt-wrapper">
        <div class="receipt">
            <div class="watermark">تم الدفع</div>
            <div class="header">
                <div class="receipt-number">#{{certificate_id}}</div>
                <h1>{{ institution_name }}</h1>
                <h2>إيصال دفع (سند قبض)</h2>
            </div>
            
            <div class="content" style="position: relative; z-index: 1;">
                <p><strong>التاريخ:</strong> {{date}}</p>
                <p><strong>استلمنا من الطالب/ة:</strong> <span style="color: #0f172a; font-weight: bold;">{{student_name}}</span></p>
                <p><strong>طريقة الدفع:</strong> {{payment_method}}</p>
                <p><strong>مبلغ وقدره:</strong> <span class="amount-highlight">{{amount}} {{currency}}</span></p>
                <p><strong>وذلك لقاء:</strong> {{invoice_title}}</p>
            </div>
            
            <div class="signature">
                <div class="signature-area">
                    <p>تم الاستلام بواسطة: <strong>{{received_by_name}}</strong></p>
                    <p>التوقيع: ____________________</p>
                </div>
            </div>
            
            <div class="footer">
                <span>طُبع في: {{date}}</span>
                <span>للتحقق من صحة الإيصال: يرجى مراجعة النظام برقم {{certificate_id}}</span>
            </div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 20px; width: 100%; display: flex; flex-direction: column; align-items: center; gap: 10px;" class="no-print">
        <button onclick="window.print()" style="padding: 10px 20px; background-color: #1e40af; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1rem; font-family: 'Cairo', sans-serif;">طباعة الإيصال</button>
        <button onclick="downloadAsImage()" style="padding: 10px 20px; background-color: #059669; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1rem; font-family: 'Cairo', sans-serif;">تنزيل الشهادة</button>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js" defer></script>
    <script>
        function downloadAsImage() {
            const btn = event.target;
            const originalText = btn.innerText;
            btn.innerText = 'جاري التحضير...';
            btn.disabled = true;
            
            html2canvas(document.querySelector('.receipt-wrapper'), {scale: 1.5, useCORS: false, logging: false, backgroundColor: "#ffffff"}).then(canvas => {
                let link = document.createElement('a');
                link.download = 'document.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
                btn.innerText = originalText;
                btn.disabled = false;
            }).catch(err => {
                alert('حدث خطأ أثناء تنزيل الصورة: ' + err.message);
                btn.innerText = originalText;
                btn.disabled = false;
            });
        }
    </script>
</body>
</html>
