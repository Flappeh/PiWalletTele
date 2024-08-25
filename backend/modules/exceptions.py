from telegram.error import BadRequest

class InvalidWalletKeyError(BadRequest):
    def __init__(self, message: str):
        super().__init__(message)