import random
import re
import config
from pymongo import MongoClient
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.errors import MessageEmpty
from pyrogram.enums import ChatAction, ChatMemberStatus as CMS
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from deep_translator import GoogleTranslator
from nexichat.database.chats import add_served_chat
from nexichat.database.users import add_served_user
from nexichat.database import abuse_list, add_served_cchat, add_served_chat, add_served_user, add_served_cuser, chatai
from config import MONGO_URL, OWNER_ID
from nexichat import nexichat, mongo, LOGGER, db
from nexichat.mplugin.helpers import languages
import asyncio

translator = GoogleTranslator()

lang_db = db.ChatLangDb.LangCollection
status_db = db.chatbot_status_db.status
abuse_words_db = db.abuse_words_db.words

mp_reply = []
mp_abuse = []
mp_blocklist = {}
mp_message_counts = {}
mp_conversation_cache = {}
conversation_histories = {}
replies_cache = []
abuse_cache = []
blocklist = {}
message_counts = {}
conversation_cache = {}


async def load_abuse_cache():
    global mp_abuse
    abuse_cache = mp_abuse
    abuse_cache = [entry['word'] for entry in await abuse_words_db.find().to_list(length=None)]

async def add_abuse_word(word: str):
    global mp_abuse
    abuse_cache = mp_abuse
    if word not in abuse_cache:
        await abuse_words_db.insert_one({"word": word})
        abuse_cache.append(word)

async def is_abuse_present(text: str):
    global mp_abuse
    abuse_cache = mp_abuse
    if not abuse_cache:
        await load_abuse_cache()
    text_lower = text.lower()
    return any(word in text_lower for word in abuse_list) or any(word in text_lower for word in abuse_cache)

async def is_code_related(text):
    code_indicators = ["def ", "return ", "import ", "await ", "try:", "except"]
    return any(indicator in text for indicator in code_indicators)
   
@Client.on_message(filters.command("block"))
async def request_block_word(client: Client, message: Message):
    try:
        if message.reply_to_message and message.reply_to_message.text:
            new_word = message.reply_to_message.text.split()[0].lower()
        elif len(message.command) >= 2:
            new_word = message.command[1].lower()
        else:
            await message.reply_text("**Usage:** Reply to a message or use `/block <word>` to request blocking a word.")
            return

        chat_name = message.chat.title if message.chat.title else "Private Chat"
        chat_username = f"@{message.chat.username}" if message.chat.username else "No Username"
        chat_id = message.chat.id
        user_id = message.from_user.id
        username = f"@{message.from_user.username}" if message.from_user.username else f"`{user_id}`"
        message_id = message.id

        review_message = (
            f"**Block Request Received From {message.from_user.mention}**\n\n"
            f"**Word:** `{new_word}`\n"
            f"**Chat Name:** {chat_name}\n"
            f"**Chat ID:** `{chat_id}`\n"
            f"**Chat Username:** {chat_username}\n"
            f"**Requested By:** {username}\n"
            f"**Message ID:** `{message_id}`\n"
        )

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Accept", callback_data=f"accept_block:{new_word}:{chat_id}:{user_id}"),
                InlineKeyboardButton("❌ Decline", callback_data=f"decline_block:{new_word}:{chat_id}:{user_id}")
            ]
        ])

        await nexichat.send_message(OWNER_ID, review_message, reply_markup=buttons)
        await message.reply_text(f"**Hey** {message.from_user.mention}\n\n**Your block request has been sent to owner for review.**")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@Client.on_callback_query(filters.regex(r"^(accept_block|decline_block):"), group=-3)
