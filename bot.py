import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# আপনার গ্রুপের সঠিক ইউজারনেম
CHANNEL_USERNAME = "@riyachatgroup70"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ১. /start এবং ফোর্স সাবস্ক্রাইব লজিক
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👥 Group Join Karo", url="https://t.me/riyachatgroup70")],
        [InlineKeyboardButton("✅ Maine Join Kar Liya", callback_data="check_join")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Arre ruko! 🙈 Pehle hamare group join karo, phir mujhse baat karo 😘",
        reply_markup=reply_markup
    )

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
                    "Yay REDME! 🎉 Ab baat karte hain~\n\nবট এখন ব্যবহারের জন্য প্রস্তুত!",
                    reply_markup=reply_markup
                )
            else:
                await query.answer("আগে গ্রুপে জয়েন করুন তারপর এই বাটনে ক্লিক করুন!", show_alert=True)
        except Exception as e:
            await query.answer("আগে গ্রুপ চেক করুন অথবা বটকে গ্রুপের অ্যাডমিন করুন!", show_alert=True)

# ২. ভয়েস ও টেক্সট মেসেজ হ্যান্ডলার (I love you লিখলে ভয়েস পাঠানো)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    text = update.message.text.lower()
    
    if "i love you" in text:
        voice_file_path = "voice.ogg"  # গিটহাবে আপলোড করা ভয়েস ফাইল
        try:
            await update.message.reply_voice(voice=open(voice_file_path, 'rb'))
        except Exception as e:
            await update.message.reply_text("hlloww 🙈")

# ৩. মডারেশন কমান্ডস (/kick, /ban, /purge)
async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        chat_id = update.effective_chat.id
        user_to_kick = update.message.reply_to_message.from_user.id
        try:
            await context.bot.ban_chat_member(chat_id, user_to_kick)
            await context.bot.unban_chat_member(chat_id, user_to_kick)
            await update.message.reply_text("ব্যবহারীকে গ্রুপ থেকে বের করে দেওয়া হয়েছে! 👞")
        except Exception as e:
            await update.message.reply_text("বটকে গ্রুপের অ্যাডমিন করুন এবং পর্যাপ্ত পারমিশন দিন!")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        chat_id = update.effective_chat.id
        user_to_ban = update.message.reply_to_message.from_user.id
        try:
            await context.bot.ban_chat_member(chat_id, user_to_ban)
            await update.message.reply_text("পার্মানেন্ট ব্যান করা হয়েছে! 🚫")
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
            await update.message.reply_text("মেসেজগুলো মুছে ফেলা হয়েছে! 🗑️")
        except Exception as e:
            await update.message.reply_text("মেসেজ ডিলিট করতে সমস্যা হয়েছে।")

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.add_handler(CommandHandler('kick', kick_user))
    application.add_handler(CommandHandler('ban', ban_user))
    application.add_handler(CommandHandler('purge', purge_messages))
    
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("বট সফলভাবে রান হচ্ছে...")
    application.run_polling()
