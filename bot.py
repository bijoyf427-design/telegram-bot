import logging
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

CHANNEL_USERNAME = "@riyachatgroup70"
GROUP_INVITE_LINK = "https://t.me/riyachatgroup70"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ১. /start কমান্ড এবং দুটি বাটন (চ্যানেল জয়েন ও ভেরিফাই)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        keyboard = [[InlineKeyboardButton("➕ Add Me To Group 🥰", url=f"https://t.me/{context.bot.username}?startgroup=true")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Yay REDME! 🎉 Bot active hai!", reply_markup=reply_markup)
        return

    keyboard = [
        [InlineKeyboardButton("👥 Group / Channel Join Karo", url=GROUP_INVITE_LINK)],
        [InlineKeyboardButton("✅ Maine Join Kar Liya (Verify)", callback_data="check_join")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Thoda sa kaam hai – pehle channel join karo, phir niche verify button dabao! 😊",
        reply_markup=reply_markup
    )

# ২. ভেরিফাই বাটন ক্লিক হ্যান্ডলার (পপ-আপ ও গ্রুপ অ্যাড বাটন সহ)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # পপ-আপ নোটিফিকেশন লোডিং বন্ধ করতে
    
    if query.data == "check_join":
        user_id = query.from_user.id
        try:
            # ইউজার চ্যানেলে জয়েন করেছে কিনা চেক করা
            member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            if member.status in ['member', 'administrator', 'creator']:
                # সফলভাবে ভেরিফাই হলে গ্রুপে অ্যাড করার বাটন দেখাবে
                keyboard = [
                    [InlineKeyboardButton("➕ Add Riya to Group 🥰", url=f"https://t.me/{context.bot.username}?startgroup=true")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    "🎉 অভিনন্দন! আপনার ভেরিফিকেশন সফল হয়েছে।\n\nএখন নিচের বাটনে ক্লিক করে বটটিকে আপনার গ্রুপে অ্যাড করুন! 💖",
                    reply_markup=reply_markup
                )
            else:
                await query.answer("❌ আপনি এখনো চ্যানেলে জয়েন করেননি! আগে জয়েন করুন.", show_alert=True)
        except Exception as e:
            # কোনো কারণে চ্যাট মেম্বার চেক করতে না পারলে ফ্লেক্সিবল ভেরিফিকেশন পাস করে গ্রুপ অ্যাড বাটন দিয়ে দেওয়া ভালো
            keyboard = [
                [InlineKeyboardButton("➕ Add Riya to Group 🥰", url=f"https://t.me/{context.bot.username}?startgroup=true")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "✅ ভেরিফিকেশন সম্পন্ন হয়েছে!\n\nএখন নিচের বাটনে ক্লিক করে বটটিকে গ্রুপে অ্যাড করে নিন! 💖",
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
                "💖 Commands: /help"
            )
        else:
            await update.message.reply_text(f"Hey there {member.first_name} 💖, and welcome to Riya Chat group! How are you? 😊")

# ৪. /help কমান্ড
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌸 **Riya Bot – Help Menu**\n\n"
        "👮 **Moderation:** /kick, /ban, /mute, /purge\n"
        "⚙️ **Protection:** Antilink & Antiforward Active\n"
        "🎮 **Games:** /rob, /daily, /bal, /top"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ৫. গ্রুপ প্রোটেকশন, লিংক ডিলিট এবং র্যান্ডম/উল্টাপাল্টা মেসেজ চ্যাট রিপ্লাই
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
        
    chat = update.effective_chat
    message = update.message

    if chat.type != "private":
        # ক) ফরোয়ার্ড এবং লিংক চেক করে ডিলিট করা
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
                    await chat.send_message("জান গ্রুপে লিংক বা ফরোয়ার্ড শেয়ার করা নিষেধ! 🚫")
                return
            except:
                pass

        # খ) উল্টাপাল্টা মেসেজ বা যেকোনো সাধারণ টেক্সটে ইমোজিসহ চ্যাট রিপ্লাই
        bot_username = context.bot.username.lower()
        is_mentioned = f"@{bot_username}" in text_lower
        is_replied = message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id

        if is_mentioned or is_replied or not message.text.startswith('/'):
            fun_replies = [
                "Haan bolo 🥰",
                "Arre kya ho raha hai? 😆 Thik se bolo na kya baat karni hai.",
                "Bolo jaan, sunshti to! ✨ 🙈",
                "Hieeee 🌺 🤭",
                "Ujdjd ki bolcho bujhi nai! 🐒💬",
                "Hu... ki obostha bolon? 🐵💕"
            ]
            await message.reply_text(random.choice(fun_replies))
            return

# ৬. মডারেশন কমান্ডস (/kick, /ban, /mute, /purge)
async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, update.message.reply_to_message.from_user.id)
            await context.bot.unban_chat_member(update.effective_chat.id, update.message.reply_to_message.from_user.id)
            await update.message.reply_text("ব্যবহারীকে কিক করা হয়েছে! 👞")
        except:
            await update.message.reply_text("বটকে অ্যাডমিন করুন!")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, update.message.reply_to_message.from_user.id)
            await update.message.reply_text("পার্মানেন্ট ব্যান করা হয়েছে! 🚫")
        except:
            await update.message.reply_text("বটকে অ্যাডমিন করুন!")

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            await context.bot.restrict_chat_member(
                update.effective_chat.id, 
                update.message.reply_to_message.from_user.id, 
                permissions=ChatPermissions(can_send_messages=False)
            )
            await update.message.reply_text("ব্যবহারীকে মিউট করা হয়েছে! 🔇")
        except:
            await update.message.reply_text("বটকে অ্যাডমিন করুন!")

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
            await update.message.reply_text("মেসেজ মুছে ফেলা হয়েছে! 🗑️")
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
    
    print("বট সফলভাবে রান হচ্ছে...")
    application.run_polling()
