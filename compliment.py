from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from ai import get_ai_summary
from config import HK_TIMEZONE, logger, COMPLIMENT_PROMPTS
from database import DatabasePool


async def compliment_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    message = update.message
    logger.info(f"Starting user compliment in chat {chat_id} with command: {message.text}")

    # Check if the message is a reply to another message
    if not message.reply_to_message:
        await message.reply_text("請回覆某個用戶嘅訊息，再用 /compliment 去吹奏佢！")
        return

    # Get the user from the replied-to message
    target_user = message.reply_to_message.from_user
    target_username = target_user.first_name if target_user.first_name else '唔知邊條粉蛋'
    if target_user.last_name:
        target_username += " " + target_user.last_name

    # Fetch the user's messages from today to give context to the AI (optional, for better compliments)
    now = datetime.now(HK_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        db_pool = DatabasePool.get_pool()
    except RuntimeError as e:
        logger.error(f"Database error: {e}")
        await message.reply_text("哎呀，資料庫未準備好，請稍後再試！")
        return

    conn = None
    user_messages = []
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_name, text, timestamp FROM messages
            WHERE chat_id = %s AND user_name = %s AND timestamp >= %s AND timestamp < %s
            ORDER BY timestamp ASC
        """, (chat_id, target_username, start_of_day, now))
        rows = cursor.fetchall()
        user_messages = [f"{row[0]}: {row[1]}" for row in rows]
    except Exception as e:
        logger.error(f"Failed to query database: {e}")
        # Proceed anyway with just the username if DB fails
        logger.info("Proceeding with compliment without message context")
    finally:
        if conn:
            db_pool.putconn(conn)

    # Prepare the AI prompt with user context
    messages_context = "\n".join(user_messages) if user_messages else "無今日訊息記錄"
    compliment_prompt = (
        f'{";".join(COMPLIMENT_PROMPTS)}'
        f"\n以下係目標用戶: ** {target_username} **"
        f"\n佢今日講咗嘅話:\n{messages_context}"
    )

    waiting_message = await message.reply_text(f"整緊讚賞俾 ** {target_username} **… ⏳")
    compliment = get_ai_summary(compliment_prompt)  # Reuse get_ai_summary with custom prompt
    logger.info(f"Generated compliment for user {target_username} in chat {chat_id}: {compliment}")

    if compliment and compliment != '系統想方加(出錯)，好對唔住':
        await waiting_message.edit_text(
            f"俾 ** {target_username} ** 嘅讚賞: 🌟\n{compliment}",
            parse_mode='Markdown'
        )
    else:
        await waiting_message.edit_text('系統想方加(出錯)，好對唔住')
