import json
import os
from telethon.sync import TelegramClient
from telethon.tl.types import Channel, Chat, User

CONFIG_FILE = "config.json"

def ask(msg, cast=str, default=None):
    val = input(f"{msg}{' [' + str(default) + ']' if default else ''}: ").strip()
    return cast(val) if val else default

def choose_channel(channels, prompt):
    print(f"\n📡 {prompt}")
    for i, ch in enumerate(channels):
        print(f"{i+1}. {ch.title} ({ch.username or 'private'})")
    while True:
        try:
            idx = int(input("Choose channel number (or 0 to skip): "))
            if idx == 0:
                return None
            return channels[idx-1]
        except (ValueError, IndexError):
            print("❌ Invalid selection. Try again.")

def main():
    print("🛠  Telegram Config Setup")

    api_id = int(ask("Enter your API ID"))
    api_hash = ask("Enter your API Hash")
    phone = ask("Enter your phone number (+91...)")
    bot_token = ask("Enter your Bot Token")

    session = "anon"
    client = TelegramClient(session, api_id, api_hash)
    client.start(phone=phone)
    
    dialogs = client.get_dialogs()
    channels = [d.entity for d in dialogs if isinstance(d.entity, Channel) and getattr(d.entity, 'megagroup', False) == False]

    source = choose_channel(channels, "Select Source Channel (restricted)")
    log = choose_channel(channels, "Select Log Channel (optional)")

    admin_id = client.get_me().id

    config = {
        "api_id": api_id,
        "api_hash": api_hash,
        "bot_token": bot_token,
        "phone_number": phone,
        "source_channel": source.username if source.username else source.id,
        "log_channel": log.username if log else None,
        "admin_id": admin_id,
        "logging_enabled": True
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Saved to {CONFIG_FILE}")
    client.disconnect()

if __name__ == "__main__":
    main()
