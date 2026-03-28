import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Get Access", url="https://t.me/northvale_capital_bot")]
    ]

    caption = """🔥 Northvale Capital — Private Trading Community

📊 AI-powered trading system  
Real-time market analysis  

💼 Advanced signal system  
🎯 Precision entries  
💎 Exclusive VIP access  

⚡ Built for serious traders  

🚀 Launching soon — limited access"""

    await update.message.reply_photo(
        photo="https://cdn.phototourl.com/free/2026-03-28-6532c40e-f04e-485b-8255-e2b361561fb5.png",
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling() 
