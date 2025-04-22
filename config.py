from datetime import timedelta, timezone
from decouple import config
import os

# Configure logging
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Telegram Bot Token
TOKEN = config('BOT_TOKEN')

# Model and API settings
MODEL = config("MODEL")
API_KEY = config("API_KEY")
BASE_URL_CHAT = config('BASE_URL_CHAT')

# Hong Kong timezone (UTC+8)
HK_TIMEZONE = timezone(timedelta(hours=8))

# COMPLIMENT PROMPTS
COMPLIMENT_PROMPTS = [
    "用繁體中文同港式口語，吹奏讚美嗰位user",
    "讚賞要針對用戶嘅特點或貢獻，唔好太generic",
    "同時讚美佢嘅所有，由外貌，頭腦，說話，相處等",
    "提供對方滿滿嘅情緒價值",
    "字數控制喺70字內",
    "加啲emoji，唔好改用戶名，格式要用 Telegram Markdown",
]

# Golden prompts
GOLDEN_PROMPTS = [
    "用繁體中文同港式口語，分析以下對話，揀出今日嘅『金句王』",
    "即係講咗最多有趣、幽默或令人印象深刻嘅話嘅用戶。列出你揀嘅理由（50字內）",
    "加啲emoji，唔好改用戶名，格式要用 Telegram Markdown",
]

# Summarize prompts
SUMMARIZE_PROMPTS = [
    "綜合以下條件總結對話",
    "用繁體中文同港式口語",
    "對話加啲emoji",
    "說話方式要輕鬆有趣幽默",
    "將頭三對討論度高嘅對話分為三個chapter，每個chapter都有一個搞笑和連登feel的的subtitle",
    "每個chapter內容要精闢地總結相關對話內容，限制150字以內",
    "加個搞笑和連登仔tone的title俾個summary",
    "轉述內容時要提及邊位user講，user名不得自行更改，user名前後要加空格及粗體",
    "除左總結對話之外，係尾段總結邊位最多野講，格式為（[名]: 說話頻率百分比）",
    "內容文字格式要用 Telegram Markdown"
]

# SUMMARIZE_USER_PROMPTS
SUMMARIZE_USER_PROMPTS = [
    "綜合以下條件總結對話",
    "用繁體中文同港式口語",
    "對話加啲emoji",
    "說話方式要輕鬆有趣幽默",
    "加個搞笑和連登仔tone的title俾個summary",
    "轉述內容時要提及邊位user講，user名不得自行更改，user名格式要用 Telegram Markdown",
    "內容文字格式要用 Telegram Markdown"
]

# Database URL
DB_URL = os.getenv("DATABASE_URL", config("DATABASE_URL"))
