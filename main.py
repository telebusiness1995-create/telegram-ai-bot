import os
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = os.getenv("TOKEN")

async def start(update, context):
    await update.message.reply_text("Bot läuft!")

if __name__ == "__main__":
    print("STARTING BOT...")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    app.run_polling()
