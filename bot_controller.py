import json
import asyncio
from telethon import TelegramClient, events, Button
from save_restrictor import fetch_and_forward, CONFIG, load_config, get_channel_list, get_entity_by_id
API_ID = CONFIG["api_id"]
API_HASH = CONFIG["api_hash"]
BOT_TOKEN = CONFIG["bot_token"]
OWNER_ID = CONFIG["admin_id"]

bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
user_client = TelegramClient("anon", API_ID, API_HASH)

# Ensure user client is running
async def start_user_client():
    await user_client.start(phone=CONFIG["phone_number"])
asyncio.get_event_loop().run_until_complete(start_user_client())

async def is_admin(event):
    return event.sender_id == OWNER_ID

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    if not await is_admin(event): return
    await event.respond(
        "👋 Welcome to Save Restrict Bot!",
        buttons=[
            [Button.text("Set Source Channel"), Button.text("Set Target Channel")],
            [Button.text("Set Log Channel"), Button.text("Toggle Logging")],
            [Button.text("Help")]
        ],
        reply_to=event.id
    )

@bot.on(events.NewMessage(pattern="/help"))
async def help_cmd(event):
    if not await is_admin(event): return
    msg = (
        "📖 *Available Commands*:\n"
        "/save `<msg_id>` or `<start_id-end_id>` - Save restricted messages\n"
        "/set_source - Set source channel\n"
        "/set_target - Set target channel\n"
        "/set_log - Set log channel\n"
        "/log_toggle - Toggle logging\n"
        "/stop - Cancel any running save process"
    )
    await event.respond(msg, parse_mode="md", reply_to=event.id)

@bot.on(events.NewMessage(pattern=r"/save (\d+)(-(\d+))?"))
async def save(event):
    if not await is_admin(event): return
    match = event.pattern_match
    start_id = int(match.group(1))
    end_id = int(match.group(3)) if match.group(3) else start_id
    await event.respond(f"🔄 Saving messages from {start_id} to {end_id}...", reply_to=event.id)

    for msg_id in range(start_id, end_id + 1):
        try:
            result = await fetch_and_forward(msg_id, user_client)
            await event.respond(f"✅ Saved message {msg_id}", reply_to=event.id)
        except Exception as e:
            await event.respond(f"❌ Error on {msg_id}: {e}", reply_to=event.id)

@bot.on(events.NewMessage(pattern="/log_toggle"))
async def log_toggle(event):
    if not await is_admin(event): return
    CONFIG["log_enabled"] = not CONFIG.get("log_enabled", False)
    save_config()
    state = "ON" if CONFIG["log_enabled"] else "OFF"
    await event.respond(f"📝 Log channel toggled {state}", reply_to=event.id)

@bot.on(events.NewMessage(pattern="/stop"))
async def stop(event):
    if not await is_admin(event): return
    # Optional: implement shared state cancel logic
    await event.respond("⛔ Cancel not yet implemented", reply_to=event.id)

# Channel selectors
@bot.on(events.NewMessage(pattern="/set_source"))
async def set_source(event):
    if not await is_admin(event): return
    channels = await get_channel_list(user_client)
    btns = [Button.inline(c.title, data=f"src_{c.id}") for c in channels]
    await event.respond("📥 Choose source channel:", buttons=btns, reply_to=event.id)

@bot.on(events.NewMessage(pattern="/set_target"))
async def set_target(event):
    if not await is_admin(event): return
    channels = await get_channel_list(user_client)
    btns = [Button.inline(c.title, data=f"tgt_{c.id}") for c in channels]
    await event.respond("📤 Choose target channel:", buttons=btns, reply_to=event.id)

@bot.on(events.NewMessage(pattern="/set_log"))
async def set_log(event):
    if not await is_admin(event): return
    channels = await get_channel_list(user_client)
    btns = [Button.inline(c.title, data=f"log_{c.id}") for c in channels]
    await event.respond("📝 Choose log channel:", buttons=btns, reply_to=event.id)

# Handle inline callback buttons
@bot.on(events.CallbackQuery())
async def callback_handler(event):
    if not await is_admin(event): return
    data = event.data.decode()
    if data.startswith("src_"):
        cid = int(data.split("_")[1])
        CONFIG["source_channel"] = cid
        save_config()
        await event.edit(f"✅ Source channel set to ID: {cid}")
    elif data.startswith("tgt_"):
        cid = int(data.split("_")[1])
        CONFIG["target_channel"] = cid
        save_config()
        await event.edit(f"✅ Target channel set to ID: {cid}")
    elif data.startswith("log_"):
        cid = int(data.split("_")[1])
        CONFIG["log_channel"] = cid
        save_config()
        await event.edit(f"✅ Log channel set to ID: {cid}")

print("🤖 Bot is running...")
bot.run_until_disconnected()
