import asyncio
import logging
import random
import time
import psutil
import config
import os
from nexichat import _boot_
from nexichat import get_readable_time
from nexichat.mplugin.helpers import is_owner
from nexichat import mongo
from datetime import datetime
from pymongo import MongoClient
from pyrogram.enums import ChatType
from pyrogram import Client, filters
from nexichat import CLONE_OWNERS, db
from config import OWNER_ID, MONGO_URL, OWNER_USERNAME
from pyrogram.errors import FloodWait, ChatAdminRequired
from nexichat.database.chats import get_served_chats, add_served_chat
from nexichat.database.users import get_served_users, add_served_user
from nexichat.database.clonestats import get_served_cchats, get_served_cusers, add_served_cuser, add_served_cchat
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from nexichat.mplugin.helpers import (
    START,
    START_BOT,
    PNG_BTN,
    CLOSE_BTN,
    HELP_BTN,
    HELP_BUTN,
    HELP_READ,
    HELP_START,
    SOURCE_READ,
)

OK = "**ʜᴇʏ👀**"
AUTO_MSG = f"""{os.getenv("AUTO_MSG")}""" if os.getenv("AUTO_MSG") else OK
GSTART = """**ʜᴇʏ ᴅᴇᴀʀ {}**\n\n**ᴛʜᴀɴᴋs ғᴏʀ sᴛᴀʀᴛ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ ʏᴏᴜ ᴄᴀɴ ᴄʜᴀɴɢᴇ ʟᴀɴɢᴜᴀɢᴇ ʙʏ ᴄʟɪᴄᴋ ᴏɴ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs.**\n**ᴄʟɪᴄᴋ ᴀɴᴅ sᴇʟᴇᴄᴛ ʏᴏᴜʀ ғᴀᴠᴏᴜʀɪᴛᴇ ʟᴀɴɢᴜᴀɢᴇ ᴛᴏ sᴇᴛ ᴄʜᴀᴛ ʟᴀɴɢᴜᴀɢᴇ ғᴏʀ ʙᴏᴛ ʀᴇᴘʟʏ.**\n\n**ᴛʜᴀɴᴋ ʏᴏᴜ ᴘʟᴇᴀsᴇ ᴇɴɪᴏʏ.**"""
STICKER = [
    "CAACAgUAAx0CepnpNQABAQ0ZZwi4keVWGDS7Zc4Ugl07nazStioAAoYKAAIFp0FW4tWKLEhqx54eBA",
    "CAACAgUAAx0CepnpNQABAQ0bZwi4ty5H4bQFRiADbIDRjvmqrvwAAs8KAAISAAFwVwABdUaWHySE3B4E",
    "CAACAgUAAx0CepnpNQABAQ0aZwi4tLgnRHxBeCGoKYkHaOtihKgAAj4MAAIfJXFXhnQ9Zw3NF_AeBA",
    
  "CAACAgUAAx0CepnpNQABAQ0cZwi4vvVDhrmnrLZJjKZXwZHm6J8AAogMAAKn83BXvz4RP6rTTEYeBA",
]


EMOJIOS = [
    "💞",
    "❤️",
    "💕",
    "💘",
    "💗",
]

BOT = "https://files.catbox.moe/6px3gg.jpg"
IMG = [
    "https://files.catbox.moe/6px3gg.jpg",
    "https://files.catbox.moe/6px3gg.jpg",
    "https://files.catbox.moe/6px3gg.jpg",
]


from nexichat import db

chatai = db.Word.WordDb
lang_db = db.ChatLangDb.LangCollection
status_db = db.ChatBotStatusDb.StatusCollection
cloneownerdb = db.clone_owners

async def get_clone_owner(bot_id):
    data = await cloneownerdb.find_one({"bot_id": bot_id})
    if data:
        return data["user_id"]
    return None


async def bot_sys_stats():
    bot_uptime = int(time.time() - _boot_)
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    UP = f"{get_readable_time((bot_uptime))}"
    CPU = f"{cpu}%"
    RAM = f"{mem}%"
    DISK = f"{disk}%"
    return UP, CPU, RAM, DISK
    

async def set_default_status(chat_id):
    try:
        if not await status_db.find_one({"chat_id": chat_id}):
            await status_db.insert_one({"chat_id": chat_id, "status": "enabled"})
    except Exception as e:
        print(f"Error setting default status for chat {chat_id}: {e}")





