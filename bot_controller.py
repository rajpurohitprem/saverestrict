import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from save_restrictor import client, save_message

CONFIG = json.load(open("config.json"))
bot = Bot(token=CONFIG["bot_token"])
dp = Dispatcher(bot)

restricted_users = set()
log_enabled = CONFIG.get("log_enabled", True)

# Command: /start
@dp.message_handler(commands=['start'])
async def cmd_start(msg: types.Message):
    if msg.from_user.id != CONFIG["admin_user_id"]:
        return
    await msg.reply("👋 Welcome to Save Restrict Bot.\nType /help to see commands.")

# Command: /help
@dp.message_handler(commands=['help'])
async def cmd_help(msg: types.Message):
    if msg.from_user.id != CONFIG["admin_user_id"]:
        return
    await msg.reply("""📘 Available Commands:
/save <msg_id> - Save restricted message
/restrict <user_id> - Block user
/allow <user_id> - Unblock user
/log_toggle - Enable/Disable logging
/stop - Stop any current operation
/help - Show this message""")

# Command: /save
@dp.message_handler(lambda m: m.text.startswith("/save "))
async def cmd_save(msg: types.Message):
    if msg.from_user.id != CONFIG["admin_user_id"]:
        return
    parts = msg.text.strip().split()
    if len(parts) < 2:
        await msg.reply("❗ Usage: /save <msg_id>")
        return
    await msg.reply("⏳ Fetching...")
    status = await save_message(parts[1])
    await msg.reply(status)

# Command: /restrict
@dp.message_handler(lambda m: m.text.startswith("/restrict "))
async def cmd_restrict(msg: types.Message):
    if msg.from_user.id != CONFIG["admin_user_id"]:
        return
    user_id = int(msg.text.split()[1])
    restricted_users.add(user_id)
    await msg.reply(f"🚫 User {user_id} restricted.")

# Command: /allow
@dp.message_handler(lambda m: m.text.startswith("/allow "))
async def cmd_allow(msg: types.Message):
    if msg.from_user.id != CONFIG["admin_user_id"]:
        return
    user_id = int(msg.text.split()[1])
    restricted_users.discard(user_id)
    await msg.reply(f"✅ User {user_id} allowed.")

# Command: /log_toggle
@dp.message_handler(commands=['log_toggle'])
async def cmd_log_toggle(msg: types.Message):
    global log_enabled
    if msg.from_user.id != CONFIG["admin_user_id"]:
        return
    log_enabled = not log_enabled
    await msg.reply(f"📝 Logging {'enabled' if log_enabled else 'disabled'}.")

# Command: /stop
@dp.message_handler(commands=['stop'])
async def cmd_stop(msg: types.Message):
    if msg.from_user.id != CONFIG["admin_user_id"]:
        return
    await msg.reply("⛔ Operation stopped. (Manual interruption supported soon)")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(client.start(phone=CONFIG["phone_number"]))
    executor.start_polling(dp, skip_updates=True)
