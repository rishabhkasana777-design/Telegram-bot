import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("8479061125:AAHeoauLABEfYRwZurdfFu1nkREs9qIi4f8")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Get Access", url="https://t.me/northvale_capital_bot")]
    ]

    caption = (
        "🔥 Northvale Capital — Private Trading Community\n\n"
        "📊 AI-powered trading system\n"
        "Real-time market analysis\n\n"
        "💼 Advanced signal system\n"
        "🎯 Precision entries\n"
        "💎 Exclusive VIP access\n\n"
        "⚡ Built for serious traders\n\n"
        "🚀 Launching soon — limited access"
    )

    await update.effective_message.reply_photo(
        photo="https://cdn.phototourl.com/free/2026-03-28-6532c40e-f04e-485b-8255-e2b361561fb5.png",
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling() 
