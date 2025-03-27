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
MODEL = "deepseek-chat"
API_KEY = config("API_KEY")
BASE_URL = "https://api.deepseek.com"

# Hong Kong timezone (UTC+8)
HK_TIMEZONE = timezone(timedelta(hours=8))

# Summarize prompts
SUMMARIZE_PROMPTS = [
    "綜合以下條件總結對話",
    "用繁體中文同港式口語",
    "對話加啲emoji",
    "說話方式要模仿連登仔，輕鬆有趣幽默",
    "將頭三對討論度高嘅對話分為三個chapter，每個chapter都有一個搞笑和連登feel的的subtitle",
    "每個chapter內容要精闢地總結相關對話內容，限制150字以內",
    "加個搞笑和連登仔tone的title俾個summary",
    "轉述內容時要提及邊位user講，user名不得自行更改，user名前後要加空格及粗體",
    "除左總結對話之外，係尾段總結邊位最多野講，格式為（[名]: 說話頻率百分比）",
    "內容文字格式需要符合telegram，例如粗體"
]

# Database URL
DB_URL = os.getenv("DATABASE_URL", config("DATABASE_URL"))
