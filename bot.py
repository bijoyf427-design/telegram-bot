import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# আপনার চ্যানেলের ইউজারনেম এবং গ্রুপের ইনভাইট লিংক
CHANNEL_USERNAME = "@riyachatgroup70"
GROUP_INVITE_LINK = "https://t.me/riyachatgroup70"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ১. /start কমান্ড: ছবি বা ওয়েলকাম টেক্সট এবং ভেরিফিকেশন বাটন
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        keyboard = [[InlineKeyboardButton("➕ Add Me To Group 🥰", url=f"https://t.me/{context.bot.username}?startgroup=true")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Yay REDME! 🎉 Bot active hai!", reply_markup=reply_markup)
        return

    keyboard = [
        [InlineKeyboardButton("👥 Group Join Karo", url=GROUP_INVITE_LINK)],
        [InlineKeyboardButton("✅ Maine Join Kar Liya", callback_data="check_join")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Thoda sa kaam hai – group join karo, phir masti karte hain 😊",
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
                keyboard = [[InlineKeyboardButton("➕ Add Me To Group 🥰", url=f"https://t.me/{context.bot.username}?startgroup=true")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.edit_text(
                    "Aa gaye finally REDME! 🥰 Kya haal hai?",
                    reply_markup=reply_markup
                )
            else:
                await query.answer("আগে গ্রুপে জয়েন করুন, তারপর ভেরিফাই বাটনে চাপ দিন!", show_alert=True)
        except Exception as e:
            await query.answer("আগে গ্রুপ চেক করুন অথবা বটকে গ্রুপের অ্যাডমিন করুন!", show_alert=True)

# ৩. গ্রুপে বট অ্যাড হলে বা নতুন মেম্বার আসলে ওয়েলকাম মেসেজ
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
        else:
            await update.message.reply_text(f"Hey there {member.first_name} 💖, and welcome to Riya Chat group! How are you?")

# ৪. /help কমান্ড (স্ক্রিনশটের মতো সাজানো মেনু)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌸 **Riya Bot – Help**\n\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        "👮 **Moderation Commands**\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        "/kick – Kisi ko group se nikalo\n"
        "/ban – Permanent ban karo\n"
        "/purge – Reply se yahan tak delete\n\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        "⚙️ **Group Settings & Protection**\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        "• Antilink Active (Auto-delete links)\n"
        "• Antiforward Active (Auto-delete forwards)"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ৫. অ্যান্টি-লিংক, অ্যান্টি-ফরোয়ার্ড ও ভয়েস ওয়ার্নিং হ্যান্ডলার
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
        
    chat = update.effective_chat

    # শুধুমাত্র গ্রুপ বা সুপারগ্রুপের জন্য চেক করবে
    if chat.type != "private":
        
        # ক) ফরোয়ার্ড চেক (অন্য চ্যাট বা চ্যানেল থেকে ফরোয়ার্ড করা মেসেজ)
        is_forwarded = bool(update.message.forward_origin or update.message.forward_from or update.message.forward_from_chat)
        
        # খ) লিংক চেক
        message_text = update.message.text or update.message.caption or ""
        text_lower = message_text.lower()
        has_link = "http://" in text_lower or "https://" in text_lower or "t.me/" in text_lower or "www." in text_lower

        # যদি ফরোয়ার্ড করা হয় অথবা লিংক দেওয়া হয়
        if is_forwarded or has_link:
            try:
                # মেসেজটি সাথে সাথে ডিলিট করে দেবে
                await update.message.delete()
                
                # ভয়েসে "জান গ্রুপে লিংক দিও না" বলার চেষ্টা করবে (voice.ogg ফাইল না থাকলে টেক্সটে বলবে)
                voice_file_path = "voice.ogg"
                try:
                    await chat.send_voice(voice=open(voice_file_path, 'rb'))
                except:
                    await chat.send_message("জান গ্রুপে লিংক দিও না! 🚫")
                return
            except Exception as e:
                pass

        # গ) সাধারণ ভয়েস রিপ্লাই ট্রিগার ("i love you" লিখলে)
        if "i love you" in text_lower:
            voice_file_path = "voice.ogg"
            try:
                await update.message.reply_voice(voice=open(voice_file_path, 'rb'))
            except Exception as e:
                await update.message.reply_text("hlloww 🙈")

# ৬. মডারেশন কমান্ডস (/kick, /ban, /purge)
async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        chat_id = update.effective_chat.id
        user_to_kick = update.message.reply_to_message.from_user.id
        try:
            await context.bot.ban_chat_member(chat_id, user_to_kick)
            await context.bot.unban_chat_member(chat_id, user_to_kick)
            await update.message.reply_text("사용자를 group se nikal diya gaya! 👞")
        except Exception as e:
            await update.message.reply_text("বটকে গ্রুপের অ্যাডমিন করুন এবং পর্যাপ্ত পারমিশন দিন!")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        chat_id = update.effective_chat.id
        user_to_ban = update.message.reply_to_message.from_user.id
        try:
            await context.bot.ban_chat_member(chat_id, user_to_ban)
            await update.message.reply_text("Permanent ban kar diya gaya! 🚫")
        except Exception as e:
            await update.message.reply_text("বটকে অ্যাডমিন করুন!")

async def purge_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        chat_id = update.effective_chat.id
        message_id_start = update.message.reply_to_message.message_id
        message_id_end = update.message.message_id
        try:
            for msg_id in range(message_id_start, message_id_end + 1):
                try:
                    await context.bot.delete_message(chat_id, msg_id)
                except:
                    pass
            await update.message.reply_text("Messages saaf kar diye gaye hain! 🗑️")
        except Exception as e:
            await update.message.reply_text("মেসেজ ডিলিট করতে সমস্যা হয়েছে।")

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()
    
    # হ্যান্ডলারগুলো রেজিস্টার করা হচ্ছে
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # মডারেশন কমান্ড
    application.add_handler(CommandHandler('kick', kick_user))
    application.add_handler(CommandHandler('ban', ban_user))
    application.add_handler(CommandHandler('purge', purge_messages))
    
    # নতুন মেম্বার ওয়েলকাম হ্যান্ডলার
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    
    # সব ধরনের মেসেজ হ্যান্ডলার
    application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_message))
    
    print("বট সফলভাবে রান হচ্ছে...")
    application.run_polling()
