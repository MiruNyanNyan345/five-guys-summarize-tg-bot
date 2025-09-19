from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from config import HK_TIMEZONE, logger, AI_CHAT_SYSTEM_PROMPT, AI_GENERATE_BASE_PROMPT
from db import DatabaseOperations
from ai import get_ai_summary


async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles AI chat functionality in group chats when the bot is mentioned or replied to.
    """
    message = update.message
    if not message or not message.text:
        return

    chat_id = message.chat_id
    try:
        bot_username = (await context.bot.get_me()).username
    except Exception as e:
        logger.error(f"無法獲取 bot 資料: {e}")
        return

    # Condition 1: Check if the message is a reply to the bot
    is_reply_to_bot = (message.reply_to_message and
                       message.reply_to_message.from_user.id == context.bot.id)

    # Condition 2: Check if the bot is mentioned in the message
    is_mention = False
    if message.entities:
        for entity in message.entities:
            if entity.type == 'mention':
                mentioned_user = message.text[entity.offset:entity.offset + entity.length]
                if mentioned_user == f"@{bot_username}":
                    is_mention = True
                    break
    if not is_reply_to_bot and not is_mention:
        return
    logger.info(f"AI 對話功能已於群組 {chat_id} 被用戶 {message.from_user.first_name} 觸發")

    # Retrieve messages from the past hour
    now = datetime.now(HK_TIMEZONE)
    start_time = now - timedelta(hours=1)

    db_ops = DatabaseOperations()
    rows = db_ops.get_messages_in_range(chat_id, start_time, now)

    if rows is None:
        await message.reply_text("哎呀，讀取對話紀錄時出錯！請稍後再試。")
        return

    # Construct conversation history, filtering out the current message to avoid duplication
    conversation_history = "\n".join([f"{row[0]}: {row[1]}" for row in rows if row[1] != message.text])
    print(f"Debug: Conversation history:\n{conversation_history}")

    current_message_text = message.text
    if is_mention:
        current_message_text = current_message_text.replace(f"@{bot_username}", "").strip()

    # Prepare the prompt for AI
    user_prompt = f"""
    # 對話紀錄 (過去一小時)
    ---
    {conversation_history if conversation_history else "（最近一個鐘冇人講過嘢）"}
    ---

    # 用戶最新嘅訊息
    {message.from_user.first_name}: "{current_message_text}"
    """

    system_prompt = f"""
    {AI_GENERATE_BASE_PROMPT}
    {AI_CHAT_SYSTEM_PROMPT}
    """

    waiting_message = await message.reply_text("諗緊點答… ⏳", reply_to_message_id=message.message_id)

    # Get AI response
    ai_response = get_ai_summary(user_prompt, system_prompt)

    # Send the AI response back to the chat
    if ai_response and ai_response != '系統想方加(出錯)，好對唔住':
        await waiting_message.edit_text(ai_response)
    else:
        await waiting_message.edit_text('我個腦hang咗機，一陣再試過🙏')
