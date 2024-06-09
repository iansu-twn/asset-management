import argparse
import logging

import ddddocr
from asset import Asset
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TIME = 20


class Taishin(Asset):
    def __init__(self, arg):
        super().__init__(arg)

    def login(self):
        try:
            self.driver.get(
                "https://richart.tw/WebBank/users/login?lang=zh-tw"
            )  # noqa: E501

            # fill in the login info
            id = WebDriverWait(self.driver, TIME).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[@id='userId']/input")
                )  # noqa: E501
            )
            id.send_keys(self.id)

            uid = self.driver.find_element(
                By.XPATH, "//*[@id='userName']/input"
            )  # noqa: E501
            uid.send_keys(self.uid)

            pwd = self.driver.find_element(
                By.XPATH,
                "/html/body/app-root/div/app-users/div/app-login/main/div/"
                + "div[1]/div/div[2]/div[1]/div[1]/form/div[1]"
                + "/div/div[3]/div/input",
            )
            pwd.send_keys(self.pwd)

            # ocr verification
            flag = True
            while flag:
                captcha_image = self.driver.find_element(
                    By.XPATH,
                    "/html/body/app-root/div/app-users/div/app-login/main/"
                    + "div/div[1]/div/div[2]/div[1]/div[1]/form/div[1]/div/"
                    + "div[4]/div/div[2]/div",
                )
                captcha_image.screenshot("code.png")
                ocr = ddddocr.DdddOcr(show_ad=False)
                with open("code.png", "rb") as fp:
                    img = fp.read()
                captcha_code = ocr.classification(img)
                code = self.driver.find_element(
                    By.XPATH,
                    "/html/body/app-root/div/app-users/div/app-login/main/"
                    + "div/div[1]/div/div[2]/div[1]/div[1]/form/div[1]/div/"
                    + "div[4]/div/div[1]/div/input",
                )
                code.send_keys(captcha_code)

                WebDriverWait(self.driver, TIME).until(
                    (
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                "/html/body/app-root/div/app-users/div/app-login/main/"  # noqa: E501
                                + "div/div[1]/div/div[2]/div[1]/div[1]/form/div[2]/button",  # noqa: E501
                            )
                        )
                    )
                ).click()

                try:
                    WebDriverWait(self.driver, TIME).until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                "/html/body/ngb-modal-window/div/div/app-modal/div[2]/div/button",  # noqa: E501
                            )
                        ),
                    ).click()
                except TimeoutException:
                    flag = False
                    logging.info(f"{self.exchange} LOGIN SUCCESSFUL")
        except Exception as e:
            logging.error(f"Error occurred while login: {e}")

    def info(self):
        # scam message confirm
        try:
            btn_scam = WebDriverWait(self.driver, TIME).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//*[@id='jqBtnCloseCookie']")
                )  # noqa: E501
            )
            btn_scam.click()
        except TimeoutException:
            pass

        unhidden = WebDriverWait(self.driver, TIME).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@id='toggleShowAmount']/i[1]")
            )
        )  # noqa: E501
        unhidden.click()

        elem = WebDriverWait(self.driver, TIME).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[@id='first-element-introduction']/div[1]/div[2]/div",
                )  # noqa: E501
            )
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
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO
    )
    parser = argparse.ArgumentParser("TAISHIN INFO")
    args = parser.parse_args()
    exchange = "TAISHIN"
    client = Taishin(exchange)
    try:
        client.login()
        cash = client.info()
        print(f"Cash: {cash}")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        client.logout()
        client.close_driver(exchange)
