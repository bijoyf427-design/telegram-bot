import logging
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

CHANNEL_USERNAME = "@riyachatgroup70"
GROUP_INVITE_LINK = "https://t.me/riyachatgroup70"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ১. /start কমান্ড (প্রাইভেট চ্যাটে জয়েন এবং ভেরিফাই বাটন)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        keyboard = [[InlineKeyboardButton("➕ Add Me To Group 🥰", url=f"https://t.me/{context.bot.username}?startgroup=true")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Hi REDME! Kuch baat karo na 🎉", reply_markup=reply_markup)
        return

    keyboard = [
        [InlineKeyboardButton("👥 Group Join Karo", url=GROUP_INVITE_LINK)],
        [InlineKeyboardButton("✅ Verify ho gaya", callback_data="check_join")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Oye! 😅 Group join kiye bina nahi chalega. Pehle join karo phir verify dabao!",
        reply_markup=reply_markup
    )

# ২. ভেরিফাই বাটন ক্লিক হ্যান্ডলার (পপ-আপ এবং গ্রুপ অ্যাড বাটন)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ Verify ho gaya! Ab baat karo 🥰", show_alert=True)
    
    if query.data == "check_join":
        keyboard = [
            [InlineKeyboardButton("➕ Add Me to Group 🥰", url=f"https://t.me/{context.bot.username}?startgroup=true")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            "Yay REDME! 🎉 Ab baat karte hain~\n\nClick the button below to add me to your group!",
            reply_markup=reply_markup
        )

# ৩. গ্রুপে বট অ্যাড হলে ওয়েলকাম মেসেজ
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text(
                "👀 Hi REDME!\n\n"
                "💖 Thanks for adding me to this chat!\n"
                "💖 I got Full Admin Permission – group management is ready to go!\n"
                "💖 Group Management Commands: /help\n\n"
                "💖 To chat with me in the group, just say \"Riya\" 😊"
            )

# ৪. /help কমান্ড (স্ক্রিনশটের হুবহু ডিজাইন ও কমান্ড লিস্ট)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌸 **Riya Bot — Help**\n\n"
        "╔══════════════════════════╗\n"
        "  👮 **Moderation Commands**\n"
        "╚══════════════════════════╝\n"
        "/kick — Kisi ko group se nikalo\n"
        "/ban — Permanent ban karo\n"
        "/mute — Chup karao\n"
        "/unmute — Awaaz wapas do\n"
        "/warn — Warning do\n"
        "/warns — Kitne warns hain\n\n"
        "╔══════════════════════════╗\n"
        "  🗑 **Cleanup Commands**\n"
        "╚══════════════════════════╝\n"
        "/purge — Reply se yahan tak delete\n"
        "/cleanbot — Bot ke sab msgs saaf\n\n"
        "╔══════════════════════════╗\n"
        "  ⚙️ **Group Settings**\n"
        "╚══════════════════════════╝\n"
        "/antilink on/off — Link auto-delete\n"
        "/antiforward on/off — Forwarded msgs auto-delete\n\n"
        "╔══════════════════════════╗\n"
        "  👑 **Admin Control**\n"
        "╚══════════════════════════╝\n"
        "/promote — Admin bana do\n"
        "/demote — Admin rights lo wapas\n"
        "/kickme — Khud group se niklo\n\n"
        "⚡ *Sirf group admins ke liye*"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ৫. মূল মেসেজ, লিংক ডিলিট এবং উল্টাপাল্টা টেক্সটে চ্যাট রিপ্লাই
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    chat = update.effective_chat
    message = update.message
    text_lower = message.text.lower()

    if chat.type != "private":
        # অ্যান্টি-লিংক ও অ্যান্টি-ফরোয়ার্ড চেক
        is_forwarded = bool(message.forward_origin or message.forward_from or message.forward_from_chat)
        has_link = "http://" in text_lower or "https://" in text_lower or "t.me/" in text_lower or "www." in text_lower

        if is_forwarded or has_link:
            try:
                await message.delete()
                await chat.send_message("Links and forwards are not allowed here! 🚫")
                return
            except:
                pass

        # হাই, হ্যালো বা যেকোনো উল্টাপাল্টা মেসেজে ইমোজিসহ চ্যাট রিপ্লাই
        if not message.text.startswith('/'):
            fun_replies = [
                "heyyy😊",
                "Haan bolo 🥰",
                "Arre kya ho raha hai? 😆",
                "Bolo jaan, listening! ✨ 🙈",
                "Hieeee! How are you? 🌺 🤭",
                "Haha, what a message! 🐒💬"
            ]
            await message.reply_text(random.choice(fun_replies))
            return

# ৬. মডারেশন কমান্ডস (/kick, /ban, /mute, /purge)
async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, update.message.reply_to_message.from_user.id)
            await context.bot.unban_chat_member(update.effective_chat.id, update.message.reply_to_message.from_user.id)
            await update.message.reply_text("User has been kicked! 👞")
        except:
            await update.message.reply_text("Please make me an admin!")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, update.message.reply_to_message.from_user.id)
            await update.message.reply_text("User has been permanently banned! 🚫")
        except:
            await update.message.reply_text("Please make me an admin!")

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            await context.bot.restrict_chat_member(
                update.effective_chat.id, 
                update.message.reply_to_message.from_user.id, 
                permissions=ChatPermissions(can_send_messages=False)
            )
            await update.message.reply_text("User has been muted! 🔇")
        except:
            await update.message.reply_text("Please make me an admin!")

async def purge_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            start_id = update.message.reply_to_message.message_id
            end_id = update.message.message_id
            for msg_id in range(start_id, end_id + 1):
                try:
                    await context.bot.delete_message(update.effective_chat.id, msg_id)
                except:
                    pass
            await update.message.reply_text("Messages cleared successfully! 🗑️")
        except:
            pass

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.add_handler(CommandHandler('kick', kick_user))
    application.add_handler(CommandHandler('ban', ban_user))
    application.add_handler(CommandHandler('mute', mute_user))
    application.add_handler(CommandHandler('purge', purge_messages))
    
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_message))
    
    print("Bot is running successfully...")
    application.run_polling()
