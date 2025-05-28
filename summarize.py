from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from config import HK_TIMEZONE, logger, GOLDEN_PROMPTS, SUMMARIZE_PROMPTS, SUMMARIZE_USER_PROMPTS
from database import DatabasePool  # Import the class instead of db_pool
from ai import get_ai_summary


async def summarize_golden_quote_king(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    logger.info(f"Starting golden quote king selection in chat {chat_id}")

    now = datetime.now(HK_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        db_pool = DatabasePool.get_pool()
    except RuntimeError as e:
        logger.error(f"Database error: {e}")
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
        """, (chat_id, start_of_day, now))
        rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Failed to query database: {e}")
        await update.message.reply_text("哎呀，讀取訊息時出錯！請稍後再試。")
        return
    finally:
        if conn:
            db_pool.putconn(conn)

    if not rows:
        await update.message.reply_text("今日靜L過太空呀，點揀金句王呀！")
        logger.info(f"No messages found for golden quote king in chat {chat_id}")
        return

    # 將訊息按用戶分組
    user_messages = {}
    for row in rows:
        user = row[0]
        if user not in user_messages:
            user_messages[user] = []
        user_messages[user].append(row[1])

    # 準備 AI 分析嘅文本
    analysis_text = "\n\n".join([f"{user}:\n" + "\n".join(msgs) for user, msgs in user_messages.items()])

    golden_prompt = f"{";".join(GOLDEN_PROMPTS)}\n\n以下係今日嘅對話:\n{analysis_text}"

    waiting_message = await update.message.reply_text("搵緊今日嘅金句王… ⏳")
    summary = get_ai_summary(golden_prompt)
    logger.info(f"Generated golden quote king summary in chat {chat_id}: {summary}")

    formatted_start = start_of_day.strftime("%Y-%m-%d %H:%M")
    formatted_end = now.strftime("%Y-%m-%d %H:%M")
    if summary and summary != '系統想方加(出錯)，好對唔住':
        await waiting_message.edit_text(
            f"由 {formatted_start} 到 {formatted_end} 嘅金句王總結: 🏆\n{summary}",
            parse_mode='Markdown'
        )
    else:
        await waiting_message.edit_text('系統想方加(出錯)，好對唔住')


async def summarize_in_range(update: Update, start_time: datetime, end_time: datetime, period_name: str) -> None:
    chat_id = update.message.chat_id
    logger.info(f"Starting summarization for {period_name} in chat {chat_id}")

    try:
        db_pool = DatabasePool.get_pool()
    except RuntimeError as e:
        logger.error(f"Database error: {e}")
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
    summary = get_ai_summary(f'以下為需要總結的對話:{text_to_summarize}')
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
    message = update.message
    logger.info(f"Starting user summarization in chat {chat_id} with command: {message.text}")

    # Check if the message is a reply to another message
    if not message.reply_to_message:
        await message.reply_text("請回覆某個用戶嘅訊息，再用 /summarize_user 來總結佢今日講咗啲咩！")
        return

    # Get the user from the replied-to message
    target_user = message.reply_to_message.from_user
    target_user_id = target_user.id
    target_username = target_user.first_name if target_user.first_name else '唔知邊條粉蛋'
    if target_user.last_name:
        target_username += " " + target_user.last_name

    now = datetime.now(HK_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        db_pool = DatabasePool.get_pool()
    except RuntimeError as e:
        logger.error(f"Database error: {e}")
        await message.reply_text("哎呀，資料庫未準備好，請稍後再試！")
        return

    conn = None
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_name, text, timestamp FROM messages
            WHERE chat_id = %s AND user_id = %s AND timestamp >= %s AND timestamp < %s
            ORDER BY timestamp ASC
        """, (chat_id, int(target_user_id), start_of_day, now))
        rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Failed to query database: {e}")
        await message.reply_text("哎呀，讀取訊息時出錯！請稍後再試。")
        return
    finally:
        if conn:
            db_pool.putconn(conn)

    if not rows:
        await message.reply_text(f"今日由00:00開始， ** {target_username} ** 無講過任何野喎！")
        return

    user_messages = [f"{row[0]}: {row[1]}" for row in rows]
    text_to_summarize = "\n".join(user_messages)

    waiting_message = await message.reply_text(f"幫緊你總結 ** {target_username} ** 今日講咗啲咩… ⏳")
    summary = get_ai_summary(f'{";".join(SUMMARIZE_USER_PROMPTS)};以下為需要總結的對話:{text_to_summarize}')
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


async def summarize_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(HK_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
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