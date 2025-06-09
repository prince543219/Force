# bot.py

from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN
from force_subscribe import enforce_subscription

app = Client(
    "ForceSubscribeBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    if await enforce_subscription(client, message):
        return  # Block if not subscribed

    await message.reply_text("✅ Welcome! You are subscribed and ready to use the bot.")

# Add other handlers as needed...

if __name__ == "__main__":
    print("Bot is running...")
    app.run()

