# سکوی ابری کرگدن // Kargadan Cloud Python SDK & CLI

<div align="center">

[![CI](https://github.com/m4tinbeigi-official/kargadan-cloud/actions/workflows/ci.yml/badge.svg)](https://github.com/m4tinbeigi-official/kargadan-cloud/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)

</div>

کتابخانه پایتون، رابط برنامه‌نویسی (API) و ابزار خط فرمان اختصاصی جهت مدیریت جامع و خودکار سرورهای ابری ساعتی، سرورهای مجازی، وضعیت پاور، ماشین‌ها، امور مالی و تیکت‌ها در پلتفرم **کرگدن (kargadan.ir)**.

این پکیج به صورت صفر تا صد با تحلیل و مهندسی معکوس ساختار Next.js App Router و اکشن‌های سمت سرور (Next.js Server Actions) توسعه یافته است و بدون نیاز به نصب هیچ‌گونه پیش‌نیاز خارجی، صرفاً با کتابخانه استاندارد پایتون (Python Standard Library) کار می‌کند.

---

## قابلیت‌های کلیدی

* **مدیریت کامل ماشین‌های مجازی (Cloud VPS):** واکشی لیست سرورها، دریافت جزئیات سخت‌افزاری، آی‌پی، مک‌آدرس و کلمه عبور اولیه روت.
* **کنترل وضعیت پاور (Power Actions):** روشن کردن (`RESUME`)، خاموش کردن نرم‌افزاری (`POWEROFF`)، قطع برق سخت‌افزاری (`POWEROFF_HARD`)، راه‌اندازی مجدد نرم‌افزاری (`REBOOT`) و ریست سخت‌افزاری (`REBOOT_HARD`).
* **ارتقا و تغییر مشخصات (Resize):** تغییر تعداد هسته پردازنده (CPU)، مقدار رم (RAM) و حجم دیسک به صورت داینامیک.
* **مدیریت رمز عبور و بازسازی:** ریست کلمه عبور روت سرور و نصب مجدد سیستم‌عامل (Rebuild OS).
* **ساخت ماشین جدید (Machine Create):** استقرار فوری سرور ابری در کلاسترهای مختلف دیتاسنتری (افرانت، فناوا، مرکز زیرساخت امام خمینی).
* **پشتیبان‌گیری و اسنپ‌شات:** ایجاد، حذف و ریستور کردن اسنپ‌شات‌ها و بک‌آپ‌های دوره‌ای.
* **امور مالی و کیف‌پول:** بررسی اعتبار، موجودی کیف‌پول، صورت‌حساب‌ها و تاریخچه تراکنش‌ها.
* **کلیدهای SSH:** تعریف، مدیریت و اتصال کلیدهای عمومی SSH.
* **تیکت‌های پشتیبانی:** ارسال تیکت، مشاهده پاسخ‌ها و بستن تیکت.
* **پشتیبانی دوگانه از پلتفرم‌ها:**
  * **مک (macOS):** شناسایی خودکار تب باز در مرورگر گوگل کروم و استفاده ایمن از سشن بدون نیاز به افشای رمز عبور یا ذخیره کوکی در فایل متنی.
  * **لینوکس، ویندوز و سرورهای مستقل (Docker/VPS):** قابلیت ورود با شماره تلفن و کد یک‌بار مصرف پیامکی (OTP) یا کلمه عبور به همراه دریافت توکن سشن.

---

## ساختار مخزن

```text
├── client.py                 # کلاینت اصلی پایتون (KargadanClient)
├── cli.py                    # ابزار تعاملی خط فرمان (CLI)
├── example.py                # اسکریپت نمونه جامع و داینامیک
├── test_sdk.py               # تست‌های پایه اتصال و واکشی اطلاعات
├── test_machine.py           # تست اختصاصی مشخصات سرور
├── DOCS_API_REFERENCE.md     # مرجع کامل مهندسی معکوس و پروتکل ارتباطی
├── pyproject.toml            # پیکربندی استاندارد بسته پایتون
├── LICENSE                   # پروانه متن‌باز MIT
└── README.md                 # راهنمای حاضر
```

---

## نحوه استفاده در پایتون (SDK)

```python
from client import KargadanClient

# ۱. مقداردهی کلاینت (به صورت خودکار تب فعال کروم را شناسایی می‌کند)
client = KargadanClient()

# ۲. مشاهده اطلاعات حساب و موجودی
me = client.get_me()
user = me.get("GetMe", {})
print(f"کاربر: {user.get('fullname')}")
print(f"موجودی: {user.get('wallet', {}).get('credit'):,} تومان")

# ۳. دریافت لیست سرورهای ابری
machines = client.list_machines()
for m in machines:
    ip = m.get("ip", [{}])[0].get("ip")
    print(f"سرور: {m.get('title')} | آی‌پی: {ip} | وضعیت: {m.get('state')}")

# ۴. کنترل پاور (خاموش، روشن، ریستارت)
# client.machine_action("<MACHINE_ID>", "REBOOT")

# ۵. دریافت رمز عبور اولیه روت و مشخصات سرور
if machines:
    m_id = machines[0].get("id")
    details = client.get_machine(m_id)
    print("رمز عبور روت:", details.get("password"))
```

---

## ابزار خط فرمان (CLI)

این پکیج همراه با یک ابزار کامل کامندلاین ارائه شده است:

```bash
# مشاهده مشخصات کاربر و موجودی کیف‌پول
python3 cli.py me

# مشاهده لیست کامل ماشین‌های ابری
python3 cli.py list

# مشاهده جزئیات و پسورد یک سرور
python3 cli.py info <MACHINE_ID>

# عملیات کنترل پاور (روشن، خاموش، ریستارت)
python3 cli.py power <MACHINE_ID> --action reboot
python3 cli.py power <MACHINE_ID> --action poweroff
python3 cli.py power <MACHINE_ID> --action resume

# ریست کردن رمز عبور روت سرور
python3 cli.py reset-password <MACHINE_ID>

# مشاهده فاکتورهای مالی
python3 cli.py invoices

# مشاهده تیکت‌های پشتیبانی
python3 cli.py tickets
```

---

## مستندات فنی و مهندسی معکوس

برای دسترسی به لیست کامل شناسه‌های اکشن سرور (`Next-Action`)، هدرها، کدهای نمونه `cURL`، تحلیل لایه احراز هویت Auth.js و پاسخ‌های استریم RSC، فایل [DOCS_API_REFERENCE.md](DOCS_API_REFERENCE.md) را مطالعه نمایید.

---

## پروانه نرم‌افزاری

این پروژه تحت پروانه [MIT License](LICENSE) منتشر شده است.
