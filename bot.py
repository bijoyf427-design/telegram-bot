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
        await update.message.reply_text("Hi REDME! Bot is active here! 🎉", reply_markup=reply_markup)
        return

    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=GROUP_INVITE_LINK)],
        [InlineKeyboardButton("✅ Verify Membership", callback_data="check_join")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Please join our channel first, then click 'Verify Membership' below! 😊",
        reply_markup=reply_markup
    )

# ২. ভেরিফাই বাটন হ্যান্ডলার
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_join":
        user_id = query.from_user.id
        try:
            member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            if member.status in ['member', 'administrator', 'creator']:
                keyboard = [
                    [InlineKeyboardButton("➕ Add Me to Group 🥰", url=f"https://t.me/{context.bot.username}?startgroup=true")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.edit_text(
                    "✅ Verification Successful! Now you can add me to your group.",
                    reply_markup=reply_markup
                )
            else:
                await query.answer("❌ You have not joined the channel yet!", show_alert=True)
        except Exception as e:
            keyboard = [
                [InlineKeyboardButton("➕ Add Me to Group 🥰", url=f"https://t.me/{context.bot.username}?startgroup=true")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(
                "✅ Verification Successful! Click below to add me to your group.",
                reply_markup=reply_markup
            )

# ৩. গ্রুপে বট অ্যাড হলে ওয়েলকাম মেসেজ
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text(
                "👀 Hi REDME!\n\n"
                "💖 Thanks for adding me to this chat!\n"
                "💖 I got Full Admin Permission – group protection is ready!\n"
                "💖 Type /help to see all commands."
            )

# ৪. /help কমান্ড
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌸 **Riya Bot — Help Menu**\n\n"
        "╔══════════════════════════╗\n"
        "  👮 **Moderation Commands**\n"
        "╚══════════════════════════╝\n"
        "/kick — Kick a user\n"
        "/ban — Ban a user\n"
        "/mute — Mute a user\n"
        "/unmute — Unmute a user\n\n"
        "╔══════════════════════════╗\n"
        "  🗑 **Cleanup Commands**\n"
        "╚══════════════════════════╝\n"
        "/purge — Delete messages\n"
        "/cleanbot — Clean bot messages\n\n"
        "╔══════════════════════════╗\n"
        "  ⚙️ **Group Settings**\n"
        "╚══════════════════════════╝\n"
        "/antilink on/off — Link filter\n"
        "/antiforward on/off — Forward filter\n\n"
        "╔══════════════════════════╗\n"
        "  👑 **Admin Control**\n"
        "╚══════════════════════════╝\n"
        "/promote — Make admin\n"
        "/demote — Remove admin\n"
        "/kickme — Leave group"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ৫. গ্রুপ চ্যাট হ্যান্ডলার (হাই, হ্যালো বা উল্টাপাল্টা মেসেজে চ্যাট রিপ্লাই এবং লিংক ডিলিট)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    chat = update.effective_chat
    message = update.message
    text_lower = message.text.lower()

    if chat.type != "private":
        # ক) লিংক বা ফরোয়ার্ড চেক
        is_forwarded = bool(message.forward_origin or message.forward_from or message.forward_from_chat)
        has_link = "http://" in text_lower or "https://" in text_lower or "t.me://" in text_lower or "www." in text_lower

        if is_forwarded or has_link:
            try:
                await message.delete()
                await chat.send_message("Links and forwards are not allowed here! 🚫")
                return
            except:
                pass

        # খ) গ্রুপে কেউ হাই, হ্যালো বা উল্টাপাল্টা মেসেজ দিলে ইমোজিসহ চ্যাট রিপ্লাই
        if not message.text.startswith('/'):
            fun_replies = [
                "Heyy there! 😊",
                "Haan bolo 🥰 What's up?",
                "Arre kya ho raha hai? 😆",
                "Bolo jaan, listening! ✨ 🙈",
                "Hieeee! How are you? 🌺 🤭",
                "Haha, what are you saying? 🐒💬"
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
