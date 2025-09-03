
# DocSign Plus (Python-only, optional features)

ویژگی‌ها:
- آپلود PDF + نسخه‌بندی خودکار
- امضای دیجیتال RSA + اعتبارسنجی
- صفحه‌های HTML ساده برای دمو (بدون ساخت فرانت‌اند)
- لیست/جزییات/دانلود/حذف سند
- کلیدهای دمو برای کاربر نمونه (در DB ذخیره می‌شود - فقط برای دمو)
- خروجی CSV از لاگ‌ها: /audit.csv
- OOP: EncryptionManager / DatabaseConnector / DocumentManager

## نصب
python -m venv venv
.\venv\Scripts\Activate.ps1  (Windows)   |   source venv/bin/activate  (Linux/Mac)
pip install -r requirements.txt

## راه‌اندازی دیتابیس
python manage.py makemigrations
python manage.py migrate

## اجرا
python manage.py runserver 8000
باز کن: http://127.0.0.1:8000/

## تست سریع
- صفحه اصلی: فرم آپلود + لینک‌ها
- اسناد: /docs/
- APIها: /api/upload/ , /api/sign/<id>/ , /api/verify/<id>/ , /hello/
- کلید دمو: /api/keys/ensure/ (فقط دمو)
- CSV لاگ: /audit.csv
