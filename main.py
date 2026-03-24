import os
from telegram.ext import Updater, CommandHandler

TOKEN = os.getenv("TOKEN")

def start(update, context):
    update.message.reply_text("Bot läuft!")

if __name__ == "__main__":
    print("BOT STARTING...")

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()
