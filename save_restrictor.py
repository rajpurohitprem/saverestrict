# save_restrictor.py
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.tl.functions.messages import GetMessagesRequest
from config import CONFIG
import os

async def fetch_and_forward(msg_id, client):
    source = CONFIG["source_channel"]
    target = CONFIG["log_channel"]

    msg = (await client(GetMessagesRequest(id=[int(msg_id)], peer=source))).messages[0]

    if msg.media:
        file = await client.download_media(msg, file="downloads/")
        await client.send_file(target, file, caption=msg.text or "")
        os.remove(file)
    else:
        await client.send_message(target, msg.text or "[Empty Message]")

    return "✅ Message saved."
