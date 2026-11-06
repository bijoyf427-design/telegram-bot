import logging
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

CHANNEL_USERNAME = "@riyachatgroup70"
GROUP_INVITE_LINK = "https://t.me/riyachatgroup70"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ১. /start এবং ফোর্স সাবস্ক্রাইব ভেরিফিকেশন
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

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_join":
        user_id = query.from_user.id
        try:
            member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            if member.status in ['member', 'administrator', 'creator']:
                keyboard = [
                    [InlineKeyboardButton("➕ Add to Group 🥰", url=f"https://t.me/{context.bot.username}?startgroup=true")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.edit_text(
                    "Aa gaye finally REDME! 🥰 Kya haal hai? Ab bot ko group me add karo~",
                    reply_markup=reply_markup
                )
            else:
                await query.answer("আগে গ্রুপে জয়েন করুন, তারপর ভেরিফাই বাটনে চাপ দিন!", show_alert=True)
        except Exception as e:
            await query.answer("আগে গ্রুপ চেক করুন অথবা বটকে গ্রুপের অ্যাডমিন করুন!", show_alert=True)

# ২. ওয়েলকাম মেসেজ
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

# ৩. /help কমান্ড (সকল কমান্ডের লিস্ট - স্ক্রিনশটের আদলে)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌸 **Riya Bot – All Commands**\n\n"
        "👮 **Moderation:**\n"
        "/kick - Kick a user\n"
        "/ban - Ban a user\n"
        "/mute - Mute a user\n"
        "/unmute - Unmute a user\n"
        "/purge - Delete messages\n"
        "/antilink - Toggle link filter\n"
        "/antiforward - Toggle forward filter\n\n"
        "🎮 **Economy & Fun Games:**\n"
        "/bal - Check your wallet\n"
        "/daily - Claim daily reward\n"
        "/rob - Steal coins from someone\n"
        "/kill - Attack another user\n"
        "/invest - Start fixed deposit (FD)\n"
        "/fd - Check active FD\n"
        "/top - Rich leaderboard\n"
        "/propose - Propose to someone"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ৪. মেসেজ হ্যান্ডলার (অ্যান্টি-লিংক, অ্যান্টি-ফরোয়ার্ড, র্যান্ডম চ্যাট রিপ্লাই ও গেম)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
        
    chat = update.effective_chat
    message = update.message
    user = update.effective_user

    if chat.type != "private":
        # অ্যান্টি-ফরোয়ার্ড ও অ্যান্টি-লিংক চেক
        is_forwarded = bool(message.forward_origin or message.forward_from or message.forward_from_chat)
        message_text = message.text or message.caption or ""
        text_lower = message_text.lower()
        has_link = "http://" in text_lower or "https://" in text_lower or "t.me/" in text_lower or "www." in text_lower

        if is_forwarded or has_link:
            try:
                await message.delete()
                voice_file_path = "voice.ogg"
                try:
                    await chat.send_voice(voice=open(voice_file_path, 'rb'))
                except:
                    await chat.send_message("জান গ্রুপে লিংক বা ফরোয়ার্ড করা নিষেধ! 🚫")
                return
            except Exception as e:
                pass

        # বটকে ট্যাগ বা র্যান্ডম টেক্সট রিপ্লাই (স্ক্রিনশটের মতো চ্যাট ফ্লো)
        bot_username = context.bot.username.lower()
        is_mentioned = f"@{bot_username}" in text_lower
        is_replied = message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id

        if is_mentioned or is_replied:
            replies = [
                "Haan bolo 🥰",
                "Arre kya ho raha hai? 😆 Thik se bolo na kya baat karni hai.",
                "Bolo jaan, sunshid to! ✨",
                "Hieeee 🌺"
            ]
            await message.reply_text(random.choice(replies))
            return

        # সাধারণ উল্টাপাল্টা টেক্সটের স্মার্ট রিপ্লাই
        if len(text_lower) > 3 and not message.text.startswith('/'):
            if random.random() < 0.3: # ৩০% চ্যান্স অটো চ্যাট রেসপন্স
                await message.reply_text("Arre kya ho raha hai? 😆 Thik se bolo na.")

# ৫. মডারেশন কমান্ডস
async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        chat_id = update.effective_chat.id
        user_id = update.message.reply_to_message.from_user.id
        try:
            await context.bot.ban_chat_member(chat_id, user_id)
            await context.bot.unban_chat_member(chat_id, user_id)
            await update.message.reply_text("ব্যবহারীকে গ্রুপ থেকে কিক করা হয়েছে! 👞")
        except:
            await update.message.reply_text("বটকে অ্যাডমিন করুন!")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        chat_id = update.effective_chat.id
        user_id = update.message.reply_to_message.from_user.id
        try:
            await context.bot.ban_chat_member(chat_id, user_id)
            await update.message.reply_text("পার্মানেন্ট ব্যান করা হয়েছে! 🚫")
        except:
            await update.message.reply_text("বটকে অ্যাডমিন করুন!")

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        chat_id = update.effective_chat.id
        user_id = update.message.reply_to_message.from_user.id
        try:
            await context.bot.restrict_chat_member(chat_id, user_id, permissions=ChatPermissions(can_send_messages=False))
            await update.message.reply_text("ব্যবহারীকে মিউট করা হয়েছে! 🔇")
        except:
            await update.message.reply_text("বটকে অ্যাডমিন করুন!")

async def purge_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        chat_id = update.effective_chat.id
        start_id = update.message.reply_to_message.message_id
        end_id = update.message.message_id
        try:
            for msg_id in range(start_id, end_id + 1):
                try:
                    await context.bot.delete_message(chat_id, msg_id)
                except:
                    pass
            await update.message.reply_text("মেসেজগুলো মুছে ফেলা হয়েছে! 🗑️")
        except:
            exceptions = "ডিলিট করতে সমস্যা হয়েছে।"

# ৬. সিম্পল ইকোনমি গেম কমান্ডস (Rob / Daily / Balance)
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Wallet: ₹1480 (Protection: Active)")

async def daily_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎉 You have successfully claimed your daily reward of ₹500!")

async def rob_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        target_name = update.message.reply_to_message.from_user.first_name
        amount = random.randint(100, 500)
        await update.message.reply_text(f"👤 You robbed ₹{amount} from {target_name} successfully! 💰")
    else:
        await update.message.reply_text("⚠️ Please reply to someone's message to rob them!")

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()
    
    # হ্যান্ডলার রেজিস্টার
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.add_handler(CommandHandler('kick', kick_user))
    application.add_handler(CommandHandler('ban', ban_user))
    application.add_handler(CommandHandler('mute', mute_user))
    application.add_handler(CommandHandler('purge', purge_messages))
    
    application.add_handler(CommandHandler('bal', balance))
    application.add_handler(CommandHandler('daily', daily_reward))
    application.add_handler(CommandHandler('rob', rob_user))
    
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_message))
    
    print("বট সফলভাবে রান হচ্ছে...")
    application.run_polling()
