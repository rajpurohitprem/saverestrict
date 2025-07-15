from telethon.tl.functions.messages import GetMessagesRequest
from config import CONFIG
import os

async def fetch_and_forward(msg_id, client):
    source = CONFIG.get("source_channel")
    target = CONFIG.get("log_channel")

    if not source or not target:
        return "⚠️ Source or Log channel not set. Use /setsourcechannel and /setlogchannel."

    try:
        messages = await client(GetMessagesRequest(id=[int(msg_id)], peer=source))
        msg = messages.messages[0]
    except Exception as e:
        return f"❌ Failed to fetch message: {e}"

    if not msg:
        return "❌ Message not found."

    try:
        if msg.media:
            downloaded = await client.download_media(msg, file="downloads/")
            await client.send_file(target, downloaded, caption=msg.message or "")
            if os.path.exists(downloaded):
                os.remove(downloaded)
        else:
            await client.send_message(target, msg.message or "[Empty message]")
    except Exception as e:
        return f"❌ Failed to send message: {e}"

    return "✅ Message saved successfully."
