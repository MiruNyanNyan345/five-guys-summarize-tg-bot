from telegram import Update
from telegram.ext import ContextTypes
from config import logger, HK_TIMEZONE, AI_GENERATE_BASE_PROMPT
from ai import get_ai_summary, get_ai_vision_response
from datetime import datetime

async def diu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Generates a playful roast for a user, based on either a replied-to text message or an image.
    """
    message = update.message
    logger.info(f"Starting diu command in chat {message.chat_id} with command: {message.text}")

    # Check if the command is a reply to another message
    if not message.reply_to_message:
        await message.reply_text("請回覆某個用戶嘅訊息或圖片，再用 /diu 來俾佢一啲搞笑嘅『懲罰』！😜")
        return

    # Get the target user's information
    target_user = message.reply_to_message.from_user
    target_username = target_user.first_name or '唔知邊條粉蛋'
    if target_user.last_name:
        target_username += " " + target_user.last_name

    response_text = ''
    waiting_message = None
    system_prompt = AI_GENERATE_BASE_PROMPT # Use the base prompt for this command

    # --- IMAGE HANDLING LOGIC ---
    # Check if the replied-to message contains a photo
    if message.reply_to_message.photo:
        photo = message.reply_to_message.photo[0]
        file = await context.bot.get_file(photo.file_id)
        image_url = file.file_path

        # Create a prompt for the vision model
        vision_prompt = f"針對呢張相，組織一句啜核嘅句子去『Diu』 {target_username}。"
        waiting_message = await message.reply_text(f"幫你睇緊點樣Diu爆 {target_username} 張相… ⏳")
        # Call the vision function
        response_text = get_ai_vision_response(vision_prompt, image_url, system_prompt)

    # --- TEXT HANDLING LOGIC ---
    # Fallback to text if no photo is present
    elif message.reply_to_message.text:
        target_message = message.reply_to_message.text
        # Create a prompt for the text model
        text_prompt = (
            f"""
            針對 {target_username} 嘅以下訊息：'{target_message}'
            組織一句句子去屌 {target_username}。
            
            #禁止事項#
            - 不用寫註解
            - 不用解釋生成結果
            """
        )
        waiting_message = await message.reply_text(f"幫你諗緊點Diu7 {target_username}… ⏳")
        # Call the standard text function
        response_text = get_ai_summary(text_prompt, system_prompt)
    else:
        await message.reply_text("請回覆一個有文字或者有圖片嘅訊息啦！")
        return

    # --- UNIFIED RESPONSE ---
    # Edit the waiting message with the final result
    if response_text and '系統' not in response_text:
        await waiting_message.edit_text(
            f"😈 {response_text}"
        )
    else:
        # Show an error if the AI response was invalid
        await waiting_message.edit_text(response_text or '無氣diu，唔好diu我🙏')
