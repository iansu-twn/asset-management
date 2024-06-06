import configparser
import json
import logging
import re
from datetime import datetime

import requests
from selenium import webdriver


class Asset:
    def __init__(self, args):
        info = self.information(args)
        self.id = info.get("id")
        self.uid = info.get("uid")
        self.pwd = info.get("pwd")
        self.pin = info.get("pin", "")
        self.api_key = info.get("api_key")
        self.api_secret = info.get("api_secret")
        self.app_id = info.get("app_id")
        self.base_url = info.get("base_url")
        self.timestamp = self.getTimestamp()
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

    def getTimestamp(self):
        return str(round(datetime.now().timestamp() * 1000))

    def getSignature(self, method, endpoint, body=None):
        raise NotImplementedError

    def getHeaders(self, signature):
        raise NotImplementedError

    def send_requests(self, method, endpoint, body=None):
        body_json = json.dumps(body) if body else ""
        signature = self.getSignature(method, endpoint, body_json)
        headers = self.getHeaders(signature)
        url = f"{self.base_url}{endpoint}"
        res = requests.request(method, url, headers=headers, data=body_json)

        if res.status_code == 200:
            return res.json()
        raise Exception(f"Error: {res.status_code}, {res.text}")
