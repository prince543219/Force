# force_subscribe.py

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from config import AUTH_CHANNEL

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

async def enforce_subscription(bot, message):
    if not AUTH_CHANNEL:
        return False  # No restriction

    user_id = message.from_user.id
    unsubscribed = await is_subscribed(bot, user_id, AUTH_CHANNEL)

    if unsubscribed:
        buttons = []
        for ch in unsubscribed:
            chat = await bot.get_chat(ch)
            link = chat.invite_link or await chat.export_invite_link()
            buttons.append([InlineKeyboardButton(f"🔗 Join {chat.title}", url=link)])
        
        bot_username = (await bot.get_me()).username
        start_param = message.command[1] if len(message.command) > 1 else "start"
        buttons.append([
            InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{bot_username}?start={start_param}")
        ])

        await message.reply_text(
            f"👋 Hello {message.from_user.mention},\n\n"
            "Please join the required channel(s) to use this bot.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return True  # Block access
    return False  # Allow access
