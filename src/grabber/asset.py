import configparser
import json
import logging
import re
import time
from datetime import datetime

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Asset:
    def __init__(self, exchange, config_path="./config/info.ini"):
        self.exchange = exchange
        info = self.information(self.exchange, config_path)
        self.id = info.get("id")
        self.uid = info.get("uid")
        self.pwd = info.get("pwd")
        self.pin = info.get("pin", "")
        self.api_key = info.get("api_key")
        self.api_secret = info.get("api_secret")
        self.app_id = info.get("app_id")
        self.base_url = info.get("base_url")
        self.timestamp = self.getTimestamp()

        # configure chrome options
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=chrome_options)

    def information(self, arg, config_path):
        cfg = configparser.ConfigParser()
        try:
            cfg.read(config_path)
            if arg not in cfg.sections():
                raise ValueError(f"Configuration section {arg} not found")
            info = {}
            for option in cfg.options(arg):
                info[option] = cfg.get(arg, option)
            return info

        except Exception as e:
            logging.error(f"Error reading configuration: {e}")
            raise

    def extract_cash(self, elem):
        try:
            text = elem.text.strip()
            cash = re.sub(r"[^\d.-]", "", text)
            return float(cash)
        except ValueError:
            logging.info("Couldn't extract cash")
            return 0.0
        except Exception as e:
            logging.info(f"Unexcepted error in extract_cash: {e}")
            return 0.0

    def close_driver(self, arg):
        self.driver.close()
        logging.info(f"{arg} LOGOUT SUCCESSFUL")

    def getTimestamp(self):
        return str(round(datetime.now().timestamp() * 1000))

    def getSignature(self, method, endpoint, body=None):
        raise NotImplementedError

    def getHeaders(self, signature):
        raise NotImplementedError

    def send_requests(self, method, endpoint, body=None, retries=5, sleep=1):
        body_json = json.dumps(body) if body else ""
        signature = self.getSignature(method, endpoint, body_json)
        headers = self.getHeaders(signature)
        url = f"{self.base_url}{endpoint}"

        attempt = 0
        while attempt < retries:
            try:
                res = requests.request(
                    method, url, headers=headers, data=body_json
                )  # noqa: E501
                res.raise_for_status()
                return res.json()
            except requests.exceptions.HTTPError as http_err:
                logging.error(
                    f"HTTP error occurred: {res.status_code}:{http_err}"
                )  # noqa: E501
            except requests.exceptions.RequestException as req_err:
                logging.error(f"Request error occurred: {req_err}")
            except Exception as err:
                logging.error(f"Other error occurred: {err}")

            attempt += 1
            time.sleep(sleep)
        raise Exception(
            f"Failed to get a successful response after {retries} attempts"
        )  # noqa: E501
