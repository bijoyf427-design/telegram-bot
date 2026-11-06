import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👥 Group Join Karo", url="https://t.me/YourGroupName")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Arre ruko! Pehle hamare group join karo, phir mujhse baat karo 😘",
        reply_markup=reply_markup
    )

if __name__ == '__main__':
        TOKEN = os.getenv("BOT_TOKEN")

    
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    
    print("বট রান হচ্ছে...")
    application.run_polling()

