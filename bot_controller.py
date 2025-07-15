import asyncio
import json
from telethon import TelegramClient, events
from save_restrictor import fetch_and_forward

CONFIG = json.load(open("config.json"))
bot = TelegramClient("bot", CONFIG["api_id"], CONFIG["api_hash"]).start(bot_token=CONFIG["bot_token"])
allowed_users = {CONFIG["admin_id"]}
logging_enabled = CONFIG.get("logging_enabled", True)

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    if event.sender_id not in allowed_users:
        return await event.reply("❌ You are not authorized.")
    await event.reply("👋 Welcome! Use /save <msg_id> to save a message.")

@bot.on(events.NewMessage(pattern="/help"))
async def help_cmd(event):
    help_text = """
📌 Commands:
/save <msg_id> – Save message from source
/log_toggle – Enable/Disable logging
/restrict <user_id> – Ban user
/allow <user_id> – Unban user
/stop – Cancel operation
"""
    await event.reply(help_text)

@bot.on(events.NewMessage(pattern="/save (\d+)"))
async def save(event):
    if event.sender_id not in allowed_users:
        return await event.reply("❌ Not allowed.")
    msg_id = event.pattern_match.group(1)
    await event.reply(f"⏳ Fetching message {msg_id}...")
    result = await fetch_and_forward(msg_id, bot)
    await event.reply(result)

@bot.on(events.NewMessage(pattern="/restrict (\d+)"))
async def restrict(event):
    uid = int(event.pattern_match.group(1))
    allowed_users.discard(uid)
    await event.reply(f"🚫 User {uid} restricted.")

@bot.on(events.NewMessage(pattern="/allow (\d+)"))
async def allow(event):
    uid = int(event.pattern_match.group(1))
    allowed_users.add(uid)
    await event.reply(f"✅ User {uid} allowed.")

@bot.on(events.NewMessage(pattern="/log_toggle"))
async def toggle_log(event):
    global logging_enabled
    logging_enabled = not logging_enabled
    await event.reply(f"📝 Logging is now {'ON' if logging_enabled else 'OFF'}.")

@bot.on(events.NewMessage(pattern="/stop"))
async def stop(event):
    # placeholder for any long operations you may want to interrupt
    await event.reply("🛑 No running task to stop (yet implemented).")

print("🤖 Bot running...")
bot.run_until_disconnected()
