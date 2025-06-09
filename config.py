import re
from os import environ

API_ID = int(environ.get("API_ID", 123456))  # Replace with your own or set via env
API_HASH = environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = environ.get("BOT_TOKEN", "your_bot_token")

id_pattern = re.compile(r'^-100\d+$')  # Only allow Telegram channel IDs

AUTH_CHANNEL = [
    int(ch) if id_pattern.match(ch) else ch
    for ch in environ.get("AUTH_CHANNEL", "").split()
]
