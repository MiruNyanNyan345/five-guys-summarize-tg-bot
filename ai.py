from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL, SUMMARIZE_PROMPTS, AI_GENERATE_BASE_PROMPT, LOVE_SYSTEM_PROMPT
import pytz
from datetime import datetime

def get_ai_summary(user_prompt: str, system_prompt="") -> str:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt if system_prompt != "" else SUMMARIZE_PROMPTS
                },
                {"role": "user",
                    "content": user_prompt
                },
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in get_ai_summary: {e}")
        return '系統想方加(出錯)，好對唔住'


def get_ai_apology() -> str:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user",
                 "content": "用繁體中文同香港式口語去道歉，請人食五仁月餅，搞笑但唔會得罪人嘅道歉，要有啲emoji，字數30以下，不用加上註解"},
            ],
            stream=False
        )
        apology = response.choices[0].message.content
        apology += "\n\n免責聲明: 唔關五仁月餅事🥮求下大家俾下面🙏"
        return apology
    except Exception as e:
        print(f"Error in get_ai_apology: {e}")
        return '哎呀，道歉失敗，唔好打我🙏'


def get_ai_love_quote(username: str, user_messages: str) -> str:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system",
                 "content": LOVE_SYSTEM_PROMPT},
                {"role": "user",
                 "content": f"username:{username}\tuser's messages:{user_messages}"},
            ],
            stream=False
        )
        love_quote = response.choices[0].message.content
        love_quote += "\n\n免責聲明: 土味情話純屬娛樂😘請勿當真💖"
        return love_quote
    except Exception as e:
        print(f"Error in get_love_quote: {e}")
        return '哎呀，情話生成失敗，愛你唔使講😜'

def get_ai_countdown(user_prompt="") -> str:
    # AI generate
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": AI_GENERATE_BASE_PROMPT
                },
                {
                    "role": "user",
                    "content": f"再修飾以下句子，使內容變得有趣: '{user_prompt}'"
                },
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in get_ai_summary: {e}")
        return f"錯撚曬！"