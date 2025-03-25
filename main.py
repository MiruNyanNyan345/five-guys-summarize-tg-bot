from datetime import datetime, timedelta, timezone
import sqlite3
import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from decouple import config
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set Telegram Bot Token
TOKEN = config('BOT_TOKEN')
application = Application.builder().token(TOKEN).build()

# Define Hong Kong timezone (UTC+8)
HK_TIMEZONE = timezone(timedelta(hours=8))

# SQLite database path (configurable for Railway volumes)
DB_DIR = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "/data")  # Directory only
DB_PATH = os.path.join(DB_DIR, "messages.db")  # Full path with filename

# Ensure the directory exists
def ensure_db_directory():
    try:
        os.makedirs(DB_DIR, exist_ok=True)
        print(f"Database directory ensured at {DB_DIR}")
    except Exception as e:
        print(f"Failed to create database directory {DB_DIR}: {e}")
        raise

# Initialize SQLite database
def init_db():
    ensure_db_directory()  # Ensure directory exists before creating DB
    try:
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
        print(f"Database initialized at {DB_PATH}")
    except sqlite3.OperationalError as e:
        print(f"Failed to initialize database at {DB_PATH}: {e}")
        raise

# Run database initialization at startup
try:
    init_db()
except Exception as e:
    print(f"Startup failed: {e}")
    exit(1)

# Handle received messages
async def log_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        chat_id = update.message.chat_id
        user = update.message.from_user
        message = update.message.text
        timestamp = update.message.date.isoformat()

        user_name = user.first_name if user.first_name else '唔知邊條粉蛋'
        if user.last_name:
            user_name += " " + user.last_name

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (chat_id, user_name, text, timestamp) VALUES (?, ?, ?, ?)",
                (chat_id, user_name, message, timestamp)
            )
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Failed to log message to database: {e}")
            await update.message.reply_text("哎呀，儲存訊息時出錯！請稍後再試。")

# Helper function to summarize messages in a given time range
async def summarize_in_range(update: Update, start_time: datetime, end_time: datetime, period_name: str) -> None:
    chat_id = update.message.chat_id

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_name, text, timestamp FROM messages
            WHERE chat_id = ? AND timestamp >= ? AND timestamp < ?
            ORDER BY timestamp ASC
        """, (chat_id, start_time.isoformat(), end_time.isoformat()))
        rows = cursor.fetchall()
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"Failed to query database: {e}")
        await update.message.reply_text("哎呀，讀取訊息時出錯！請稍後再試。")
        return

    if not rows:
        await update.message.reply_text(f"No messages to summarize for {period_name} in this chat!")
        return

    day_messages = [f"{row[0]}: {row[1]}" for row in rows]
    text_to_summarize = "\n".join(day_messages)

    waiting_message = await update.message.reply_text("等一等，幫緊你...幫緊你... ⏳")
    summary = get_ai_summary(text_to_summarize)

    formatted_start = start_time.astimezone(HK_TIMEZONE).strftime("%Y-%m-%d %H:%M")
    formatted_end = end_time.astimezone(HK_TIMEZONE).strftime("%Y-%m-%d %H:%M")
    if summary and summary != '系統想方加(出錯)，好對唔住':
        await waiting_message.edit_text(
            f"由{formatted_start} - {formatted_end}嘅{period_name}對話總結為: 📝\n{summary}"
        )
    else:
        await waiting_message.edit_text('系統想方加(出錯)，好對唔住')

# Command handlers (unchanged from previous version)
async def summarize_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(HK_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    await summarize_in_range(update, start_of_day, now, "全日")

async def summarize_morning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(HK_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    morning_start = start_of_day.replace(hour=6, minute=0)
    morning_end = start_of_day.replace(hour=12, minute=0)
    if now < morning_end:
        morning_end = now
    await summarize_in_range(update, morning_start, morning_end, "今日早晨 (06:00-12:00)")

async def summarize_afternoon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(HK_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    afternoon_start = start_of_day.replace(hour=12, minute=0)
    afternoon_end = start_of_day.replace(hour=18, minute=0)
    if now < afternoon_end:
        afternoon_end = now
    await summarize_in_range(update, afternoon_start, afternoon_end, "今日下午 (12:00-18:00)")

async def summarize_night(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(HK_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    night_start = start_of_day.replace(hour=18, minute=0)
    night_end = start_of_day + timedelta(days=1)
    if now < night_end:
        night_end = now
    await summarize_in_range(update, night_start, night_end, "今晚 (18:00-05:59)")

async def summarize_last_hour(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(HK_TIMEZONE)
    last_hour_start = now - timedelta(hours=1)
    await summarize_in_range(update, last_hour_start, now, "過去一小時")

async def summarize_last_3_hours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(HK_TIMEZONE)
    last_3_hours_start = now - timedelta(hours=3)
    await summarize_in_range(update, last_3_hours_start, now, "過去三小時")

async def apologize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    print(f"Starting apology generation for chat {chat_id}")

    waiting_message = await update.message.reply_text("度緊呢單野點拆… ⏳")
    apology = get_ai_apology()
    print(f"Generated apology for chat {chat_id}: {apology}")

    if apology and apology != '哎呀，道歉失敗，唔好打我🙏':
        await waiting_message.edit_text(apology)
    else:
        await waiting_message.edit_text('哎呀，道歉失敗，唔好打我🙏')

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

# Generate apology using DeepSeek API
def get_ai_apology() -> str:
    client = OpenAI(api_key=config("API_KEY"), base_url="https://api.deepseek.com")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user",
                 "content": "用繁體中文同香港式口語去道歉，搞笑但唔會得罪人嘅道歉，要有啲emoji，字數30以下"},
            ],
            stream=False
        )
        apology = response.choices[0].message.content
        apology += "\n\n免責聲明: 唔關五仁月餅事🥮求下大家俾下面🙏"
        return apology
    except Exception as e:
        print(f"Error in get_ai_apology: {e}")
        return '哎呀，道歉失敗，唔好打我🙏'

# Register handlers
application.add_handler(MessageHandler(filters.Text() & ~filters.Command(), log_message))
application.add_handler(CommandHandler("summarize", summarize_day))
application.add_handler(CommandHandler("summarize_morning", summarize_morning))
application.add_handler(CommandHandler("summarize_afternoon", summarize_afternoon))
application.add_handler(CommandHandler("summarize_night", summarize_night))
application.add_handler(CommandHandler("summarize_last_hour", summarize_last_hour))
application.add_handler(CommandHandler("summarize_last_3_hours", summarize_last_3_hours))
application.add_handler(CommandHandler("apologize", apologize)) 

# Start the bot
if __name__ == "__main__":
    print("Starting bot...")
    application.run_polling()
