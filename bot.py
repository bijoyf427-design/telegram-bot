import logging
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

CHANNEL_USERNAME = "@riyachatgroup70"
GROUP_INVITE_LINK = "https://t.me/riyachatgroup70"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ১. /start কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
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

# ৩. /help কমান্ড
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
        "/antilink — Link filter\n"
        "/antiforward — Forward filter\n\n"
        "╔══════════════════════════╗\n"
        "  👑 **Admin Control**\n"
        "╚══════════════════════════╝\n"
        "/promote — Make admin\n"
        "/demote — Remove admin\n"
        "/kickme — Leave group"
    )
    if update.effective_chat.type == "private":
        await update.message.reply_text(help_text, parse_mode="Markdown")
    else:
        await update.message.reply_text("Help menu sent to your private chat! 🌸")

# ৪. গ্রুপ মেসেজ ও স্মার্ট চ্যাট রেসপন্স হ্যান্ডলার (এখানে কোনো ফালতু ওয়েলকাম মেসেজ বা হেসেল নেই)
async def group_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    chat = update.effective_chat
    message = update.message
    message_text = message.text
    text_lower = message_text.lower()

    if chat.type in ["group", "supergroup"]:
        # ক) লিংক বা ফরোয়ার্ড চেক করে ডিলিট করা
        is_forwarded = bool(message.forward_origin or message.forward_from or message.forward_from_chat)
        has_link = "http://" in text_lower or "https://" in text_lower or "t.me/" in text_lower or "www." in text_lower

        if is_forwarded or has_link:
            try:
                await message.delete()
                await chat.send_message("Links and forwards are not allowed here! 🚫")
                return
            except:
                pass

        # খ) গ্রুপে কেউ কমান্ড ছাড়া হাই, হ্যালো বা যেকোনো সাধারণ টেক্সট দিলে স্মার্ট চ্যাট রিপ্লাই করবে
        if not message_text.startswith('/'):
            fun_replies = [
                "Haan bolo 🥰 What's up?",
                "Arre kya ho raha hai? 😆",
                "Bolo jaan, listening! ✨ 🙈",
                "Hieeee! How are you? 🌺 🤭",
                "Haha, what are you saying? 🐒💬",
                "Hu... tell me something nice! 🐵💕",
                "Hey there! Got your message 😊"
            ]
            await message.reply_text(random.choice(fun_replies))
            return

# ৫. মডারেশন কমান্ডস (/kick, /ban, /mute, /purge)
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
    
    # হ্যান্ডলারগুলো রেজিস্টার করা হচ্ছে
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.add_handler(CommandHandler('kick', kick_user))
    application.add_handler(CommandHandler('ban', ban_user))
    application.add_handler(CommandHandler('mute', mute_user))
    application.add_handler(CommandHandler('purge', purge_messages))
    
    # গ্রুপের সাধারণ টেক্সট মেসেজ হ্যান্ডলার
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), group_message_handler))
    
    print("Bot is running successfully...")
    application.run_polling()
