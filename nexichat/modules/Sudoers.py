from pyrogram import filters
from pyrogram.types import Message

from config import MONGO_URL, OWNER_ID
from nexichat import nexichat as app
from nexichat import SUDOERS
from nexichat.database import add_sudo, remove_sudo

@app.on_message(filters.command("addsudo") & filters.user(OWNER_ID))
async def useradd(client, message: Message):
    if MONGO_URL is None:
        return await message.reply_text(
            "**Dᴜᴇ ᴛᴏ ʙᴏᴛ's ᴘʀɪᴠᴀᴄʏ ɪssᴜᴇs, Yᴏᴜ ᴄᴀɴ'ᴛ ᴍᴀɴᴀɢᴇ sᴜᴅᴏ ᴜsᴇʀs ᴡʜᴇɴ ʏᴏᴜ'ʀᴇ ᴜsɪɴɢ Yᴜᴋᴋɪ's Dᴀᴛᴀʙᴀsᴇ.\n\nPʟᴇᴀsᴇ ғɪʟʟ ʏᴏᴜʀ MONGO_DB_URI ɪɴ ʏᴏᴜʀ ᴠᴀʀs ᴛᴏ ᴜsᴇ ᴛʜɪs ғᴇᴀᴛᴜʀᴇ**"
        )
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴜsᴇʀɴᴀᴍᴇ/ᴜsᴇʀ_ɪᴅ.")
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        if user.id in SUDOERS:
            return await message.reply_text(f"{user.mention} ɪs ᴀʟʀᴇᴀᴅʏ ᴀ sᴜᴅᴏ ᴜsᴇʀ.")
        added = await add_sudo(user.id)
        if added:
            SUDOERS.add(user.id)
            await message.reply_text(f"ᴀᴅᴅᴇᴅ **{user.mention}** ᴛᴏ sᴜᴅᴏ ᴜsᴇʀs.")
        else:
            await message.reply_text("ғᴀɪʟᴇᴅ")
        return
    if message.reply_to_message.from_user.id in SUDOERS:
        return await message.reply_text(
            f"{message.reply_to_message.from_user.mention} ɪs ᴀʟʀᴇᴀᴅʏ ᴀ sᴜᴅᴏ ᴜsᴇʀ."
        )
    added = await add_sudo(message.reply_to_message.from_user.id)
    if added:
        SUDOERS.add(message.reply_to_message.from_user.id)
        await message.reply_text(
            f"ᴀᴅᴅᴇᴅ **{message.reply_to_message.from_user.mention}** ᴛᴏ sᴜᴅᴏ ᴜsᴇʀs."
        )
    else:
        await message.reply_text("ғᴀɪʟᴇᴅ")
    return


@app.on_message(filters.command(["rmsudo", "delsudo"]) & filters.user(OWNER_ID))
async def userdel(client, message: Message):
    if MONGO_URL is None:
        return await message.reply_text(
            "**Dᴜᴇ ᴛᴏ ʙᴏᴛ's ᴘʀɪᴠᴀᴄʏ ɪssᴜᴇs, Yᴏᴜ ᴄᴀɴ'ᴛ ᴍᴀɴᴀɢᴇ sᴜᴅᴏ ᴜsᴇʀs ᴡʜᴇɴ ʏᴏᴜ'ʀᴇ ᴜsɪɴɢ Yᴜᴋᴋɪ's Dᴀᴛᴀʙᴀsᴇ.\n\nPʟᴇᴀsᴇ ғɪʟʟ ʏᴏᴜʀ MONGO_DB_URI ɪɴ ʏᴏᴜʀ ᴠᴀʀs ᴛᴏ ᴜsᴇ ᴛʜɪs ғᴇᴀᴛᴜʀᴇ**"
        )
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴜsᴇʀɴᴀᴍᴇ/ᴜsᴇʀ_ɪᴅ.")
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        if user.id not in SUDOERS:
            return await message.reply_text("ɴᴏᴛ ᴀ ᴘᴀʀᴛ ᴏꜰ ʙᴏᴛ's sᴜᴅᴏ.")
        removed = await remove_sudo(user.id)
        if removed:
            SUDOERS.remove(user.id)
            await message.reply_text("ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ʙᴏᴛ's sᴜᴅᴏ ᴜsᴇʀ.")
            return
        await message.reply_text("sᴏᴍᴇᴛʜɪɴɢ ᴡʀᴏɴɢ ʜᴀᴘᴘᴇɴᴇᴅ")
        return
    user_id = message.reply_to_message.from_user.id
    if user_id not in SUDOERS:
        return await message.reply_text("ɴᴏᴛ ᴀ ᴘᴀʀᴛ ᴏꜰ ʙᴏᴛ's sᴜᴅᴏ.")
    removed = await remove_sudo(user_id)
    if removed:
        SUDOERS.remove(user_id)
        await message.reply_text("ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ʙᴏᴛ's sᴜᴅᴏ ᴜsᴇʀ.")
        return
    await message.reply_text("sᴏᴍᴇᴛʜɪɴɢ ᴡʀᴏɴɢ ʜᴀᴘᴘᴇɴᴇᴅ.")


