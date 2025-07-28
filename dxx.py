from telegram import Update
from telegram.ext import ContextTypes
from config import logger, HK_TIMEZONE, AI_GENERATE_BASE_PROMPT
from ai import get_ai_summary
from datetime import datetime

async def diu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    message = update.message
    logger.info(f"Starting fuck command in chat {chat_id} with command: {message.text}")

    # Check if the message is a reply to another message
    if not message.reply_to_message:
        await message.reply_text("請回覆某個用戶嘅訊息，再用 /diu 來俾佢一啲搞笑嘅『懲罰』！😜")
        return

    # Get the user and the replied-to message content
    target_user = message.reply_to_message.from_user
    target_message = message.reply_to_message.text or "佢無講具體嘢，純粹搗亂😝"
    target_username = target_user.first_name if target_user.first_name else '唔知邊條粉蛋'
    if target_user.last_name:
        target_username += " " + target_user.last_name

    # Prepare the prompt for AI-generated punishment, focusing on the replied message
    user_prompt = (
        f"針對{target_username}嘅以下訊息：'{target_message}'，去屌{target_user}"
    )

    waiting_message = await message.reply_text(f"幫你諗緊點Diu7 {target_username}… ⏳")
    punishment = get_ai_summary(user_prompt, AI_GENERATE_BASE_PROMPT)
    logger.info(f"Generated punishment for {target_username} in chat {chat_id}: {punishment}")

    now = datetime.now(HK_TIMEZONE)
    formatted_time = now.strftime("%Y-%m-%d %H:%M")
    if punishment and punishment != '系統想方加(出錯)，好對唔住':
        await waiting_message.edit_text(
            f"😈{punishment}"
        )
    else:
        await waiting_message.edit_text('無氣diu，唔好diu我🙏')