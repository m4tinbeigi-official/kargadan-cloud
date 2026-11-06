# راهنمای جامع و مرجع فنی API سکوی ابری کرگدن (kargadan.ir)

این مستند مرجع فنی و مهندسی معکوس‌شده کامل از زیرساخت ارتباطی و ای‌پی‌آی (API) سکوی ابری کرگدن است که به شما امکان می‌دهد تمام قابلیت‌های پنل (مدیریت سرورهای ابری، تغییر وضعیت خاموش/روشن/ریستارت، ساخت ماشین جدید، ریسایز، بک‌آپ و اسنپ‌شات، کلیدهای SSH، امور مالی و تیکت‌ها) را به صورت خودکار و از طریق اسکریپت و کلاینت برنامه‌نویسی کنترل کنید.

---

## ۱. معماری کلی سیستم و پروتکل ارتباطی

پلتفرم کرگدن بر پایه تکنولوژی‌های زیر توسعه یافته است:
* **فرانت‌اند و لایه ارکستراسیون:** فریم‌ورک Next.js (نسخه ۱۴ و ۱۵ با معماری App Router).
* **لایه احراز هویت:** کتابخانه استاندارد Auth.js (NextAuth v5) با کوکی سشن امضاشده.
* **موتور ارتباطی کلاینت-سرور:** پروتکل Next.js Server Actions از طریق هدر `Next-Action` به همراه پاسخ‌های استریم کامپوننت‌های سمت سرور (React Server Components / RSC).
* **موتور مجازی‌سازی پایه:** کلاستر ابری متن‌باز اوپن‌نبیولا (OpenNebula / ONE) با مجازی‌ساز KVM.
* **درگاه پشتیبان:** هسته Avocado GraphQL در پشت سرورهای Next.js.

### سه روش اصلی برای برقراری ارتباط با API:
1. **روش اول (توصیه‌شده و مستقیم):** ارسال مستقیم درخواست HTTP POST به سرور با هدر `Next-Action` و کوکی سشن معتبر.
2. **روش دوم (همگام‌سازی با مرورگر مک):** اجرای اسکریپت درون تب فعال گوگل کروم سیستم از طریق اپل‌اسکریپت (AppleScript IPC) که کوکی‌های محافظت‌شده `HttpOnly` را به صورت خودکار به ارث می‌برد.
3. **روش سوم (توکن JWT Bearer):** استفاده از توکن `accessToken` به دست آمده از سشن برای فراخوانی مستقیم مایکروسرویس‌ها.

---

## ۲. احراز هویت و مدیریت نشست (Authentication)

احراز هویت در کرگدن بر پایه سشن‌های نشست Auth.js استوار است که کوکی `authjs.session-token` (یا `__Secure-authjs.session-token` روی پروتکل امن HTTPS) را روی کلاینت ذخیره می‌کند.

### چرخه لاگین با کد یک‌بار مصرف پیامکی (OTP):

#### مرحله ۱: ارسال شماره و درخواست پیامک کد
* **متد:** `POST`
* **آدرس:** `https://kargadan.ir/auth/login/otp`
* **هدرها:**
  ```http
  Next-Action: 4050db76e9473e24037587108bbe73ef9886880eed
  Content-Type: application/json
  Accept: text/x-component
  ```
* **بدنه درخواست (JSON Array):**
  ```json
  [
    {
      "cellphone": "09123456789"
    }
  ]
  ```
* **پاسخ سرور:** کد با موفقیت پیامک شده و تایمر ۱۲۰ ثانیه فعال می‌شود.

#### مرحله ۲: دریافت توکن CSRF
قبل از ارسال کد، توکن CSRF دریافت می‌شود:
* **متد:** `GET`
* **آدرس:** `https://kargadan.ir/api/auth/csrf`
* **نمونه پاسخ:**
  ```json
  {
    "csrfToken": "957c3a71137f253eb14ed60346b5d126ddedce4d1333a331b28703715832b1e0"
  }
  ```

