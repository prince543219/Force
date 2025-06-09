from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import asyncio

API_ID = 28716246   # Replace with your API ID
API_HASH = "d9277abd08e0277e0a899415916e39b3"
BOT_TOKEN = "7094072498:AAF7mDbdRRbSpYII7wMDjuh8J_0EAD5bK_U"

GROUP_ID = -1002079289711  # Your group ID
CHANNEL_USERNAME = "moviiieeeesss"  # Without @
WELCOME_IMAGE_URL = "https://files.catbox.moe/3ic0hd.jpg"  # Replace with actual image URL

app = Client("join_to_unmute_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to check membership
async def is_user_in_channel(client, user_id):
    try:
        member = await client.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ... [previous code remains unchanged]

@app.on_message(filters.new_chat_members)
async def welcome(client, message):
    for user in message.new_chat_members:
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user.id,
            permissions=ChatPermissions()  # Mute user
        )

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")]]
        )

        await client.send_photo(
            chat_id=message.chat.id,
            photo=WELCOME_IMAGE_URL,
            caption=f"👋 Welcome {user.mention()}!\n\nTo chat in this group, you must join our channel first.",
            reply_markup=keyboard
        )

        await check_join_and_unmute(client, user.id, user)

async def check_join_and_unmute(client, user_id, user_obj=None):
    for _ in range(20):  # Retry up to 20 times
        if await is_user_in_channel(client, user_id):
            await client.restrict_chat_member(
                chat_id=GROUP_ID,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_change_info=False,
                    can_invite_users=True,
                    can_pin_messages=False
                )
            )
            mention = user_obj.mention() if user_obj else f"[User](tg://user?id={user_id})"
            await client.send_message(GROUP_ID, f"✅ {mention} joined the channel and are now unmuted!")
            return
        await asyncio.sleep(3)

@app.on_message(filters.group & filters.text)
async def monitor_messages(client, message):
    user_id = message.from_user.id

    if await is_user_in_channel(client, user_id):
        return  # All good

    try:
        await message.delete()
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")]]
        )
        await client.send_photo(
            chat_id=message.chat.id,
            photo=WELCOME_IMAGE_URL,
            caption=f"🚫 {message.from_user.mention()} must join the channel to speak in the group!",
            reply_markup=keyboard,
        )
    except Exception as e:
        print(f"Failed to delete or warn: {e}")

app.run()
