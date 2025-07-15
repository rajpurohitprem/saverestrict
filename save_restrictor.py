import os
import json
import asyncio
from telethon import TelegramClient, events
from tqdm import tqdm
from telethon.tl.types import Message

CONFIG_FILE = "config.json"
SESSION_FILE = "anon"
DOWNLOAD_DIR = "downloads"

# Load config
def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

CONFIG = load_config()

# Telethon client
client = TelegramClient(SESSION_FILE, CONFIG["api_id"], CONFIG["api_hash"])

# Ensure download dir exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def fetch_and_forward(msg_id, bot):
    try:
        source = await client.get_entity(CONFIG["source_channel"])
        target = await client.get_entity(CONFIG["target_channel"])

        message = await client.get_messages(source, ids=msg_id)
        if not message:
            return False, f"Message ID {msg_id} not found."

        if message.media:
            filename = os.path.join(DOWNLOAD_DIR, f"{msg_id}")

            size_info = {"value": 0}
            def progress_dl(cur, total):
                size_info["value"] = total
                tqdm.write(f"📥 Downloading {cur/1024:.1f}/{total/1024:.1f} KB", end="\r")

            file_path = await client.download_media(message, file=filename, progress_callback=progress_dl)

            upload_bar = tqdm(total=size_info["value"], unit='B', unit_scale=True, desc="📤 Uploading")
            def progress_ul(sent, total):
                upload_bar.update(sent - upload_bar.n)

            await client.send_file(
                target,
                file_path,
                caption=message.text or message.message or "",
                progress_callback=progress_ul
            )
            upload_bar.close()
            os.remove(file_path)

        elif message.text or message.message:
            await client.send_message(target, message.text or message.message)

        return True, f"✅ Message {msg_id} saved."

    except Exception as e:
        return False, f"❌ Error on message {msg_id}: {e}"


# Bot Controller
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

ADMIN_ID = CONFIG.get("admin_id")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("Unauthorized.")
    await update.message.reply_text("👋 Bot is active. Use /save <msg_id> or /save <start>-<end>")

async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("Unauthorized.")

    if not context.args:
        return await update.message.reply_text("❗ Usage: /save <msg_id> or <start>-<end>")

    await client.start(phone=CONFIG["phone"])

    arg = context.args[0]
    if '-' in arg:
        start_id, end_id = map(int, arg.split('-'))
        for mid in range(start_id, end_id + 1):
            await update.message.reply_text(f"⏳ Saving {mid}...")
            success, msg = await fetch_and_forward(mid, client)
            await update.message.reply_text(msg)
    else:
        msg_id = int(arg)
        await update.message.reply_text(f"⏳ Saving {msg_id}...")
        success, msg = await fetch_and_forward(msg_id, client)
        await update.message.reply_text(msg)

if __name__ == '__main__':
    app = Application.builder().token(CONFIG["bot_token"]).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("save", save))

    asyncio.get_event_loop().run_until_complete(client.connect())
    app.run_polling()


async def get_channel_list():
    client = await get_client()
    dialogs = await client.get_dialogs()
    return [d for d in dialogs if d.is_channel and not d.is_user]
