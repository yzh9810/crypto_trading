import asyncio

class UserAccountParam:
    def __init__(self, accountId, key, secret, passphrase):
        self.accountId = accountId
        self.apiKey = key
        self.apiSecret = secret
        self.passphrase = passphrase
        self.orderLock = asyncio.Lock()