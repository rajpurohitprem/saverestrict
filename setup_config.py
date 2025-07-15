import json
import os

CONFIG_FILE = "config.json"

config = {}

print("\n🔧 Telegram API Configuration")
config["api_id"] = int(input("API ID: "))
config["api_hash"] = input("API Hash: ")
config["phone_number"] = input("Phone Number (+91...): ")
config["bot_token"] = input("Bot Token: ")

print("\n✅ Saved basic configuration")

# Optional fields (can be set from Telegram bot too)
config["source_channel"] = ""
config["target_channel"] = ""
config["log_channel"] = ""
config["admin_id"] = int(input("Admin Telegram ID: "))
config["logging_enabled"] = True

with open(CONFIG_FILE, "w") as f:
    json.dump(config, f, indent=2)

print("\n✅ Configuration saved to config.json")
