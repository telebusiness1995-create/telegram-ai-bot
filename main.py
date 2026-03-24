import os
import requests
from telegram import Update, ReplyKeyboardMarkup, LabeledPrice
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
    PreCheckoutQueryHandler,
    CallbackQueryHandler
)

TOKEN = os.getenv("TOKEN")
AI_API_KEY = os.getenv("OPENAI_KEY")

FREE_LIMIT = 5
PREMIUM_PACK_MESSAGES = 50
PREMIUM_PRICE_STARS = 500

user_messages = {}
user_premium = {}
user_mode = {}

MODES = {
    "Normal": "Du bist freundlich und hilfsbereit.",
    "Flirty": "Du bist charmant und leicht verspielt.",
    "Intensiv": "Du bist emotional und nahbar."
}


def ask_ai(message, mode):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": mode},
            {"role": "user", "content": message}
        ]
    }

    r = requests.post(url, headers=headers, json=data)
    return r.json()["choices"][0]["message"]["content"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Normal", "Flirty"], ["Intensiv"]]

    await update.message.reply_text(
        "Wähle deinen Modus 😊",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def send_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = [LabeledPrice("Premium Pack (50 Messages)", PREMIUM_PRICE_STARS)]

    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="Premium Zugriff 💎",
        description="50 zusätzliche Nachrichten freischalten",
        payload="premium_pack",
        provider_token="",
        currency="XTR",
        prices=prices
    )


async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # Mode wählen
    if text in MODES:
        user_mode[user_id] = MODES[text]
        user_messages[user_id] = 0
        user_premium[user_id] = 0
        await update.message.reply_text(f"Modus gesetzt: {text} 💖")
        return

    if user_id not in user_mode:
        await update.message.reply_text("Bitte zuerst Modus wählen 😊")
        return

    # Premium check
    if user_premium.get(user_id, 0) > 0:
        user_premium[user_id] -= 1
    else:
        user_messages[user_id] = user_messages.get(user_id, 0) + 1

        if user_messages[user_id] > FREE_LIMIT:
            await update.message.reply_text(
                "Du hast dein Free Limit erreicht 💎\nHol dir Premium um weiter zu chatten!"
            )
            await send_payment(update, context)
            return

    reply = ask_ai(text, user_mode[user_id])
    await update.message.reply_text(reply)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.add_handler(PreCheckoutQueryHandler(precheckout))

app.run_polling()
