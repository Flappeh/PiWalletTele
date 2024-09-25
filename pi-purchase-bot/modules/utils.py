from time import time
import os
import logging
import sys
from .database import PiWallet,PiAccount, Schedule
from datetime import datetime, timedelta

dir_path = os.path.dirname(os.path.realpath(__file__))
loggers = {}

def get_logger(name=None):
    global loggers
    if not name:
        name = __name__
    if loggers.get(name):
        return loggers.get(name)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger

logger = get_logger()

def store_phrase(phrase:str, balance: str):
    try:
        wallet = PiWallet.get(
            PiWallet.pass_phrase == phrase
        )
        wallet.balance = balance
        wallet.last_update = datetime.now()
        wallet.save()
    except:
        logger.info("Wallet doesn't exist, creating one")
        PiWallet.create(
            balance = balance,
            pass_phrase = phrase
        )
        
        
def get_wallet_account() -> PiAccount:
    account  = PiAccount.select().where(PiAccount.last_used < datetime.now() - timedelta(days=1)).get()
    account.last_used = datetime.now()
    account.save()
    print(f"Account : {account}")
    return account

def delete_wallet_account(account: PiAccount):
    PiAccount.delete(account)

def get_all_schedule():
    try:
        schedules = Schedule.select().where(Schedule.done == False)
        return schedules
    except:
        logger.error("Error getting schedules list")

def store_schedule(job_name,chat_id, user_data):
    try:
        schedule: Schedule = Schedule.create(
            name=job_name,
            chat_id=chat_id,
            pass_phrase = user_data['phrase'],
            schedule = user_data['time'],
            amount = user_data['amount']
        )
        schedule.save()
    except:
        logger.error(f"Error saving schedule for phrase: {user_data['phrase']}")

def check_schedule(time: datetime):
    logger.debug(f"Checking schedule table for time : {time}")
    try:
        schedules = Schedule.select().where(
            Schedule.schedule.between(time - timedelta(minutes=30), time + timedelta(minutes=30))
        )
        if len(schedules) != 0:
            return False
        return True        
    except:
        logger.error("Error checking schedule")
        return False
def finish_schedule(job_name):
    try:
        schedule = Schedule.get(Schedule.name == job_name)
        schedule.done = True
        schedule.save()
    except:
        logger.error(f"Error updating finished schedule with name : {job_name}")