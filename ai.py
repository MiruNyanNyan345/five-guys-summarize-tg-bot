from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL, SUMMARIZE_PROMPTS


def get_ai_summary(text: str) -> str:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user",
                 "content": f'{";".join(SUMMARIZE_PROMPTS)};以下為需要總結的對話:{text}'},
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
