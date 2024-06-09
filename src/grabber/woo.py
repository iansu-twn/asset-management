import argparse
import hashlib
import hmac
import logging

import pandas as pd
from asset import Asset


class Woo(Asset):
    def __init__(self, exchange):
        super().__init__(exchange)

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

    def getBalance(self):
        method = "GET"
        endpoint = "/v3/balances"
        try:
            res = self.send_requests(method, endpoint)
            rows = []
            for row in res.get("data").get("holding"):
                dt = {
                    "token": row["token"],
                    "holding": row["holding"] + row["frozen"] + row["staked"],
                    "price": row["markPrice"],
                }
                rows.append(dt)
            df = pd.DataFrame(rows)
            df["value"] = df["holding"] * df["price"]
            logging.info(f"{self.exchange} GET BALANCE SUCCESS")
            return df
        except Exception as e:
            logging.error(f"Error occurred while fetching balances: {e}")
            return pd.DataFrame()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO
    )
    parser = argparse.ArgumentParser("WOO INFO")
    args = parser.parse_args()
    exchange = "WOO"
    client = Woo(exchange)

    try:
        # get balance
        balance = client.getBalance()
        print(f"Cash: {round(balance.value.sum(), 3)}")
    except Exception as e:
        logging.error(f"Error: {e}")
