from telethon.sync import TelegramClient
from telethon.tl.types import DocumentAttributeFilename
from telethon import events
from config import CONFIG, save_config
from save_restrictor import fetch_and_forward
import asyncio

api_id = CONFIG["api_id"]
api_hash = CONFIG["api_hash"]
phone = CONFIG["phone_number"]

client = TelegramClient("anon", api_id, api_hash)

@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    if event.sender_id != CONFIG["admin_id"]:
        return await event.reply("⛔ Access Denied.")

    await event.reply(
        "**Save Restrict Bot** is online.\n\n"
        "Available commands:\n"
        "`/save <msg_id>` – Save message from source channel\n"
        "`/setsourcechannel` – Choose source channel\n"
        "`/setlogchannel` – Choose log channel\n"
        "`/help` – Show this help"
    )

@client.on(events.NewMessage(pattern="/help"))
async def help_cmd(event):
    await start(event)

@client.on(events.NewMessage(pattern="/save (\d+)"))
async def save(event):
    if event.sender_id != CONFIG["admin_id"]:
        return await event.reply("⛔ Access Denied.")

    msg_id = int(event.pattern_match.group(1))
    try:
        result = await fetch_and_forward(msg_id, client)
        await event.reply(result)
    except Exception as e:
        await event.reply(f"❌ Error:\n`{e}`")

@client.on(events.NewMessage(pattern="/setsourcechannel"))
async def set_source(event):
    if event.sender_id != CONFIG["admin_id"]:
        return await event.reply("⛔ Access Denied.")

    dialogs = await client.get_dialogs()
    channels = [d for d in dialogs if d.is_channel]

    if not channels:
        return await event.reply("No channels found.")

    msg = "**📡 Your Channels:**\n"
    for i, ch in enumerate(channels, 1):
        msg += f"{i}. {ch.name} — `{ch.id}`\n"
    msg += "\nReply with the number of the channel to set as `source_channel`"

    await event.reply(msg)
    reply = await client.wait_for(events.NewMessage(from_users=event.sender_id))

    try:
        index = int(reply.raw_text.strip()) - 1
        chosen = channels[index]
    except:
        return await reply.reply("❌ Invalid choice.")

    CONFIG["source_channel"] = chosen.id
    save_config(CONFIG)
    await reply.reply(f"✅ Source channel set to **{chosen.name}** (`{chosen.id}`)")

@client.on(events.NewMessage(pattern="/setlogchannel"))
async def set_log(event):
    if event.sender_id != CONFIG["admin_id"]:
        return await event.reply("⛔ Access Denied.")

    dialogs = await client.get_dialogs()
    channels = [d for d in dialogs if d.is_channel]

    if not channels:
        return await event.reply("No channels found.")

    msg = "**📤 Your Channels:**\n"
    for i, ch in enumerate(channels, 1):
        msg += f"{i}. {ch.name} — `{ch.id}`\n"
    msg += "\nReply with the number of the channel to set as `log_channel`"

    await event.reply(msg)
    reply = await client.wait_for(events.NewMessage(from_users=event.sender_id))

    try:
        index = int(reply.raw_text.strip()) - 1
        chosen = channels[index]
    except:
        return await reply.reply("❌ Invalid choice.")

    CONFIG["log_channel"] = chosen.id
    save_config(CONFIG)
    await reply.reply(f"✅ Log channel set to **{chosen.name}** (`{chosen.id}`)")

# Start bot
print("🤖 Bot is running...")
client.start(phone)
client.run_until_disconnected()
