<div dir="rtl">

# ایونت پلنت | پلتفرم مدیریت و برنامه‌ریزی رویداد

پلتفرم ای‌پی‌آی‌محور برای مدیریت رویداد با دو نقش برگزارکننده و شرکت‌کننده، رویداد چندمرحله‌ای، ویژگی داینامیک بدون جیسون‌فیلد، ثبت‌نام، بازخورد و نتیجه. پیاده‌سازی با جنگو و داکر.

</div>

<div dir="rtl">

## ۱. تکنولوژی‌ها

</div>

- Python 3.12, Django, DRF
- JWT با SimpleJWT
- PostgreSQL 16, Redis 7
- Docker, Docker Compose

<div dir="rtl">

## ۲. ساختار پروژه

</div>

```text
config/settings/base.py
config/settings/dev.py
config/urls.py
core/ : user, register, login, roles
event/ : event, stage, attribute, registration, feedback, result
Dockerfile
docker-compose.yml
entrypoint.sh
```

<div dir="rtl">

## ۳. اجرا با داکر

فقط به داکر نیاز داری. اول فایل محیطی را بساز بعد بالا بیاور:

</div>

```bash
cp .env.example .env
docker-compose up --build
```

<div dir="rtl">

آدرس‌ها بعد از بالا آمدن:

وب روی پورت هشت‌هزار، دیتابیس روی پورت پنج‌هزاروچهارصدوه‌چهل‌ودو، ادمین جنگو روی مسیر ادمین.

مایگریشن خودکار با انتری‌پوینت اجرا می‌شود و نیازی به اجرای دستی نیست.

برای توقف:

</div>

```bash
docker-compose down
```

<div dir="rtl">

## ۴. متغیرهای محیطی

فایل نمونه محیطی را کنار کامپوز بساز:

</div>

```env
SECRET_KEY=dev-insecure-key-change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=eventplanet
DB_USER=eventuser
DB_PASSWORD=eventpass
DB_HOST=db
DB_PORT=5432
```

<div dir="rtl">

نکته مهم: نام‌های دیتابیس در سرویس وب و سرویس دیتابیس باید یکی باشند. اگر فایل محیطی نباشد، وب نباید کرش کند. پس در کامپوز برای سرویس وب مقدار پیش‌فرض بگذار.

## ۵. ساخت سوپریوزر

</div>

```bash
docker-compose exec web python manage.py createsuperuser
```

<div dir="rtl">

شماره موبایل باید یازده رقم و با صفرنه شروع شود. بعد می‌توانی وارد ادمین شوی.

## ۶. احراز هویت

مبنا شماره موبایل و جی‌دابلیو‌تی است. نقش یکی از این دو است:

</div>

```text
participant
organizer
```

<div dir="rtl">

ثبت‌نام:

</div>

```json
POST /api/auth/register/
{
  "phone": "09121234567",
  "first_name": "Sara",
  "last_name": "Ahmadi",
  "password": "StrongPass123",
  "role": "participant"
}
```

<div dir="rtl">

لاگین با موبایل و پسورد است و خروجی شامل اکسس و رفرش و نقش است:

</div>

```json
POST /api/auth/login/
{
  "phone": "09121234567",
  "password": "StrongPass123"
}
```

<div dir="rtl">

استفاده در هدر درخواست‌ها:

</div>

```text
Authorization: Bearer <access>
```

<div dir="rtl">

تمدید، پروفایل و خروج:

</div>

```text
POST /api/auth/refresh/
GET /api/auth/me/
POST /api/auth/logout/
```

<div dir="rtl">

## ۷. گروه‌بندی ای‌پی‌آی‌ها

### ۷.۱ عمومی — بدون توکن، فقط منتشرشده

</div>

```text
GET /api/events/
GET /api/events/{id}/
GET /api/results/
GET /api/stages/?event=1
```

<div dir="rtl">

### ۷.۲ شرکت‌کننده — با توکن و نقش شرکت‌کننده

</div>

```text
POST /api/registrations/
GET /api/registrations/
DELETE /api/registrations/{id}/
POST /api/feedbacks/
GET /api/feedbacks/
```

<div dir="rtl">

### ۷.۳ برگزارکننده — با توکن و مالکیت رویداد

</div>

```text
POST /api/events/
PUT,PATCH,DELETE /api/events/{id}/
POST /api/events/{id}/change-status/
POST /api/stages/
POST /api/stage-assignments/
GET /api/registrations/
GET /api/feedbacks/
POST /api/results/
POST /api/attributes/
POST /api/attribute-values/
```

<div dir="rtl">

مثال تغییر وضعیت:

</div>

```json
POST /api/events/1/change-status/
{
  "status": "published"
}
```

<div dir="rtl">

## ۸. چرخه عمر رویداد

فقط این مسیر مجاز است:

</div>

```text
draft -> published -> closed -> finished
```

<div dir="rtl">

ایجاد همیشه با پیش‌نویس است. تغییر مستقیم وضعیت با ویرایش بسته است و فقط از مسیر تغییر وضعیت انجام می‌شود. فقط مالک می‌تواند وضعیت را عوض کند.

## ۹. تصمیم ثبت‌نام و ظرفیت

ثبت‌نام و ظرفیت برای کل رویداد است، نه برای مرحله.

دلیل: ظرفیت روی مدل رویداد است، ثبت‌نام با ترکیب رویداد و کاربر یکتا است، مرحله ظرفیت جدا ندارد و انتساب مرحله فقط برای نقش اجرایی مثل سخنران و داور است.

## ۱۰. ویژگی داینامیک بدون جیسون‌فیلد

طراحی با دو جدول انجام شده است. جدول اول تعریف مستقل و مشترک بین رویدادهاست. جدول دوم مقدار مخصوص هر رویداد است. نوع‌ها متن و عدد و بولین و تاریخ هستند و فقط ستون مربوط به همان نوع پر می‌شود. هیچ جیسون‌فیلدی استفاده نشده و برای هر ویژگی ستون جدید ساخته نشده است.

</div>

```json
POST /api/events/
{
  "title": "Python Workshop",
  "capacity": 50,
  "attributes_data": [
    { "attribute": 1, "value": "advanced" },
    { "attribute": 2, "value": 3 }
  ]
}
```

<div dir="rtl">

## ۱۱. قوانین اصلی

۱. لیست عمومی فقط منتشرشده را نشان می‌دهد
۲. ثبت‌نام فقط برای منتشرشده، با چک ظرفیت و بدون تکرار
۳. فقط مالک می‌تواند ویرایش و حذف کند
۴. وضعیت فقط طبق مسیر مجاز عوض می‌شود
۵. بازخورد فقط بعد از پایان و فقط از ثبت‌نام‌شده
۶. نتیجه فقط بعد از پایان و برای عموم قابل مشاهده است
۷. دسترسی نقش‌محور در سطح ای‌پی‌آی اعمال می‌شود

## ۱۲. عیب‌یابی

اگر خطای متغیر دیتابیس گرفتی فایل محیطی را چک کن. اگر خطای عکس گرفتی پیلو را نصب کن. اگر لیست قدیمی دیدی کش لیست را در توسعه غیرفعال کن.

</div>