from datetime import datetime, timedelta, timezone
import sqlite3
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from decouple import config
from openai import OpenAI

# Set Telegram Bot Token
TOKEN = config('BOT_TOKEN')
application = Application.builder().token(TOKEN).build()

# Define Hong Kong timezone (UTC+8)
HK_TIMEZONE = timezone(timedelta(hours=8))

# SQLite database path (configurable for Railway volumes)
DB_PATH = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "/data") + "/messages.db"

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_name TEXT,
            text TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# Run database initialization at startup
init_db()

# Handle received messages
async def log_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        chat_id = update.message.chat_id
        user = update.message.from_user
        message = update.message.text
        timestamp = update.message.date.isoformat()  # Store as ISO string

        # Extract user info
        user_name = user.first_name if user.first_name else '唔知邊條粉蛋'
        if user.last_name:
            user_name += " " + user.last_name

        # Insert message into SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (chat_id, user_name, text, timestamp) VALUES (?, ?, ?, ?)",
            (chat_id, user_name, message, timestamp)
        )
        conn.commit()
        conn.close()

# Helper function to summarize messages in a given time range
async def summarize_in_range(update: Update, start_time: datetime, end_time: datetime, period_name: str) -> None:
    chat_id = update.message.chat_id

    # Query messages from SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_name, text, timestamp FROM messages
        WHERE chat_id = ? AND timestamp >= ? AND timestamp < ?
        ORDER BY timestamp ASC
    """, (chat_id, start_time.isoformat(), end_time.isoformat()))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text(f"No messages to summarize for {period_name} in this chat!")
        return

    # Format messages with username
    day_messages = [f"{row[0]}: {row[1]}" for row in rows]
    text_to_summarize = "\n".join(day_messages)

    # Get AI summary
    waiting_message = await update.message.reply_text("等一等，我諗緊嘢… ⏳")
    summary = get_ai_summary(text_to_summarize)

    formatted_start = start_time.astimezone(HK_TIMEZONE).strftime("%Y-%m-%d %H:%M")
    formatted_end = end_time.astimezone(HK_TIMEZONE).strftime("%Y-%m-%d %H:%M")
    if summary and summary != '系統想方加(出錯)，好對唔住':
        await waiting_message.edit_text(f"由{formatted_start} - {formatted_end}嘅{period_name}對話總結為: 📝\n{summary}")
    else:
        await waiting_message.edit_text('系統想方加(出錯)，好對唔住')

# Command to summarize full day (00:00 yesterday - now)
async def summarize_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(HK_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    await summarize_in_range(update, start_of_day, now, "全日")

# Command to summarize morning (06:00 - 12:00 today)
async def summarize_morning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(HK_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    morning_start = start_of_day.replace(hour=6, minute=0)
    morning_end = start_of_day.replace(hour=12, minute=0)
    if now < morning_end:
        morning_end = now
    await summarize_in_range(update, morning_start, morning_end, "今日早晨 (06:00-12:00)")

# Command to summarize afternoon (12:00 - 18:00 today)
async def summarize_afternoon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(HK_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    afternoon_start = start_of_day.replace(hour=12, minute=0)
    afternoon_end = start_of_day.replace(hour=18, minute=0)
    if now < afternoon_end:
        afternoon_end = now
    await summarize_in_range(update, afternoon_start, afternoon_end, "今日下午 (12:00-18:00)")

# Command to summarize night (18:00 today - 05:59 tomorrow or now)
async def summarize_night(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(HK_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    night_start = start_of_day.replace(hour=18, minute=0)
    night_end = start_of_day + timedelta(days=1)  # Tomorrow’s 00:00
    if now < night_end:
        night_end = now
    await summarize_in_range(update, night_start, night_end, "今晚 (18:00-05:59)")

# Command to summarize last hour
async def summarize_last_hour(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(HK_TIMEZONE)
    last_hour_start = now - timedelta(hours=1)
    await summarize_in_range(update, last_hour_start, now, "過去一小時")

# Command to summarize last 3 hours
async def summarize_last_3_hours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(HK_TIMEZONE)
    last_3_hours_start = now - timedelta(hours=3)
    await summarize_in_range(update, last_3_hours_start, now, "過去三小時")

# Summarize text using DeepSeek API
def get_ai_summary(text: str) -> str:
    client = OpenAI(api_key=config("API_KEY"), base_url="https://api.deepseek.com")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user",
                 "content": f'用繁體中文同香港式口語去總結以下對話；加個搞笑嘅title俾個summary，最好有啲連登feel；內容不要太複雜；說話方式可以輕鬆啲，但說話不要得罪人；精闢地描述每個重點；可以講得輕鬆有趣啲；轉述內容時要提及邊位講；除左總結對話之外，係尾段總結邊位最多野講，格式為（[名]: 說話頻率百分比）加啲emoji: {text}'},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in get_ai_summary: {e}")
        return '系統想方加(出錯)，好對唔住'

# Register handlers
application.add_handler(MessageHandler(filters.Text() & ~filters.Command(), log_message))
application.add_handler(CommandHandler("summarize", summarize_day))
application.add_handler(CommandHandler("summarize_morning", summarize_morning))
application.add_handler(CommandHandler("summarize_afternoon", summarize_afternoon))
application.add_handler(CommandHandler("summarize_night", summarize_night))
application.add_handler(CommandHandler("summarize_last_hour", summarize_last_hour))
application.add_handler(CommandHandler("summarize_last_3_hours", summarize_last_3_hours))

# Start the bot
if __name__ == "__main__":
    application.run_polling()
