from telegram.ext import Application, MessageHandler, filters, CommandHandler
from compliment import compliment_user
from config import TOKEN, logger, AI_GENERATE_BASE_PROMPT
from database import DatabasePool, init_db, log_message  # Import DatabasePool instead of init_db_pool
from summarize import (summarize_day, summarize_morning, summarize_afternoon,
                       summarize_night, summarize_last_hour, summarize_last_3_hours,
                       summarize_user, summarize_golden_quote_king)
from dxx import diu
from love import send_love_quote
from ai import get_ai_apology, get_ai_countdown, get_ai_answer
import pytz
from datetime import datetime, timedelta
from ai_chat import handle_chat

application = Application.builder().token(TOKEN).build()


async def donate(update, context):
    await update.message.reply_text(
        "支持我哋嘅開發，請喺呢度請杯咖啡 ☕： https://buymeacoffee.com/fiveguyshk",
        disable_web_page_preview=False
    )


async def countdown_to_retirement(update, context):
    chat_id = update.message.chat_id
    logger.info(f"Starting countdown to retirement for chat {chat_id}")

    # Check if year parameter is provided
    if not context.args:
        await update.message.reply_text("請提供退休年份，例如：/countdown_to_retirement 2050")
        return

    try:
        retirement_year = int(context.args[0])
    except ValueError:
        await update.message.reply_text("年份必須係數字，例如：/countdown_to_retirement 2050")
        return

    # Define Hong Kong time zone
    hk_tz = pytz.timezone('Asia/Hong_Kong')

    # Get current time in Hong Kong
    now = datetime.now(hk_tz)
    current_year = now.year

    # Validate retirement year
    if retirement_year <= current_year:
        await update.message.reply_text(f"退休年份必須大過而家嘅年份 ({current_year})！")
        return

    # Set target to January 1st of the retirement year
    target = datetime(retirement_year, 1, 1, 0, 0, 0, tzinfo=hk_tz)

    # Calculate time difference
    time_left = target - now
    total_minutes = (time_left.days * 24 * 60) + (time_left.seconds // 60)
    total_minutes += 1

    # Format the countdown message
    waiting_message = await update.message.reply_text("計緊仲有幾耐就退休...")
    countdown_message = get_ai_countdown(f"距離退休仲有 {total_minutes:,} 分鐘")
    if countdown_message:
        await waiting_message.edit_text(countdown_message)
    else:
        await waiting_message.edit_text('計唔L到，叫五仁哥人手計🙇‍♂️')


async def countdown_to_work(update, context):
    chat_id = update.message.chat_id
    logger.info(f"Starting countdown to work for chat {chat_id}")

    # Define Hong Kong time zone
    hk_tz = pytz.timezone('Asia/Hong_Kong')

    # Get current time in Hong Kong
    now = datetime.now(hk_tz)

    # Get day of the week (0 = Monday, 6 = Sunday)
    weekday = now.weekday()

    # Check if it's within working hours (Monday-Friday, 9 AM to 6 PM)
    current_hour = now.hour
    if weekday < 5 and 9 <= current_hour < 18:  # Monday to Friday, 9 AM to 6 PM
        await update.message.reply_text("返緊工喇柒頭...😓")
        return

    # Calculate time to next workday start (9 AM)
    if weekday >= 5:  # Saturday or Sunday
        # Next Monday 9 AM
        days_until_monday = (7 - weekday) % 7
        target = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
        if days_until_monday == 0:  # If Sunday, add one day to get to Monday
            target += timedelta(days=1)
    else:  # Monday to Friday, outside working hours
        if current_hour >= 18:  # After 6 PM, target is next day 9 AM
            target = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
            # If next day is Saturday, skip to Monday
            if (now + timedelta(days=1)).weekday() >= 5:
                target += timedelta(days=2 if (now + timedelta(days=1)).weekday() == 5 else 1)
        else:  # Before 9 AM
            target = now.replace(hour=9, minute=0, second=0, microsecond=0)

    # Calculate time difference in minutes
    time_left = target - now
    total_minutes = (time_left.days * 24 * 60) + (time_left.seconds // 60)
    total_minutes += 1

    waiting_message = await update.message.reply_text("計緊仲有幾耐就返工...")
    countdown_message = get_ai_countdown(f"距離返工時間仲有 {total_minutes:,} 分鐘")
    if countdown_message:
        await waiting_message.edit_text(countdown_message)
    else:
        await waiting_message.edit_text('計唔L到，叫五仁哥人手計🙇‍♂️')


async def countdown(update, context):
    chat_id = update.message.chat_id
    logger.info(f"Starting countdown for chat {chat_id}")

    # Define Hong Kong time zone
    hk_tz = pytz.timezone('Asia/Hong_Kong')

    # Get current time in Hong Kong
    now = datetime.now(hk_tz)

    # Get day of the week (0 = Monday, 6 = Sunday)
    weekday = now.weekday()

    # Set target time to 6 PM today in Hong Kong
    target = now.replace(hour=18, minute=0, second=0, microsecond=0)

    # Calculate time difference in minutes
    time_left = target - now
    total_minutes = time_left.seconds // 60
    total_minutes += 1

    # Check if it's Saturday or Sunday
    if weekday >= 5:  # Saturday (5) or Sunday (6)
        await update.message.reply_text("放緊假呀！😎")
        return

    # Check if it's Monday to Friday outside 9 AM to 6 PM
    current_hour = now.hour
    if current_hour < 9 or current_hour >= 18:
        await update.message.reply_text("放左工了！🎉")
        return
    waiting_message = await update.message.reply_text("計緊仲有幾耐先收工...")
    countdown_message = get_ai_countdown(f"仲有 {total_minutes} 分鐘就放工")
    if countdown_message:
        await waiting_message.edit_text(countdown_message)
    else:
        await waiting_message.edit_text('計唔L到，叫五仁哥人手計🙇‍♂️')


async def apologize(update, context):
    chat_id = update.message.chat_id
    print(f"Starting apology generation for chat {chat_id}")

    waiting_message = await update.message.reply_text("度緊呢單野點拆… ⏳")
    apology = get_ai_apology()
    print(f"Generated apology for chat {chat_id}: {apology}")

    if apology and apology != '哎呀，道歉失敗，唔好打我🙏':
        await waiting_message.edit_text(apology)
    else:
        await waiting_message.edit_text('哎呀，道歉失敗，唔好打我🙏')


async def answer(update, context):
    chat_id = update.message.chat_id
    message = update.message
    logger.info(f"Starting answer command in chat {chat_id} with command: {message.text}")

    # Check if context args are provided
    if not context.args:
        await message.reply_text("請提供問題，例如：/answer 你點解咁叻？")
        return

    # Join context args to form the target message
    target_message = ' '.join(context.args)

    # Prepare the prompt for AI-generated answer, focusing on the replied message
    user_prompt = (
        f"解答以下提問：'{target_message}'"
    )

    waiting_message = await message.reply_text(f"幫你諗緊… ⏳")
    answer = get_ai_answer(user_prompt)
    logger.info(f"Generated answer for chat {chat_id}: {answer}")

    if answer and answer != '系統想方加(出錯)，好對唔住':
        await waiting_message.edit_text(
            f"🤖{answer}"
        )
    else:
        await waiting_message.edit_text('無氣答，唔好打我🙏')


if __name__ == "__main__":
    try:
        DatabasePool.init_pool()  # Call the static method to initialize
        init_db()
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        print(f"Bot cannot start due to: {e}")
        exit(1)

    # Register the AI chat handler for mentions and replies
    application.add_handler(MessageHandler(filters.TEXT & ~filters.Command(), handle_chat))

    #   Register the message logging handler for all text messages
    application.add_handler(MessageHandler(filters.Text() & ~filters.Command(), log_message))

    # Register handlers for commands
    application.add_handler(CommandHandler("summarize", summarize_day))
    application.add_handler(CommandHandler("summarize_user", summarize_user))
    application.add_handler(CommandHandler("golden_quote_king", summarize_golden_quote_king))
    application.add_handler(CommandHandler("compliment", compliment_user))
    application.add_handler(CommandHandler("apologize", apologize))
    application.add_handler(CommandHandler("love", send_love_quote))
    application.add_handler(CommandHandler("countdown", countdown))
    application.add_handler(CommandHandler("countdown_to_work", countdown_to_work))
    application.add_handler(CommandHandler("countdown_to_retirement", countdown_to_retirement))
    application.add_handler(CommandHandler("diu", diu))
    application.add_handler(CommandHandler("ask", answer))
    application.add_handler(CommandHandler("donate", donate))

    print("Starting bot...")
    application.run_polling()
