import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from save_restrictor import fetch_and_forward

# Load config
with open("config.json") as f:
    CONFIG = json.load(f)

BOT_TOKEN = CONFIG["bot_token"]
ADMIN_ID = int(CONFIG["admin_id"])

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Access denied.")
    await update.message.reply_text("👋 Welcome to Save Restrict Bot.\nUse /help for commands.")

# Command: /help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Access denied.")
    await update.message.reply_text(
        "📚 Commands:\n"
        "/save <msg_id> - Save restricted message\n"
        "/set_source - Set source channel\n"
        "/set_target - Set target channel\n"
        "/set_log - Set log channel\n"
        "/log_toggle - Toggle logging\n"
        "/stop - (manual)\n"
    )

# Command: /save
async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Access denied.")
    if len(context.args) != 1 or not context.args[0].isdigit():
        return await update.message.reply_text("Usage: /save <msg_id>")
    
    msg_id = int(context.args[0])
    await update.message.reply_text("⏳ Saving...")

    result = await fetch_and_forward(msg_id)
    await update.message.reply_text(result or "✅ Done")

# Setup app
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("save", save))

print("🤖 Bot running...")
app.run_polling()
