from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetMessagesRequest
from telethon.tl.types import InputPeerChannel, InputMessageID
from telethon.tl.functions.channels import GetFullChannelRequest
from tqdm import tqdm
import json
import os

CONFIG = json.load(open("config.json"))
SESSION = "anon"

client = TelegramClient(SESSION, CONFIG["api_id"], CONFIG["api_hash"])

async def fetch_and_forward(msg_id, bot):
    await client.start(phone=CONFIG["phone_number"])

    source = await client.get_entity(CONFIG["source_channel"])
    log_channel = await bot.get_entity(CONFIG["log_channel"])

    try:
        msg = await client(GetMessagesRequest(id=[int(msg_id)]))
        if msg.messages:
            m = msg.messages[0]
            progress = tqdm(total=1, desc="Downloading...", unit="msg")
            await bot.send_message(log_channel, m)
            progress.update(1)
            progress.close()
            return "✅ Message saved."
        else:
            return "⚠️ Message not found."
    except Exception as e:
        return f"❌ Error: {e}"
