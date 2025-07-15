from telethon import events
import json

# Load config at top
with open("config.json", "r") as f:
    CONFIG = json.load(f)

async def save_config():
    with open("config.json", "w") as f:
        json.dump(CONFIG, f, indent=2)

@bot.on(events.NewMessage(pattern="/set_source"))
async def set_source(event):
    if event.sender_id != CONFIG["admin_id"]:
        return await event.reply("❌ Unauthorized")
    await event.reply("📥 Please send the source channel username or ID (like @channel or -1001234567890).")

    @bot.on(events.NewMessage(from_users=CONFIG["admin_id"]))
    async def get_source_channel(ev):
        CONFIG["source_channel"] = ev.raw_text.strip()
        await save_config()
        await ev.reply(f"✅ Source channel set to `{CONFIG['source_channel']}`")
        bot.remove_event_handler(get_source_channel)  # Remove after use
