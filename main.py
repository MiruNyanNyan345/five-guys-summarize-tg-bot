from datetime import datetime, timedelta, timezone
import openai
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from decouple import config

# Set Telegram Bot Token
TOKEN = config('BOT_TOKEN')
application = Application.builder().token(TOKEN).build()

# Store messages by chat ID
messages = {}  # Changed to a dictionary to store messages per chat

# Handle received messages
async def log_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("log_message triggered!")
    if update.message and update.message.text:
        chat_id = update.message.chat_id  # Get the chat ID (group or private)
        print(f"Message received in chat {chat_id}: {update.message.text}")
        message = update.message.text
        timestamp = update.message.date  # This is offset-aware (UTC)

        # Initialize the list for this chat_id if it doesn't exist
        if chat_id not in messages:
            messages[chat_id] = []

        # Append the message to the chat-specific list
        messages[chat_id].append({"text": message, "time": timestamp})
        print(f"Messages list for chat {chat_id}: {messages[chat_id]}")

# Command to summarize daily messages
async def summarize_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id  # Get the current chat ID
    now = datetime.now(timezone.utc)  # Make now offset-aware (UTC)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    end_of_day = now

    # Check if there are messages for this chat_id
    if chat_id not in messages or not messages[chat_id]:
        await update.message.reply_text("No messages to summarize from yesterday in this chat!")
        return

    # Filter messages for this chat within the time range
    day_messages = [msg["text"] for msg in messages[chat_id] if start_of_day <= msg["time"] < end_of_day]
    if not day_messages:
        await update.message.reply_text("No messages to summarize from yesterday in this chat!")
        return

    # Send a "please wait" message
    waiting_message = await update.message.reply_text("等一等，我諗緊嘢… ⏳")

    text_to_summarize = "\n".join(day_messages)  # Join messages with newlines
    summary = get_ai_summary(text_to_summarize)

    # Edit the waiting message with the summary or error
    if summary and summary != '系統想方加(出錯)，好對唔住':
        formatted_start = start_of_day.strftime("%Y-%m-%d %H:%M")
        formatted_end = end_of_day.strftime("%Y-%m-%d %H:%M")
        await waiting_message.edit_text(f"由{formatted_start} - {formatted_end}嘅對話總結為: 📝\n{summary}")
    else:
        await waiting_message.edit_text('系統想方加(出錯)，好對唔住')

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
        summary = response.choices[0].message.content
        return summary
    except openai.APIError as e:
        # Capture API-related errors
        print(f"API Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Error details: {e.response.text}")
            return '系統想方加(出錯)，好對唔住'
    except Exception as e:
        # Capture other unexpected errors
        print(f"Other Error: {e}")
        return '系統想方加(出錯)，好對唔住'

# Register handlers
application.add_handler(MessageHandler(filters.Text() & ~filters.Command(), log_message))
application.add_handler(CommandHandler("summarize", summarize_day))

# Start the bot
application.run_polling()Ï