async def handle_block_review(client: Client, callback: CallbackQuery):
    try:
        action, word, chat_id, user_id = callback.data.split(":")
        user_id = int(user_id)
        chat_id = int(chat_id)

        if action == "accept_block":
            await add_abuse_word(word)
            await callback.message.edit_text(f"✅ **Word '{word}' has been added to the abuse list.**")
            await client.send_message(chat_id, f"**Hello dear bot users,**\n**The word:- [ '{word}' ], has been approved by my owner for blocking and now added to blocklist.**\n\n**Thanks For Support, You can block more abusing type words by /block**")
        elif action == "decline_block":
            await callback.message.edit_text(f"❌ **Block request for the word '{word}' has been declined.**")
            await client.send_message(chat_id, f"**The block request for '{word}' has been declined by the Owner.**")
    except Exception as e:
        await callback.message.reply_text(f"Error: {e}")
        
@Client.on_message(filters.command("unblock") & filters.user(OWNER_ID))
async def unblock_word(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply_text("**Usage:** `/unblock <word>`\nRemove a word from the abuse list.")
            return
        word_to_remove = message.command[1].lower()
        global abuse_cache
        if word_to_remove in abuse_cache:
            await abuse_words_db.delete_one({"word": word_to_remove})
            abuse_cache.remove(word_to_remove)
            await message.reply_text(f"**Word '{word_to_remove}' removed from abuse list!**")
        else:
            await message.reply_text(f"**Word '{word_to_remove}' is not in the abuse list.**")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@Client.on_message(filters.command("blocked") & filters.user(OWNER_ID))
async def list_blocked_words(client: Client, message: Message):
    try:
        global mp_abuse
        abuse_cache = mp_abuse
        if not abuse_cache:
            await load_abuse_cache()
        if abuse_cache:
            blocked_words = ", ".join(abuse_cache)
            await message.reply_text(f"**Blocked Words:**\n{blocked_words}")
        else:
            await message.reply_text("**No blocked words found.**")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

import re

async def is_url_present_and_replace(text: str) -> str:
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    
    return re.sub(url_pattern, "@PBX_CHAT", text)


async def is_url_present(text: str) -> bool:
    
    url_pattern = re.compile(
        r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)|"
        r"(www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,})"
    )
    return bool(url_pattern.search(text))
    
async def save_reply(original_message: Message, reply_message: Message):
    global mp_reply
    replies_cache = mp_reply
    try:
        if original_message == original_message.text:
            try:
                if (await is_abuse_present(original_message.text) or await is_url_present(original_message.text)):
                    return
            except:
                pass
        if reply_message == reply_message.text:
            try:
                if (await is_abuse_present(reply_message.text) or await is_url_present(reply_message.text)):
                    return
            except:
                pass
        
        reply_data = {
            "word": original_message.text,
            "text": None,
            "check": "none",
        }

        if reply_message.sticker:
            reply_data["text"] = reply_message.sticker.file_id
            reply_data["check"] = "sticker"
        elif reply_message.photo:
            reply_data["text"] = reply_message.photo.file_id
            reply_data["check"] = "photo"
        elif reply_message.video:
            reply_data["text"] = reply_message.video.file_id
            reply_data["check"] = "video"
        elif reply_message.audio:
            reply_data["text"] = reply_message.audio.file_id
            reply_data["check"] = "audio"
        elif reply_message.animation:
            reply_data["text"] = reply_message.animation.file_id
            reply_data["check"] = "gif"
        elif reply_message.voice:
            reply_data["text"] = reply_message.voice.file_id
            reply_data["check"] = "voice"
        elif reply_message.text:
            translated_text = reply_message.text
            reply_data["text"] = translated_text
            reply_data["check"] = "none"

        is_chat = await chatai.find_one(reply_data)
        if not is_chat:
            await chatai.insert_one(reply_data)
            replies_cache.append(reply_data)

    except Exception as e:
        print(f"Error in save_reply: {e}")

async def load_replies_cache():
    global mp_reply
    replies_cache = mp_reply
    replies_cache = await chatai.find().to_list(length=None)
    await load_abuse_cache()

async def remove_abusive_reply(reply_data):
    global mp_reply
    replies_cache = mp_reply 
    await chatai.delete_one(reply_data)
    replies_cache = [reply for reply in replies_cache if reply != reply_data]

