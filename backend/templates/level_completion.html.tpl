<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>شهادة اجتياز مستوى - {{ certificate_id }}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&family=Amiri:ital,wght@0,400;0,700;1,400&display=swap');
        
        body {
            font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f4f8;
            background-image: radial-gradient(#e2e8f0 1px, transparent 1px);
            background-size: 20px 20px;
            margin: 0;
            padding: 40px;
            text-align: center;
        }
        .certificate-wrapper {
            background-color: white;
            padding: 20px;
            max-width: 850px;
            margin: 0 auto;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1), 0 5px 15px rgba(0,0,0,0.05);
            position: relative;
        }
        .certificate-container {
            border: 4px double #d4af37; /* Gold double border */
            padding: 50px;
            position: relative;
            background: linear-gradient(135deg, #ffffff 0%, #fdfbf7 100%);
        }
        .certificate-container::before {
            content: '';
            position: absolute;
            top: 10px; left: 10px; right: 10px; bottom: 10px;
            border: 1px solid #1e3a8a; /* Navy inner border */
            pointer-events: none;
        }
        .header {
            margin-bottom: 40px;
        }
        .header h1 {
            color: #d4af37;
            font-family: 'Amiri', serif;
            font-size: 3.5rem;
            font-weight: 700;
            margin: 0;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
        }
        .header h2 {
            color: #1e3a8a; /* Navy blue */
            font-size: 1.8rem;
            font-weight: 600;
            margin-top: 10px;
            letter-spacing: 1px;
        }
        .content {
            font-size: 1.4rem;
            line-height: 2;
            color: #334155;
            margin-bottom: 40px;
        }
        .student-name {
            font-family: 'Amiri', serif;
            font-size: 2.5rem;
            font-weight: bold;
            color: #1e3a8a;
            border-bottom: 2px solid #d4af37;
            display: inline-block;
            padding: 0 40px 10px 40px;
            margin: 30px 0;
        }
        .footer {
            display: flex;
            justify-content: space-between;
            margin-top: 60px;
            padding-top: 20px;
            position: relative;
        }
        .signature-block {
            text-align: center;
            width: 250px;
        }
        .signature-block p {
            margin: 5px 0;
            color: #64748b;
            font-size: 1.1rem;
        }
        .signature-block strong {
            display: block;
            margin-top: 10px;
            font-size: 1.3rem;
            color: #1e3a8a;
            border-top: 1px dashed #cbd5e1;
            padding-top: 10px;
        }
        .badge {
            position: absolute;
            top: 40px;
            right: 40px;
            background: linear-gradient(135deg, #d4af37 0%, #b89324 100%);
            color: white;
            width: 100px;
            height: 100px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.5rem;
            box-shadow: 0 4px 10px rgba(212, 175, 55, 0.4);
            border: 4px solid white;
            z-index: 10;
        }
        .cert-id {
            position: absolute;
            bottom: -35px;
            left: 0;
            font-size: 0.9rem;
            color: #94a3b8;
            font-family: monospace;
        }
        .seal {
            width: 120px;
            height: 120px;
            border: 2px dashed #1e3a8a;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #1e3a8a;
            font-size: 0.9rem;
            opacity: 0.5;
            margin: 0 auto;
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
        }
        @media print {
            body { background: white; padding: 0; }
            .certificate-wrapper { box-shadow: none; max-width: 100%; margin: 0; padding: 10px; }
            .badge { box-shadow: none; border: 2px solid #d4af37; background: #d4af37 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
            .certificate-container { border: 4px double #d4af37; background: white !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
            button { display: none !important; }
        }
    </style>
</head>
<body>
    <div class="certificate-wrapper">
        <div class="certificate-container">
            <div class="badge">تفوق</div>
            <div class="header">
                <h1>شهادة اجتياز مستوى</h1>
                <h2>{{ institution_name }}</h2>
            </div>
            
            <div class="content">
                تشهد إدارة الأكاديمية بأن الطالب/ـة:<br>
                <div class="student-name">{{ student_name }}</div><br>
                قد اجتاز بنجاح المستوى الدراسي المقرّر بجدارة واستحقاق، وتم ترفيعه إلى المستوى التالي.<br>
                مع تمنياتنا بدوام التوفيق والنجاح.
            </div>
            
            <div class="footer">
                <div class="signature-block">
                    <p>تاريخ الإصدار</p>
                    <strong>{{ issue_date }}</strong>
                </div>
                <div class="seal">الختم الرسمي</div>
                <div class="signature-block">
                    <p>المدير العام</p>
                    <strong>إدارة {{ institution_name }}</strong>
                </div>
                <div class="cert-id">رقم الشهادة: {{ certificate_id }}</div>
            </div>
        </div>
    </div>
    
    <div style="margin-top: 20px; display: flex; justify-content: center; gap: 10px;" class="no-print">
        <button onclick="window.print()" style="padding: 10px 20px; background-color: #2563eb; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem;">طباعة الشهادة</button>
        <button onclick="downloadAsImage()" style="padding: 10px 20px; background-color: #059669; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1rem; font-family: 'Cairo', sans-serif;">تنزيل الشهادة</button>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js" defer></script>
    <script>
        function downloadAsImage() {
            const btn = event.target;
            const originalText = btn.innerText;
            btn.innerText = 'جاري التحضير...';
            btn.disabled = true;
            
            html2canvas(document.querySelector('.certificate-wrapper'), {scale: 1.5, useCORS: false, logging: false, backgroundColor: "#ffffff"}).then(canvas => {
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
