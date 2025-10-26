import os
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
import httpx


BOT_TOKEN = "8271496353:AAFsle6gIYeRdL1slpjxtbKoAR23I24oeR4"  
PROXY_URL = "http://127.0.0.1:2081"     

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_firstname = update.effective_user.first_name
    await update.message.reply_text(
        f"آهای {user_firstname} من هنوز زنده ام"
    )

async def main():
    print("STEP 0: setting proxy env for httpx/telegram...")

    
    os.environ["HTTP_PROXY"] = PROXY_URL
    os.environ["HTTPS_PROXY"] = PROXY_URL

    print("STEP 1: building Application...")

    app = Application.builder().token(BOT_TOKEN).build()

    print("STEP 2: adding handlers (/start)...")
    app.add_handler(CommandHandler("start", start))

    print("STEP 3: initialize & start bot...")
    await app.initialize()
    await app.start()

    print("STEP 4: start_polling() ... listening for /start in Telegram")
    await app.updater.start_polling()

    print(" Bot is running via proxy env  and waiting forever")
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("BOOT: running main() ...")
    asyncio.run(main())
