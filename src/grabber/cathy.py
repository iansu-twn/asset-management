import argparse
import time

from selenium import webdriver


class Cathy:
    def __init__(self, id, uid, pwd):
        self.id = id
        self.uid = uid
        self.pwd = pwd
        self.driver = webdriver.Chrome()

    def login(self):
        self.driver.get("https://www.cathaybk.com.tw/mybank/")

        # fill in the login info
        id = self.driver.find_element("xpath", "//*[@id='CustID']")
        id.send_keys(self.id)

        uid = self.driver.find_element("xpath", "//*[@id='UserIdKeyin']")
        uid.send_keys(self.uid)

        pwd = self.driver.find_element("xpath", "//*[@id='PasswordKeyin']")
        pwd.send_keys(self.pwd)

        btn_login = self.driver.find_element(
            "xpath", "//*[@id='divCUBNormalLogin']/div[2]/button"
        )
        btn_login.click()
        time.sleep(3)

    def close_driver(self):
        self.driver.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("CATHY INFO")
    parser.add_argument("--id", type=str)
    parser.add_argument("--uid", type=str)
    parser.add_argument("--pwd", type=str)
    args = parser.parse_args()
    client = Cathy(args.id, args.uid, args.pwd)
    client.login()
    client.close_driver()
