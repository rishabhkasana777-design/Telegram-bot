import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Join Now", url="https://t.me/northvale_capital_bot")]
    ]
    
await update.message.reply_text(
    "🚀 Welcome to Northvale Capital\n\nThe new era of AI trading 📊\n\nLaunching soon...",
    reply_markup=InlineKeyboardMarkup(keyboard)
)
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling()
