from telegram.ext import Application, MessageHandler, filters, CommandHandler
from config import TOKEN, logger
from database import init_db_pool, init_db, log_message
from summarize import (summarize_day, summarize_morning, summarize_afternoon,
                       summarize_night, summarize_last_hour, summarize_last_3_hours, summarize_by_user)
from aplogize import apologize

application = Application.builder().token(TOKEN).build()

if __name__ == "__main__":
    try:
        init_db_pool()
        init_db()
    except Exception as e:
        print(f"Startup failed: {e}")
        exit(1)

    # Register handlers
    application.add_handler(MessageHandler(filters.Text() & ~filters.Command(), log_message))
    application.add_handler(CommandHandler("summarize", summarize_day))
    application.add_handler(CommandHandler("summarize_morning", summarize_morning))
    application.add_handler(CommandHandler("summarize_afternoon", summarize_afternoon))
    application.add_handler(CommandHandler("summarize_night", summarize_night))
    application.add_handler(CommandHandler("summarize_last_hour", summarize_last_hour))
    application.add_handler(CommandHandler("summarize_last_3_hours", summarize_last_3_hours))
    application.add_handler(CommandHandler("summarize_by_user", summarize_by_user))
    application.add_handler(CommandHandler("apologize", apologize))

    print("Starting bot...")
    application.run_polling()
