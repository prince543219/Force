import re
from os import environ

API_ID = 28716246
API_HASH = "d9277abd08e0277e0a899415916e39b3"
BOT_TOKEN = "7094072498:AAF7mDbdRRbSpYII7wMDjuh8J_0EAD5bK_U"

id_pattern = re.compile(r'^-100\d+$')  # Only allow Telegram channel IDs

AUTH_CHANNEL = [
    int(ch) if id_pattern.match(ch) else ch
    for ch in environ.get("AUTH_CHANNEL", "-1002383654865").split()
]

