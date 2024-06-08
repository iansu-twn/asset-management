import argparse
import logging

from asset import Asset
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Cathy(Asset):
    def __init__(self, exchange):
        super().__init__(exchange)

    def login(self):
        try:
            self.driver.get("https://www.cathaybk.com.tw/mybank/")

            # fill in the login info
            id = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='CustID']"))
            )
            id.send_keys(self.id)

            uid = self.driver.find_element(By.XPATH, "//*[@id='UserIdKeyin']")
            uid.send_keys(self.uid)

            pwd = self.driver.find_element(
                By.XPATH, "//*[@id='PasswordKeyin']"
            )  # noqa: E501
            pwd.send_keys(self.pwd)

            btn_login = self.driver.find_element(
                By.XPATH, "//*[@id='divCUBNormalLogin']/div[2]/button"
            )
            btn_login.click()

            # wait for the NTC balance element to confirm login success
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//*[@id='TD-balance']")
                )  # noqa: E501
            )
        except Exception as e:
            logging.error(f"Error during login: {e}")
            self.close_driver(self.exchange)

    def info(self):
        logging.info(f"{self.exchange} LOGIN SUCCESSFUL")
        try:
            # ntd info
            elem_ntd = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//*[@id='TD-balance']")
                )  # noqa: E501
            )
            ntd = self.extract_cash(elem_ntd)

            # foreign info
            self.driver.find_element(By.XPATH, "//*[@id='tabFTD']").click()
            elem_foreign = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//*[@id='FTD-balance']")
                )  # noqa: E501
            )
            foreign = self.extract_cash(elem_foreign)

            # stock info
            self.driver.find_element(By.XPATH, "//*[@id='tabFUND']").click()
            elem_stock = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//*[@id='FUND-balance']")
                )  # noqa: E501
            )
            stock = self.extract_cash(elem_stock)
            return ntd, foreign, stock
        except Exception as e:
            logging.error(f"Error when retrieving account info: {e}")
            self.close_driver(self.exchange)
            return 0.0, 0.0, 0.0

    def logout(self):
        try:
            self.driver.find_element(
                By.XPATH, "//*[@id='sub-menu']/div/div[3]/a[1]"
            ).click()
        except Exception as e:
            logging.error(f"Error when logout: {e}")


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser("CATHY INFO")
    args = parser.parse_args()
    exchange = "CATHY"
    client = Cathy(exchange)
    try:
        client.login()
        ntd, foreign, stock = client.info()
        print(f"NTD: {ntd}")
        print(f"foreign: {foreign}")
        print(f"stock: {stock}")
        print(f"total: {ntd+foreign+stock}")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        client.logout()
        client.close_driver(exchange)
