# bot.py
import os
from typing import List, Optional

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest

from main import get_stock_info, format_stock_message
from analysis import format_technical_analysis
from news import (
    register_news_handlers_and_jobs,
    build_symbol_board_news,
    build_live_market_news_text,   
)
from sales_data import build_sales_report_for_symbol
from news import (
    register_news_handlers_and_jobs,
    build_symbol_board_news,
    build_live_market_news_text,
)

BOT_TOKEN = "8271496353:AAFsle6gIYeRdL1slpjxtbKoAR23I24oeR4"


# ----------------- مدیریت پروکسی محیط -----------------
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


# ----------------- هندلرهای اصلی (استارت، نماد، تحلیل) -----------------
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


async def board_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        " تحلیل تابلو (board) هنوز به طور کامل پیاده‌سازی نشده.\n"
        "فعلاً می‌تونی از این‌ها استفاده کنی:\n"
        "• فقط اسم نماد → اطلاعات لحظه‌ای\n"
        "• /ta فملی → تحلیل تکنیکال ساده\n"
        "• /fund فملی → گزارش فروش/بنیادی ساده\n"
        "وقتی بخش تابلو آماده شد، از همین دستور /board بهت خبر می‌دم. "
    )
    await update.message.reply_text(text)


async def news_live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    خبر لایو از وضعیت فعلی بازار بر اساس نقشه TSETMC.
    """
    try:
        text = build_live_market_news_text()
    except Exception as e:
        print(f"[news_live] error: {e}")
        text = "نتوانستم خلاصه لایو بازار را بسازم (مشکل ارتباط با سایت TSETMC یا ساختار داده)."

    await update.message.reply_text(text)


async def handle_symbol_or_ta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    هر متن معمولی کاربر:
      - اگر شروع شود با «تحلیل»، تحلیل تکنیکال
      - وگرنه: اطلاعات نماد
    """
    text = (update.message.text or "").strip()

    # اگر شروع شد با "تحلیل ..."
    if text.startswith("تحلیل"):
        symbol = text.replace("تحلیل", "").strip()
        if not symbol:
            await update.message.reply_text(
                "بعد از کلمه «تحلیل» لطفاً نماد را هم بنویسید. مثال: تحلیل فملی"
            )
            return
        reply = format_technical_analysis(symbol)
        await update.message.reply_text(reply)
        return

    # در غیر این صورت فرض می‌کنیم فقط نماد است
    info = get_stock_info(text)
    reply_text = format_stock_message(info)
    await update.message.reply_text(reply_text)


async def fund_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /fund شسینا
    /fund فملی
    """
    args = context.args
    if not args:
        await update.message.reply_text(
            "لطفا بعد از /fund نام نماد را بفرستيد. مثال:\n"
            "/fund شسینا"
        )
        return

    symbol = args[0]
    text = build_sales_report_for_symbol(symbol)
    await update.message.reply_text(text)


async def ta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /ta فملی"""
    if not context.args:
        await update.message.reply_text("لطفا نماد را بعد از دستور بنویسید. مثال: /ta فملی")
        return
    symbol = context.args[0]
    reply = format_technical_analysis(symbol)
    await update.message.reply_text(reply)


# ----------------- main -----------------
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

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(request)
        .build()
    )

    # کامندهای اصلی
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ta", ta_command))
    app.add_handler(CommandHandler("board", board_command))
    app.add_handler(CommandHandler("fund", fund_command))
    app.add_handler(CommandHandler("news_live", news_live))

    # متن آزاد: نماد یا «تحلیل فملی»
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol_or_ta))

    # ثبت کامندهای خبری و جاب‌های صبح/عصر (داخل news.py)
    register_news_handlers_and_jobs(app)

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
