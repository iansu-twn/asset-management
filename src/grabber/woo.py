import hashlib
import hmac

from asset import Asset


class Woo(Asset):
    def __init__(self, arg):
        super().__init__(arg)

    def getSignature(self, method, endpoint, body=""):
        sign_string = f"{self.timestamp}{method}{endpoint}{body}"
        return hmac.new(
            self.api_secret.encode(), sign_string.encode(), hashlib.sha256
        ).hexdigest()

    def getHeaders(self, signature):
        return {
            "x-api-key": self.api_key,
            "x-api-signature": signature,
            "x-api-timestamp": self.timestamp,
            "Content-Type": "application/json",
        }
