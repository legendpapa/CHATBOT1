from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden, PeerIdInvalid
from nexichat import nexichat
from config import UPDATE_CHNL as MUST_JOIN

@Client.on_message(filters.incoming & filters.private, group=-2)
async def must_join_channel(client: Client, msg: Message):
    if not MUST_JOIN:
        return
    if not msg.from_user:
        return
    try:
        try:
            m = msg.from_user.id
            await nexichat.get_chat_member(MUST_JOIN, m)
        except UserNotParticipant:
            try:
                if MUST_JOIN.isalpha():
                    link = "https://t.me/" + MUST_JOIN
                else:
                    chat_info = await nexichat.get_chat(MUST_JOIN)
                    link = chat_info.invite_link
                try:
                    await msg.reply_photo(
                        photo="https://envs.sh/Tn_.jpg",
                        caption=(
                            f"**👋 ʜᴇʟʟᴏ {msg.from_user.mention},**\n\n"
                            f"**ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ [ᴄʜᴀɴɴᴇʟ]({link}) ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇs ʜᴇʀᴇ**"
                        ),
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("๏ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ๏", url=link)]]
                        ),
                    )
                    return
                except ChatWriteForbidden:
                    return
                except Exception as e:
                    return
            except PeerIdInvalid:
                return
    except PeerIdInvalid:
        return
    except ChatAdminRequired:
        print(f"๏ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ᴀs ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴍᴜsᴛ_Jᴏɪɴ ᴄʜᴀᴛ ๏: {MUST_JOIN} !")
