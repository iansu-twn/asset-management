import argparse

from asset import Asset


class Ctbc(Asset):
    def __init__(self, arg):
        super().__init__(arg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("CTBC INFO")
    args = parser.parse_args()
    client = Ctbc("CTBC")
