# bot.py
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

from api.main import get_stock_info, format_stock_message
#from newsletter.handlers import register_newsletter_handlers 


# ----------------- Env / Proxy helpers -----------------
def load_settings():
    global BOT_TOKEN
    load_dotenv()

    BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set in .env")

    telegram_proxy_enabled = os.getenv("TELEGRAM_PROXY_ENABLED", "False").lower() == "true"
    proxy_telegram = os.getenv("PROXY_TELEGRAM", "").strip()

    return telegram_proxy_enabled, proxy_telegram


def clean_proxy_env():
    """Remove OS-level proxies so فقط چیزهایی که ما تنظیم کرده‌ایم اعمال شوند."""
    for var in [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ]:
        if var in os.environ:
            print(f"[bot] Removing {var} from env")
        os.environ.pop(var, None)


# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"سلام {user.first_name}\n"
        "من گربه وال‌استریت هستم 🐱📈\n\n"
        "فعلا در این نسخه فقط اطلاعات نماد را بهت نشان می‌دهم.\n"
        "کافی است اسم نماد بورسی را بفرستی، مثلا:\n"
        "فملی\n"
        "فولاد\n"
        "خساپا\n"
    )
    await update.message.reply_text(text)


async def handle_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = (update.message.text or "").strip()
    if not symbol:
        await update.message.reply_text("لطفا نام نماد را بفرست.")
        return

    info = get_stock_info(symbol)
    if not info:
        await update.message.reply_text(f"نتوانستم اطلاعاتی برای نماد «{symbol}» پیدا کنم.")
        return

    reply_text = format_stock_message(info)
    await update.message.reply_text(reply_text)


# main 
def main():
    # 1) بارگذاری تنظیمات از .env
    telegram_proxy_enabled, proxy_telegram = load_settings()

    print("Before cleaning proxy env vars:")
    print("  HTTP_PROXY =", os.environ.get("HTTP_PROXY"))
    print("  HTTPS_PROXY =", os.environ.get("HTTPS_PROXY"))
    print("  http_proxy =", os.environ.get("http_proxy"))
    print("  https_proxy =", os.environ.get("https_proxy"))

    # 2) تمیز کردن پروکسی‌های سیستم
    clean_proxy_env()

    print("After cleaning proxy env vars:")
    print("  HTTP_PROXY =", os.environ.get("HTTP_PROXY"))
    print("  HTTPS_PROXY =", os.environ.get("HTTPS_PROXY"))
    print("  http_proxy =", os.environ.get("http_proxy"))
    print("  https_proxy =", os.environ.get("https_proxy"))

    # 3) ساخت HTTPXRequest با یا بدون پروکسی
    request_kwargs = {
        "connect_timeout": 20.0,
        "read_timeout": 20.0,
        "write_timeout": 20.0,
        "pool_timeout": 20.0,
        "http_version": "1.1",
    }

    if telegram_proxy_enabled and proxy_telegram:
        print(f"[BOT] Using Telegram proxy: {proxy_telegram}")
        request_kwargs["proxy"] = proxy_telegram
    else:
        print("[BOT] No proxy for Telegram (direct connection).")

    request = HTTPXRequest(**request_kwargs)

    # 4) ساخت اپ تلگرام
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(request)
        .build()
    )

    # 5) هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol))

    # try:
    #     register_newsletter_handlers(app)
    # except Exception as e:
    #     print(f"[WARN] newsletter handlers not registered: {e}")

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
