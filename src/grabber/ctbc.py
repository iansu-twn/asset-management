import argparse

from selenium import webdriver


class Ctbc:
    def __init__(self, id, uid, pwd):
        self.id = id
        self.uid = uid
        self.pwd = pwd
        self.driver = webdriver.Chrome()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("CTBC INFO")
    parser.add_argument("--id", type=str)
    parser.add_argument("--uid", type=str)
    parser.add_argument("--pwd", type=str)
    args = parser.parse_args()
    client = Ctbc(args.id, args.uid, args.pwd)