@Client.on_message(filters.new_chat_members)
async def welcomejej(client, message: Message):
    chat = message.chat
    bot_id = client.me.id
    await add_served_cchat(bot_id, message.chat.id)
    await add_served_chat(message.chat.id)
    await set_default_status(message.chat.id)
    users = len(await get_served_cusers(bot_id))
    chats = len(await get_served_cchats(bot_id))
    try:
        for member in message.new_chat_members:
            if member.id == client.me.id:
                try:
                    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("sᴇʟᴇᴄᴛ ʟᴀɴɢᴜᴀɢᴇ", callback_data="choose_lang")]])    
                    await message.reply_text(text="**тнαикѕ ꜰᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴩ.**\n\n**ᴋɪɴᴅʟʏ  ꜱᴇʟᴇᴄᴛ  ʙᴏᴛ  ʟᴀɴɢᴜᴀɢᴇ  ꜰᴏʀ  ᴛʜɪꜱ  ɢʀᴏᴜᴩ  ʙʏ  ᴛʏᴩᴇ  ☞  /lang**", reply_markup=reply_markup)
                    await message.reply_text(f"**{AUTO_MSG}**")
                except Exception as e:
                    print(f"{e}")
                    pass
                try:
                    invitelink = await client.export_chat_invite_link(message.chat.id)
                    link = f"[ɢᴇᴛ ʟɪɴᴋ]({invitelink})"
                except ChatAdminRequired:
                    link = "No Link"
                
                try:
                    groups_photo = await client.download_media(
                        chat.photo.big_file_id, file_name=f"chatpp{chat.id}.png"
                    )
                    chat_photo = (
                        groups_photo if groups_photo else "https://envs.sh/IL_.jpg"
                    )
                except AttributeError:
                    chat_photo = "https://envs.sh/IL_.jpg"
                except Exception as e:
                    pass

                count = await client.get_chat_members_count(chat.id)
                username = chat.username if chat.username else "𝐏ʀɪᴠᴀᴛᴇ 𝐆ʀᴏᴜᴘ"
                msg = (
                    f"**🎉ᴄʜᴀᴛ ʙᴏᴛ ᴀᴅᴅᴇᴅ ɪɴ ᴀ #ɴᴇᴡ_ɢʀᴏᴜᴘ❤️**\n\n"
                    f"**💫ᴄʜᴀᴛ ɴᴀᴍᴇ:** {chat.title}\n"
                    f"**💕ᴄʜᴀᴛ ɪᴅ:** `{chat.id}`\n"
                    f"**🔐ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ:** @{username}\n"
                    f"**🖇️ɢʀᴏᴜᴘ ʟɪɴᴋ:** {link}\n"
                    f"**♥️ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs:** {count}\n"
                    f"**💞ᴀᴅᴅᴇᴅ ʙʏ:** {message.from_user.mention}\n\n"
                    f"**ᴛᴏᴛᴀʟ ᴄʜᴀᴛs :** {chats}"
                )

                try:
                    bot_id = client.me.id
                    owner_id = await get_clone_owner(bot_id)
                    
                    if owner_id:
                        await client.send_photo(
                            int(owner_id),
                            photo=chat_photo,
                            caption=msg,
                            reply_markup=InlineKeyboardMarkup(
                                [[InlineKeyboardButton(f"{message.from_user.first_name}", user_id=message.from_user.id)]]
                            )
                        )
                except Exception as e:
                    print(f"Err: {e}")
    except Exception as e:
        print(f"Err: {e}")




@Client.on_message(filters.command(["start", "aistart"]))
async def start(_, m: Message):
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    if m.chat.type == ChatType.PRIVATE:
        accha = await m.reply_text(
            text=random.choice(EMOJIOS),
        )
        await accha.delete()
        await asyncio.sleep(0.5)
        umm = await m.reply_sticker(sticker=random.choice(STICKER))
        chat_photo = BOT  
        if m.chat.photo:
            try:
                userss_photo = await client.download_media(m.chat.photo.big_file_id)
                await umm.delete()
                if userss_photo:
                    chat_photo = userss_photo
            except AttributeError:
                chat_photo = BOT  

        users = len(await get_served_cusers(bot_id))
        chats = len(await get_served_cchats(bot_id))
        UP, CPU, RAM, DISK = await bot_sys_stats()
        await m.reply_photo(photo=chat_photo, caption=START.format(users, chats, UP), reply_markup=InlineKeyboardMarkup(START_BOT))
        await m.reply_text(f"**{AUTO_MSG}**")
        await add_served_cuser(bot_id, m.chat.id) 
        await add_served_user(m.chat.id)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"{m.chat.first_name}", user_id=m.chat.id)]])

        owner_id = await get_clone_owner(bot_id) 
        if owner_id:
            await client.send_photo(
                int(owner_id),
                photo=chat_photo,
                caption=f"{m.from_user.mention} ʜᴀs sᴛᴀʀᴛᴇᴅ ʙᴏᴛ. \n\n**ɴᴀᴍᴇ :** {m.chat.first_name}\n**ᴜsᴇʀɴᴀᴍᴇ :** @{m.chat.username}\n**ɪᴅ :** {m.chat.id}\n\n**ᴛᴏᴛᴀʟ ᴜsᴇʀs :** {users}",
                reply_markup=keyboard
            )
        
    else:
        await m.reply_photo(
            photo=random.choice(IMG),
            caption=GSTART.format(m.from_user.mention or "can't mention"),
            reply_markup=InlineKeyboardMarkup(HELP_START),
        )
        await m.reply_text(f"**{AUTO_MSG}**")
        await add_served_cchat(bot_id, m.chat.id)
        await add_served_chat(m.chat.id)

