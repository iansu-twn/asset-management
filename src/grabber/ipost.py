import argparse
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class Ipost():
    def __init__(self, id, uid, pwd):
        self.id = id
        self.uid = uid
        self.pwd = pwd
        self.driver = webdriver.Chrome()

    def login(self):
        self.driver.get(
            "https://ipost.post.gov.tw/pst/home.html"
        )
        # check scam msg
        try:
            elem = self.driver.find_element(
                "xpath",
                "//*[@id='modal']/div[2]/button"
            )
            elem.click()
        except NoSuchElementException:
            pass

        # change login page
        time.sleep(3)
        self.driver.find_element(
            "xpath",
            "//*[@id='content_wh']/div[1]/div/ul/li[1]/a"
        ).click()

        # fill in the login info
        id = self.driver.find_element(
            "xpath",
            "//*[@id='cifID']"
        )
        id.send_keys(self.id)

        uid = self.driver.find_element(
            "xpath",
            "//*[@id='userID_1_Input']"
        )
        uid.send_keys(self.uid)

        pwd = self.driver.find_element(
            "xpath",
            "//*[@id='userPWD_1_Input']"
        )
        pwd.send_keys(self.pwd)

        # ocr verification code


if __name__ == "__main__":
    parser = argparse.ArgumentParser("IPOST INFO")
    parser.add_argument("--id", type=str)
    parser.add_argument("--uid", type=str)
    parser.add_argument("--pwd", type=str)
    args = parser.parse_args()

    client = Ipost(args.id, args.uid, args.pwd)
    client.login()