@app.on_message(filters.command(["sudo", "sudolist"]))
async def sudoers_list(client, message: Message):
    text = "🔥<u> **ᴏᴡɴᴇʀ:**</u>\n"
    count = 0
    try:
        user = await app.get_users(OWNER_ID)
        user_name = user.first_name if not user.mention else user.mention
        count += 1
        text += f"{count}➤ {user_name}\n"
    except Exception:
        pass

    smex = 0
    for user_id in SUDOERS:
        if user_id != OWNER_ID:
            try:
                user = await app.get_users(user_id)
                user_name = user.first_name if not user.mention else user.mention
                if smex == 0:
                    smex += 1
                    text += "\n🔥<u> **sᴜᴅᴏᴇʀs:**</u>\n"
                count += 1
                text += f"{count}➤ {user_name} ({user.id})\n"
            except Exception:
                continue

    if not text:
        await message.reply_text("ɴᴏ sᴜᴅᴏ ᴜsᴇʀs ғᴏᴜɴᴅ.")
    else:
        await message.reply_text(text)



import os
import re
import subprocess
import sys
import traceback

from pyrogram import filters
from pyrogram.types import Message


async def edit_or_reply(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    await func(**kwargs)


@app.on_edited_message(
    filters.command("sh") & filters.user(OWNER_ID) & ~filters.forwarded & ~filters.via_bot
)
@app.on_message(filters.command("sh") & filters.user(OWNER_ID) & ~filters.forwarded & ~filters.via_bot)
async def shellrunner(_, message: Message):
    if len(message.command) < 2:
        return await edit_or_reply(message, text="<b>ᴇxᴀᴍᴩʟᴇ :</b>\n/sh git pull")
    text = message.text.split(None, 1)[1]
    if "\n" in text:
        code = text.split("\n")
        output = ""
        for x in code:
            shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", x)
            try:
                process = subprocess.Popen(
                    shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except Exception as err:
                return await edit_or_reply(message, text=f"<b>ERROR :</b>\n<pre>{err}</pre>")
            output += f"<b>{x}</b>\n"
            output += process.stdout.read()[:-1].decode("utf-8")
            output += "\n"
    else:
        shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", text)
        for a in range(len(shell)):
            shell[a] = shell[a].replace('"', "")
        try:
            process = subprocess.Popen(
                shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(exc_type, exc_obj, exc_tb)
            return await edit_or_reply(
                message, text=f"<b>ERROR :</b>\n<pre>{''.join(errors)}</pre>"
            )
        output = process.stdout.read()[:-1].decode("utf-8")
    if str(output) == "\n":
        output = None
    if output:
        if len(output) > 4096:
            with open("output.txt", "w+") as file:
                file.write(output)
            await app.send_document(
                message.chat.id,
                "output.txt",
                reply_to_message_id=message.id,
                caption="<code>Output</code>",
            )
            return os.remove("output.txt")
        await edit_or_reply(message, text=f"<b>OUTPUT :</b>\n<pre>{output}</pre>")
    else:
        await edit_or_reply(message, text="<b>OUTPUT :</b>\n<code>None</code>")
