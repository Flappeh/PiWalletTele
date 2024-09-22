from .database import db,TeleUser,PiAccount,PiWallet,Schedule


db.connect()
db.create_tables([TeleUser,PiAccount,PiWallet,Schedule])