@Client.on_message(filters.command("help"))
async def help(client: Client, m: Message):
    bot_id = client.me.id
    if m.chat.type == ChatType.PRIVATE:
        hmm = await m.reply_photo(
            photo=random.choice(IMG),
            caption=HELP_READ,
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
        )

    else:
        await m.reply_photo(
            photo=random.choice(IMG),
            caption="**ʜᴇʏ, ᴘᴍ ᴍᴇ ғᴏʀ ʜᴇʟᴘ ᴄᴏᴍᴍᴀɴᴅs!**",
            reply_markup=InlineKeyboardMarkup(HELP_BUTN),
        )
        await add_served_cchat(bot_id, m.chat.id)
        await add_served_chat(m.chat.id)


@Client.on_message(filters.command("repo"))
async def repo(client: Client, m: Message):
    await m.reply_text(
        text=SOURCE_READ,
        reply_markup=InlineKeyboardMarkup(CLOSE_BTN),
        disable_web_page_preview=True,
    )




@Client.on_message(filters.command("ping"))
async def ping(client: Client, message: Message):
    bot_id = client.me.id
    start = datetime.now()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    loda = await message.reply_photo(
        photo=random.choice(IMG),
        caption="ᴘɪɴɢɪɴɢ...",
    )

    ms = (datetime.now() - start).microseconds / 1000
    await loda.edit_text(
        text=f"ʜᴇʏ ʙᴀʙʏ 👻\n{(await client.get_me()).mention} ᴄʜᴀᴛʙᴏᴛ ɪꜱ ᴀʟɪᴠᴇ 💫 ᴀɴᴅ ᴡᴏʀᴋɪɴɢ ꜰɪɴᴇ ᴡɪᴛʜ ᴀ ᴘɪɴɢ ᴏꜰ\n\n**➥** `{ms}` ms\n**➲ ᴄᴘᴜ:** {CPU}\n**➲ ʀᴀᴍ:** {RAM}\n**➲ ᴅɪsᴋ:** {DISK}\n**➲ ᴜᴘᴛɪᴍᴇ »** {UP}\n\n<b>||**๏ ᴍᴀᴅᴇ ᴡɪᴛʜ ❣️ ʙʏ [ʙᴀᴅ ᴍᴜɴᴅᴀ](https://t.me/{OWNER_USERNAME})**||</b>",
        reply_markup=InlineKeyboardMarkup(PNG_BTN),
    )
    if message.chat.type == ChatType.PRIVATE:
        await add_served_cuser(bot_id, message.from_user.id)
        await add_served_user(message.from_user.id)
    else:
        await add_served_cchat(bot_id, message.chat.id)
        await add_served_chat(message.chat.id)


@Client.on_message(filters.command("stats"))
async def stats(cli: Client, message: Message):
    bot_id = (await cli.get_me()).id
    users = len(await get_served_cusers(bot_id))
    chats = len(await get_served_cchats(bot_id))
    
    await message.reply_text(
        f"""{(await cli.get_me()).mention} Chatbot Stats:

➻ **Chats:** {chats}
➻ **Users:** {users}"""
    )


from pyrogram.enums import ParseMode

from nexichat import nexichat


