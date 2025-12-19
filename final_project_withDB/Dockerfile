# استخدام نسخة بايثون خفيفة
FROM python:3.11-slim

# إعداد مجلد العمل داخل الحاوية
WORKDIR /app

# 1. نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. نسخ باقي ملفات المشروع
COPY . .

# 3. إنشاء مستخدم عادي (للأمان)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 4. فتح المنفذ 5000
EXPOSE 5000

# 5. أمر التشغيل (يربط بملف run.py والمتغير app)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]