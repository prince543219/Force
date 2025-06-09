# force_subscribe.py

# -------- CONFIGURATION --------
AUTH_CHANNEL = [-1002383654865]  # Replace with your channel ID(s) only (no @usernames)

API_ID = '28716246'
API_HASH = 'd9277abd08e0277e0a899415916e39b3'
BOT_TOKEN = '7094072498:AAF7mDbdRRbSpYII7wMDjuh8J_0EAD5bK_U'

# --------- BOT IMPORTS ---------
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, FloodWait
import asyncio

# --------- BOT INSTANCE ---------
app = Client(
    "force_subscribe_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# --------- FORCE SUBSCRIBE LOGIC ---------
async def is_subscribed(bot, user_id, channels):
    unsubscribed = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status in ["kicked", "left"]:
                unsubscribed.append(ch)
        except UserNotParticipant:
            unsubscribed.append(ch)
        except Exception:
            continue
    return unsubscribed

async def get_join_buttons(bot, unsubscribed, user_id, start_param="start"):
    buttons = []
    for ch in unsubscribed:
        try:
            chat = await bot.get_chat(ch)
            link = chat.invite_link or await chat.export_invite_link()
            buttons.append([InlineKeyboardButton(f"🔗 Join {chat.title}", url=link)])
        except Exception:
            continue
    bot_username = (await bot.get_me()).username
    buttons.append([
        InlineKeyboardButton("♻️ Verify After Joining ♻️", url=f"https://t.me/{bot_username}?start={start_param}")
    ])
    return InlineKeyboardMarkup(buttons)

# --------- GROUP MESSAGE HANDLER ---------
@app.on_message(filters.group & ~filters.service)
async def group_message_handler(bot, message):
    if not AUTH_CHANNEL or not message.from_user or message.from_user.is_bot:
        return

    try:
        unsubscribed = await is_subscribed(bot, message.from_user.id, AUTH_CHANNEL)
        if not unsubscribed:
            return  # User is subscribed, allow message

        # Check if bot has permission to delete messages
        bot_member = await bot.get_chat_member(message.chat.id, (await bot.get_me()).id)
        if bot_member.status not in ["administrator", "creator"]:
            print("[ERROR] Bot is not an admin in the group.")
            return

        # Check if admin privileges allow deleting messages
        if not getattr(bot_member.privileges, "can_delete_messages", False):
            print("[ERROR] Bot lacks delete message permission.")
            return

        # Delete unauthorized message
        await message.delete()

        # Send warning message with button
        reply_markup = await get_join_buttons(bot, unsubscribed, message.from_user.id)

        await message.reply_text(
            f"🚫 {message.from_user.mention}, you must <b>join the required channel(s)</b> before sending messages here.\n\n"
            "After joining, click <b>Verify After Joining</b> and resend your message.",
            reply_markup=reply_markup,
            quote=True,
            disable_web_page_preview=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as err:
        print(f"[ERROR] {err}")


# --------- RUN THE BOT ---------
if __name__ == "__main__":
    print("✅ Bot is running...")
    app.run()

