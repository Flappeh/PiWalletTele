from dotenv import load_dotenv
import os
from typing import Final

load_dotenv(override=True)

TOKEN = os.getenv("TOKEN") 
BOT_USERNAME  = os.getenv("BOT_USERNAME") 
BLOCKCHAIN_URI = os.getenv("BLOCKCHAIN_URI") 
ANDROID_SERVER_URL= os.getenv("ANDROID_SERVER_URL")
WALLET_DEST= os.getenv("WALLET_DEST")
DEV_MODE = bool(os.getenv("DEV_MODE")) if os.getenv("DEV_MODE") else False
TIMEOUT_LIMIT = int(os.getenv("TIMEOUT_LIMIT"))
TRY_SEND_DURATION = int(os.getenv("TRY_SEND_DURATION"))

def get_all_env():
    data = [f"{i}: {j}" for i,j in os.environ.items()]
    return "\n".join(data)
