from ai import get_ai_love_quote
from config import HK_TIMEZONE, logger, COMPLIMENT_PROMPTS
from db import DatabaseOperations
from datetime import datetime

async def send_love_quote(update, context):
    chat_id = update.message.chat_id
    message = update.message
    logger.info(f"Starting user compliment in chat {chat_id} with command: {message.text}")

    # Get the user from the replied-to message
    target_user = message.reply_to_message.from_user
    target_user_id = target_user.id
    target_username = target_user.first_name if target_user.first_name else '唔知邊條粉蛋'
    if target_user.last_name:
        target_username += " " + target_user.last_name

    now = datetime.now(HK_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    db_ops = DatabaseOperations()
    rows = db_ops.get_user_messages_in_range(chat_id, target_user_id, start_of_day, now)
    
    # Check if the message is a reply to another message
    if not message.reply_to_message:
        await message.reply_text("請回覆某個用戶嘅訊息，再用 /love 去對佢示愛！")
        return

    user_messages = ""
    if rows is None or not rows:
        user_messages = ""
    else:
        user_messages = "\t".join([f"{row[0]}: {row[1]}" for row in rows])
        
    waiting_message = await update.message.reply_text(f"諗緊啲甜言蜜語同 ** {target_username} ** 講… ⏳")
    love_quote = get_ai_love_quote(target_username, user_messages)
    logger.info(f"Generated love quote for chat {chat_id}: {love_quote}")

    if love_quote and love_quote != '哎呀，情話生成失敗，愛你唔使講😜':
        await waiting_message.edit_text(love_quote)
    else:
        await waiting_message.edit_text('哎呀，情話生成失敗，愛你唔使講😜')