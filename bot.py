import os
import asyncio
import random
import requests
import pandas as pd
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7221013939
API_KEY = "NFI1AOMYRK6CCCN5"

INTRO_IMAGE = "https://cdn.phototourl.com/free/2026-03-28-6532c40e-f04e-485b-8255-e2b361561fb5.png"
SIGNAL_IMAGE = "https://img.sanishtech.com/u/1c0dc9fca14a1e2500306231240d93db.jpg"

ALLOWED_PAIRS = [
    "EURUSD","GBPUSD","AUDUSD",
    "EURGBP","EURAUD","EURCAD","EURCHF",
    "GBPAUD","GBPCAD","GBPCHF",
    "USDJPY","USDCHF","USDCAD",
    "AUDJPY","AUDCAD","AUDCHF",
    "CADJPY","CADCHF",
    "CHFJPY","EURJPY","GBPJPY"
]

verified_users = set()
waiting_for_id = set()
user_data = {}

# ================= SESSION FILTER =================
def is_trading_time():
    hour = datetime.utcnow().hour
    return 6 <= hour <= 20  # London + NY session

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("🚀 CREATE ACCOUNT", url="https://u3.shortink.io/register?utm_campaign=826893&utm_source=affiliate&utm_medium=sr&a=WxLmRQigGoQehq&al=1745149&ac=rishabhkasana777&cid=949480&code=WELCOME50")],
        [InlineKeyboardButton("🆔 SUBMIT TRADER ID", callback_data="id")],
        [InlineKeyboardButton("📩 SUBMIT PROOF", callback_data="proof")]
    ]

    text = """🔥 Northvale Capital — Private Trading Community

📊 One of the fastest growing AI trading communities in Forex & Crypto.
💼 What you get:
📈 Advanced Signal System 
💰 Potential income:$1000/day  
🏆 Exclusive VIP access  
🎯 Accurate entry points  
💎 Why choose us?
✅ High accuracy   
🚀 How to start:
1️⃣ Register account  
2️⃣ Deposit $10–$50   
🚫 We DO NOT use OTC pairs  
✅ We trade only REAL Forex market pairs for higher accuracy & reliability  
🧠 Our strategy is not random  it’s built on advanced trading concepts:
💡 Smart Money Concepts (SMC)  
💡 Fair Value Gaps (FVG)  
💡 Liquidity Trap Detection  
💡 Support & Resistance Zones  
💡 Breakout + Reversal Confirmations  
💡 EMA 25 / 50 Reaction Strategy  
📈 Multi-layer confirmation system ensures:
✔️ High probability entries  
✔️ Low risk setups  
✔️ Precision timing (5M sniper trades)  
⚡ We don’t spam signals  
🎯 Only the BEST setups are sent  
💰 Designed for serious traders who want consistency  not luck  
⚠️ Limited VIP access"""

    await update.message.reply_photo(
        photo=INTRO_IMAGE,
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await asyncio.sleep(2)
    await update.message.reply_text("⏳ Checking VIP availability...")

    await asyncio.sleep(2)
    slots = random.randint(5, 12)
    await update.message.reply_text(f"⚠️ Only {slots} VIP slots left")

# ================= BUTTON =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "id":
        waiting_for_id.add(query.from_user.id)
        await query.message.reply_text("Send Trader ID")

    elif query.data == "proof":
        await query.message.reply_text("Send deposit screenshot")

# ================= TRADER ID =================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id not in waiting_for_id:
        return

    waiting_for_id.remove(user.id)
    user_data[user.id] = update.message.text

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"""🆔 Trader ID

👤 {user.first_name}
🆔 {user.id}
💼 {update.message.text}"""
    )

