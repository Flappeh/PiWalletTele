from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from modules.environment import BOT_USERNAME,TOKEN
from modules.blockchain import get_balance_from_public_key
from modules.androidBot import AndroidBot
from typing import List
import datetime
from modules.utils import get_logger

logger = get_logger()
# Commands

def check_time(update: Update) -> bool:
    if update.message.date.timestamp() < datetime.datetime.now().timestamp() - 5:
        return True
    return False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_time(update):
        return
    keyboard = [
        [
            InlineKeyboardButton("Help", callback_data="help"),
        ],
        [
            InlineKeyboardButton("Check Wallet", callback_data="check_wallet"),
            InlineKeyboardButton("Check Phrase", callback_data="check_phrase"),
        ],
        [InlineKeyboardButton("Administration", callback_data="admin")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("*Pi Wallet Bot 2024*\n\n Silahkan pilih command", 
                                    reply_markup=reply_markup,
                                    parse_mode=ParseMode.MARKDOWN_V2)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Help text")
    else:
        if check_time(update):
            return
        await update.message.reply_text("This is the help Text")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()
        
    try:
        await query.delete_message()
        match query.data:
            case "check_wallet":
                await from_wallet_command(update=update, context=context)
            case "check_phrase":
                await from_passphrase_command(update=update, context=context)
            case "help":
                await help_command(update=update, context=context)
            case _:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Unknown Command")
    except Exception as e:
        logger.error(f"Error running command after button with identifier {query.data} is clicked!, detail: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error occurred")

async def from_wallet_helper(update: Update, context: ContextTypes.DEFAULT_TYPE, wallet_key: List[str]):
    if len(wallet_key) != 1:
            await update.message.reply_text("Mohon masukkan hanya satu wallet per transaksi")
            return
    key = wallet_key[0]
    try:
        data = get_balance_from_public_key(key)
        if not data:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="None")
            return
        await context.bot.send_message(chat_id=update.effective_chat.id, text=data)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=str(e))
     
async def from_wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = ""
    if update.callback_query:
        
        query = update.callback_query
        await query.answer()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Masukkan public key wallet yang ingin di cari")
        
        print("Callback query received:", query.data)
        data = query.data.split()
    else:
        if check_time(update):
            return
        data = context.args    
    await from_wallet_helper(update,context,data)
        
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

async def from_passphrase_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_time(update):
        return
    phrase: List[str] = context.args
    if len(phrase) != 24:
        await update.message.reply_text("Passphrase harus 24 kata!")
        return
    proses_message = await update.message.reply_text("Sedang memproses request...") 
    try:
        phrase = ' '.join(phrase)
        bot = AndroidBot()
        data = bot.open_wallet_from_passphrase(phrase)
        if "Invalid" in data:
            await update.message.reply_text("Invalid Phrase Given")
        else:
            await update.message.reply_text(f"Jumlah wallet {data}")
        del bot
    except Exception as e:
        await update.message.reply_text("Error occured, please contact administrator")
        logger.error(f"Error retrieving passphrase details, {e}")
    await context.bot.delete_message(chat_id=update.effective_chat.id,message_id=proses_message.message_id)
# Responses

def handle_response(text: str) -> str:
    # This is the logic for processing the request
    string_content: str = text.lower()
    
    if 'hello' in string_content:
        return "Hello"
    if 'test' in string_content:
        return "Test triggered"
    return "Nothing known"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_time(update):
        return
    message_type: str = update.message.chat.type # Group or Private Chat
    text: str = update.message.text
    
    print(f"User: ({update.message.chat.id}) in {message_type} sent: {text}")
    
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else: 
        response: str = handle_response(text)
    
    print('Bot ', response )
    await update.message.reply_text(response)
    

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error : {context.error}")
    

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    # Command
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('check_wallet', from_wallet_command))
    app.add_handler(CommandHandler('check_phrase', from_passphrase_command))
    app.add_handler(CallbackQueryHandler(button))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Errors
    app.add_error_handler(handle_error)
    
    app.run_polling(poll_interval=3)
    