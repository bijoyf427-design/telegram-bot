import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import google.generativeai as genai

# লগিং সেটআপ
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- কনফিগারেশন ---
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"          # @BotFather থেকে পাওয়া বোট টোকেন এখানে বসান
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"      # Google AI Studio থেকে পাওয়া জেমিনি API Key এখানে বসান
GROUP_USERNAME = "@riyachatgroup70"         # আপনার গ্রুপের ইউজারনেম
GROUP_CHAT_ID = -100xxxxxxxxxx              # আপনার গ্রুপের নিউমেরিক চ্যাট আইডি (মাইনাস দিয়ে শুরু সুপারগ্রুপ আইডি)

# জেমিনি এআই কনফিগার
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# ১. /start কমান্ড হ্যান্ডলার (গ্রুপ জয়েন ভেরিফিকেশন সহ)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("👥 Group Join Karo", url=f"https://t.me/{GROUP_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("✅ Maine Join Kar Liya", callback_data="check_join")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"🌸 **Riya Bot** - Verification Menu\n\n"
        f"Hm, pehle group join karo jaan, phir baat karte hain 🥰\n\n"
        f"Welcome {user.first_name}!"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# ২. জয়েন চেক করার কলব্যাক
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    try:
        member = await context.bot.get_chat_member(chat_id=GROUP_CHAT_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            await query.message.reply_text(f"✅ Verification Successful! Now you can add me to your group.\n\nAa gaye finally {query.from_user.first_name}! 😘")
        else:
            await query.answer("❌ Abhi group join nahi kiya. Pehle join karo!", show_alert=True)
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        await query.answer("❌ Check karne mein samasya hui. Kripya group ID thik karein.", show_alert=True)

# ৩. স্ক্রিনশটের মতো প্রফেশনাল /help মেনু কমান্ড
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌸 **Riya Bot – Full Help Menu**\n\n"
        "👮 **Moderation Commands:**\n"
        "• `/kick` - Kisi ko group se nikalo[span_3](start_span)[span_3](end_span)\n"
        "• `/ban` - Permanent ban karo[span_4](start_span)[span_4](end_span)\n"
        "• `/mute` - Chup karao[span_5](start_span)[span_5](end_span)\n"
        "• `/unmute` - Awaaz wapas do[span_6](start_span)[span_6](end_span)\n"
        "• `/warn` - Warning do[span_7](start_span)[span_7](end_span)\n"
        "• `/pin` - Message pin karo[span_8](start_span)[span_8](end_span)\n\n"
        "🛡️ **Protection & Settings:**\n"
        "• `/antilink` - Link auto-delete protection[span_9](start_span)[span_9](end_span)\n"
        "• `/antifoward` - Forwarded msgs auto-delete[span_10](start_span)[span_10](end_span)\n"
        "• `/purge` - Bulk message delete[span_11](start_span)[span_11](end_span)\n\n"
        "👑 **Admin & Fun:**\n"
        "• `/promote` - Admin bana do[span_12](start_span)[span_12](end_span)\n"
        "• `/demote` - Admin rights lo wapas[span_13](start_span)[span_13](end_span)\n"
        "• `/id` - Telegram ID dekho\n"
        "• `/rob` - Economy game & coins steal[span_14](start_span)[span_14](end_span)\n\n"
        "🤖 *To chat with me using AI, just reply to my message or mention me!*"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ৪. মডারেশন কমান্ড হ্যান্ডলারসমূহ (যেমন: /kick, /ban ইত্যাদি)
async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message.reply_to_message:
        try:
            user_to_kick = message.reply_to_message.from_user.id
            await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=user_to_kick)
            await context.bot.unban_chat_member(chat_id=update.effective_chat.id, user_id=user_to_kick) # শুধু কিক করার জন্য আনব্যান করা হয়
            await message.reply_text(f"👢 Kicked user successfully! ⚠️")
        except Exception as e:
            await message.reply_text(f"❌ Error: {e} (Make sure I am admin!)")
    else:
        await message.reply_text("⚠️ Reply to a message to kick the user!")

# ৫. অ্যান্টি-লিংক ও স্প্যাম ফিল্টার (গ্রুপের জন্য)
async def anti_link_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message or not message.text:
        return

    if update.effective_chat.type in ['group', 'supergroup']:
        text = message.text.lower()
        if "t.me/" in text or "http://" in text or "https://" in text or "www." in text:
            try:
                user_status = (await update.effective_chat.get_member(message.from_user.id)).status
                if user_status not in ['administrator', 'creator']:
                    await message.delete()
                    warning_msg = await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"⚠️ {message.from_user.first_name}, yahan link ya spam bhejna mana hai!"
                    )
                    context.job_queue.run_once(delete_warning_message, 5, data=warning_msg)
            except Exception as e:
                logger.error(f"Error in anti-link: {e}")

async def delete_warning_message(context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.job.data.delete()
    except:
        pass

# ৬. কেউ গ্রুপ ছেড়ে গেলে বা ব্যাক নিলে তার বিরুদ্ধে মজার মেসেজ দেওয়া
async def track_left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    record = update.effective_message.left_chat_member
    if record:
        funny_messages = [
            f"😂 {record.first_name} bhag gaya! Shayad WiFi ka bill nahi bhar raha tha 💸",
            f"👋 Arre {record.first_name} chala gaya! Bye bye tata khatam! 🚶‍♂️",
            f"🙄 {group_leave_msg := record.first_name} group chhod ke chala gaya, rona mat koi! 😭"
        ]
        import random
        await update.effective_message.reply_text(random.choice(funny_messages))

# ৭. জেমিনি এআই (Gemini AI) স্মার্ট অটো-রিপ্লাই সিস্টেম
async def ai_responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message or not message.text:
        return

    chat_type = update.effective_chat.type
    user_text = message.text
    is_group = chat_type in ['group', 'supergroup']
    bot_username = context.bot.username

    # গ্রুপে হলে বোটকে মেনশন করলে বা রিপ্লাই দিলে, অথবা ইনবক্সে সরাসরি উত্তর দেবে
    should_reply = not is_group or (f"@{bot_username.lower()}" in user_text.lower()) or (message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id)

    if should_reply:
        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # জেমিনি এআই প্রম্পট ও রেসপন্স
            prompt = f"You are a friendly, slightly flirty, and smart Telegram AI anime bot named Riya. Talk naturally like a human in Hinglish/Bangla mix as per user query: {user_text}"
            response = ai_model.generate_content(prompt)
            
            await message.reply_text(response.text)
        except Exception as e:
            logger.error(f"AI Error: {e}")

def main():
    application = Application.builder().token(TOKEN).build()

    # হ্যান্ডলার রেজিস্টার
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("kick", kick_command))
    application.add_handler(CallbackQueryHandler(button_callback, pattern="check_join"))
    
    # গ্রুপ ফিল্টার ও ট্র্যাকার
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), anti_link_filter), group=1)
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, track_left_member), group=2)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_responder), group=3)

    print("Professional Riya Bot is running successfully...")
    application.run_polling()

if __name__ == "__main__":
    main()