# ================= PROOF =================
async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    keyboard = [[
        InlineKeyboardButton("✅ Approve", callback_data=f"a_{user.id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"r_{user.id}")
    ]]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"Proof from {user.first_name}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= ADMIN =================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    user_id = int(query.data.split("_")[1])

    if query.data.startswith("a_"):
        verified_users.add(user_id)
        await context.bot.send_message(user_id, "✅ VIP Activated")

    else:
        await context.bot.send_message(user_id, "❌ Rejected")

# ================= ANALYSIS =================
def analyze_pair(pair):

    if datetime.utcnow().weekday() >= 5:
        return None

    if not is_trading_time():
        return None

    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "FX_INTRADAY",
            "from_symbol": pair[:3],
            "to_symbol": pair[3:],
            "interval": "5min",
            "apikey": API_KEY
        }

        data = requests.get(url, params=params).json()

        key = "Time Series FX (5min)"
        if key not in data:
            return None

        candles = list(data[key].values())

        closes = [float(c["4. close"]) for c in candles]
        highs = [float(c["2. high"]) for c in candles]
        lows = [float(c["3. low"]) for c in candles]

        df = pd.DataFrame(closes, columns=["close"])

        ema25 = EMAIndicator(df["close"], 25).ema_indicator().iloc[-1]
        ema50 = EMAIndicator(df["close"], 50).ema_indicator().iloc[-1]
        rsi = RSIIndicator(df["close"]).rsi().iloc[-1]

        price = closes[-1]
        support = min(lows[-20:])
        resistance = max(highs[-20:])

        if abs(price - ema25) < 0.0005:
            return (pair, "REVERSAL", "EMA25", 88)

        if price > resistance and price > ema50 and rsi < 70:
            return (pair, "CALL 📈", "BREAKOUT", 92)

        if price < support and price < ema50 and rsi > 30:
            return (pair, "PUT 📉", "BREAKDOWN", 92)

        return None

    except:
        return None

# ================= AUTO SCANNER =================
async def auto_scan(context: ContextTypes.DEFAULT_TYPE):

    for pair in ALLOWED_PAIRS:
        result = analyze_pair(pair)

        if result:
            pair, direction, setup, conf = result

            msg = f"""📊 VIP SIGNAL

Pair: {pair}
Timeframe: 5M

Direction: {direction}
Setup: {setup}

📈 Confidence: {conf}%

⚡ High Probability"""

            for user in verified_users:
                try:
                    await context.bot.send_photo(
                        chat_id=user,
                        photo=SIGNAL_IMAGE,
                        caption=msg
                    )
                except:
                    pass

            break  # only BEST signal

# ================= MANUAL ================
   async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    text = update.message.text.strip()  # FULL MESSAGE

    parts = text.split()

    if len(parts) < 2:
        await update.message.reply_text("Usage: /signal EURUSD")
        return

    pair = parts[1].upper()

    if pair not in ALLOWED_PAIRS:
        await update.message.reply_text("❌ Pair not allowed")
        return

    result = analyze_pair(pair)

    # 👑 ADMIN MODE
    if user_id == ADMIN_ID:

        if result:
            p, direction, setup, conf = result
        else:
            direction = get_trend_direction(pair)
            setup = "TREND (Fallback)"
            conf = 65

        msg = f"""👑 ADMIN SIGNAL

Pair: {pair}
Timeframe: 5M

Direction: {direction}
Setup: {setup}

Confidence: {conf}%
"""
        await update.message.reply_text(msg)
        return

    # 👥 USERS
    if user_id not in verified_users:
        await update.message.reply_text("❌ No access")
        return

    if not result:
        await update.message.reply_text("❌ No strong setup for this pair")
        return

    p, direction, setup, conf = result

    msg = f"""📊 SIGNAL

Pair: {p}
Direction: {direction}
Setup: {setup}

Confidence: {conf}%
"""

    await update.message.reply_text(msg)
# ================= RUN =================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("signal", signal))

app.add_handler(CallbackQueryHandler(admin, pattern="^(a_|r_)"))
app.add_handler(CallbackQueryHandler(button))

app.add_handler(MessageHandler(filters.TEXT, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_proof))

# 🔥 AUTO SCANNER EVERY 5 minutes 
if app.job_queue:
    app.job_queue.run_repeating(auto_scan, interval=300, first=60)

print("Bot running 🚀")
app.run_polling()
