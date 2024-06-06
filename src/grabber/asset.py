import configparser
import logging
import re

from selenium import webdriver


class Asset:
    def __init__(self, args):
        info = self.information(args)
        self.id = info.get("id")
        self.uid = info.get("uid")
        self.pwd = info.get("pwd")
        self.pin = info.get("pin", "")
        self.driver = webdriver.Chrome()

    def information(self, arg):
        cfg = configparser.ConfigParser()
        cfg.read("./config/info.ini")
        info = {}
        for option in cfg.options(arg):
            info[option] = cfg.get(arg, option)
        return info

    def extract_cash(self, elem):
        try:
            text = elem.text.strip()
            cash = re.sub(r"[^\d.-]", "", text)
            return int(cash)
        except ValueError:
            logging.info("Couldn't extract cash")
            return 0
        except Exception as e:
            print(e)
            return 0

    def close_driver(self):
        self.driver.close()
