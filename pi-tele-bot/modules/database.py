from peewee import *
import os

DIRNAME = os.getcwd()

db = SqliteDatabase(DIRNAME + '/data/database.db')

class TeleUser(Model):
    name = CharField()
    phone = CharField()
    pasword = CharField()
    
    class Meta:
        database = db


class PiAccount(Model):
    phone = CharField()
    password = CharField()
    
    class Meta:
        database = db
    

class PiWallet(Model):
    public_key = CharField()
    pass_phrase = CharField()
    balance = FloatField()
    
    class Meta:
        database = db
    
class PhoneNumber(Model):
    phone = CharField()
    last_used = DateTimeField()

db.connect()
db.create_tables([TeleUser,PiAccount,PiWallet, PhoneNumber])