#### مرحله ۳: ثبت کد تایید ۵ رقمی و دریافت کوکی سشن
* **متد:** `POST`
* **آدرس:** `https://kargadan.ir/api/auth/callback/otp`
* **هدرها:**
  ```http
  Content-Type: application/x-www-form-urlencoded
  X-Auth-Return-Redirect: 1
  ```
* **بدنه درخواست (URL Encoded):**
  ```text
  cellphone=09123456789&code=12345&referrer_code=&csrfToken=957c3a...&callbackUrl=https%3A%2F%2Fkargadan.ir%2Fdashboard
  ```
* **پاسخ سرور:** سرور هدر `Set-Cookie` حاوی `authjs.session-token` را ارسال کرده و کاربر لاگین می‌شود.

#### استخراج توکن JWT نشست:
پس از ورود، با فراخوانی آدرس زیر توکن کامل JWT به همراه اطلاعات کاربر برمی‌گردد:
* **متد:** `GET`
* **آدرس:** `https://kargadan.ir/api/auth/session`

---

## ۳. کاتالوگ کامل اکشن‌های سرور (Server Actions Reference)

در جدول زیر، شناسه‌های هش‌شده هر اکشن (Action ID) و پارامترهای دقیق آن گردآوری شده است:

| دسته‌بندی | نام اکشن | شناسه اکشن (Action ID) | پارامترهای ورودی | کارکرد |
| :--- | :--- | :--- | :--- | :--- |
| **اطلاعات حساب** | `GetMe` | `00ebc0d0b18fa652247eca82cb58cfc282e40a0d1e` | `[]` | واکشی مشخصات کامل کاربر، موجودی کیف پول و سطح کاربری |
| **ماشین‌های ابری** | `CloudMachinesClient` | `4015ad04fdca6ef1345bb2440f262c57c5f8f53e1b` | `[{"page":1,"limit":50,"sort_by":"DESC","sort_field":"ID"}]` | دریافت لیست تمام سرورهای مجازی حساب |
| **جزئیات ماشین** | `CloudMachineClient` | `40b8d653f88a301a89c7ef902fbd71c43e511083c2` | `[{"id":"<machine_id>"}]` | دریافت اطلاعات دقیق سخت‌افزار، آی‌پی و پسورد سرور |
| **کنترل وضعیت پاور** | `MachineActionClient` | `40629f5e30edfe7a85648165cc82f12ba67454a6af` | `[{"machine_id":"<id>","action_name":"<ACTION>"}]` | خاموش/روشن، ریستارت و توقف سرور |
| **ساخت سرور جدید** | `MachineCreateClient` | `40b61394de498aceefe59eb349b2bfce06f7047472` | `[{"title":"...","cluster_id":"...","template_id":"...","cpu":2,"memory":4,"disk":20}]` | ایجاد و راه‌اندازی فوری ماشین ابری |
| **تغییر منابع (ریسایز)** | `MachineResizeClient` | `4045802c6bfb82f63ce532d3a63ededdbd2383437f` | `[{"machine_id":"<id>","cpu":4,"memory":8,"disk":40}]` | ارتقا یا کاهش منابع پردازنده، رم و دیسک |
| **تغییر پسورد روت** | `MachineResetPasswordClient` | `40290c6bf4f3a3b5ed10932e35fc79499d606e62d8` | `[{"id":"<machine_id>"}]` | ریست و تولید رمز عبور جدید روت سرور |
| **نصب مجدد (ریبیلد)** | `MachineRebuildClient` | `402ff5abcfc1634e83946729b277a3fcf287f7726a` | `[{"id":"<machine_id>","template_id":"<tpl_id>"}]` | بازسازی کامل سیستم‌عامل سرور |
| **حذف سرور** | `MachineDeleteClient` | `400c6f874d96143e3a01e732f79b97b9184d4a2d84` | `[{"id":"<machine_id>"}]` | حذف دائم ماشین و آزادسازی منابع |
| **لاگ‌های سرور** | `CloudMachineLogsClient` | `402f4b196ff8db9c13a7d3741928ba8789d885648e` | `[{"machine_id":"<id>"}]` | تاریخچه عملیات‌های انجام‌شده روی سرور |
| **نمودار مصرف منابع** | `CloudMachineGraphClient` | `4031661af8757665aba773bb3c619e550fcb99e238` | `[{"id":"<id>","graph_count":1000}]` | مانیتورینگ زنده CPU، رم، دیسک و ترافیک |
| **کلاسترها** | `CloudClustersClient` | `406d51c17008cd7eadbff8906eedac547d04ed0084` | `[]` | لیست کلاسترها و دیتاسنترها (فناوا، افرانت، امام خمینی) |
| **تمپلیت‌های سیستم‌عامل** | `CloudTemplatesClient` | `40cd8214ad4ac8752c5a86dd34f185e09fd02555ef` | `[{"cluster_id":"<cluster_id>"}]` | لیست ایمیج‌های سیستم‌عامل در کلاستر انتخابی |
| **ایجاد اسنپ‌شات** | `SnapshotCreateClient` | `40941114ca4d50a1dd54b56cdd8f59312352546750` | `[{"machine_id":"<id>","name":"<name>"}]` | ساخت اسنپ‌شات لحظه‌ای از دیسک سرور |
| **بازگردانی اسنپ‌شات** | `SnapshotRestoreClient` | `406aedb660293ce061f359ff9ec2ab4f08714f41c3` | `[{"machine_id":"<id>","snapshot_id":"<sid>"}]` | ریستور کردن دیسک به اسنپ‌شات مشخص |
| **کلیدهای SSH** | `CertificateCreateClient` | `405e18397fa8c182e2dbd64a0bc82b224718dec9ac` | `[{"title":"...","public_key":"ssh-rsa ..."}]` | افزودن پابلیک کی SSH جهت اتصال بدون پسورد |
| **شارژ کیف پول** | `WalletChargeClient` | `40c19e7616b0699caed120d97549e55bd5d5c568d8` | `[{"amount":1000000}]` | ایجاد درخواست شارژ اعتبار کیف پول |
| **دریافت لینک درگاه** | `PaymentGetUrlClient` | `40fe4a898955f8d6181c38a19f6e0eb4098b2d5854` | `[{"gateway":"...","amount":...}]` | دریافت لینک پرداخت بانکی شتابی |
| **فاکتورها** | `InvoicesClient` | `40cba87cb5fdb66301c4026405d3484a824691c49c` | `[{"page":1,"limit":50}]` | لیست فاکتورها و وضعیت پرداخت |
| **تیکت‌ها** | `TicketsClient` | `40d858a6444acdbc73bedaa312d6fa91924a033f56` | `[{"page":1,"limit":50}]` | لیست تیکت‌های پشتیبانی |
| **ایجاد تیکت** | `TicketCreate` | `40a45de2c0e17856084a9ec36f942c44a382ce9077` | `[{"title":"...","department_id":"...","priority":"...","message":"..."}]` | ارسال تیکت جدید به پشتیبانی فنی |

