import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)

# 🔐 ENV VARIABLES (Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7221013939
REF_LINK = "YOUR_REF_LINK_HERE"

verified_users = set()
user_stats = {}

pairs = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC",
    "AUD/USD OTC", "EUR/GBP OTC",
    "BTC/USD", "ETH/USD", "LTC/USD"
]

directions = ["CALL ⬆️", "PUT ⬇️"]

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
    keyboard = [
        [InlineKeyboardButton("📄 CREATE ACCOUNT", url=REF_LINK)],
        [InlineKeyboardButton("✅ VERIFY ACCOUNT", callback_data="joined")],
        [InlineKeyboardButton("📩 SUBMIT PROOF", callback_data="proof")]
    ]

    text = """🔥 Northvale Capital — Private Trading Community

📊 AI-powered trading system
⚡ Real-time market analysis

💼 Advanced signals
🎯 Precision entries
💎 VIP access

🚀 Built for serious traders
"""

    await update.message.reply_photo(
        photo="https://cdn.phototourl.com/free/2026-03-28-6532c40e-f04e-485b-8255-e2b361561fb5.png",
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🔘 BUTTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "joined":
        await query.message.reply_text("🔒 Activation required to unlock VIP signals")
    elif query.data == "proof":
        await query.message.reply_text("📩 Send screenshot now")

# 📩 HANDLE PROOF
async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Approve user:\n/approve {user_id}"
    )

    await update.message.reply_text("⏳ Waiting for approval")

# ✅ APPROVE USER
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Use: /approve user_id")
        return

    user_id = int(context.args[0])
    verified_users.add(user_id)
    user_stats[user_id] = {"win": 0, "loss": 0}

    await context.bot.send_message(
        chat_id=user_id,
        text="✅ Access granted. Signals started."
    )

# 📊 SIGNAL COMMAND
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in verified_users:
        await update.message.reply_text("❌ Locked. Verify first.")
        return

    await update.message.reply_text(generate_signal())

# 🤖 AUTO SIGNALS LOOP
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

# 🚀 MAIN APP
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("signal", signal))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.PHOTO, handle_proof))

# ⏱ AUTO JOB (every 60 sec)
app.job_queue.run_repeating(auto_signals, interval=60, first=10)

print("Bot running...")
app.run_polling()
