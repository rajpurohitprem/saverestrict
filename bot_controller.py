import json
from telethon import TelegramClient, events
from save_restrictor import fetch_and_forward

# Load config
with open("config.json", "r") as f:
    CONFIG = json.load(f)

# Bot setup using Telethon
bot = TelegramClient("anon", CONFIG["api_id"], CONFIG["api_hash"])
admin_id = CONFIG["admin_id"]

# Save updated config
def save_config():
    with open("config.json", "w") as f:
        json.dump(CONFIG, f, indent=2)

# Start command
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    if event.sender_id != admin_id:
        return await event.reply("❌ Unauthorized.")
    await event.reply("👋 Welcome! Use /help to see commands.")

# Help
@bot.on(events.NewMessage(pattern="/help"))
async def help_cmd(event):
    if event.sender_id != admin_id:
        return
    await event.reply("""
📘 Commands:
/set_source – Set source channel
/set_target – Set target channel
/set_log – Set log channel
/save <msg_id> – Save message
/log_toggle – Toggle logging
/stop – Cancel operations
    """)

# Set Source Channel
@bot.on(events.NewMessage(pattern="/set_source"))
async def set_source(event):
    if event.sender_id != admin_id:
        return
    await event.reply("📥 Send the source channel username or ID (e.g. @channel or -100xxxx):")

    @bot.on(events.NewMessage(from_users=admin_id))
    async def receive_source(ev):
        CONFIG["source_channel"] = ev.raw_text.strip()
        save_config()
        await ev.reply(f"✅ Source channel set to `{CONFIG['source_channel']}`")
        bot.remove_event_handler(receive_source)

# Set Target Channel
@bot.on(events.NewMessage(pattern="/set_target"))
async def set_target(event):
    if event.sender_id != admin_id:
        return
    await event.reply("🎯 Send the target channel username or ID:")

    @bot.on(events.NewMessage(from_users=admin_id))
    async def receive_target(ev):
        CONFIG["target_channel"] = ev.raw_text.strip()
        save_config()
        await ev.reply(f"✅ Target channel set to `{CONFIG['target_channel']}`")
        bot.remove_event_handler(receive_target)

# Set Log Channel
@bot.on(events.NewMessage(pattern="/set_log"))
async def set_log(event):
    if event.sender_id != admin_id:
        return
    await event.reply("🪵 Send the log channel username or ID:")

    @bot.on(events.NewMessage(from_users=admin_id))
    async def receive_log(ev):
        CONFIG["log_channel"] = ev.raw_text.strip()
        save_config()
        await ev.reply(f"✅ Log channel set to `{CONFIG['log_channel']}`")
        bot.remove_event_handler(receive_log)

# Toggle logging
@bot.on(events.NewMessage(pattern="/log_toggle"))
async def log_toggle(event):
    if event.sender_id != admin_id:
        return
    CONFIG["logging_enabled"] = not CONFIG.get("logging_enabled", True)
    save_config()
    status = "ON ✅" if CONFIG["logging_enabled"] else "OFF ❌"
    await event.reply(f"📋 Logging is now: {status}")

# Save command
@bot.on(events.NewMessage(pattern=r"/save (\d+)"))
async def save(event):
    if event.sender_id != admin_id:
        return await event.reply("❌ Unauthorized.")
    msg_id = int(event.pattern_match.group(1))
    await event.reply("⏳ Saving message...")
    await event.reply("⏳ Saving message...")
    result = await fetch_and_forward(msg_id)
    await event.respond(result or "✅ Done")  # respond = reply using bot


# Run the bot
print("🤖 Bot running...")
bot.start(bot_token=CONFIG["bot_token"])
bot.run_until_disconnected()