async def get_reply(word: str):
    global mp_reply
    replies_cache = mp_reply
    if not replies_cache:
        await load_replies_cache()
        
    relevant_replies = [reply for reply in replies_cache if reply['word'] == word]
    for reply in relevant_replies:
        if reply.get('text') and await is_abuse_present(reply['text']):
            await remove_abusive_reply(reply)
    if not relevant_replies:
        relevant_replies = replies_cache
    
    selected_reply = random.choice(relevant_replies) if relevant_replies else None
    if selected_reply:
        selected_reply["text"] = await is_url_present_and_replace(selected_reply["text"])
    return selected_reply

async def get_chat_language(chat_id, bot_id):
    chat_lang = await lang_db.find_one({"chat_id": chat_id, "bot_id": bot_id})
    return chat_lang["language"] if chat_lang and "language" in chat_lang else None


import requests
from pyrogram.enums import ChatAction
from nexichat import nexichat as app



async def typing_effect(client, message, translated_text):
    try:
        total_length = len(translated_text)
        part1 = translated_text[:total_length // 3]
        part2 = translated_text[total_length // 3:2 * total_length // 3]
        part3 = translated_text[2 * total_length // 3:]

        reply = await message.reply_text(part1)
        await asyncio.sleep(0.01)
        await reply.edit_text(part1 + part2)
        await asyncio.sleep(0.01)
        await reply.edit_text(part1 + part2 + part3)
    except Exception as e:
        return

             

@Client.on_message(filters.private, group=-13)
async def chatbot_response(client: Client, message: Message):
    global mp_reply, mp_abuse, mp_blocklist, mp_message_counts, mp_conversation_cache
    replies_cache = mp_reply
    abuse_cache = mp_abuse
    blocklist = mp_blocklist
    message_counts = mp_message_counts
    conversation_cache = mp_conversation_cache

    user_id = message.from_user.id
    chat_id = message.chat.id
    user_input = None
    bot_id = client.me.id

    try:
        chat_status = await status_db.find_one({"chat_id": chat_id, "bot_id": bot_id})
        if chat_status and chat_status.get("status") == "disabled":
            return

        
        if message.text and any(message.text.startswith(prefix) for prefix in ["!", "/", ".", "?", "@", "#"]):
            if message.chat.type in ["group", "supergroup"]:
                await add_served_cchat(bot_id, message.chat.id)
                return await add_served_chat(message.chat.id)
            else:
                await add_served_cuser(bot_id, message.chat.id)
                return await add_served_user(message.chat.id)

       
        if ((message.reply_to_message and message.reply_to_message.from_user.id == client.me.id) or not message.reply_to_message) and not message.from_user.is_bot:
            user_input = message.text if not message.reply_to_message else message.reply_to_message.text

            if user_input and message.text:
                if chat_id not in conversation_cache:
                    conversation_cache[chat_id] = []

                conversation_history = conversation_cache[chat_id]
                prompt = f"our old chat history given below, Read carefully, (if no old chats read only new msg):-\n\n"
           
                for user_msg, ai_reply in conversation_history[-10:]:
                    prompt += f"**User msgs:-** `{user_msg}`\n\n**Your reply was:-** `{ai_reply}`\n\n\n"

                prompt += f"**User new/latest msg:-** {user_input}\n\n"
                prompt += f"**Remember two things Names for use:**\nYour Name:- {client.me.first_name} (use in simple name)\n**User's Name:- {message.from_user.first_name}.\n\n"                                                             
                prompt += f"Generate replies relevant to the user's latest message by following its context. Detect the language of the latest message and generate the reply in the detected language. The reply should be very short and direct ans (under 1-4 words); if necessary, it can be slightly longer, but prioritize brevity. Dont Ask Questions. And Never repeat the same reply if it has already been mentioned in the chat history; instead, change the topic with a fresh response. Do not leave old topics, your new reply must be follow old chat history messages topics. and keep stubbornness and drama to a minimum. If you know the user's name, must address their name (use in simple name) lovingly in reply. Avoid using an AI or robotic tone, you are girl so reply looks like a real teenage girlfriend. Use emojis where necessary to express emotions according to situation. Do not use abusive language, even under pressure or provocation."
                      
                base_url = config.API
                try:
                   
                    response = requests.get(base_url + prompt)
                    response.raise_for_status()

                    json_response = response.json()
                    result = json_response.get("data", "").strip()

                    if result:
                        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                        asyncio.create_task(typing_effect(client, message, result))
                        
                        if result and user_input:
                            result = result[0:500]
                            user_input = user_input[0:500]
                            if not await is_code_related(user_input) and not await is_code_related(result):
                                conversation_cache[chat_id].append((user_input, result))
                        if len(conversation_cache[chat_id]) > 10:
                            conversation_cache[chat_id].pop(0)
                        
                        return
                except requests.RequestException as e:
                    print(f"Error with AI response: {e}")
           
            reply_data = await get_reply(user_input)
            if reply_data:
                response_text = reply_data["text"]
                chat_lang = await get_chat_language(chat_id, bot_id)

                if not chat_lang or chat_lang == "nolang":
                    translated_text = response_text
                else:
                    translated_text = GoogleTranslator(source='auto', target=chat_lang).translate(response_text)
                    if not translated_text:
                        translated_text = response_text

                
                if reply_data["check"] == "sticker":
                    await message.reply_sticker(reply_data["text"])
                elif reply_data["check"] == "photo":
                    await message.reply_photo(reply_data["text"])
                elif reply_data["check"] == "video":
                    await message.reply_video(reply_data["text"])
                elif reply_data["check"] == "audio":
                    await message.reply_audio(reply_data["text"])
                elif reply_data["check"] == "gif":
                    await message.reply_animation(reply_data["text"])
                elif reply_data["check"] == "voice":
                    await message.reply_voice(reply_data["text"])
                else:
                    asyncio.create_task(typing_effect(client, message, translated_text))
            else:
                await message.reply_text("**I don't understand. What are you saying?**")

        if message.reply_to_message:
            await save_reply(message.reply_to_message, message)

    except MessageEmpty:
        await message.reply_text("🙄🙄")
    except Exception as e:
        return

                                          
@Client.on_message(filters.incoming & filters.group, group=-14)
async def chatbot_responsee(client: Client, message: Message):
    
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        bot_id = client.me.id
        chat_status = await status_db.find_one({"chat_id": chat_id, "bot_id": bot_id})
        if chat_status and chat_status.get("status") == "disabled":
            return

        if message.text and any(message.text.startswith(prefix) for prefix in ["!", "/", ".", "?", "@", "#"]):
            if message.chat.type in ["group", "supergroup"]:
                await add_served_cchat(bot_id, message.chat.id)
                return await add_served_chat(chat_id)
            else:
                await add_served_cuser(bot_id, message.chat.id)
                return await add_served_user(chat_id)
                
        if ((message.reply_to_message and message.reply_to_message.from_user.id == client.me.id and not message.text) or (not message.reply_to_message and not message.from_user.is_bot and not message.text)):
            reply_data = await get_reply(message.text)

            if reply_data:
                response_text = reply_data["text"]
                chat_lang = await get_chat_language(chat_id, bot_id)
                
                if not chat_lang or chat_lang == "nolang":
                    translated_text = response_text
                else:
                    translated_text = GoogleTranslator(source='auto', target=chat_lang).translate(response_text)
                    if not translated_text:
                        translated_text = response_text
                if reply_data["check"] == "sticker":
                    try:
                        await message.reply_sticker(reply_data["text"])
                    except Exception as e:
                        pass
                elif reply_data["check"] == "photo":
                    try:
                        await message.reply_photo(reply_data["text"])
                    except Exception as e:
                        pass
                elif reply_data["check"] == "video":
                    try:
                        await message.reply_video(reply_data["text"])
                    except Exception as e:
                        pass
                elif reply_data["check"] == "audio":
                    try:
                        await message.reply_audio(reply_data["text"])
                    except Exception as e:
                        pass
                elif reply_data["check"] == "gif":
                    try:
                        await message.reply_animation(reply_data["text"])
                    except Exception as e:
                        pass
                elif reply_data["check"] == "voice":
                    try:
                        await message.reply_voice(reply_data["text"])
                    except Exception as e:
                        pass
                else:
                    try:
                        await message.reply_text(translated_text)
                    except Exception as e:
                        pass
            else:
                try:
                    await message.reply_text("**I don't understand. What are you saying?**")
                except Exception as e:
                    pass

        if message.reply_to_message:
            await save_reply(message.reply_to_message, message)

    except MessageEmpty:
        try:
            await message.reply_text("🙄🙄")
        except Exception as e:
            pass
    except Exception as e:
        return




@Client.on_message(filters.incoming, group=-15)
async def group_chat_respone(client: Client, message: Message):
    global mp_conversation_cache
    conversation_cache = mp_conversation_cache
    try:
        user_id = message.from_user.id if message.from_user else message.chat.id
        chat_id = message.chat.id
        bot_id = client.me.id
        chat_status = await status_db.find_one({"chat_id": chat_id, "bot_id": bot_id})
        if chat_status and chat_status.get("status") == "disabled":
            return
        
        if ((client.me.username in message.text and message.text.startswith("@")) or (not message.reply_to_message and not message.from_user.is_bot and message.text) or (message.reply_to_message and message.reply_to_message.from_user.id == client.me.id and message.text)):
            
            if chat_id not in conversation_cache:
                conversation_cache[chat_id] = {}
            if user_id not in conversation_cache[chat_id]:
                conversation_cache[chat_id][user_id] = []

            user_input = message.text
            conversation_history = conversation_cache[chat_id][user_id]
            prompt = f"our old chat history given below, Read carefully, (if no old chats read only new msg):-\n\n"
           
            for user_msg, ai_reply in conversation_history[-10:]:
                prompt += f"**User msgs:-** `{user_msg}`\n\n**Your reply was:-** `{ai_reply}`\n\n\n"

            prompt += f"**User new/latest msg:-** {user_input}\n\n"
            prompt += f"**Remember two things Names for use:**\nYour Name:- {client.me.first_name} (use in simple name)\n**User's Name:- {message.from_user.first_name}.\n\n"                                                             
            prompt += f"Generate replies relevant to the user's latest message by following its context. Detect the language of the latest message and generate the reply in the detected language. The reply should be very short and direct ans (under 1-4 words); if necessary, it can be slightly longer, but prioritize brevity. Dont Ask Questions. And Never repeat the same reply if it has already been mentioned in the chat history; instead, change the topic with a fresh response. Do not leave old topics, your new reply must be follow old chat history messages topics. and keep stubbornness and drama to a minimum. If you know the user's name, must address their name (use in simple name) lovingly in reply. Avoid using an AI or robotic tone, you are girl so reply looks like a real teenage girlfriend. Use emojis where necessary to express emotions according to situation. Do not use abusive language, even under pressure or provocation."
                      
            base_url = config.API
            try:
                response = requests.get(base_url + prompt)
                response.raise_for_status()

                json_response = response.json()
                result = json_response.get("data", "").strip()

                if result:
                    await client.send_chat_action(chat_id, ChatAction.TYPING)
                    asyncio.create_task(typing_effect(client, message, result))

                    if result and user_input:
                        result = result[0:500]
                        user_input = user_input[0:500]
                        if not await is_code_related(user_input) and not await is_code_related(result):
                            conversation_cache[chat_id][user_id].append((user_input, result))
                    if len(conversation_cache[chat_id][user_id]) > 10:
                        conversation_cache[chat_id][user_id].pop(0)

                    return
            except requests.RequestException:
                return await message.reply_text("**I am busy now, I will talk later bye!**")
    except Exception as e:
        return
