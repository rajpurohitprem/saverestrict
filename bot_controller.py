import asyncio
import json
import re
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest
from telethon.tl.types import InputPeerEmpty
from telethon.tl.types import PeerChannel
from telethon.errors import ChannelPrivateError
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.tl.types import Message
from telethon.tl.types import MessageService
from telethon.errors.rpcerrorlist import MessageIdInvalidError
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from save_restrictor import fetch_and_forward

with open("config.json") as f:
    CONFIG = json.load(f)

TELETHON_CLIENT = TelegramClient("anon", CONFIG["api_id"], CONFIG["api_hash"])
BOT_OWNER = int(CONFIG.get("admin", 0))
channel_choices = []
current_setting_command = None

async def get_joined_channels():
    await TELETHON_CLIENT.connect()
    result = await TELETHON_CLIENT(GetDialogsRequest(
        offset_date=None, offset_id=0, offset_peer=InputPeerEmpty(), limit=100, hash=0
    ))
    channels = [dialog.entity for dialog in result.dialogs if hasattr(dialog.entity, 'megagroup') or hasattr(dialog.entity, 'broadcast')]
    return channels

async def check_forward_restricted(channel):
    try:
        history = await TELETHON_CLIENT(GetHistoryRequest(peer=channel, limit=1, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
        if not history.messages:
            return True
        message = history.messages[0]
        return not getattr(message, 'forward', None)
    except ChannelPrivateError:
        return True

async def handle_channel_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_setting_command
    text = update.message.text
    channel = next((c for c in channel_choices if c.title == text), None)
    if not channel:
        await update.message.reply_text("Invalid selection. Try again.")
        return

    restricted = await check_forward_restricted(channel)

    CONFIG[current_setting_command] = channel.id
    with open("config.json", "w") as f:
        json.dump(CONFIG, f, indent=2)

    await update.message.reply_text(f"✅ {current_setting_command} set to '{channel.title}'. Forward-Restricted: {'Yes' if restricted else 'No'}")

    current_setting_command = None

async def set_channel(update: Update, context: ContextTypes.DEFAULT_TYPE, key):
    global channel_choices, current_setting_command
    if update.effective_user.id != BOT_OWNER:
        return
    current_setting_command = key
    channel_choices = await get_joined_channels()
    button_list = [[ch.title] for ch in channel_choices]
    await update.message.reply_text(
        f"Choose a channel to set as {key}:",
        reply_markup=ReplyKeyboardMarkup(button_list, one_time_keyboard=True, resize_keyboard=True)
    )

async def set_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_channel(update, context, "source_channel")

async def set_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_channel(update, context, "target_channel")

async def set_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_channel(update, context, "log_channel")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /save <id> or /save <start>-<end>. Use /help for all commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
/start - Start Bot
/save <msg_id> or <start>-<end> - Save messages from source
/set_source - Set Source Channel
/set_target - Set Target Channel
/set_log - Set Log Channel
/log_toggle - Toggle logging
/help - Show this help
    """)

async def log_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CONFIG["logging"] = not CONFIG.get("logging", False)
    with open("config.json", "w") as f:
        json.dump(CONFIG, f, indent=2)
    await update.message.reply_text(f"Logging is now {'enabled' if CONFIG['logging'] else 'disabled'}.")

async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != BOT_OWNER:
        return
    if not context.args:
        await update.message.reply_text("Usage: /save <msg_id> or /save <start>-<end>")
        return

    arg = context.args[0]
    match = re.match(r"(\d+)-(\d+)", arg)
    if match:
        start, end = int(match[1]), int(match[2])
        for msg_id in range(start, end + 1):
            try:
                await fetch_and_forward(msg_id)
                await update.message.reply_text(f"✅ Saved message ID {msg_id}")
            except MessageIdInvalidError:
                await update.message.reply_text(f"❌ Invalid message ID: {msg_id}")
    else:
        try:
            msg_id = int(arg)
            await fetch_and_forward(msg_id)
            await update.message.reply_text(f"✅ Saved message ID {msg_id}")
        except ValueError:
            await update.message.reply_text("Invalid message ID format.")

async def main():
    app = Application.builder().token(CONFIG["bot_token"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("set_source", set_source))
    app.add_handler(CommandHandler("set_target", set_target))
    app.add_handler(CommandHandler("set_log", set_log))
    app.add_handler(CommandHandler("log_toggle", log_toggle))
    app.add_handler(CommandHandler("save", save))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_channel_selection))

    await app.initialize()
    await TELETHON_CLIENT.start(phone=CONFIG["phone_number"])
    await app.start()
    print("Bot is running...")
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == '__main__':
    asyncio.run(main())
