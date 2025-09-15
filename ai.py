# ai.py

import requests  # Use requests for synchronous HTTP calls
import base64
from openai import OpenAI  # Use the synchronous OpenAI client
from config import API_KEY, BASE_URL, MODEL, AI_GENERATE_BASE_PROMPT, LOVE_SYSTEM_PROMPT, AI_ANSWER_SYSTEM_PROMPT, logger

# --- CLIENT INITIALIZATION ---
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# --- VISION FUNCTION (SYNCHRONOUS) ---
def get_ai_vision_response(user_prompt: str, image_url: str, system_prompt: str) -> str:
    """
    Generates a response from the AI based on a text prompt and an image using synchronous calls.
    Includes enhanced logging to inspect the full API response.
    """
    logger.info("Starting get_ai_vision_response function.")
    try:
        logger.info(f"Downloading image from URL: {image_url}")
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()
        image_bytes = response.content
        logger.info("Image downloaded successfully.")

        logger.info("Encoding image to Base64.")
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        logger.info("Image encoded successfully.")

        logger.info("Calling OpenAI API for vision response.")
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
        
        # --- NEW DEBUGGING LINES ---
        # Log the full, raw response object from the API to see its structure.
        logger.info(f"Full API Response: {api_response}")
        
        # Check if the response is valid before trying to access its content.
        if api_response.choices and api_response.choices[0].message:
            logger.info("OpenAI API call successful, content found.")
            return api_response.choices[0].message.content
        else:
            # This will now catch cases where the API returns 200 OK but an empty/filtered response.
            logger.error("API call was successful but returned no content/choices.")
            return "AI 成功回應，但內容係空嘅，可能係安全設定擋咗。"

    except requests.exceptions.Timeout:
        logger.error("Timeout occurred while downloading image.")
        return '下載圖片超時，張相可能太大或者網絡有問題'
    except requests.exceptions.RequestException as http_err:
        logger.error(f"HTTP error occurred while downloading image: {http_err}")
        return '下載唔到張圖，請再試一次'
    except APITimeoutError:
        logger.error("OpenAI API call timed out.")
        return 'AI諗太耐諗到瞓著咗，請再試一次'
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_ai_vision_response: {e}")
        # Log the actual API response object if an error occurs during parsing
        if 'api_response' in locals():
            logger.error(f"API response at time of error: {locals().get('api_response')}")
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
