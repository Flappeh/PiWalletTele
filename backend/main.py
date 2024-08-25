from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from modules.environment import BOT_USERNAME,TOKEN, get_all_env
from modules.blockchain import get_balance_from_public_key

# Commands

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello There")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is the help Text")


async def from_wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallet_key: str = context.args    
    if len(wallet_key) > 1:
        await update.message.reply_text("Only one key allowed per request")
        return
    key = wallet_key[0]
    try:
        data = get_balance_from_public_key(key)
        if not data:
            await update.message.reply_text("None")
            return
        await update.message.reply_text(text=data)
    except Exception as e:
        await update.message.reply_text(e)


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
    app.add_handler(CommandHandler('wallet', from_wallet_command))
    
    # Messages
    app.add_handler(MessageHandler(filters.Text, handle_message))
    
    # Errors
    app.add_error_handler(handle_error)
    
    app.run_polling(poll_interval=3)
    