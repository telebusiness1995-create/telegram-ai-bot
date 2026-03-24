import os
from telegram import Update, LabeledPrice
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai

# 🔑 Keys aus Render Environment Variables
TOKEN = os.getenv("TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

openai.api_key = OPENAI_KEY

# 🧠 User Memory (einfach gehalten)
user_messages = {}
premium_users = {}

FREE_LIMIT = 5
PREMIUM_PRICE = 500  # Telegram Stars (XTR)


# 🤖 AI Antwort
async def ask_ai(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": text}
        ]
    )
    return response["choices"][0]["message"]["content"]


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Willkommen!\nWähle deinen Modus:\nNormal / Flirty / Fetisch"
    )


# 💬 Nachrichten Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    text = update.message.text

    # Premium Check
    if user_id in premium_users:
        reply = await ask_ai(text)
        await update.message.reply_text(reply)
        return

    # Free Limit Tracking
    count = user_messages.get(user_id, 0)
    count += 1
    user_messages[user_id] = count

    if count > FREE_LIMIT:
        await send_paywall(update)
        return

    reply = await ask_ai(text)
    await update.message.reply_text(reply)


# 💰 Paywall / Invoice
async def send_paywall(update: Update):
    prices = [LabeledPrice("Premium Access", PREMIUM_PRICE)]

    await update.message.reply_invoice(
        title="Premium AI Access",
        description="Unbegrenzte Nachrichten + bessere Antworten",
        payload="premium_access",
        provider_token="",  # WICHTIG für Telegram Stars
        currency="XTR",
        prices=prices
    )


# 💳 Zahlung bestätigt
async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    premium_users[user_id] = True

    await update.message.reply_text("✅ Premium aktiviert! Du hast jetzt unbegrenzten Zugriff.")


# 🚀 MAIN
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.add_handler(MessageHandler(filters.PRE_CHECKOUT_QUERY, precheckout))

    print("Bot startet...")
    app.run_polling()
