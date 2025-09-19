from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from config import HK_TIMEZONE, logger, AI_CHAT_SYSTEM_PROMPT, AI_GENERATE_BASE_PROMPT
from db import DatabaseOperations
from ai import get_ai_summary

from database import log_message, log_bot_reply


async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles AI chat functionality in group chats when the bot is mentioned or replied to.
    """

    await log_message(update, context)  # Log the incoming message

    message = update.message
    if not message or not message.text:
        return

    bot = await context.bot.get_me()
    bot_username = bot.username
    bot_id = bot.id

    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot_id
    is_mentioning_bot = f"@{bot_username}" in message.text

    if not (is_reply_to_bot or is_mentioning_bot):
        return
    logger.info(f"Bot is mentioned or replied to in chat {message.chat_id}. Triggering AI response.")

    now = datetime.now(HK_TIMEZONE)
    one_hour_ago = now - timedelta(hours=1)

    db_ops = DatabaseOperations()
    rows = db_ops.get_messages_in_range(message.chat_id, one_hour_ago, now)

    if rows is None:
        await message.reply_text("哎呀，讀取對話紀錄時出錯！🤯")
        return

    #  Format chat history
    chat_history = "\n".join([f"{row[0]}: {row[1]}" for row in rows])

    # Prepare the prompt for AI
    user_prompt = f"""
    # 對話紀錄 (過去一小時)
    ---
    {chat_history if chat_history else "（最近一個鐘冇人講過嘢）"}
    ---

    # 用戶最新嘅訊息
    {message.from_user.first_name}: "{message.text}"
    """

    system_prompt = f"""
    {AI_GENERATE_BASE_PROMPT}
    {AI_CHAT_SYSTEM_PROMPT}
    """

    waiting_message = await message.reply_text("諗緊點答… ⏳", reply_to_message_id=message.message_id)

    ai_response = get_ai_summary(user_prompt, system_prompt)

    if ai_response and '系統' not in ai_response:
        sent_message = await waiting_message.edit_text(ai_response)

        await log_bot_reply(
            chat_id=sent_message.chat_id,
            chat_title=sent_message.chat.title if sent_message.chat.title else "Private Chat",
            text=sent_message.text,
            bot_id=bot.id,
            bot_name=bot.name
        )
    else:
        await waiting_message.edit_text('系統諗到hang咗機，一陣再試過啦！😵')
