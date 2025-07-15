from telethon.sync import TelegramClient
from telethon import events
from config import CONFIG, save_config
from save_restrictor import fetch_and_forward
import asyncio

api_id = CONFIG["api_id"]
api_hash = CONFIG["api_hash"]
phone = CONFIG["phone_number"]
admin_id = CONFIG["admin_id"]

client = TelegramClient("anon", api_id, api_hash)

@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    if event.sender_id != admin_id:
        return await event.reply("⛔ Access Denied.")
    await event.reply(
        "**🟢 Save Restrict Bot is Running**\n\n"
        "**Commands:**\n"
        "`/save <msg_id>` – Save from source channel\n"
        "`/setsourcechannel` – Choose source channel\n"
        "`/setlogchannel` – Choose target channel\n"
        "`/help` – Show help"
    )

@client.on(events.NewMessage(pattern="/help"))
async def help_cmd(event):
    return await start(event)

@client.on(events.NewMessage(pattern=r"/save (\d+)"))
async def save(event):
    if event.sender_id != admin_id:
        return await event.reply("⛔ Access Denied.")

    msg_id = int(event.pattern_match.group(1))
    try:
        result = await fetch_and_forward(msg_id, client)
        await event.reply(result)
    except Exception as e:
        await event.reply(f"❌ Error: {e}")

@client.on(events.NewMessage(pattern="/setsourcechannel"))
async def set_source_channel(event):
    if event.sender_id != admin_id:
        return await event.reply("⛔ Access Denied.")

    dialogs = await client.get_dialogs()
    channels = [d for d in dialogs if d.is_channel]

    if not channels:
        return await event.reply("❌ No channels found.")

    text = "**📡 Choose Source Channel:**\n"
    for i, ch in enumerate(channels, 1):
        text += f"{i}. {ch.name} — `{ch.id}`\n"
    text += "\nReply with the number."

    await event.reply(text)
    response = await client.wait_for(events.NewMessage(from_users=admin_id))
    try:
        index = int(response.raw_text.strip()) - 1
        selected = channels[index]
    except:
        return await response.reply("❌ Invalid choice.")

    CONFIG["source_channel"] = selected.id
    save_config(CONFIG)
    await response.reply(f"✅ Source channel set to: `{selected.name}` (`{selected.id}`)")

@client.on(events.NewMessage(pattern="/setlogchannel"))
async def set_log_channel(event):
    if event.sender_id != admin_id:
        return await event.reply("⛔ Access Denied.")

    dialogs = await client.get_dialogs()
    channels = [d for d in dialogs if d.is_channel]

    if not channels:
        return await event.reply("❌ No channels found.")

    text = "**📥 Choose Log Channel:**\n"
    for i, ch in enumerate(channels, 1):
        text += f"{i}. {ch.name} — `{ch.id}`\n"
    text += "\nReply with the number."

    await event.reply(text)
    response = await client.wait_for(events.NewMessage(from_users=admin_id))
    try:
        index = int(response.raw_text.strip()) - 1
        selected = channels[index]
    except:
        return await response.reply("❌ Invalid choice.")

    CONFIG["log_channel"] = selected.id
    save_config(CONFIG)
    await response.reply(f"✅ Log channel set to: `{selected.name}` (`{selected.id}`)")

print("✅ Bot is starting...")
client.start(phone)
client.run_until_disconnected()
