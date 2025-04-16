from ai import get_ai_love_quote

async def send_love_quote(update, context):
    chat_id = update.message.chat_id
    print(f"Starting love quote generation for chat {chat_id}")

    waiting_message = await update.message.reply_text("諗緊啲甜言蜜語… ⏳")
    love_quote = get_ai_love_quote()
    print(f"Generated love quote for chat {chat_id}: {love_quote}")

    if love_quote and love_quote != '哎呀，情話生成失敗，愛你唔使講😜':
        await waiting_message.edit_text(love_quote)
    else:
        await waiting_message.edit_text('哎呀，情話生成失敗，愛你唔使講😜')