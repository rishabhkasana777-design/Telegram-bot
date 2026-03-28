
import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# 🔐 ENV VARIABLES (Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 👇 CHANGE THIS
ADMIN_ID = 7221013939
REF_LINK =  "https://u3.shortink.io/register?utm_campaign=826893&utm_source=affiliate&utm_medium=sr&a=WxLmRQigGoQehq&al=1745149&ac=rishabhkasana777&cid=949480&code=WELCOME50"

# 🧠 DATA
verified_users = set()
user_stats = {}

pairs = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC",
    "AUD/USD OTC", "EUR/GBP OTC",
    "BTC/USD", "ETH/USD", "LTC/USD"
]

directions = ["CALL 📈", "PUT 📉"]

# 📊 SIGNAL GENERATOR
def generate_signal():
    pair = random.choice(pairs)
    direction = random.choice(directions)
    confidence = random.randint(78, 95)

    return f"""📊 SIGNAL

Pair: {pair}
Direction: {direction}
Expiry: 1 min
Confidence: {confidence}%

⚡ Enter now!
"""

# 🚀 START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return

    user_id = update.effective_user.id

    keyboard = [
        [InlineKeyboardButton("🚀 Start Earning Now", url=REF_LINK)],
        [InlineKeyboardButton("✅ Verify Account", callback_data="joined")],
        [InlineKeyboardButton("📩 Submit Proof", callback_data="proof")]
    ]

    text = """🔥 Northvale Capital — Private Trading Community

📊 AI-powered trading system  
⚡ Real-time CALL/PUT signals  
💰 Earn up to $500–$1000/day  

⚠️ Limited VIP slots — Not everyone gets access  

👇 Complete steps below to unlock signals
"""

    await message.reply_photo(
        photo="https://cdn.phototourl.com/free/2026-03-28-6532c40e-f04e-485b-8255-e2b361561fb5.png",
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # 🔥 LIVE FEEL
    await asyncio.sleep(2)
    await message.reply_text("📡 Connecting to server...")
    await asyncio.sleep(2)
    await message.reply_text("✅ System ready! Complete steps above")

# 🎯 BUTTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "joined":
        await query.message.reply_text("🔒 Complete registration first using button above")

    elif query.data == "proof":
        await query.message.reply_text("📩 Send your deposit screenshot now")

# 📸 HANDLE PROOF
async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"New user proof:\n/approve {user_id}"
    )

    await update.effective_message.reply_text("⏳ Waiting for admin approval")

# ✅ APPROVE USER
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.effective_message.reply_text("❌ Use: /approve user_id")
        return

    user_id = int(context.args[0])

    verified_users.add(user_id)
    user_stats[user_id] = {"win": 0, "loss": 0}

    await context.bot.send_message(
        chat_id=user_id,
        text="✅ Access granted! Signals started 🔥"
    )

# 📊 SIGNAL COMMAND
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in verified_users:
        await update.effective_message.reply_text("❌ Locked. Verify first.")
        return

    await update.effective_message.reply_text(generate_signal())

# 🤖 AUTO SIGNALS
async def auto_signals(context: ContextTypes.DEFAULT_TYPE):
    for user_id in verified_users:
        try:
            result = random.choice(["win", "loss"])
            user_stats[user_id][result] += 1

            stats = user_stats[user_id]

            await context.bot.send_message(
                chat_id=user_id,
                text=generate_signal() +
                f"\n📊 W: {stats['win']} / L: {stats['loss']}"
            )
        except:
            pass

# 💸 HYPE MESSAGES
hype_messages = [
    "💰 User just made $320 profit!",
    "🔥 Signal hit! Big win!",
    "📈 VIP member doubled account today!",
    "⚡ Another winning trade!",
]

async def auto_hype(context: ContextTypes.DEFAULT_TYPE):
    for user_id in verified_users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=random.choice(hype_messages)
            )
        except:
            pass

# 🚀 MAIN APP
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("signal", signal))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.PHOTO, handle_proof))

# ⏱ AUTO JOBS
app.job_queue.run_repeating(auto_signals, interval=120, first=20)
app.job_queue.run_repeating(auto_hype, interval=180, first=30)

print("Bot running... 🚀")
app.run_polling()