@Client.on_message(filters.command("id"))
async def getid(client, message):
    chat = message.chat
    your_id = message.from_user.id
    message_id = message.id
    reply = message.reply_to_message

    text = f"**[ᴍᴇssᴀɢᴇ ɪᴅ:]({message.link})** `{message_id}`\n"
    text += f"**[ʏᴏᴜʀ ɪᴅ:](tg://user?id={your_id})** `{your_id}`\n"

    if not message.command:
        message.command = message.text.split()

    if not message.command:
        message.command = message.text.split()

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await client.get_users(split)).id
            text += f"**[ᴜsᴇʀ ɪᴅ:](tg://user?id={user_id})** `{user_id}`\n"

        except Exception:
            return await message.reply_text("ᴛʜɪs ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ.", quote=True)

    text += f"**[ᴄʜᴀᴛ ɪᴅ:](https://t.me/{chat.username})** `{chat.id}`\n\n"

    if (
        not getattr(reply, "empty", True)
        and not message.forward_from_chat
        and not reply.sender_chat
    ):
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ɪᴅ:]({reply.link})** `{reply.id}`\n"
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ:](tg://user?id={reply.from_user.id})** `{reply.from_user.id}`\n\n"

    if reply and reply.forward_from_chat:
        text += f"ᴛʜᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀɴɴᴇʟ, {reply.forward_from_chat.title}, ʜᴀs ᴀɴ ɪᴅ ᴏғ `{reply.forward_from_chat.id}`\n\n"
        print(reply.forward_from_chat)

    if reply and reply.sender_chat:
        text += f"ɪᴅ ᴏғ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴄʜᴀᴛ/ᴄʜᴀɴɴᴇʟ, ɪs `{reply.sender_chat.id}`"
        print(reply.sender_chat)

    await message.reply_text(
        text,
        disable_web_page_preview=True,
        parse_mode=ParseMode.DEFAULT,
    )


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUTO_SLEEP = 5
IS_BROADCASTING = False
broadcast_lock = asyncio.Lock()

@Client.on_message(filters.command(["broadcast", "gcast"]))
async def broadcast_message(client, message):
    global IS_BROADCASTING
    bot_id = (await client.get_me()).id
    user_id = message.from_user.id
    if not await is_owner(bot_id, user_id):
        await message.reply_text("You don't have permission to use this command on this bot.")
        return
        
    async with broadcast_lock:
        if IS_BROADCASTING:
            return await message.reply_text(
                "A broadcast is already in progress. Please wait for it to complete."
            )

        IS_BROADCASTING = True
        try:
            query = message.text.split(None, 1)[1].strip()
        except IndexError:
            query = message.text.strip()
        except Exception as eff:
            return await message.reply_text(
                f"**Error**: {eff}"
            )
        try:
            if message.reply_to_message:
                broadcast_content = message.reply_to_message
                broadcast_type = "reply"
                flags = {
                    "-pin": "-pin" in query,
                    "-pinloud": "-pinloud" in query,
                    "-nogroup": "-nogroup" in query,
                    "-user": "-user" in query,
                }
            else:
                if len(message.command) < 2:
                    return await message.reply_text(
                        "**Please provide text after the command or reply to a message for broadcasting.**"
                    )
                
                flags = {
                    "-pin": "-pin" in query,
                    "-pinloud": "-pinloud" in query,
                    "-nogroup": "-nogroup" in query,
                    "-user": "-user" in query,
                }

                for flag in flags:
                    query = query.replace(flag, "").strip()

                if not query:
                    return await message.reply_text(
                        "Please provide a valid text message or a flag: -pin, -nogroup, -pinloud, -user"
                    )

                
                broadcast_content = query
                broadcast_type = "text"
            

            await message.reply_text("**Started broadcasting...**")

            if not flags.get("-nogroup", False):
                sent = 0
                pin_count = 0
                chats = await get_served_cchats(bot_id)

                for chat in chats:
                    chat_id = int(chat["chat_id"])
                    if chat_id == message.chat.id:
                        continue
                    try:
                        if broadcast_type == "reply":
                            m = await client.forward_messages(
                                chat_id, message.chat.id, [broadcast_content.id]
                            )
                        else:
                            m = await client.send_message(
                                chat_id, text=broadcast_content
                            )
                        sent += 1

                        if flags.get("-pin", False) or flags.get("-pinloud", False):
                            try:
                                await m.pin(
                                    disable_notification=flags.get("-pin", False)
                                )
                                pin_count += 1
                            except Exception as e:
                                continue

                    except FloodWait as e:
                        flood_time = int(e.value)
                        logger.warning(
                            f"FloodWait of {flood_time} seconds encountered for chat {chat_id}."
                        )
                        if flood_time > 200:
                            logger.info(
                                f"Skipping chat {chat_id} due to excessive FloodWait."
                            )
                            continue
                        await asyncio.sleep(flood_time)
                    except Exception as e:
                        
                        continue

                await message.reply_text(
                    f"**Broadcasted to {sent} chats and pinned in {pin_count} chats.**"
                )

            if flags.get("-user", False):
                susr = 0
                users = await get_served_cusers(bot_id)

                for user in users:
                    user_id = int(user["user_id"])
                    try:
                        if broadcast_type == "reply":
                            m = await client.forward_messages(
                                user_id, message.chat.id, [broadcast_content.id]
                            )
                        else:
                            m = await client.send_message(
                                user_id, text=broadcast_content
                            )
                        susr += 1

                    except FloodWait as e:
                        flood_time = int(e.value)
                        logger.warning(
                            f"FloodWait of {flood_time} seconds encountered for user {user_id}."
                        )
                        if flood_time > 200:
                            logger.info(
                                f"Skipping user {user_id} due to excessive FloodWait."
                            )
                            continue
                        await asyncio.sleep(flood_time)
                    except Exception as e:
                        
                        continue

                await message.reply_text(f"**Broadcasted to {susr} users.**")

        finally:
            IS_BROADCASTING = False
