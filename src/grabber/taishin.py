import argparse
import time

import ddddocr
from asset import Asset
from selenium.common.exceptions import NoSuchElementException


class Taishin(Asset):
    def __init__(self, arg):
        super().__init__(arg)

    def login(self):
        self.driver.get("https://richart.tw/WebBank/users/login?lang=zh-tw")
        time.sleep(3)
        # fill in the login info
        id = self.driver.find_element("xpath", "//*[@id='userId']/input")
        id.send_keys(self.id)

        uid = self.driver.find_element("xpath", "//*[@id='userName']/input")
        uid.send_keys(self.uid)

        pwd = self.driver.find_element(
            "xpath",
            "/html/body/app-root/div/app-users/div/app-login/main/div/"
            + "div[1]/div/div[2]/div[1]/div[1]/form/div[1]"
            + "/div/div[3]/div/input",
        )
        pwd.send_keys(self.pwd)

        # ocr verification
        flag = True
        while flag:
            image = self.driver.find_element(
                "xpath",
                "/html/body/app-root/div/app-users/div/app-login/main/"
                + "div/div[1]/div/div[2]/div[1]/div[1]/form/div[1]/div/"
                + "div[4]/div/div[2]/div",
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
                + "div[4]/div/div[1]/div/input",
            )
            code.send_keys(catch)
            self.driver.find_element(
                "xpath",
                "/html/body/app-root/div/app-users/div/app-login/main/"
                + "div/div[1]/div/div[2]/div[1]/div[1]/form/div[2]/button",
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

    def info(self):
        unhidden = self.driver.find_element(
            "xpath", "//*[@id='toggleShowAmount']/i[1]"
        )  # noqa: E501
        unhidden.click()
        time.sleep(3)
        elem = self.driver.find_element(
            "xpath", "//*[@id='first-element-introduction']/div[1]/div[2]/div"
        )
        cash = self.extract_cash(elem)
        return cash

    def logout(self):
        self.driver.find_element(
            "xpath",
            "/html/body/app-root/div/app-dashboard/richart-header/header/div/div/nav/div[2]/div/a",  # noqa: E501
        ).click()
        self.driver.find_element(
            "xpath",
            "/html/body/ngb-modal-window/div/div/app-modal/div[2]/div[2]/button",  # noqa: E501
        ).click()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("TAISHIN INFO")
    args = parser.parse_args()
    client = Taishin("TAISHIN")
    client.login()
    cash = client.info()
    print(f"Cash: {cash}")
    client.logout()
    client.close_driver()
