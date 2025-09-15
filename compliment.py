# compliment.py

from telegram import Update
from telegram.ext import ContextTypes

# Import the new vision function and the existing summary function
from ai import get_ai_summary, get_ai_vision_response
from config import logger, COMPLIMENT_PROMPTS, AI_GENERATE_BASE_PROMPT

async def compliment_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Generates a compliment for a user, based on either a replied-to text message or an image.
    """
    message = update.message
    logger.info(f"Starting user compliment in chat {message.chat_id} with command: {message.text}")

    # Check if the command is a reply to another message
    if not message.reply_to_message:
        await message.reply_text("請回覆某個用戶嘅訊息或圖片，再用 /compliment 去吹奏佢！")
        return

    # Get the target user's information from the replied message
    target_user = message.reply_to_message.from_user
    target_username = target_user.first_name or '唔知邊條粉蛋'
    if target_user.last_name:
        target_username += " " + target_user.last_name

    response_text = ''
    waiting_message = None
    system_prompt = f"{AI_GENERATE_BASE_PROMPT}\n{COMPLIMENT_PROMPTS}"

    # --- IMAGE HANDLING LOGIC ---
    # Check if the replied-to message contains a photo
    if message.reply_to_message.photo:
        # Get the lowest resolution 
        photo = message.reply_to_message.photo[0]
        # Get the file object from Telegram's servers
        file = await context.bot.get_file(photo.file_id)
        # The file_path is a temporary public URL to the image
        image_url = file.file_path

        # Create a prompt for the vision model
        vision_prompt = f"針對呢張相入面嘅 {target_username} ，用你最啜核嘅方式讚美佢。"

        waiting_message = await message.reply_text(f"睇緊 {target_username} 張靚相，度緊點讚… ⏳")
        # Call the new vision function
        response_text = await get_ai_vision_response(vision_prompt, image_url, system_prompt)

    # --- TEXT HANDLING LOGIC ---
    # Fallback to text if no photo is present
    elif message.reply_to_message.text:
        target_message = message.reply_to_message.text
        # Create a prompt for the text model
        text_prompt = (
            f"\n以下係目標用戶: ** {target_username} **"
            f"\n佢講咗嘅話: '{target_message}'"
        )
        waiting_message = await message.reply_text(f"分析緊 ** {target_username} ** 講過嘅嘢… ⏳")
        # Call the standard summary/text function
        response_text = await get_ai_summary(text_prompt, system_prompt)
    else:
        await message.reply_text("請回覆一個有文字或者有圖片嘅訊息啦！")
        return

    # --- UNIFIED RESPONSE ---
    # Edit the waiting message with the final result
    if response_text and '系統' not in response_text:
        await waiting_message.edit_text(
            f"俾 ** {target_username} ** 嘅讚賞: 🌟\n{response_text}"
        )
    else:
        # Show an error if the AI response was invalid
        await waiting_message.edit_text(response_text or '系統想方加(出錯)，好對唔住')