---

## ۴. مقادیر مجاز برای کنترل پاور ماشین (Machine Actions)

فیلد `action_name` در اکشن `MachineActionClient` منحصراً مقادیر زیر را می‌پذیرد:
* `RESUME`: روشن کردن سرور خاموش‌شده (Power On / Start).
* `POWEROFF`: خاموش کردن نرم‌افزاری و ایمن سرور (Graceful ACPI Shutdown).
* `POWEROFF_HARD`: قطع برق سخت‌افزاری سرور (Force Power Off).
* `REBOOT`: راه‌اندازی مجدد نرم‌افزاری (Soft Reboot).
* `REBOOT_HARD`: ریست سخت‌افزاری سیستم (Hard Reset).

---

## ۵. نمونه فراخوانی خام با cURL

### نمونه ۱: دریافت لیست سرورها
```bash
curl -X POST https://kargadan.ir/dashboard \
  -H "Next-Action: 4015ad04fdca6ef1345bb2440f262c57c5f8f53e1b" \
  -H "Content-Type: application/json" \
  -H "Accept: text/x-component" \
  -H "Cookie: authjs.session-token=YOUR_SESSION_TOKEN_HERE" \
  -d '[{"page":1,"limit":10,"sort_by":"DESC","sort_field":"ID"}]'
```

