# newsletter/handlers.py
from __future__ import annotations
from telegram import Update
from telegram.ext import ContextTypes

from .subscribers import (
    add_subscriber,
    remove_subscriber,
    is_subscribed,
)


async def subscribe_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if is_subscribed(chat_id):
        await update.message.reply_text(
            "شما قبلا عضو خبرنامه روزانه بودید.\n"
            "هر روز خلاصه وضعیت بازار برایتان ارسال می‌شود."
        )
        return

    add_subscriber(chat_id)
    await update.message.reply_text(
        "عضویت شما در خبرنامه روزانه با موفقیت انجام شد.\n"
        "از این پس هر صبح و عصر خلاصه اخبار و وضعیت بازار را دریافت خواهید کرد."
    )


async def unsubscribe_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not is_subscribed(chat_id):
        await update.message.reply_text(
            "شما در خبرنامه عضو نیستید که بخواهم لغوش کنم."
        )
        return

    remove_subscriber(chat_id)
    await update.message.reply_text(
        "لغو عضویت با موفقیت انجام شد.\n"
        "دیگر پیام‌های روزانه دریافت نخواهید کرد."
    )


async def my_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if is_subscribed(chat_id):
        await update.message.reply_text(
            "وضعیت شما:\n"
            "عضو خبرنامه روزانه هستید."
        )
    else:
        await update.message.reply_text(
            "وضعیت شما:\n"
            "در خبرنامه عضو نیستید."
        )


def register_newsletter_handlers(app):
    """
    این تابع در bot.py فراخوانی می‌شود تا هندلرهای خبرنامه ثبت شوند.
    """
    from telegram.ext import CommandHandler

    app.add_handler(CommandHandler("subscribe_news", subscribe_news))
    app.add_handler(CommandHandler("unsubscribe_news", unsubscribe_news))
    app.add_handler(CommandHandler("my_subscription", my_subscription))
