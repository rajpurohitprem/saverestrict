import json
import os

CONFIG_FILE = "config.json"

# Load config from config.json
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        CONFIG = json.load(f)
else:
    CONFIG = {
        "api_id": 12345,
        "api_hash": "your_api_hash",
        "bot_token": "your_bot_token",
        "phone_number": "+910000000000",
        "source_channel": "",
        "log_channel": "",
        "admin_id": 123456789,
        "allowed_users": [],
        "logging_enabled": True
    }

# Save config back to config.json
def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)
