import argparse
import time

import ddddocr
from asset import Asset
from selenium.common.exceptions import NoSuchElementException


class Ipost(Asset):
    def __init__(self, arg):
        super().__init__(arg)

    def login(self):
        self.driver.get("https://ipost.post.gov.tw/pst/home.html")
        flag = True
        while flag:
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
            time.sleep(3)
            # fill in the login info
            id = self.driver.find_element("xpath", "//*[@id='cifID']")
            id.send_keys(self.id)

            uid = self.driver.find_element(
                "xpath", "//*[@id='userID_1_Input']"
            )  # noqa: E501
            uid.send_keys(self.uid)

            pwd = self.driver.find_element(
                "xpath", "//*[@id='userPWD_1_Input']"
            )  # noqa: E501
            pwd.send_keys(self.pwd)

            # ocr verification
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
                self.driver.switch_to.alert.accept()
            except Exception:
                flag = False
                break
            self.driver.refresh()
            time.sleep(3)
        time.sleep(10)

    def info(self):
        elem = self.driver.find_element(
            "xpath", "//*[@id='css_table2']/div[2]/div[3]/span"
        )
        cash = self.extract_cash(elem)
        return cash


if __name__ == "__main__":
    parser = argparse.ArgumentParser("IPOST INFO")
    args = parser.parse_args()
    client = Ipost("IPOST")
    client.login()
    cash = client.info()
    print(f"Cash: {cash}")
    client.close_driver()
