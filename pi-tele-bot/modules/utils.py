from time import time
import os
import logging
import sys

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

# def hmacDigest(data:str, key:str):
#     keyEncoded = key.encode()
#     dataEncoded = data.encode()

#     h = hmac.new(keyEncoded, dataEncoded, hashlib.sha256)

#     return h.hexdigest()

# def hash_password(password: str):
#     return bcrypt.hashpw(str.encode(password), bcrypt.gensalt(12))

# def check_password(password: str, hashed_pass:str):
#     return bcrypt.checkpw(str.encode(password), str.encode(hashed_pass))
