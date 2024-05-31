import argparse
import time

import ddddocr
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class Ipost:
    def __init__(self, id, uid, pwd):
        self.id = id
        self.uid = uid
        self.pwd = pwd
        self.driver = webdriver.Chrome()

    def login(self):
        self.driver.get("https://ipost.post.gov.tw/pst/home.html")
        # check scam msg
        try:
            elem = self.driver.find_element(
                "xpath", "//*[@id='modal']/div[2]/button"
            )  # noqa: E501
            elem.click()
        except NoSuchElementException:
            pass

        # change login page
        time.sleep(3)
        self.driver.find_element(
            "xpath", "//*[@id='content_wh']/div[1]/div/ul/li[1]/a"
        ).click()

        # fill in the login info
        id = self.driver.find_element("xpath", "//*[@id='cifID']")
        id.send_keys(self.id)

        uid = self.driver.find_element("xpath", "//*[@id='userID_1_Input']")
        uid.send_keys(self.uid)

        pwd = self.driver.find_element("xpath", "//*[@id='userPWD_1_Input']")
        pwd.send_keys(self.pwd)

        # ocr verification
        flag = True
        while flag:
            image = self.driver.find_element(
                "xpath", "//*[@id='tab1']/div[14]/img"
            )  # noqa: E501
            image.screenshot("code.png")
            ocr = ddddocr.DdddOcr(show_ad=False)
            with open("code.png", "rb") as fp:
                img = fp.read()
            catch = ocr.classification(img)
            code = self.driver.find_element(
                "xpath", "//*[@id='tab1']/div[11]/input"
            )  # noqa: E501
            code.send_keys(catch)
            self.driver.find_element(
                "xpath",
                "//*[@id='tab1']/div[12]/a",
            ).click()
            try:
                time.sleep(5)
                elem = self.driver.find_element(
                    "xpath",
                    "/html/body/ngb-modal-window/div/div/app-modal/"
                    + "div[2]/div/button",
                )
                elem.click()
            except NoSuchElementException:
                flag = False
        time.sleep(3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("IPOST INFO")
    parser.add_argument("--id", type=str)
    parser.add_argument("--uid", type=str)
    parser.add_argument("--pwd", type=str)
    args = parser.parse_args()
    client = Ipost(args.id, args.uid, args.pwd)
    client.login()
