import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7221013939

REF_LINK = "https://u3.shortink.io/register?utm_campaign=826893&utm_source=affiliate&utm_medium=sr&a=WxLmRQigGoQehq&al=1745149&ac=rishabhkasana777&cid=949480&code=WELCOME50"

verified_users = set()
user_stats = {}
waiting_for_id = set()

pairs = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC",
    "AUD/USD OTC", "EUR/GBP OTC",
    "BTC/USD", "ETH/USD", "LTC/USD"
]

directions = ["CALL 📈", "PUT 📉"]

# 📊 SIGNAL
def generate_signal():
    pair = random.choice(pairs)
    direction = random.choice(directions)
    confidence = random.randint(80, 95)

    return f"""📊 SIGNAL

Pair: {pair}
Direction: {direction}
Expiry: 1 min
Confidence: {confidence}%

⚡ Enter now!
"""

# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return

    keyboard = [
        [InlineKeyboardButton("🚀 CREATE ACCOUNT", url=REF_LINK)],
        [InlineKeyboardButton("🆔 SUBMIT TRADER ID", callback_data="trader_id")],
        [InlineKeyboardButton("📩 SUBMIT PROOF", callback_data="proof")]
    ]

    text = """🔥 Northvale Capital — Private Trading Community
📊 One of the fastest-growing AI trading communities in Forex & Crypto.
💼 What you get:
📈 Advanced Signal System — Real-time CALL/PUT signals  
⚡ Fast execution — Never miss trades  
💰 Potential income: $500–$1000/day  
🤖 AI-assisted trading support  
🏆 Exclusive VIP access  
🎯 Accurate entry points  
💎 Why choose us?
✅ High accuracy signals  
✅ Beginner-friendly  
✅ Daily opportunities  
✅ Private serious traders only  
🚀 How to start:
1️⃣ Register your account  
2️⃣ Deposit minimum amount  
3️⃣ Submit proof / trader ID  
4️⃣ Get VIP access  
⚠️ Limited VIP access — Not everyone gets approved  
👤 Founder:Northvale.ai
📩 Instagram for support  

👇 Click below to continue
"""

    # MAIN MESSAGE
    await message.reply_photo(
        photo="https://cdn.phototourl.com/free/2026-03-28-6532c40e-f04e-485b-8255-e2b361561fb5.png",
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # VIP FLOW (SAFE)
    await asyncio.sleep(2)
    await message.reply_text("⏳ Checking VIP availability...")

    await asyncio.sleep(2)
    await message.reply_text("📊 Scanning active traders...")

    await asyncio.sleep(2)
    slots = random.randint(8, 18)
    await message.reply_text(f"⚠️ Only {slots} VIP slots remaining today")

    await asyncio.sleep(2)
    await message.reply_text("🚀 Complete steps now to secure your access")

# 🔘 BUTTONS
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "trader_id":
        waiting_for_id.add(user_id)
        await query.message.reply_text("🆔 Send your Pocket Option Trader ID")

    elif query.data == "proof":
        await query.message.reply_text("📩 Send your deposit screenshot")

# 🆔 HANDLE ID
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in waiting_for_id:
        return

    trader_id = update.effective_message.text
    waiting_for_id.remove(user_id)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆔 Trader ID\nUser: {user_id}\nID: {trader_id}\n\n/approve {user_id}"
    )

    await update.effective_message.reply_text("⏳ Waiting for verification")

# 📸 PROOF
async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 Proof submitted\n/approve {user_id}"
    )

    await update.effective_message.reply_text("⏳ Waiting for approval")

# ✅ APPROVE
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.effective_message.reply_text("Use: /approve user_id")
        return

    user_id = int(context.args[0])
    verified_users.add(user_id)
    user_stats[user_id] = {"win": 0, "loss": 0}

    await context.bot.send_message(
        chat_id=user_id,
        text="✅ Access granted! Signals started 🔥"
    )

# 📊 SIGNAL CMD
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in verified_users:
        await update.effective_message.reply_text("❌ Locked. Verify first.")
        return

    await update.effective_message.reply_text(generate_signal())

# 🤖 AUTO SIGNAL
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

# 💸 HYPE
hype_messages = [
    "💰 User made profit!",
    "🔥 Signal hit!",
    "📈 Big win today!",
    "⚡ Another trade closed!"
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

# 🚀 APP
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("signal", signal))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_proof))

app.job_queue.run_repeating(auto_signals, interval=120, first=20)
app.job_queue.run_repeating(auto_hype, interval=180, first=30)

print("Bot running 🚀")
app.run_polling()
