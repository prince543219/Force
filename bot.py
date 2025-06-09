from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ChatPermissions
import asyncio

API_ID = 28716246
API_HASH = "d9277abd08e0277e0a899415916e39b3"
BOT_TOKEN = "7094072498:AAF7mDbdRRbSpYII7wMDjuh8J_0EAD5bK_U"

GROUP_ID = -1002079289711
CHANNEL_ID = -1002348011774  # Channel ID instead of username
WELCOME_IMAGE_URL = "https://files.catbox.moe/3ic0hd.jpg"

app = Client("join_to_unmute_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Check if user is in the channel
async def is_user_in_channel(client, user_id):
    try:
        member = await client.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# Welcome and restrict new members
@app.on_message(filters.new_chat_members)
async def welcome(client, message):
    for user in message.new_chat_members:
        if await is_user_in_channel(client, user.id):
            await client.send_message(
                message.chat.id,
                f"✅ {user.mention()} is already a channel member and can chat!"
            )
        else:
            await client.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user.id,
                permissions=ChatPermissions()  # mute
            )

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔔 Join Channel", url="https://t.me/moviiieeeesss")],  # You must use username or invite link for join button
                [InlineKeyboardButton("✅ Verify", callback_data=f"verify_{user.id}")]
            ])

            await client.send_photo(
                chat_id=message.chat.id,
                photo=WELCOME_IMAGE_URL,
                caption=f"👋 Welcome {user.mention()}!\n\nTo chat here, please join our channel and click **Verify**.",
                reply_markup=keyboard
            )

            asyncio.create_task(check_join_and_unmute(client, user.id, user))

# Check periodically if the user joined and unmute
async def check_join_and_unmute(client, user_id, user_obj=None):
    for _ in range(10):  # ~20 seconds
        if await is_user_in_channel(client, user_id):
            await unmute_user(client, GROUP_ID, user_id, user_obj)
            return
        await asyncio.sleep(2)

# Manual verification via button
@app.on_callback_query(filters.regex(r"^verify_(\d+)$"))
async def verify_callback(client, callback_query: CallbackQuery):
    user_id = int(callback_query.matches[0].group(1))
    from_user = callback_query.from_user

    if from_user.id != user_id:
        await callback_query.answer("❌ You can't verify for someone else!", show_alert=True)
        return

    if await is_user_in_channel(client, user_id):
        await unmute_user(client, GROUP_ID, user_id, from_user)
        await callback_query.answer("✅ You are now verified and unmuted!", show_alert=True)
    else:
        await callback_query.answer("🚫 You're not in the channel yet. Please join first.", show_alert=True)

# Grant permissions to unmute
async def unmute_user(client, chat_id, user_id, user_obj=None):
    try:
        await client.restrict_chat_member(
            chat_id=chat_id,
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
        await client.send_message(chat_id, f"✅ {mention} has joined the channel and is now unmuted!")
    except Exception as e:
        print(f"Failed to unmute user: {e}")

# Block messages from unverified users
@app.on_message(filters.group & filters.text)
async def monitor_messages(client, message):
    user_id = message.from_user.id

    if await is_user_in_channel(client, user_id):
        return

    try:
        await message.delete()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔔 Join Channel", url="https://t.me/moviiieeeesss")],  # Still use username or invite link
            [InlineKeyboardButton("✅ Verify", callback_data=f"verify_{user_id}")]
        ])
        await client.send_photo(
            chat_id=message.chat.id,
            photo=WELCOME_IMAGE_URL,
            caption=f"🚫 {message.from_user.mention()}, you must join the channel to chat!",
            reply_markup=keyboard,
        )
    except Exception as e:
        print(f"Failed to delete message or send warning: {e}")

app.run()
