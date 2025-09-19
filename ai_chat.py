from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from config import HK_TIMEZONE, logger, AI_CHAT_SYSTEM_PROMPT, AI_GENERATE_BASE_PROMPT
from db import DatabaseOperations
from ai import get_ai_summary


async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    處理對 bot 嘅直接提及 (mention) 同回覆 (reply)，
    並根據過去一個鐘嘅對話內容生成 AI 回覆。
    """
    message = update.message
    # 如果訊息為空或冇文字內容，就唔處理
    if not message or not message.text:
        return

    chat_id = message.chat_id
    try:
        bot_username = (await context.bot.get_me()).username
    except Exception as e:
        logger.error(f"無法獲取 bot 資料: {e}")
        return

    # 條件一：檢查係咪回覆緊 bot 嘅訊息
    is_reply_to_bot = (message.reply_to_message and
                       message.reply_to_message.from_user.id == context.bot.id)

    # 條件二：檢查訊息有冇提及 (mention) bot
    is_mention = False
    if message.entities:
        for entity in message.entities:
            if entity.type == 'mention':
                # 從訊息文字中提取被提及嘅用戶名
                mentioned_user = message.text[entity.offset:entity.offset + entity.length]
                # 檢查被提及嘅係咪呢個 bot
                if mentioned_user == f"@{bot_username}":
                    is_mention = True
                    break

    # 如果唔係回覆 bot 或者提及 bot，就結束
    if not is_reply_to_bot and not is_mention:
        return

    logger.info(f"AI 對話功能已於群組 {chat_id} 被用戶 {message.from_user.first_name} 觸發")

    # 從資料庫讀取過去一個鐘嘅對話紀錄
    now = datetime.now(HK_TIMEZONE)
    start_time = now - timedelta(hours=1)

    db_ops = DatabaseOperations()
    rows = db_ops.get_messages_in_range(chat_id, start_time, now)

    if rows is None:
        await message.reply_text("哎呀，讀取對話紀錄時出錯！請稍後再試。")
        return

    # 格式化對話紀錄，準備傳送俾 AI
    # 我哋會排除觸發今次事件嘅訊息本身
    conversation_history = "\n".join([f"{row[0]}: {row[1]}" for row in rows if row[1] != message.text])

    current_message_text = message.text
    # 如果係提及 bot，就喺訊息中移除 bot 嘅 username
    if is_mention:
        current_message_text = current_message_text.replace(f"@{bot_username}", "").strip()

    # 準備俾 AI 嘅指示 (Prompt)
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

    # 獲取 AI 生成嘅回覆
    ai_response = get_ai_summary(user_prompt, system_prompt)

    # 送出回覆
    if ai_response and ai_response != '系統想方加(出錯)，好對唔住':
        await waiting_message.edit_text(ai_response)
    else:
        await waiting_message.edit_text('我個腦hang咗機，一陣再試過🙏')
