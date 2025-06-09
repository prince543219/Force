# force_subscribe.py

from pyrogram import Client, filters
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

async def get_join_buttons(bot, unsubscribed, user, start_param="start"):
    buttons = []
    for ch in unsubscribed:
        chat = await bot.get_chat(ch)
        link = chat.invite_link or await chat.export_invite_link()
        buttons.append([InlineKeyboardButton(f"🔗 Join {chat.title}", url=link)])
    bot_username = (await bot.get_me()).username
    buttons.append([
        InlineKeyboardButton("♻️ Verify After Joining ♻️", url=f"https://t.me/{bot_username}?start={start_param}")
    ])
    return InlineKeyboardMarkup(buttons)

@Client.on_message(filters.group & ~filters.service)
async def group_message_handler(bot, message):
    if not AUTH_CHANNEL:
        return
    if message.from_user.is_bot:
        return

    # Check if bot is admin with delete permission
    bot_member = await bot.get_chat_member(message.chat.id, (await bot.get_me()).id)
    if not bot_member.can_delete_messages:
        return

    # Check if user is subscribed
    unsubscribed = await is_subscribed(bot, message.from_user.id, AUTH_CHANNEL)
    if unsubscribed:
        # Delete the user's message
        await message.delete()

        # Prepare join buttons
        start_param = message.command[1] if hasattr(message, "command") and len(message.command) > 1 else "start"
        reply_markup = await get_join_buttons(bot, unsubscribed, message.from_user, start_param)

        # Warn in the group with join links
        await message.reply_text(
            f"{message.from_user.mention}, you must <b>join the required channel(s)</b> before sending messages here.\n\n"
            "After joining, click <b>Verify After Joining</b> and try sending your message again.",
            reply_markup=reply_markup,
            quote=True,
            disable_web_page_preview=True
        )
