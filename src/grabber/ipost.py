import argparse
import logging

import ddddocr
from asset import Asset
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Ipost(Asset):
    def __init__(self, exchange):
        super().__init__(exchange)

    def login(self):
        try:
            self.driver.get("https://ipost.post.gov.tw/pst/home.html")
            flag = True
            while flag:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//*[@id='modal']/div[2]/button")
                        )
                    ).click()
                except TimeoutException:
                    pass

                # change login page
                btn_login = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//*[@id='content_wh']/div[1]/div/ul/li[1]/a",
                        )  # noqa:E501
                    )
                )
                btn_login.click()
                # fill in the login info
                id = self.driver.find_element(By.XPATH, "//*[@id='cifID']")
                id.send_keys(self.id)

                uid = self.driver.find_element(
                    By.XPATH, "//*[@id='userID_1_Input']"
                )  # noqa: E501
                uid.send_keys(self.uid)

                pwd = self.driver.find_element(
                    By.XPATH, "//*[@id='userPWD_1_Input']"
                )  # noqa: E501
                pwd.send_keys(self.pwd)

                # ocr verification
                captcha_image = self.driver.find_element(
                    By.XPATH, "//*[@id='tab1']/div[14]/img"
                )  # noqa: E501
                captcha_image.screenshot("code.png")
                ocr = ddddocr.DdddOcr(show_ad=False)
                with open("code.png", "rb") as fp:
                    img = fp.read()
                captch_code = ocr.classification(img)
                code = self.driver.find_element(
                    By.XPATH, "//*[@id='tab1']/div[11]/input"
                )  # noqa: E501
                code.send_keys(captch_code)
                self.driver.find_element(
                    By.XPATH,
                    "//*[@id='tab1']/div[12]/a",
                ).click()
                try:
                    WebDriverWait(self.driver, 3).until(
                        EC.alert_is_present()
                    ).accept()  # noqa:E501
                except TimeoutException:
                    flag = False

                if flag:
                    self.driver.refresh()

            # confirm login success
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@id='wrapper']/div/div/div/ng-include/div/div[1]/div/div[1]",  # noqa:E501
                    )
                )
            )
            logging.info(f"{self.exchange} LOGIN SUCCESSFUL")
            # time.sleep(10)
        except Exception as e:
            logging.error(f"Error occurred while trying to login: {e}")
            self.close_driver(exchange)

    def info(self):
        try:
            elem = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//*[@id='css_table2']/div[2]/div[3]/span")
                )
            )
            cash = self.extract_cash(elem)
            return cash
        except Exception as e:
            logging.error(f"Error occurred while fetching account info: {e}")
            self.close_driver(exchange)
            return 0.0


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser("IPOST INFO")
    args = parser.parse_args()
    exchange = "IPOST"
    client = Ipost(exchange)
    try:
        client.login()
        cash = client.info()
        print(f"Cash: {cash}")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        client.close_driver(exchange)
