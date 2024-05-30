import argparse
import time

import ddddocr
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class Taishin():
    def __init__(self, id, uid, pwd):
        self.id = id
        self.uid = uid
        self.pwd = pwd
        self.driver = webdriver.Chrome()

    def login(self):
        self.driver.get(
            "https://richart.tw/WebBank/users/login?lang=zh-tw"
        )
        time.sleep(3)
        # fill in the login info
        id = self.driver.find_element(
            "xpath",
            "//*[@id='userId']/input"
        )
        id.send_keys(self.id)

        uid = self.driver.find_element(
            "xpath",
            "//*[@id='userName']/input"
        )
        uid.send_keys(self.uid)

        pwd = self.driver.find_element(
            "xpath",
            "/html/body/app-root/div/app-users/div/app-login/main/div/"
            + "div[1]/div/div[2]/div[1]/div[1]/form/div[1]"
            + "/div/div[3]/div/input"
        )
        pwd.send_keys(self.pwd)

        # ocr verification
        flag = True
        while flag:
            image = self.driver.find_element(
                "xpath",
                "/html/body/app-root/div/app-users/div/app-login/main/"
                + "div/div[1]/div/div[2]/div[1]/div[1]/form/div[1]/div/"
                + "div[4]/div/div[2]/div"
            )
            image.screenshot("code.png")
            ocr = ddddocr.DdddOcr(show_ad=False)
            with open("code.png", "rb") as fp:
                img = fp.read()
            catch = ocr.classification(img)
            code = self.driver.find_element(
                "xpath",
                "/html/body/app-root/div/app-users/div/app-login/main/"
                + "div/div[1]/div/div[2]/div[1]/div[1]/form/div[1]/div/"
                + "div[4]/div/div[1]/div/input"
            )
            code.send_keys(catch)
            self.driver.find_element(
                "xpath",
                "/html/body/app-root/div/app-users/div/app-login/main/"
                + "div/div[1]/div/div[2]/div[1]/div[1]/form/div[2]/button"
            ).click()
            try:
                time.sleep(5)
                elem = self.driver.find_element(
                    "xpath",
                    "/html/body/ngb-modal-window/div/div/app-modal/"
                    + "div[2]/div/button"
                )
                elem.click()
            except NoSuchElementException:
                flag = False
        time.sleep(3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("TAISHIN INFO")
    parser.add_argument("--id", type=str)
    parser.add_argument("--uid", type=str)
    parser.add_argument("--pwd", type=str)
    args = parser.parse_args()
    client = Taishin(args.id, args.uid, args.pwd)
    client.login()
