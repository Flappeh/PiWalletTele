from time import time
import os
import logging
import sys
from .database import db, PiWallet

dir_path = os.path.dirname(os.path.realpath(__file__))
loggers = {}

def get_logger():
    global loggers
    if loggers.get(__name__):
        return loggers.get(__name__)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger

def store_phrase(phrase:str, balance: str):
    PiWallet.replace(
            pass_phrase = phrase,
            balance = balance
        ).on_conflict_replace().execute()