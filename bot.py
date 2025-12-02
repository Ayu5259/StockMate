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
from main import get_stock_info, fetch_market_map

BOT_TOKEN = "8271496353:AAFsle6gIYeRdL1slpjxtbKoAR23I24oeR4"

# env proxy
def clean_proxy_env():
    """Remove all proxy env vars for this process."""
    for var in [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ]:
        os.environ.pop(var, None)

# Main handelers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await update.message.reply_text(text)

async def handle_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip()
    info = get_stock_info(symbol)
    if info:
        reply_text = f"نماد: {info['lVal18AFC']}\nقیمت: {info.get('pClosing', 'N/A')}"
    else:
        reply_text = f"نماد {symbol} پیدا نشد."
    await update.message.reply_text(reply_text)

# main
def main():
    print("Before cleaning proxy env vars:")
    print("  HTTP_PROXY =", os.environ.get("HTTP_PROXY"))
    print("  HTTPS_PROXY =", os.environ.get("HTTPS_PROXY"))
    print("  http_proxy =", os.environ.get("http_proxy"))
    print("  https_proxy =", os.environ.get("https_proxy"))

    clean_proxy_env()

    print("After cleaning proxy env vars:")
    print("  HTTP_PROXY =", os.environ.get("HTTP_PROXY"))
    print("  HTTPS_PROXY =", os.environ.get("HTTPS_PROXY"))
    print("  http_proxy =", os.environ.get("http_proxy"))
    print("  https_proxy =", os.environ.get("https_proxy"))

    request = HTTPXRequest(
        connect_timeout=20.0,
        read_timeout=20.0,
        write_timeout=20.0,
        pool_timeout=20.0,
        http_version="1.1",
    )

    print("Bot is running.")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("symbol", handle_symbol))

    app.run_polling()

   
if __name__ == "__main__":
    main()
