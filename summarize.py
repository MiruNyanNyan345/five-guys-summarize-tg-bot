from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from config import HK_TIMEZONE, logger
from database import db_pool
from ai import get_ai_summary


async def summarize_in_range(update: Update, start_time: datetime, end_time: datetime, period_name: str) -> None:
    chat_id = update.message.chat_id
    logger.info(f"Starting summarization for {period_name} in chat {chat_id}")

    if db_pool is None:
        logger.error("Database pool not initialized")
        await update.message.reply_text("哎呀，資料庫未準備好，請稍後再試！")
        return

    conn = None
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_name, text, timestamp FROM messages
            WHERE chat_id = %s AND timestamp >= %s AND timestamp < %s
            ORDER BY timestamp ASC
        """, (chat_id, start_time, end_time))
        rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Failed to query database: {e}")
        await update.message.reply_text("哎呀，讀取訊息時出錯！請稍後再試。")
        return
    finally:
        if conn:
            db_pool.putconn(conn)

    if not rows:
        await update.message.reply_text(f"No messages to summarize for {period_name} in this chat!")
        logger.info(f"No messages found for {period_name} in chat {chat_id}")
        return

    day_messages = [f"{row[0]}: {row[1]}" for row in rows]
    text_to_summarize = "\n".join(day_messages)

    waiting_message = await update.message.reply_text("幫緊你幫緊你… ⏳")
    summary = get_ai_summary(text_to_summarize)
    logger.info(f"Generated summary for {period_name} in chat {chat_id}: {summary}")

    formatted_start = start_time.astimezone(HK_TIMEZONE).strftime("%Y-%m-%d %H:%M")
    formatted_end = end_time.astimezone(HK_TIMEZONE).strftime("%Y-%m-%d %H:%M")
    if summary and summary != '系統想方加(出錯)，好對唔住':
        await waiting_message.edit_text(
            f"由{formatted_start} - {formatted_end}嘅{period_name}對話總結為: 📝\n{summary}",
            parse_mode='Markdown'
        )
    else:
        await waiting_message.edit_text('系統想方加(出錯)，好對唔住')


async def summarize_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    message_text = update.message.text
    logger.info(f"Starting user summarization in chat {chat_id} with command: {message_text}")

    args = message_text.split()
    if len(args) < 2 or not args[1].startswith('@'):
        await update.message.reply_text("請用格式 /summarize_user @username，例如 /summarize_user @john_doe")
        return

    target_username = args[1][1:]

    now = datetime.now(HK_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if db_pool is None:
        logger.error("Database pool not initialized")
        await update.message.reply_text("哎呀，資料庫未準備好，請稍後再試！")
        return

    conn = None
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_name, text, timestamp FROM messages
            WHERE chat_id = %s AND user_name = %s AND timestamp >= %s AND timestamp < %s
            ORDER BY timestamp ASC
        """, (chat_id, target_username, start_of_day, now))
        rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Failed to query database: {e}")
        await update.message.reply_text("哎呀，讀取訊息時出錯！請稍後再試。")
        return
    finally:
        if conn:
            db_pool.putconn(conn)

    if not rows:
        await update.message.reply_text(f"今日由00:00開始， ** {target_username} ** 無講過任何野喎！")
        return

    user_messages = [f"{row[0]}: {row[1]}" for row in rows]
    text_to_summarize = "\n".join(user_messages)

    waiting_message = await update.message.reply_text(f"幫緊你總結 ** {target_username} ** 今日講咗啲咩… ⏳")
    summary = get_ai_summary(text_to_summarize)
    logger.info(f"Generated summary for user {target_username} in chat {chat_id}: {summary}")

    formatted_start = start_of_day.strftime("%Y-%m-%d %H:%M")
    formatted_end = now.strftime("%Y-%m-%d %H:%M")
    if summary and summary != '系統想方加(出錯)，好對唔住':
        await waiting_message.edit_text(
            f"由 {formatted_start} 到 {formatted_end}， ** {target_username} ** 講咗嘅總結: 📝\n{summary}",
            parse_mode='Markdown'
        )
    else:
        await waiting_message.edit_text('系統想方加(出錯)，好對唔住')
