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
user_status = {}  # new, joined, deposited, verified

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

# 🚀 START
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

📊 One of the fastest-growing AI trading communities in Forex & Crypto.

💼 What you get:
📈 Advanced Signal System  
⚡ Fast execution  
💰 Potential income: $500–$1000/day  
🤖 AI-assisted trading  
🏆 Exclusive VIP access  
🎯 Accurate entry points  

💎 Why choose us?
✅ High accuracy  
✅ Beginner-friendly  
✅ Daily opportunities  

🚀 How to start:
1️⃣ Register account  
2️⃣ Deposit $10–$50  
3️⃣ Submit proof  
4️⃣ Get VIP access  
⚠️ Limited VIP access  

👇 Click below to continue
"""

    await message.reply_photo(
        photo="https://cdn.phototourl.com/free/2026-03-28-6532c40e-f04e-485b-8255-e2b361561fb5.png",
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # VIP urgency flow
    await asyncio.sleep(2)
    await message.reply_text("⏳ Checking VIP availability...")

    await asyncio.sleep(2)
    await message.reply_text("📊 Scanning active traders...")

    await asyncio.sleep(2)
    slots = random.randint(5, 12)
    await message.reply_text(f"⚠️ Only {slots} VIP slots remaining — filling fast")

    await asyncio.sleep(2)
    await message.reply_text("🚀 Complete steps now to secure your access")

# 🔘 BUTTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "trader_id":
        waiting_for_id.add(user_id)
        await query.message.reply_text("🆔 Send your Pocket Option Trader ID")

    elif query.data == "proof":
        await query.message.reply_text(
            "📩 Send your deposit screenshot\n\n"
            "💰 Minimum: $10 - $50\n"
            "⚠️ Without deposit, access will NOT be granted"
        )

# 🆔 HANDLE TRADER ID
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

# 📸 HANDLE PROOF
async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    user_status[user_id] = "deposited"

    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ]

    caption = f"""📩 Deposit Proof Submitted

👤 User: {user_id}
📛 Name: {user.first_name}

Choose action:"""

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("⏳ Proof received. Waiting for approval.")

# ✅ ADMIN APPROVE / REJECT
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
            text="✅ Deposit verified! VIP access granted 🔥"
        )

        await query.edit_message_caption("✅ APPROVED")

    elif data.startswith("reject_"):
        user_id = int(data.split("_")[1])

        user_status[user_id] = "joined"

        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Deposit not verified. Deposit $10–$50 and resend proof."
        )

        await query.edit_message_caption("❌ REJECTED")

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

# 💰 LIVE PROFIT FEED
profit_msgs = [
    "💰 User just made $87 profit!",
    "📈 VIP member earned $120 today!",
    "🔥 Signal closed in profit!",
    "⚡ Another win booked!"
]

async def live_profit_feed(context: ContextTypes.DEFAULT_TYPE):
    for user_id in user_status:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=random.choice(profit_msgs)
            )
        except:
            pass

# 🔔 REMINDER SYSTEM
async def reminder_system(context: ContextTypes.DEFAULT_TYPE):
    for user_id, status in user_status.items():
        try:
            if status == "joined":
                await context.bot.send_message(
                    chat_id=user_id,
                    text="⚠️ You haven’t activated VIP access.\n"
                         "💰 Deposit $10–$50 now.\n"
                         "⏳ Slots filling fast!"
                )

            elif status == "deposited":
                await context.bot.send_message(
                    chat_id=user_id,
                    text="⏳ Your proof is under review...\n"
                         "🚀 Stay ready!"
                )
        except:
            pass

# 📊 ADMIN STATS
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    total = len(user_status)
    deposited = len([u for u in user_status if user_status[u] == "deposited"])
    verified = len([u for u in user_status if user_status[u] == "verified"])

    await update.message.reply_text(
        f"📊 BOT STATS\n\n"
        f"👥 Users: {total}\n"
        f"💰 Deposited: {deposited}\n"
        f"✅ Verified: {verified}"
    )

# 🚀 APP SETUP
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("signal", signal))
app.add_handler(CommandHandler("stats", stats))

app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(CallbackQueryHandler(admin_decision, pattern="^(approve_|reject_)"))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_proof))

# ⏰ AUTO TASKS
app.job_queue.run_repeating(auto_signals, interval=120, first=20)
app.job_queue.run_repeating(live_profit_feed, interval=180, first=30)
app.job_queue.run_repeating(reminder_system, interval=600, first=60)

print("Bot running 🚀")
app.run_polling()
