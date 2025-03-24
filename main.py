from datetime import datetime, timedelta, timezone  # Add timezone

import openai
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from decouple import config
# 設定 Telegram Bot Token
TOKEN = config('BOT_TOKEN')
application = Application.builder().token(TOKEN).build()

# 儲存訊息
messages = []


# 處理接收到的訊息
async def log_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("log_message triggered!")
    if update.message and update.message.text:
        print(f"Message received: {update.message.text}")
        message = update.message.text
        timestamp = update.message.date  # This is offset-aware (UTC)
        messages.append({"text": message, "time": timestamp})
        print(f"Messages list: {messages}")


# 總結一天訊息的命令
async def summarize_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global messages
    # Use UTC timezone for consistency with Telegram's timestamps
    now = datetime.now(timezone.utc)  # Make now offset-aware (UTC)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    end_of_day = start_of_day + timedelta(days=2)

    day_messages = [msg["text"] for msg in messages if start_of_day <= msg["time"] < end_of_day]
    if not day_messages:
        await update.message.reply_text("昨天沒有訊息可總結！")
        return

    text_to_summarize = "\n".join(day_messages)
    summary = get_ai_summary(text_to_summarize)
    await update.message.reply_text(f"昨天的討論總結：\n{summary}")


# 使用 Hugging Face API 總結
def get_ai_summary(text: str) -> str:

    client = OpenAI(api_key=config("API_KEY"), base_url="https://api.deepseek.com")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": f'用繁體中文和口語化的廣東話總結這段文字：{text}'},
            ],
            stream=False
        )
        summary = response.choices[0].message.content
        return summary
    except openai.APIError as e:
        # 捕獲 API 相關錯誤
        print(f"API 錯誤：{e}")
        if hasattr(e, 'response') and e.response:
            print(f"錯誤詳情：{e.response.text}")
    except Exception as e:
        # 捕獲其他意外錯誤
        print(f"其他錯誤：{e}")


# 註冊處理器
application.add_handler(MessageHandler(filters.Text() & ~filters.Command(), log_message))
application.add_handler(CommandHandler("summarize", summarize_day))

# 啟動機器人
application.run_polling()
