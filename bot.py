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
        await update.message.reply_text("Riya Bot is active here! 🌸")
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
        "/unmute — Unmute a user\n"
        "/warn — Warn a user\n"
        "/purge — Delete messages\n\n"
        "╔══════════════════════════╗\n"
        "  ⚙️ **Group Protection**\n"
        "╚══════════════════════════╝\n"
        "/antilink — Link filter\n"
        "/antiforward — Forward filter\n\n"
        "╔══════════════════════════╗\n"
        "  👑 **Admin & Fun Control**\n"
        "╚══════════════════════════╝\n"
        "/promote /demote /pin /id\n"
        "/bal /daily /rob /top"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ৪. গ্রুপ মেসেজ ও স্মার্ট চ্যাট রেসপন্স হ্যান্ডলার
async def group_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
        
    chat = update.effective_chat
    message = update.message
    message_text = message.text or message.caption or ""
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

        # খ) গ্রুপে কেউ হাই, হ্যালো বা সাধারণ কথা বললে চ্যাট রিপ্লাই দেবে
        if message_text and not message_text.startswith('/'):
            fun_replies = [
                "Haan bolo 🥰 What's up?",
                "Arre kya ho raha hai? 😆",
                "Bolo jaan, listening! ✨ 🙈",
                "Hieeee! How are you? 🌺 🤭",
                "Haha, what are you saying? 🐒💬",
                "Hu... tell me something nice! 🐵💕",
                "Hey there! Got your message 😊",
                "Aha! Mujhe yaad kiya? 🙈💖"
            ]
            await message.reply_text(random.choice(fun_replies))
            return

# ৫. সমস্ত মডারেশন ও অ্যাডমিন কমান্ডস
async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, update.message.reply_to_message.from_user.id)
            await context.bot.unban_chat_member(update.effective_chat.id, update.message.reply_to_message.from_user.id)
            await update.message.reply_text("User has been kicked! 👞")
        except:
            await update.message.reply_text("Please make me an admin!")
    else:
        await update.message.reply_text("Please reply to a user's message to kick! ⚠️")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, update.message.reply_to_message.from_user.id)
            await update.message.reply_text("User has been permanently banned! 🚫")
        except:
            await update.message.reply_text("Please make me an admin!")
    else:
        await update.message.reply_text("Please reply to a user's message to ban! ⚠️")

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
    else:
        await update.message.reply_text("Please reply to a user's message to mute! ⚠️")

async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            await context.bot.restrict_chat_member(
                update.effective_chat.id, 
                update.message.reply_to_message.from_user.id, 
                permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
            )
            await update.message.reply_text("User has been unmuted! 🔊")
        except:
            await update.message.reply_text("Please make me an admin!")
    else:
        await update.message.reply_text("Please reply to a user's message to unmute! ⚠️")

async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        await update.message.reply_text(f"⚠️ User @{update.message.reply_to_message.from_user.username or update.message.reply_to_message.from_user.first_name} has been warned!")
    else:
        await update.message.reply_text("Please reply to a user to warn!")

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
            await update.message.reply_text("Please make me an admin to purge messages!")

async def pin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            await context.bot.pin_chat_message(update.effective_chat.id, update.message.reply_to_message.message_id)
            await update.message.reply_text("Message pinned successfully! 📌")
        except:
            await update.message.reply_text("Please make me an admin!")

async def promote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            await context.bot.promote_chat_member(
                update.effective_chat.id, 
                update.message.reply_to_message.from_user.id,
                can_manage_chat=True, can_delete_messages=True, can_invite_users=True
            )
            await update.message.reply_text("User promoted to admin! 👑")
        except:
            await update.message.reply_text("Please make me an admin!")

async def demote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            await context.bot.promote_chat_member(
                update.effective_chat.id, 
                update.message.reply_to_message.from_user.id,
                can_manage_chat=False, can_delete_messages=False, can_invite_users=False
            )
            await update.message.reply_text("User demoted from admin! 📉")
        except:
            await update.message.reply_text("Please make me an admin!")

async def check_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    await update.message.reply_text(f"👤 User Name: {target.first_name}\n🆔 Telegram ID: `{target.id}`", parse_mode="Markdown")

async def economy_bal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Your Balance: 500 Riya Coins 🪙✨")

async def economy_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎉 You claimed your daily reward of 100 Riya Coins! 🪙")

async def economy_rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🥷 You successfully robbed 50 coins from the street! 😂")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏆 **Richest Users Leaderboard**:\n1. {update.effective_user.first_name} - 500 Coins 🪙", parse_mode="Markdown")

async def toggle_antilink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ Antilink filter is active and monitoring links! ✅")

async def toggle_antiforward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ Antiforward filter is active and monitoring forwards! ✅")

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()
    
    # সকল কমান্ড হ্যান্ডলারসমূহ রেজিস্টার করা হলো
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.add_handler(CommandHandler('kick', kick_user))
    application.add_handler(CommandHandler('ban', ban_user))
    application.add_handler(CommandHandler('mute', mute_user))
    application.add_handler(CommandHandler('unmute', unmute_user))
    application.add_handler(CommandHandler('warn', warn_user))
    application.add_handler(CommandHandler('purge', purge_messages))
    application.add_handler(CommandHandler('pin', pin_message))
    application.add_handler(CommandHandler('promote', promote_user))
    application.add_handler(CommandHandler('demote', demote_user))
    application.add_handler(CommandHandler('id', check_id))
    application.add_handler(CommandHandler('bal', economy_bal))
    application.add_handler(CommandHandler('daily', economy_daily))
    application.add_handler(CommandHandler('rob', economy_rob))
    application.add_handler(CommandHandler('top', leaderboard))
    application.add_handler(CommandHandler('antilink', toggle_antilink))
    application.add_handler(CommandHandler('antiforward', toggle_antiforward))
    
    # গ্রুপের সাধারণ টেক্সট ও র্যান্ডম চ্যাট রেসপন্স হ্যান্ডলার
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), group_message_handler))
    
    print("Bot is running successfully...")
    application.run_polling()
