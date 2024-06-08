import argparse
import logging

from asset import Asset


class Binance(Asset):
    def __init__(self, exchange):
        super().__init__(exchange)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser("BINANCE INFO")
    args = parser.parse_args()
    exchange = "BINANCE"
    client = Binance(exchange)
