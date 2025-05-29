from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL, SUMMARIZE_PROMPTS, LIHKG_BASE_PROMPT


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
                {
                    "role": "user",
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

def get_ai_love_quote(username: str) -> str:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system",
                 "content": LIHKG_BASE_PROMPT},
                {"role": "user",
                 "content": f"#上https://www.threads.net/上搵熱門的土味情話\n#只返回一句\n#將情話的對像轉換成{username}\n#轉換成繁體中文\n#要求搞笑，甜蜜，肉麻# 加上帶emoji\n#不用解析"},
            ],
            stream=False
        )
        love_quote = response.choices[0].message.content
        love_quote += "\n\n免責聲明: 土味情話純屬娛樂😘請勿當真💖"
        return love_quote
    except Exception as e:
        print(f"Error in get_love_quote: {e}")
        return '哎呀，情話生成失敗，愛你唔使講😜'
    
def get_ai_generate_image(text: str) -> str:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    try:
        response = client.images.generate(
            model="grok-2-image-latest", 
            prompt=text,
            n=1,
            response_format="url"
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        print(f"Error in get_openai_image: {e}")
        return '哎呀，生成圖片失敗，唔好怪我🙏'