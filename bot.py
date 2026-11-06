import logging
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

CHANNEL_USERNAME = "@riyachatgroup70"
GROUP_INVITE_LINK = "https://t.me/riyachatgroup70"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ১. /start কমান্ড এবং দুটি বাটন (সম্পূর্ণ ইংরেজিতে)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        keyboard = [[InlineKeyboardButton("➕ Add Me To Group 🥰", url=f"https://t.me/{context.bot.username}?startgroup=true")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Hey REDME! 🎉 Bot is active here!", reply_markup=reply_markup)
        return

    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=GROUP_INVITE_LINK)],
        [InlineKeyboardButton("✅ Verify Membership", callback_data="check_join")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome! Please join our channel first, then click on 'Verify Membership' below. 😊",
        reply_markup=reply_markup
    )

# ২. ভেরিফাই বাটন হ্যান্ডলার এবং চ্যানেল চেক (কেউ চ্যানেল ছাড়লে কাজ করবে না)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_join":
        user_id = query.from_user.id
        try:
            # চেক করা ইউজার চ্যানেলে আছে কি না
            member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            if member.status in ['member', 'administrator', 'creator']:
                keyboard = [
                    [InlineKeyboardButton("➕ Add Riya to Group 🥰", url=f"https://t.me/{context.bot.username}?startgroup=true")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    "🎉 Verification Successful!\n\nYou are now verified. Click the button below to add me to your group! 💖",
                    reply_markup=reply_markup
                )
            else:
                await query.answer("❌ You have not joined the channel yet! Please join first.", show_alert=True)
        except Exception as e:
            await query.answer("❌ Error checking membership! Make sure you joined the channel.", show_alert=True)

# ৩. গ্রুপে বট অ্যাড হলে ওয়েলকাম মেসেজ (ইংলিশে)
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text(
                "👀 Hi REDME!\n\n"
                "💖 Thanks for adding me to this chat!\n"
                "💖 I got Full Admin Permission – group protection is ready!\n"
                "💖 Type /help to see all commands."
            )
        else:
            await update.message.reply_text(f"Hey there {member.first_name} 💖, and welcome to Riya Chat group! How are you? 😊")

# ৪. /help কমান্ড (ইংলিশ মেনু)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌸 **Riya Bot – Help Menu**\n\n"
        "👮 **Moderation:** /kick, /ban, /mute, /purge\n"
        "⚙️ **Protection:** Antilink & Antiforward Active\n"
        "🎮 **Games:** /rob, /daily, /bal, /top"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ৫. মূল মেসেজ, অ্যান্টি-লিংক, অ্যান্টি-ফরোয়ার্ড এবং স্মার্ট ইমোজি চ্যাট রিপ্লাই
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
        
    chat = update.effective_chat
    message = update.message
    user = update.effective_user

    if chat.type != "private":
        # ক) চ্যানেল লিভ করেছে কি না চেক করা (যদি ইউজার চ্যানেল থেকে বের হয়ে যায় তবে গ্রুপে কাজ করবে না)
        try:
            member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)
            if member.status not in ['member', 'administrator', 'creator']:
                return # চ্যানেল থেকে বের হয়ে গেলে বট কোনো রেসপন্স বা কাজ করবে না
        except:
            pass

        # খ) ফরোয়ার্ড এবং লিংক চেক করে ডিলিট করা
        is_forwarded = bool(message.forward_origin or message.forward_from or message.forward_from_chat)
        message_text = message.text or message.caption or ""
        text_lower = message_text.lower()
        has_link = "http://" in text_lower or "https://" in text_lower or "t.me/" in text_lower or "www." in text_lower

        if is_forwarded or has_link:
            try:
                await message.delete()
                try:
                    await chat.send_voice(voice=open("voice.ogg", 'rb'))
                except:
                    await chat.send_message("Hey! Links and forwards are not allowed here! 🚫")
                return
            except:
                pass

        # গ) বটকে ট্যাগ, রিপ্লাই বা যেকোনো উল্টাপাল্টা মেসেজ দিলে ইমোজিসহ স্মার্ট রিপ্লাই
        bot_username = context.bot.username.lower()
        is_mentioned = f"@{bot_username}" in text_lower
        is_replied = message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id

        if is_mentioned or is_replied or not message.text.startswith('/'):
            fun_replies = [
                "Haan bolo 🥰",
                "Arre kya ho raha hai? 😆 What do you want to say?",
                "Bolo jaan, listening! ✨ 🙈",
                "Hieeee 🌺 🤭",
                "What are you typing? Haha! 🐒💬",
                "Hu... what's up? 🐵💕"
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
            await update.message.reply_text("Please make me an admin with proper permissions!")

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
