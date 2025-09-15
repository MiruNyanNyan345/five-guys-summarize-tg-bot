# ai.py

import requests  # Use requests for synchronous HTTP calls
import base64
from openai import OpenAI  # Use the synchronous OpenAI client
from config import API_KEY, BASE_URL, MODEL, AI_GENERATE_BASE_PROMPT, LOVE_SYSTEM_PROMPT, AI_ANSWER_SYSTEM_PROMPT

# --- CLIENT INITIALIZATION ---
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# --- VISION FUNCTION (SYNCHRONOUS) ---
def get_ai_vision_response(user_prompt: str, image_url: str, system_prompt: str) -> str:
    """
    Generates a response from the AI based on a text prompt and an image using synchronous calls.
    It downloads the image, encodes it in Base64, and sends the data directly.
    Args:
        user_prompt: The text prompt related to the image.
        image_url: The public URL of the image from Telegram.
        system_prompt: The system message to guide the AI's behavior.
    Returns:
        The AI-generated text response as a string.
    """
    try:
        # Step 1: Synchronously download the image content from the URL
        response = requests.get(image_url)
        response.raise_for_status()
        image_bytes = response.content

        # Step 2: Encode the downloaded image content into a Base64 string
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # Step 3: Call the AI API with the Base64 encoded image data (no await)
        api_response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            stream=False,
            max_tokens=200
        )
        return api_response.choices[0].message.content
    except requests.exceptions.RequestException as http_err:
        print(f"HTTP error occurred while downloading image: {http_err}")
        return '下載唔到張圖，請再試一次'
    except Exception as e:
        print(f"Error in get_ai_vision_response: {e}")
        return '系統分析唔到張圖，好對唔住'


# --- TEXT-ONLY FUNCTIONS (SYNCHRONOUS) ---

def get_ai_answer(user_prompt: str) -> str:
    """
    Generates a text-based answer from the AI.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": AI_ANSWER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in get_ai_answer: {e}")
        return '系統想方加(出錯)，好對唔住'

def get_ai_summary(user_prompt: str, system_prompt="") -> str:
    """
    Generates a text-based summary or response from the AI.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt if system_prompt else AI_GENERATE_BASE_PROMPT
                },
                {"role": "user", "content": user_prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in get_ai_summary: {e}")
        return '系統想方加(出錯)，好對唔住'

def get_ai_apology() -> str:
    """
    Generates a humorous apology.
    """
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
    """
    Generates a cheesy love quote.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": LOVE_SYSTEM_PROMPT},
                {"role": "user", "content": f"username:{username}\tuser's messages:{user_messages}"},
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
    """
    Generates a creative countdown message.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": AI_GENERATE_BASE_PROMPT},
                {"role": "user", "content": f"再修飾以下句子，使內容變得有趣: '{user_prompt}'"},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in get_ai_countdown: {e}")
        return f"錯撚曬！"
