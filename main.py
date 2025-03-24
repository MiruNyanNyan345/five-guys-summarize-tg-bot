from datetime import datetime, timedelta, timezone
import openai
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from decouple import config

# Set Telegram Bot Token
TOKEN = config('BOT_TOKEN')
application = Application.builder().token(TOKEN).build()

# Define Hong Kong timezone (UTC+8)
HK_TIMEZONE = timezone(timedelta(hours=8))

# Store messages by chat ID
messages = {}  # Dictionary to store messages per chat


# Handle received messages
async def log_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("log_message triggered!")
    if update.message and update.message.text:
        chat_id = update.message.chat_id
        print(f"Message received in chat {chat_id}: {update.message.text}")
        message = update.message.text
        timestamp = update.message.date  # Telegram provides UTC time

        if chat_id not in messages:
            messages[chat_id] = []

        messages[chat_id].append({"text": message, "time": timestamp})
        print(f"Messages list for chat {chat_id}: {messages[chat_id]}")


# Helper function to summarize messages in a given time range
async def summarize_in_range(update: Update, start_time: datetime, end_time: datetime, period_name: str) -> None:
    chat_id = update.message.chat_id
    if chat_id not in messages or not messages[chat_id]:
        await update.message.reply_text(f"No messages to summarize for {period_name} in this chat!")
        return

    # Convert message timestamps to HK time for comparison
    day_messages = [msg["text"] for msg in messages[chat_id] if
                    start_time <= msg["time"].astimezone(HK_TIMEZONE) < end_time]
    if not day_messages:
        await update.message.reply_text(f"No messages to summarize for {period_name} in this chat!")
        return

    waiting_message = await update.message.reply_text("等一等，我諗緊嘢… ⏳")
    text_to_summarize = "\n".join(day_messages)
    summary = get_ai_summary(text_to_summarize)

    formatted_start = start_time.strftime("%Y-%m-%d %H:%M")
    formatted_end = end_time.strftime("%Y-%m-%d %H:%M")
    if summary and summary != '系統想方加(出錯)，好對唔住':
        await waiting_message.edit_text(f"由{formatted_start} - {formatted_end}嘅{period_name}對話總結為: 📝\n{summary}")
    else:
        await waiting_message.edit_text('系統想方加(出錯)，好對唔住')


# Command to summarize full day (00:00 yesterday - now)
async def summarize_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(HK_TIMEZONE)  # Use HK timezone
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
                 "content": f'用繁體中文同香港式口語去總結以下對話，可以生動啲同搞笑啲: {text}'},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except openai.APIError as e:
        print(f"API Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Error details: {e.response.text}")
            return '系統想方加(出錯)，好對唔住'
    except Exception as e:
        print(f"Other Error: {e}")
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
application.run_polling()
