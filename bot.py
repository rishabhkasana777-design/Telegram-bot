import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7221013939

REF_LINK = "https://u3.shortink.io/register?utm_campaign=826893&utm_source=affiliate&utm_medium=sr&a=WxLmRQigGoQehq&al=1745149&ac=rishabhkasana777&cid=949480&code=WELCOME50"

# ================= STORAGE =================
verified_users = set()
user_stats = {}
waiting_for_id = set()
user_status = {}  # joined / deposited / verified
user_data_store = {}  # name + trader id

pairs = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC",
    "AUD/USD OTC", "EUR/GBP OTC",
    "BTC/USD", "ETH/USD", "LTC/USD"
]

directions = ["CALL 📈", "PUT 📉"]

# ================= SIGNAL =================
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

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return

    user_id = message.chat.id
    user_status[user_id] = "joined"

    keyboard = [
        [InlineKeyboardButton("🚀 CREATE ACCOUNT", url=REF_LINK)],
        [InlineKeyboardButton("🆔 SUBMIT TRADER ID", callback_data="trader_id")],
        [InlineKeyboardButton("📩 SUBMIT PROOF", callback_data="proof")]
    ]

    text = """🔥 Northvale Capital — Private Trading Community
📊 AI-based Forex & Crypto trading system
💼 Features:
📈 Advanced signals   
💰 Potential income $500–$1000/day  

🚀 Steps:
1️⃣ Create account  
2️⃣ Deposit $10–$50  
3️⃣ Submit proof  
4️⃣ Get VIP access  
⚠️ Limited slots   

👇 Continue below
"""

    await message.reply_photo(
        photo="https://cdn.phototourl.com/free/2026-03-28-6532c40e-f04e-485b-8255-e2b361561fb5.png",
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # VIP urgency
    await asyncio.sleep(2)
    await message.reply_text("⏳ Checking VIP availability...")
    await asyncio.sleep(2)
    await message.reply_text("📊 Scanning traders...")
    await asyncio.sleep(2)
    slots = random.randint(5, 12)
    await message.reply_text(f"⚠️ Only {slots} VIP slots remaining")
    await asyncio.sleep(2)
    await message.reply_text("🚀 Complete steps now")

# ================= BUTTON =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "trader_id":
        waiting_for_id.add(user_id)
        await query.message.reply_text("🆔 Send your Trader ID")

    elif query.data == "proof":
        await query.message.reply_text(
            "📩 Send deposit screenshot\n\n"
            "💰 Required: $10–$50"
        )

# ================= TRADER ID =================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    if user_id not in waiting_for_id:
        return

    trader_id = update.effective_message.text
    waiting_for_id.remove(user_id)

    user_data_store[user_id] = {
        "name": user.first_name,
        "trader_id": trader_id
    }

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"""🆔 TRADER ID

👤 Name: {user.first_name}
🆔 User ID: {user_id}
💼 Trader ID: {trader_id}"""
    )

    await update.effective_message.reply_text("⏳ ID submitted. Now send proof.")

# ================= PROOF =================
async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    user_status[user_id] = "deposited"

    data = user_data_store.get(user_id, {})
    name = data.get("name", user.first_name)
    trader_id = data.get("trader_id", "Not provided")

    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ]

    caption = f"""📩 DEPOSIT PROOF

👤 Name: {name}
🆔 User ID: {user_id}
💼 Trader ID: {trader_id}

Choose:"""

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("⏳ Waiting for approval")

# ================= ADMIN ACTION =================
async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    data = query.data

    if data.startswith("approve_"):
        user_id = int(data.split("_")[1])

        verified_users.add(user_id)
        user_stats[user_id] = {"win": 0, "loss": 0}
        user_status[user_id] = "verified"

        await context.bot.send_message(
            chat_id=user_id,
            text="✅ Approved! Signals unlocked 🔥"
        )

        await query.edit_message_caption("✅ APPROVED")

    elif data.startswith("reject_"):
        user_id = int(data.split("_")[1])

        user_status[user_id] = "joined"

        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Rejected. Deposit properly and resend proof."
        )

        await query.edit_message_caption("❌ REJECTED")

# ================= SIGNAL =================
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in verified_users:
        await update.message.reply_text("❌ Access denied")
        return

    await update.message.reply_text(generate_signal())

# ================= AUTO SIGNAL =================
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

# ================= PROFIT FEED =================
async def live_profit_feed(context: ContextTypes.DEFAULT_TYPE):
    msgs = [
        "💰 User made $90",
        "📈 Big win!",
        "🔥 Profit booked",
        "⚡ Signal hit"
    ]

    for user_id in user_status:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=random.choice(msgs)
            )
        except:
            pass

# ================= REMINDER =================
async def reminder(context: ContextTypes.DEFAULT_TYPE):
    for user_id, status in user_status.items():
        try:
            if status == "joined":
                await context.bot.send_message(
                    chat_id=user_id,
                    text="⚠️ Deposit pending ($10–$50)\nComplete now"
                )
            elif status == "deposited":
                await context.bot.send_message(
                    chat_id=user_id,
                    text="⏳ Under review..."
                )
        except:
            pass

# ================= STATS =================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    total = len(user_status)
    dep = len([u for u in user_status if user_status[u] == "deposited"])
    ver = len([u for u in user_status if user_status[u] == "verified"])

    await update.message.reply_text(
        f"Users: {total}\nDeposited: {dep}\nVerified: {ver}"
    )

# ================= APP =================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("signal", signal))
app.add_handler(CommandHandler("stats", stats))

# IMPORTANT ORDER
app.add_handler(CallbackQueryHandler(admin_decision, pattern="^(approve_|reject_)"))
app.add_handler(CallbackQueryHandler(button_handler))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_proof))

# JOBS
app.job_queue.run_repeating(auto_signals, interval=120, first=20)
app.job_queue.run_repeating(live_profit_feed, interval=180, first=30)
app.job_queue.run_repeating(reminder, interval=600, first=60)

print("Bot running 🚀")
app.run_polling()
