from .database import db,TeleUser,PiAccount,PiWallet,PhoneNumber


db.connect()
db.create_tables([TeleUser,PiAccount,PiWallet, PhoneNumber])