from telegram.ext import Application, MessageHandler, filters, CommandHandler

from compliment import compliment_user
from config import TOKEN, logger, AI_GENERATE_BASE_PROMPT
from database import DatabasePool, init_db, log_message  # Import DatabasePool instead of init_db_pool
from summarize import (summarize_day, summarize_morning, summarize_afternoon,
                       summarize_night, summarize_last_hour, summarize_last_3_hours,
                       summarize_user, summarize_golden_quote_king)
from fuck import fuck_user
from love import send_love_quote
from ai import get_ai_apology, get_ai_countdown
import pytz
from datetime import datetime

application = Application.builder().token(TOKEN).build()


async def countdown(update, context):
    chat_id = update.message.chat_id
    logger.info(f"Starting countdown for chat {chat_id}")


    # Check if it's Saturday or Sunday
    if weekday >= 5:  # Saturday (5) or Sunday (6)
        await update.message.reply_text("放緊假呀！😎")
        return

    # Check if it's Monday to Friday outside 9 AM to 6 PM
    current_hour = now.hour
    if current_hour < 9 or current_hour >= 18:
        await update.message.reply_text("放左工了！🎉")
        return

    message = get_ai_countdown()
    await update.message.reply_text(message)


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


if __name__ == "__main__":
    try:
        DatabasePool.init_pool()  # Call the static method to initialize
        init_db()
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        print(f"Bot cannot start due to: {e}")
        exit(1)

    # Register handlers
    application.add_handler(MessageHandler(filters.Text() & ~filters.Command(), log_message))
    # application.add_handler(CommandHandler("summarize_morning", summarize_morning))
    # application.add_handler(CommandHandler("summarize_afternoon", summarize_afternoon))
    # application.add_handler(CommandHandler("summarize_night", summarize_night))
    # application.add_handler(CommandHandler("summarize_last_hour", summarize_last_hour))
    # application.add_handler(CommandHandler("summarize_last_3_hours", summarize_last_3_hours))
    application.add_handler(CommandHandler("summarize", summarize_day))
    application.add_handler(CommandHandler("summarize_user", summarize_user))
    application.add_handler(CommandHandler("golden_quote_king", summarize_golden_quote_king))
    application.add_handler(CommandHandler("compliment", compliment_user))
    application.add_handler(CommandHandler("apologize", apologize))
    application.add_handler(CommandHandler("love", send_love_quote))
    application.add_handler(CommandHandler("countdown", countdown))
    application.add_handler(CommandHandler("diu", fuck_user))

    print("Starting bot...")
    application.run_polling()
