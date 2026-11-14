import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import google.generativeai as genai

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Credentials from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini AI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-pro")
else:
    gemini_model = None

# Group Link for Join Button
GROUP_LINK = "https://t.me/Random_Talks_Club"

# /start command with professional look & buttons
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("👥 Group Join Karo", url=GROUP_LINK)],
        [InlineKeyboardButton("✅ Maine Join Kar Liya", callback_data="verify_join")],
        [InlineKeyboardButton("➕ Add to Group 🤤", url=f"https://t.me/{context.bot.username}?startgroup=true")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"Ek kaam karo – group join karo, phir seedha aa jao mere paas 😎\n\n"
        f"Welcome **{user_name}**! 🥰 Ab kuch bolo na"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# Verification Popup Callback (Alert Box)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "verify_join":
        # Shows a popup alert box like the screenshot
        await query.answer("✅ Verify ho gaya! Ab baat karo 😘", show_alert=True)
        
        user_name = query.from_user.first_name
        keyboard = [
            [InlineKeyboardButton("➕ Add to Group 🤤", url=f"https://t.me/{context.bot.username}?startgroup=true")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        success_text = f"Welcome **{user_name}**! 🥰 Ab kuch bolo na"
        await query.message.reply_text(success_text, reply_markup=reply_markup, parse_mode="Markdown")

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌸 **Riya Bot - Full Help Menu**\n\n"
        "👮 **Moderation Commands:**\n"
        "• /kick - Kisi ko group se nikalo (Reply to user)\n"
        "• /ban - Permanent ban karo\n"
        "• /mute - Chup karao\n"
        "• /unmute - Awaaz wapas do\n"
        "• /warn - Warning do\n"
        "• /pin - Message pin karo\n\n"
        "🛡️ **Protection & Settings:**\n"
        "• /antilink - Link auto-delete protection\n"
        "• /antifoward - Forwarded msgs auto-delete\n"
        "• /purge - Bulk message delete\n\n"
        "👑 **Admin & Fun:**\n"
        "• /promote - Admin bana do\n"
        "• /demote - Admin rights lo wapas\n"
        "• /id - Telegram ID dekho\n"
        "• /rob - Economy game & coins steal\n\n"
        "🤖 **To chat with me using AI, just reply to my message or mention me!**"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# /kick command
async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a message to kick the user!")
        return
    
    chat_id = update.effective_chat.id
    user_to_kick = update.message.reply_to_message.from_user.id
    try:
        await context.bot.ban_chat_member(chat_id, user_to_kick)
        await context.bot.unban_chat_member(chat_id, user_to_kick)
        await update.message.reply_text("👢 Kicked successfully!")
    except Exception:
        await update.message.reply_text("❌ Failed to kick: Admin permission missing!")

# /rob command simulation
async def rob_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use: /rob <amount> (REPLY To Someone, OR /rob <amount> <username>)")

# AI Chat & Message Handler (Typing action + Gemini Response)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    text = message.text
    is_private = update.effective_chat.type == "private"
    is_replied = message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id
    is_mentioned = context.bot.username in text

    # Respond if it's private chat, or bot is replied/mentioned in group
    if is_private or is_replied or is_mentioned:
        if not gemini_model:
            await message.reply_text("AI is not configured properly.")
            return
        
        try:
            # Show typing status
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            response = gemini_model.generate_content(text)
            reply_text = response.text if response and response.text > "" else "Hlloww 🙈 Phir batao kya chal raha hai?"
            await message.reply_text(reply_text)
        except Exception as e:
            logger.error(f"Gemini Error: {e}")
            await message.reply_text("Acha ji! Thoda busy hu, thode der baad baat karte hain! 😉")

def main():
    if not TOKEN:
        logger.error("No token provided!")
        return

    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("kick", kick_command))
    application.add_handler(CommandHandler("rob", rob_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Message handler for text and AI conversation
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
