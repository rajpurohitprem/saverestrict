import json
import os

CONFIG_PATH = "config.json"

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError("config.json not found. Run setup_config.py first.")

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)
