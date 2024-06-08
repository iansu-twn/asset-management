import argparse
import logging
import time

import pandas as pd
from asset import Asset
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Firstrade(Asset):
    def __init__(self, exchange):
        super().__init__(exchange)

    def login(self):
        try:
            self.driver.get(
                "https://invest.firstrade.com/cgi-bin/login?ft_locale=zh-tw"
            )  # noqa: E501
            # fill in the login info
            uid = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[@id='username']")
                )  # noqa: E501
            )
            uid.send_keys(self.uid)

            pwd = self.driver.find_element(By.XPATH, "//*[@id='password']")
            pwd.send_keys(self.pwd)

            btn_login = self.driver.find_element(
                By.XPATH, "//*[@id='loginButton']"
            )  # noqa: E501
            btn_login.click()

            btn_confirm = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div/main/div/div/div[3]/a")
                )
            )
            btn_confirm.click()

            pin = self.driver.find_element(By.XPATH, "//*[@id='pin']")
            pin.send_keys(self.pin)

            btn_pin = self.driver.find_element(
                By.XPATH, "//*[@id='form-pin']/div[2]/button"
            )  # noqa: E501
            btn_pin.click()
            time.sleep(5)
        except Exception as e:
            logging.error(f"Error during login: {e}")
            self.close_driver(self.exchange)

    def info(self):
        try:
            logging.info(f"{self.exchange} LOGIN SUCCESSFUL")
            self.driver.find_element(
                By.XPATH, "//*[@id='myaccount_link']/a"
            ).click()  # noqa: E501
            time.sleep(5)

            # cash
            cash_text = self.driver.find_element(
                By.XPATH,
                "//*[@id='maincontent']/div/table/tbody/tr/td[1]/div/div[2]/table[1]/tbody/tr[1]/td[1]",  # noqa: E501
            ).text
            cash = float(cash_text.replace(",", "").strip()[1:])

            # stock
            self.driver.find_element(
                By.XPATH, "//*[@id='myaccount_menu']/li[2]/a/span"
            ).click()
            time.sleep(3)
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            elem = soup.find("table", {"id": "positiontable"})
            stock = self.parse_table(elem)
            return cash, stock
        except Exception as e:
            logging.error(f"Error retrieving account info: {e}")
            self.close_driver(self.exchange)
            return 0.0, pd.DataFrame()

    def parse_table(self, elem):
        try:
            data = elem.find("tbody").find_all("tr")
            rows = []

            try:
                for row in data:
                    cols = row.find_all("td")
                    dt = {
                        "symbol": cols[0].text.strip(),
                        "qty": cols[1].text,
                        "price": cols[2].text,
                        "cap": float(cols[5].text.replace(",", "")),
                        "unit_cost": float(cols[6].text.replace(",", "")),
                        "total_cost": float(cols[7].text.replace(",", "")),
                        "pnl": float(cols[8].text.replace(",", "").strip()[1:])
                        * (1 if (cols[8].text)[0] == "+" else -1),
                        "pnl_%": float(
                            cols[9].text.replace(",", "").strip()[1:]
                        )  # noqa: E501
                        * (1 if (cols[9].text)[0] == "+" else -1),
                    }
                    rows.append(dt)
            except ValueError as e:
                logging.error(f"Error parsing row: {e}")

            df = pd.DataFrame(rows)
            return df
        except Exception as e:
            logging.error(f"Error parsing table: {e}")
            return pd.DataFrame()


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser("FIRSTRADE INFO")
    args = parser.parse_args()
    exchange = "FIRSTRADE"
    client = Firstrade(exchange)
    try:
        client.login()
        cash, stock = client.info()
        print(f"cash: {round(cash, 3)}")
        print(f"cap: {round(stock.cap.sum(), 3)}")
        print(f"asset: {round(cash + stock.cap.sum(), 3)}")
        print(f"pnl: {round(stock.pnl.sum(), 3)}")
        print(f"cost: {round(stock.total_cost.sum(), 3)}")
        print(
            f"pnl_%: {round(stock.pnl.sum()/stock.total_cost.sum() * 100, 3)}"
        )  # noqa: E501
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        client.close_driver(exchange)
