from telegram.ext import Application, MessageHandler, filters, CommandHandler

from compliment import compliment_user
from config import TOKEN, logger
from database import DatabasePool, init_db, log_message  # Import DatabasePool instead of init_db_pool
from summarize import (summarize_day, summarize_morning, summarize_afternoon,
                       summarize_night, summarize_last_hour, summarize_last_3_hours,
                       summarize_user, summarize_golden_quote_king)
from fuck import fuck_user
from love import send_love_quote
from ai import get_ai_apology
import pytz
from datetime import datetime

application = Application.builder().token(TOKEN).build()

async def countdown(update, context):
    chat_id = update.message.chat_id
    logger.info(f"Starting countdown for chat {chat_id}")

    # Define Hong Kong time zone
    hk_tz = pytz.timezone('Asia/Hong_Kong')
    
    # Get current time in Hong Kong
    now = datetime.now(hk_tz)
    
    # Get day of the week (0 = Monday, 6 = Sunday)
    weekday = now.weekday()
    
    # Check if it's Saturday or Sunday
    if weekday >= 5:  # Saturday (5) or Sunday (6)
        await update.message.reply_text("放緊假呀！😎")
        return
    
    # Check if it's Monday to Friday outside 9 AM to 6 PM
    current_hour = now.hour
    if current_hour < 9 or current_hour >= 18:
        await update.message.reply_text("放左工了！🎉")
        return
    
    # Set target time to 6 PM today in Hong Kong
    target = now.replace(hour=18, minute=0, second=0, microsecond=0)
    
    # Calculate time difference in minutes
    time_left = target - now
    total_minutes = time_left.seconds // 60

    # Format the countdown message
    countdown_message = f"仲有 {total_minutes} 分鐘 就放工！💼 捱多陣啦！"
    await update.message.reply_text(countdown_message)

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

async def generate_image(update, context):
    chat_id = update.message.chat_id
    logger.info(f"Starting image generation for chat {chat_id}")

    # Get the prompt from command Secondary Bot API is not supported for this request.
    prompt = " ".join(context.args) if context.args else None
    if not prompt:
        await update.message.reply_text("請喺 /image 後面加個描述，例如：/image 一隻喵星人喺月球跳舞 🐱🌙")
        return

    waiting_message = await update.message.reply_text("畫緊你嘅圖… ⏳")
    image_url = get_ai_generate_image(prompt)
    logger.info(f"Image generation result for chat {chat_id}: {image_url}")

    if image_url and not image_url.startswith('哎呀'):
        try:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                caption=f"生成圖片：{prompt} 🎨\n\n免責聲明: 圖片由OpenAI生成，純屬娛樂🖼️"
            )
            await waiting_message.delete()  # Remove waiting message
        except Exception as e:
            logger.error(f"Error sending image in chat {chat_id}: {e}")
            await waiting_message.edit_text("哎呀，發送圖片失敗，唔好怪我🙏")
    else:
        await waiting_message.edit_text(image_url or '哎呀，生成圖片失敗，唔好怪我🙏')

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
    application.add_handler(CommandHandler("summarize", summarize_day))
    application.add_handler(CommandHandler("summarize_morning", summarize_morning))
    application.add_handler(CommandHandler("summarize_afternoon", summarize_afternoon))
    application.add_handler(CommandHandler("summarize_night", summarize_night))
    application.add_handler(CommandHandler("summarize_last_hour", summarize_last_hour))
    application.add_handler(CommandHandler("summarize_last_3_hours", summarize_last_3_hours))
    application.add_handler(CommandHandler("summarize_user", summarize_user))
    application.add_handler(CommandHandler("golden_quote_king", summarize_golden_quote_king))
    application.add_handler(CommandHandler("compliment", compliment_user))
    application.add_handler(CommandHandler("apologize", apologize))
    application.add_handler(CommandHandler("love", send_love_quote))
    application.add_handler(CommandHandler("image", generate_image))
    application.add_handler(CommandHandler("countdown", countdown))
    application.add_handler(CommandHandler("fuck", fuck_user))

    print("Starting bot...")
    application.run_polling()
