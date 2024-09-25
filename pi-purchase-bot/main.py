from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler, CallbackContext, ConversationHandler, Defaults
from modules.environment import BOT_USERNAME,TOKEN
from modules.blockchain import get_balance_from_public_key
from modules.androidBot import start_bot_phrase_process, start_phrase_process_after_error, start_change_user_process, start_transaction_process
from typing import List
from datetime import datetime, timedelta
from modules.utils import get_logger, store_schedule, finish_schedule, get_all_schedule, check_schedule
import random
import string
import pytz

logger = get_logger(__name__)
# Commands

# State for scheduler_input
PHRASE, TIME, AMOUNT = range(3)

def check_time(update: Update) -> bool:
    if update.message.date.timestamp() < datetime.now().timestamp() - 600:
        return True
    return False

def validate_datetime(message: str):
    try:
        data = datetime.strptime(message, "%d-%m-%Y:%H:%M:%S")
        # if data.timestamp() < datetime.now().timestamp() + 1800:
        #     return False, data
        return True, data
    except:
        return False, None

def validate_amount(message: str):
    try:
        data = float(message)
        return True, data
    except:
        return False, None

async def run_transaction_job(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    data = job.data
    await context.bot.send_message(job.chat_id, text=f"Job {job.name} mulai!")
    start_transaction_process(data['phrase'], data['amount'])
    finish_schedule(job.name)
    await context.bot.send_message(job.chat_id, text=f"Selesai menjalankan schedule {job.name}")
    
async def schedule_job_run(update: Update, context: CallbackContext, user_data):
    job_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    store_schedule(job_name=job_name, user_data=user_data,chat_id=update.effective_chat.id)
    context.job_queue.run_once(
        callback=run_transaction_job, 
        chat_id= update.effective_chat.id,
        data=user_data,
        when=user_data['time'],
        name=job_name
        )
    
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_time(update):
        return
    await update.message.reply_text("""
*Pi Wallet Bot*

Command yang dapat dilakukan:

/help \\-\\> Show command ini

/phrase *<24\\-phrase\\>* \\-\\> Perintah bot untuk search wallet berdasarkan 24 word phrase

/wallet *<public\\-key\\>* \\-\\> Perintah bot untuk search wallet berdasarkan public key

/schedule *<24\\-phrase\\>* *<Jumlah\\Coin\\>* *<Waktu\\-Transaksi\\>*   \\-\\> Perintah bot untuk kirim coin dari wallet yang disediakan

/change \\-\\> *Ganti user* Pi Account
""",
    parse_mode=ParseMode.MARKDOWN_V2)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Help text")
    else:
        if check_time(update):
            return
        await update.message.reply_text("""
*Pi Wallet Bot*

Command yang dapat dilakukan:

/help \\-\\> Show command ini

/phrase *<24\\-phrase\\>* \\-\\> Perintah bot untuk search wallet berdasarkan 24 word phrase

/wallet *<public\\-key\\>* \\-\\> Perintah bot untuk search wallet berdasarkan public key

/schedule *<24\\-phrase\\>* *<Jumlah\\Coin\\>* *<Waktu\\-Transaksi\\>*   \\-\\> Perintah bot untuk kirim coin dari wallet yang disediakan

/change \\-\\> *Ganti user* Pi Account
""",
    parse_mode=ParseMode.MARKDOWN_V2)

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

async def schedule_transaction_command(update: Update, context: CallbackContext):
    if check_time(update):
        return
    await update.message.reply_text("Enter 24 phrase wallet")
    return PHRASE

async def schedule_get_phrase(update: Update, context: CallbackContext) -> int:
    data = update.message.text.split()
    if len(data) != 24:
        await update.message.reply_text("Phrase harus 24 kata!, silahkan kirim ulang.")
        return PHRASE
    context.user_data['phrase'] = update.message.text
    await update.message.reply_text('Kapan waktu transaksi dilakukan \n(Format : "Tanggal-Bulan-Tahun:Jam:Menit:Detik" )\n Contoh : 01-01-2024:12:30:36')
    return TIME

async def schedule_get_time(update:Update, context: CallbackContext) -> int:
    result, time_data = validate_datetime(update.message.text)
    if result == False and time_data == None:
        await update.message.reply_text("Format tidak dikenal, coba lagi.\nContoh : 01-01-2024:12:30:36")
        return TIME
    elif result == False and time_data:
        await update.message.reply_text("Waktu yang dikirim minimal 30 menit dari saat ini")
        return TIME
    # if check_schedule(time_data) == False:
    #     await update.message.reply_text("Sudah ada schedule yang berjalan pada jam yang diberikan. Jika ingin cancel, /cancel")
    #     return TIME
    context.user_data['time'] = time_data - timedelta(minutes=3)
    await update.message.reply_text("Berapa nominal yang ingin dikirim")
    return AMOUNT

async def schedule_get_amount(update:Update, context: CallbackContext) -> int:
    result, amount = validate_amount(update.message.text)
    if result == False:
        await update.message.reply_text("Invalid amount, coba lagi.")
        return AMOUNT
    if amount <= 0.2:
        await update.message.reply_text("Amount minimal yang bisa dikirim adalah 0.3")
        return AMOUNT
    context.user_data['amount'] = amount
    user_data = context.user_data
    await update.message.reply_text(f"""
Terima kasih. Berikut info yang diterima

Phrase : {user_data['phrase']}

Waktu : {user_data['time'] + timedelta(minutes=3)}

Jumlah coin : {user_data['amount']}

""")
    await schedule_job_run(update, context, user_data)
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Jadwal telah di cancel")
    return ConversationHandler.END
    
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")    

async def proses_phrase(proses_message, context: ContextTypes.DEFAULT_TYPE, phrase: str) -> str:
    try:
        data = start_bot_phrase_process(phrase)
        if "Invalid" in data:
            return "Phrase yang dikirim invalid!"
        if "timeout" in data:
            return "Timeout limit telah tercapai, mohon request ulang!"
        elif "Error butuh ganti ke user lain" in data:
            await context.bot.edit_message_text(text=f"Limit user tercapai, proses ganti user",chat_id=proses_message.chat_id,message_id=proses_message.id)
            data = start_phrase_process_after_error(phrase)
            return f"""
*Pi Wallet Bot*

*Phrase*: 
{phrase}

*Jumlah wallet*: 
{data}
        """
        else:
            return f"""
*Pi Wallet Bot*

*Phrase*: 
{phrase}

*Jumlah wallet*: 
{data}
        """
    except Exception as e:
        logger.error(f"Error retrieving passphrase details, {e}")
        return "Error occured, please contact administrator"

async def from_passphrase_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_time(update):
        return
    phrase: List[str] = context.args
    if len(phrase) != 24:
        await update.message.reply_text("Passphrase harus 24 kata!")
        return
    phrase = ' '.join(phrase)
    proses_message = await update.message.reply_text("Sedang memproses request...",reply_to_message_id=update.message.id)
    data = await proses_phrase(proses_message,context,phrase)
    data = data.replace('.', '\\.').replace('!','\\!')
    await context.bot.edit_message_text(
        text=data,
        chat_id=proses_message.chat_id,
        message_id=proses_message.id,
        parse_mode=ParseMode.MARKDOWN_V2
    )
    
async def change_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_time(update):
        return
    proses_message = await update.message.reply_text("Sedang memproses request...",reply_to_message_id=update.message.id) 
    try:
        data = await start_change_user_process()
        if data == "timeout":            
            return "Timeout limit telah tercapai, mohon request ulang!"
        await context.bot.edit_message_text(text=f"Done Processing",chat_id=proses_message.chat_id,message_id=proses_message.id)
    except Exception as e:
        await update.message.reply_text("Error occured, please contact administrator")
        logger.error(f"Error retrieving passphrase details, {e}")

def remove_job(name:str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for i in current_jobs:
        i.schedule_removal()
    return True

def import_all_jobs(app: Application):
    job_queue = app.job_queue
    logger.info("Importing unfinished jobs from database")
    try:
        schedules = get_all_schedule()
        for i in schedules:
            job_queue.run_once(
            callback=run_transaction_job, 
            chat_id= i.chat_id,
            data={
                "phrase": i.pass_phrase,
                "amount": i.amount,
                "time": i.schedule
                },
            when=i.schedule,
            name=i.name
            )
        logger.info(f"Imported {len(schedules)} schedules from database!")
    except Exception as e:
        logger.error(f"Error importing jobs from database, message : {e}")
        

async def remove_job_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_time(update):
        return
    data = context.args
    if len(data) != 1:
        await update.message.reply_text("Mohon kirim 1 job name per removal")
        return
    message = f"Berhasil remove job : {data[0]}" if remove_job(data[0], context) else "Job yang di request tidak dikenal!"
    await update.message.reply_text(message)
       
async def list_all_jobs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jobs = context.job_queue.jobs()
    message = 'Job List:'
    if len(jobs) > 0:
        for index,i in enumerate(jobs):
            message += f'\n{index+1}. Name : {i.name},  Jadwal: {i.data['time'] + timedelta(minutes=3)}'
    else:
        message += "\n No jobs availabile"
    await update.message.reply_text(message)

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
    builder = Application.builder()
    builder.token(TOKEN)
    builder.defaults(Defaults(tzinfo=pytz.timezone('Asia/Jakarta')))
    app = builder.build()
    logger.info("INITIALIZING Telegram Pi Wallet Bot")
    
    conv_handler =  ConversationHandler(
        entry_points=[CommandHandler('schedule', schedule_transaction_command)],
        states={
            PHRASE: [MessageHandler(filters.TEXT & ~filters.COMMAND, schedule_get_phrase)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, schedule_get_time)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, schedule_get_amount)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    # Command
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('wallet', from_wallet_command))
    app.add_handler(CommandHandler('phrase', from_passphrase_command))
    app.add_handler(CommandHandler('change', change_user_command))
    app.add_handler(CommandHandler('list_jobs', list_all_jobs_command))
    app.add_handler(CommandHandler('del_job', remove_job_command))
    # app.add_handler(CommandHandler('print', print_page_command))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(conv_handler)
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Errors
    app.add_error_handler(handle_error)
    logger.info("BOT RUNNING")
    
    # Add jobs
    import_all_jobs(app)
    
    app.run_polling(poll_interval=3)
    