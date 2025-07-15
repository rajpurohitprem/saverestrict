import asyncio import json import os from telethon import TelegramClient, events from telethon.tl.types import PeerChannel from save_restrictor import ( fetch_and_forward, CONFIG, load_config, save_config, get_channel_list, get_entity_by_id )

Load config

load_config()

bot = TelegramClient('bot', CONFIG['api_id'], CONFIG['api_hash']).start(bot_token=CONFIG['bot_token']) user_client = TelegramClient('anon', CONFIG['api_id'], CONFIG['api_hash'])

async def start_user_client(): await user_client.start(phone=CONFIG['phone'])

@bot.on(events.NewMessage(pattern='/start')) async def start(event): if event.sender_id != CONFIG['admin_id']: return await event.reply("✅ Bot is running!\nCommands:\n/set_source <id>\n/set_target <id>\n/set_log <id>\n/log_toggle\n/save <start_id>-<end_id>")

@bot.on(events.NewMessage(pattern='/set_source')) async def set_source(event): if event.sender_id != CONFIG['admin_id']: return try: parts = event.raw_text.split() if len(parts) == 2: channel_id = int(parts[1]) entity = await get_entity_by_id(user_client, channel_id) if entity: CONFIG['source_channel'] = channel_id save_config() await event.reply("✅ Source channel set.") else: await event.reply("❌ Could not find source channel.") else: await event.reply("❌ Usage: /set_source <channel_id>") except Exception as e: await event.reply(f"❌ Error: {e}")

@bot.on(events.NewMessage(pattern='/set_target')) async def set_target(event): if event.sender_id != CONFIG['admin_id']: return try: parts = event.raw_text.split() if len(parts) == 2: channel_id = int(parts[1]) entity = await get_entity_by_id(user_client, channel_id) if entity: CONFIG['target_channel'] = channel_id save_config() await event.reply("✅ Target channel set.") else: await event.reply("❌ Could not find target channel.") else: await event.reply("❌ Usage: /set_target <channel_id>") except Exception as e: await event.reply(f"❌ Error: {e}")

@bot.on(events.NewMessage(pattern='/set_log')) async def set_log(event): if event.sender_id != CONFIG['admin_id']: return try: parts = event.raw_text.split() if len(parts) == 2: channel_id = int(parts[1]) entity = await get_entity_by_id(user_client, channel_id) if entity: CONFIG['log_channel'] = channel_id save_config() await event.reply("✅ Log channel set.") else: await event.reply("❌ Could not find log channel.") else: await event.reply("❌ Usage: /set_log <channel_id>") except Exception as e: await event.reply(f"❌ Error: {e}")

@bot.on(events.NewMessage(pattern='/log_toggle')) async def toggle_log(event): if event.sender_id != CONFIG['admin_id']: return CONFIG['log_enabled'] = not CONFIG.get('log_enabled', False) save_config() await event.reply(f"📝 Logging is now {'enabled' if CONFIG['log_enabled'] else 'disabled'}.")

@bot.on(events.NewMessage(pattern='/save')) async def save(event): if event.sender_id != CONFIG['admin_id']: return try: parts = event.raw_text.split() if len(parts) == 2 and '-' in parts[1]: start_id, end_id = map(int, parts[1].split('-')) result = await fetch_and_forward(start_id, end_id, bot) await event.reply(f"✅ Done. {result} messages sent.") else: await event.reply("❌ Usage: /save <start_id>-<end_id>") except Exception as e: await event.reply(f"❌ Error: {e}")

async def main(): await start_user_client() print("✅ User client started.") await bot.run_until_disconnected()

if name == 'main': asyncio.get_event_loop().run_until_complete(main())

