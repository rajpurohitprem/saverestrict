from telethon import TelegramClient, events, Button
import json
import asyncio
from save_restrictor import fetch_and_forward
from config import CONFIG, save_config

# Load values
api_id = CONFIG["api_id"]
api_hash = CONFIG["api_hash"]
bot_token = CONFIG["bot_token"]
admin_id = CONFIG["admin_id"]
phone = CONFIG["phone_number"]

# Clients
client = TelegramClient("anon", api_id, api_hash)
bot = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)

# Allowed users
allowed_users = CONFIG.get("allowed_users", [])
if admin_id not in allowed_users:
    allowed_users.append(admin_id)

running = False

# ──────────────── Commands ──────────────── #

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    if event.sender_id != admin_id:
        return
    await event.respond("🤖 **Save Restrict Bot is Ready**\n\nUse /help to see commands.")

@bot.on(events.NewMessage(pattern="/help"))
async def help_cmd(event):
    if event.sender_id != admin_id:
        return
    await event.respond(
        "**🛠 Commands:**\n"
        "/save <msg_id> - Save message from source\n"
        "/set_source - Choose source channel\n"
        "/set_log - Choose log (target) channel\n"
        "/log_toggle - Toggle log ON/OFF\n"
        "/restrict <user_id> - Ban user\n"
        "/allow <user_id> - Allow user\n"
        "/stop - Stop running operation"
    )

@bot.on(events.NewMessage(pattern="/save (\d+)"))
async def save(event):
    if event.sender_id not in allowed_users:
        return

    global running
    if running:
        await event.respond("⚠️ Already running. Use /stop to cancel.")
        return

    running = True
    msg_id = event.pattern_match.group(1)
    await event.respond("⏳ Fetching message...")

    result = await fetch_and_forward(msg_id, bot)
    await event.respond(result)

    running = False

@bot.on(events.NewMessage(pattern="/stop"))
async def stop(event):
    global running
    if event.sender_id != admin_id:
        return
    running = False
    await event.respond("⛔ Operation stopped.")

@bot.on(events.NewMessage(pattern="/log_toggle"))
async def toggle_log(event):
    if event.sender_id != admin_id:
        return
    CONFIG["logging_enabled"] = not CONFIG.get("logging_enabled", False)
    save_config(CONFIG)
    status = "ON ✅" if CONFIG["logging_enabled"] else "OFF ❌"
    await event.respond(f"🗂 Logging turned {status}")

@bot.on(events.NewMessage(pattern="/restrict (\d+)"))
async def restrict(event):
    if event.sender_id != admin_id:
        return
    uid = int(event.pattern_match.group(1))
    if uid in allowed_users:
        allowed_users.remove(uid)
    CONFIG["allowed_users"] = allowed_users
    save_config(CONFIG)
    await event.respond(f"🚫 User {uid} restricted.")

@bot.on(events.NewMessage(pattern="/allow (\d+)"))
async def allow(event):
    if event.sender_id != admin_id:
        return
    uid = int(event.pattern_match.group(1))
    if uid not in allowed_users:
        allowed_users.append(uid)
    CONFIG["allowed_users"] = allowed_users
    save_config(CONFIG)
    await event.respond(f"✅ User {uid} allowed.")

# ──────────────── Set Channels ──────────────── #

@bot.on(events.NewMessage(pattern="/set_source"))
async def set_source(event):
    if event.sender_id != admin_id:
        return

    await client.start(phone=phone)
    dialogs = await client.get_dialogs()
    channels = [d for d in dialogs if d.is_channel]

    buttons = [Button.inline(c.name[:30], data=f"setsrc:{c.entity.id}") for c in channels]
    chunks = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    await event.respond("📡 **Choose Source Channel**:", buttons=chunks)
    await client.disconnect()

@bot.on(events.NewMessage(pattern="/set_log"))
async def set_log(event):
    if event.sender_id != admin_id:
        return

    await client.start(phone=phone)
    dialogs = await client.get_dialogs()
    channels = [d for d in dialogs if d.is_channel]

    buttons = [Button.inline(c.name[:30], data=f"setlog:{c.entity.id}") for c in channels]
    chunks = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    await event.respond("📤 **Choose Log Channel**:", buttons=chunks)
    await client.disconnect()

@bot.on(events.CallbackQuery(pattern=b"setsrc:(-?\d+)"))
async def cb_setsrc(event):
    cid = int(event.pattern_match.group(1))
    CONFIG["source_channel"] = cid
    save_config(CONFIG)
    await event.edit(f"✅ Source channel set to `{cid}`")

@bot.on(events.CallbackQuery(pattern=b"setlog:(-?\d+)"))
async def cb_setlog(event):
    cid = int(event.pattern_match.group(1))
    CONFIG["log_channel"] = cid
    save_config(CONFIG)
    await event.edit(f"✅ Log (target) channel set to `{cid}`")

# ──────────────── Start Bot ──────────────── #

print("🤖 Bot is running...")
bot.run_until_disconnected()
