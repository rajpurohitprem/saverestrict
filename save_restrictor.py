import os
import json
import asyncio
from telethon import TelegramClient
from telethon.tl.types import Message
from tqdm import tqdm

CONFIG_PATH = "config.json"
SENT_LOG = "sent_ids.txt"
DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
open(SENT_LOG, "a").close()  # ensure log file exists

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)

CONFIG = load_config()

def log_sent_id(msg_id):
    with open(SENT_LOG, "a") as f:
        f.write(f"{msg_id}\n")

async def get_channel_list(client):
    dialogs = await client.get_dialogs()
    channels = [d for d in dialogs if d.is_channel and not d.is_user]
    return channels

async def get_entity_by_id(client, channel_id):
    try:
        return await client.get_entity(int(channel_id))
    except Exception:
        return None

async def fetch_and_forward(msg_id, client):
    config = load_config()

    source = await get_entity_by_id(client, config.get("source_channel_id"))
    target = await get_entity_by_id(client, config.get("target_channel_id"))
    log_channel = await get_entity_by_id(client, config.get("log_channel"))

    if not source or not target:
        raise Exception("Source or Target channel is invalid or not set.")

    msg = await client.get_messages(source, ids=msg_id)
    if not msg:
        raise Exception(f"Message ID {msg_id} not found in source.")

    if isinstance(msg, Message) and msg.media:
        file_path = os.path.join(DOWNLOAD_DIR, f"{msg.id}")
        bar = tqdm(desc="📥 Downloading", total=100, unit="%", leave=False)

        def download_callback(cur, total):
            percent = int((cur / total) * 100)
            bar.n = percent
            bar.refresh()

        file = await client.download_media(msg, file=file_path, progress_callback=download_callback)
        bar.close()

        if not file:
            raise Exception(f"Failed to download media for message ID {msg.id}")

        up_bar = tqdm(desc="📤 Uploading", total=os.path.getsize(file), unit="B", unit_scale=True, leave=False)

        def upload_callback(sent, total):
            up_bar.update(sent - up_bar.n)

        await client.send_file(
            target,
            file,
            caption=msg.text or msg.message or "",
            progress_callback=upload_callback
        )
        up_bar.close()
        os.remove(file)

        if log_channel:
            await client.send_message(log_channel, f"✅ Saved media from message ID {msg_id}")

    elif msg.text or msg.message:
        await client.send_message(target, msg.text or msg.message)
        if log_channel:
            await client.send_message(log_channel, f"✅ Saved text message ID {msg_id}")

    log_sent_id(msg.id)
    return True
