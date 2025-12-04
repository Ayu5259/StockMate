"""
کارهای اصلی این ماژول:
1. راه‌اندازی ربات تلگرام با استفاده از python-telegram-bot
2. تعریف هندلرهای اصلی (مثل /start و دریافت نام نماد به صورت پیام متنی)
3. استفاده از توابع api.main برای گرفتن اطلاعات نماد و ساختن متن پاسخ

در حال حاضر:
- کاربر می‌تواند با دستور /start راهنما را ببیند.
- با ارسال نام یک نماد (مثل «فملی») اطلاعات همان نماد را دریافت می‌کند.
"""

import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest  # برای کنترل timeout و تنظیمات شبکه
from api.main import get_stock_info, format_stock_message

# نکته امنیتی:
# در عمل، بهتر است توکن را از متغیر محیطی (ENV) بخوانی،
# نه این که آن را مستقیم داخل کد بنویسی.
# این کار برای تست شخصی اشکال ندارد، ولی برای کد پابلیک/گیت باید حتماً مخفی باشد.
BOT_TOKEN = "8271496353:AAFsle6gIYeRdL1slpjxtbKoAR23I24oeR4"


def clean_proxy_env() -> None:
    """
    پاک کردن تمام متغیرهای محیطی مربوط به پروکسی برای همین پروسس.

    منطق کلی:
    - بعضی وقت‌ها سیستم یا محیط (مثلا VPN، نرم‌افزارهای دیگر)
      متغیرهای HTTP_PROXY و HTTPS_PROXY را تنظیم می‌کنند.
    - این تنظیمات ممکن است باعث مشکل در اتصال ربات به تلگرام شود.
    - با این تابع، قبل از راه‌اندازی ربات، این متغیرها را حذف می‌کنیم تا
      ربات مستقیم و بدون پروکسی به تلگرام وصل شود (یا پروکسی را خودمان مدیریت کنیم).
    """
    for var in [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ]:
        os.environ.pop(var, None)


#Bot main handelers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    هندلر دستور /start

    کارهایی که انجام می‌دهد:
    - نمایش یک پیام خوش‌آمدگویی
    - توضیح نحوه‌ی استفاده از ربات (ارسال نماد، تحلیل تکنیکال، خبرنامه و ...)

    ورودی‌ها:
        update: آبجکت شامل اطلاعات پیام و کاربر
        context: کانتکست ربات (برای دسترسی به دیتاهای اضافی در آینده)
    """
    user = update.effective_user
    text = (
        f"سلام {user.first_name}\n"
        "من گربه وال‌استریت هستم 🐱📈\n\n"
        "برای دیدن اطلاعات یک نماد:\n"
        "فقط اسم نماد را مرحمت بفرمایید (مثال: فملی ، وآوا)\n\n"
        "برای تحلیل تکنیکال:\n"
        "/ta فملی\n"
        "یا بنویسید: تحلیل فملی\n\n"
        "برای دریافت خودکار خلاصه اخبار بورس هر روز:\n"
        "/subscribe_news را بفرستید.\n\n"
        "برای دیدن خلاصه وضعیت لایو بازار:\n"
        "/news_live\n\n"
        "برای خلاصه تابلوی امروز بازار:\n"
        "/news_tablo\n"
    )
    # ارسال پیام راهنما به همان چتی که /start ارسال شده است
    await update.message.reply_text(text)


async def handle_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    هندلر پیام‌های متنی که قرار است به عنوان نام نماد تفسیر شوند.

    منطق کلی:
    - متن پیام را به عنوان نماد (symbol) می‌گیریم.
    - اگر خالی بود، از کاربر می‌خواهیم نماد را ارسال کند.
    - اگر نماد وجود داشت، از get_stock_info اطلاعات می‌گیریم.
    - با format_stock_message یک متن فارسی مرتب می‌سازیم و به کاربر می‌فرستیم.
    - در صورت بروز خطا، یک پیام خطای دوستانه برای کاربر، و جزئیات خطا در کنسول چاپ می‌شود.

    ورودی‌ها:
        update: شامل پیام متنی کاربر
        context: کانتکست ربات (فعلاً استفاده‌ای ندارد ولی برای آینده مفید است)
    """
    symbol = (update.message.text or "").strip()

    if not symbol:
        await update.message.reply_text("لطفا اسم نماد را هم مرحمت بفرمایید.")
        return

    try:
        info = get_stock_info(symbol)
        reply_text = format_stock_message(info)
    except Exception as e:
        # برای لاگ خودمان در کنسول (در آینده می‌توان با logging جایگزین کرد)
        print(f"[handle_symbol] error for symbol '{symbol}': {e}")
        reply_text = (
            "اووپس ... در گرفتن اطلاعات این نماد به مشکل خوردم. "
            "کمی بعد دوباره امتحان کن."
        )

    await update.message.reply_text(reply_text)


#main
def main() -> None:
    """
    نقطه شروع اجرای ربات.

    کارهایی که این تابع انجام می‌دهد:
    1. چاپ وضعیت متغیرهای پروکسی قبل و بعد از پاک‌سازی (برای دیباگ).
    2. پاک کردن متغیرهای پروکسی با clean_proxy_env.
    3. ساختن یک HTTPXRequest با timeoutهای مشخص برای ارتباط پایدارتر.
    4. ساخت Application (اپلیکیشن ربات) با توکن و تنظیمات شبکه.
    5. ثبت هندلرها:
        - /start → تابع start
        - هر پیام متنی ساده (غیر از دستورات) → تابع handle_symbol
    6. اجرای polling برای دریافت پیام‌ها از تلگرام.
    """
    # فقط برای دیباگ و مشاهده وضعیت قبل از پاک کردن پروکسی‌ها
    print("Before cleaning proxy env vars:")
    print("  HTTP_PROXY =", os.environ.get("HTTP_PROXY"))
    print("  HTTPS_PROXY =", os.environ.get("HTTPS_PROXY"))
    print("  http_proxy =", os.environ.get("http_proxy"))
    print("  https_proxy =", os.environ.get("https_proxy"))

    clean_proxy_env()

    # دوباره وضعیت متغیرها را بعد از پاک کردن نمایش می‌دهیم
    print("After cleaning proxy env vars:")
    print("  HTTP_PROXY =", os.environ.get("HTTP_PROXY"))
    print("  HTTPS_PROXY =", os.environ.get("HTTPS_PROXY"))
    print("  http_proxy =", os.environ.get("http_proxy"))
    print("  https_proxy =", os.environ.get("https_proxy"))

    # تنظیمات درخواست‌های شبکه به تلگرام
    request = HTTPXRequest(
        connect_timeout=20.0,
        read_timeout=20.0,
        write_timeout=20.0,
        pool_timeout=20.0,
        http_version="1.1",
    )

    print("Bot is running.")

    # ساختن اپلیکیشن ربات با توکن و تنظیمات درخواست
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(request)
        .build()
    )

    # هندلر دستور /start
    app.add_handler(CommandHandler("start", start))

    # هندلر مخصوص نمادها:
    # هر پیام متنی که دستور (command) نباشد، به عنوان نام نماد فرض می‌کنیم.
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol))

    # شروع polling برای دریافت پیام‌ها از تلگرام
    app.run_polling()


if __name__ == "__main__":
    main()