### نمونه ۲: ریستارت کردن سرور
```bash
curl -X POST https://kargadan.ir/dashboard/machines/<MACHINE_ID> \
  -H "Next-Action: 40629f5e30edfe7a85648165cc82f12ba67454a6af" \
  -H "Content-Type: application/json" \
  -H "Accept: text/x-component" \
  -H "Cookie: authjs.session-token=YOUR_SESSION_TOKEN_HERE" \
  -d '[{"machine_id":"<MACHINE_ID>","action_name":"REBOOT"}]'
```

---

## ۶. ساختار پاسخ سرور و نحوه پارس کردن داده‌های RSC

سرور پاسخ‌ها را در قالب استریم تکست بازمی‌گرداند. هر سطر دارای فرمت `<INDEX>:<JSON_PAYLOAD>` است:
```text
0:{"a":"$@1","f":"","q":"","i":false,"b":"8Ufe0L1_dnqW3F9puGmYs"}
1:{"CloudMachinesClient":{"data":[{"id":"vm-abc12","title":"my-server","status":"1","status_human":"فعال","state":"POWER_ON","state_title":"روشن","one_vm_id":"15000","password":"...","cpu":"2","memory":"4","disk":"20","ip":[{"ip":"185.143.232.10"}]}]}}
```
بخش اصلی دیتای هر اکشن همواره درون کلید ایندکس `1` قرار دارد.

---

## ۷. کتابخانه کامل و آماده پایتون (SDK)

کد کامل ماژولار پایتون در مسیر `projects/kargadan-api/client.py` پیاده‌سازی شده است و نیازی به نصب هیچ پکیج اضافه‌ای ندارد (صرفاً کتابخانه استاندارد پایتون):

```python
from client import KargadanClient

# اتصال خودکار به سشن فعال کروم در مک
client = KargadanClient()

# دریافت مشخصات کاربر و موجودی
me = client.get_me()
print(me["GetMe"]["fullname"], me["GetMe"]["wallet"]["credit"])

# لیست سرورها
machines = client.list_machines()
for m in machines:
    print(m["id"], m["title"], m["ip"][0]["ip"], m["state"])

# کنترل پاور (ریستارت سرور)
client.machine_action("<MACHINE_ID>", "REBOOT")

# دریافت مشخصات کامل و پسورد اولیه سرور
details = client.get_machine("<MACHINE_ID>")
print("Password:", details["password"])
```

---

## ۸. دستورات خط فرمان (CLI) آماده اجرا

ابزار کامندلاین در مسیر `projects/kargadan-api/cli.py` قرار دارد و دستورات زیر را پوشش می‌دهد:

```bash
# مشاهده مشخصات حساب و موجودی
python3 projects/kargadan-api/cli.py me

# مشاهده لیست کامل ماشین‌ها
python3 projects/kargadan-api/cli.py list

# مشاهده جزئیات یک سرور مشخص
python3 projects/kargadan-api/cli.py info <MACHINE_ID>

# ریستارت کردن سرور
python3 projects/kargadan-api/cli.py power <MACHINE_ID> --action reboot

# خاموش کردن سرور
python3 projects/kargadan-api/cli.py power <MACHINE_ID> --action poweroff

# روشن کردن سرور
python3 projects/kargadan-api/cli.py power <MACHINE_ID> --action resume

# مشاهده فاکتورها
python3 projects/kargadan-api/cli.py invoices

# مشاهده تیکت‌های پشتیبانی
python3 projects/kargadan-api/cli.py tickets
```
