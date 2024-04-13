from pyrogram import filters
from pymongo import MongoClient
from AnonXMusic import app
from config import MONGO_DB_URI
from pyrogram.types import *
from pyrogram.errors import MessageNotModified
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.types import InputMediaPhoto
from typing import Union
import asyncio
import random
from pyrogram import Client, filters
import requests
import os
import time 
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, Message

mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client["natu_rankings"]
collection = db["ranking"]

user_data = {}
today = {}
banned_users = {}

MISHI = [
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
    "https://telegra.ph/file/a6a5b78007e4ca766794a.jpg",
]

# Function to check if a user is banned
def is_user_banned(user_id):
    return user_id in banned_users and time.time() < banned_users[user_id]

# Function to ban a user for 10 minutes
def ban_user(user_id):
    banned_users[user_id] = time.time() + 600

# Function to notify user about the ban
async def notify_ban(user_id):
    try:
        await app.send_message(user_id, "You are banned for 10 minutes.")
    except Exception as e:
        print(f"Failed to notify user {user_id} about ban: {e}")

@app.on_message(filters.group & filters.group, group=6)
def today_watcher(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if user is banned, if yes, return
    if is_user_banned(user_id):
        return

    # Check if user sent too many consecutive messages
    if user_id in user_data:
        user_data[user_id]["consecutive_messages"] += 1
        if user_data[user_id]["consecutive_messages"] >= 12:
            ban_user(user_id)
            asyncio.run(notify_ban(user_id))  # Notify user about the ban
            return
    else:
        user_data[user_id] = {"consecutive_messages": 1}

    if chat_id in today and user_id in today[chat_id]:
        today[chat_id][user_id]["total_messages"] += 1
    else:
        if chat_id not in today:
            today[chat_id] = {}
        if user_id not in today[chat_id]:
            today[chat_id][user_id] = {"total_messages": 1}
        else:
            today[chat_id][user_id]["total_messages"] = 1

    # Check if user is spamming
    if today[chat_id][user_id]["total_messages"] > 10:
        ban_user(user_id)

@app.on_message(filters.group & filters.group, group=11)
def _watcher(_, message):
    user_id = message.from_user.id

    # Check if user is banned, if yes, return
    if is_user_banned(user_id):
        return
    
    user_data.setdefault(user_id, {}).setdefault("total_messages", 0)
    user_data[user_id]["total_messages"] += 1    
    collection.update_one({"_id": user_id}, {"$inc": {"total_messages": 1}}, upsert=True)

@app.on_message(filters.command("today"))
async def today_(_, message):
    chat_id = message.chat.id
    if chat_id in today:
        total_messages_count = sum(user_data['total_messages'] for user_data in today[chat_id].values())
        users_data = [(user_id, user_data["total_messages"]) for user_id, user_data in today[chat_id].items()]
        sorted_users_data = sorted(users_data, key=lambda x: x[1], reverse=True)[:10]

        if sorted_users_data:
            response = f"✦ 📈 ᴛᴏᴅᴀʏ ᴛᴏᴛᴀʟ ᴍᴇssᴀɢᴇs: {total_messages_count}\n\n"
            for idx, (user_id, total_messages) in enumerate(sorted_users_data, start=1):
                try:
                    user_name = (await app.get_users(user_id)).first_name
                except:
                    user_name = "Unknown"
                user_info = f"{idx}. {user_name} ➠ {total_messages} messages\n"
                response += user_info
            button = InlineKeyboardMarkup(
                [[    
                   InlineKeyboardButton("ᴏᴠᴇʀᴀʟʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", callback_data="overall"),
                ]])
            await message.reply_photo(random.choice(MISHI), caption=response, reply_markup=button)
        else:
            await message.reply_text("❅ ɴᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛᴏᴅᴀʏ.")
    else:
        await message.reply_text("❅ ɴᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛᴏᴅᴀʏ.")
