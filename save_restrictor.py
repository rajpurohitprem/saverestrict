from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetMessagesRequest
from telethon.tl.types import InputPeerChannel, PeerChannel
from telethon.errors import MessageIdInvalidError
from tqdm import tqdm
import os
import json
import logging

CONFIG = json.load(open("config.json"))
client = TelegramClient("anon", CONFIG["api_id"], CONFIG["api_hash"])

if not os.path.exists("log.txt"):
    open("log.txt", "w").close()

logging.basicConfig(filename='log.txt', level=logging.INFO)

async def save_message(msg_id):
    await client.start(phone=CONFIG["phone_number"])
    try:
        entity = await client.get_entity(CONFIG["source_channel"])
        messages = await client(GetMessagesRequest(id=[int(msg_id)]))
        msg = messages.messages[0]

        media = msg.media
        if media:
            filename = await client.download_media(media, progress_callback=lambda d, t: tqdm(total=t).update(d))
            logging.info(f"Downloaded media from msg_id {msg_id} to {filename}")
        else:
            filename = None
            logging.info(f"No media found in msg_id {msg_id}")

        if CONFIG.get("log_channel"):
            await client.send_message(CONFIG["log_channel"], msg.text or "Media saved.", file=filename)
        return "✅ Message saved."
    except MessageIdInvalidError:
        return "❌ Invalid Message ID."
    except Exception as e:
        logging.error(f"Error saving msg {msg_id}: {str(e)}")
        return f"❌ Error: {str(e)}"
