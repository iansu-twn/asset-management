import argparse
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


class Firstrade:
    def __init__(self, uid, pwd, pin):
        self.uid = uid
        self.pwd = pwd
        self.pin = pin
        self.driver = webdriver.Chrome()

    def login(self):
        self.driver.get(
            "https://invest.firstrade.com/cgi-bin/login?ft_locale=zh-tw"
        )  # noqa: E501
        # fill in the login info
        uid = self.driver.find_element("xpath", "//*[@id='username']")
        uid.send_keys(self.uid)

        pwd = self.driver.find_element("xpath", "//*[@id='password']")
        pwd.send_keys(self.pwd)

        btn_login = self.driver.find_element("xpath", "//*[@id='loginButton']")
        btn_login.click()

        btn_confirm = self.driver.find_element(
            "xpath", "/html/body/div/main/div/div/div[3]/a"
        )
        btn_confirm.click()

        pin = self.driver.find_element("xpath", "//*[@id='pin']")
        pin.send_keys(self.pin)

        btn_pin = self.driver.find_element(
            "xpath", "//*[@id='form-pin']/div[2]/button"
        )  # noqa: E501
        btn_pin.click()
        time.sleep(5)

    def info(self):
        self.driver.find_element(
            "xpath", "//*[@id='myaccount_link']/a"
        ).click()  # noqa: E501
        time.sleep(3)

        cash = float(
            self.driver.find_element(
                "xpath",
                "//*[@id='maincontent']/div/table/tbody/tr/td[1]/"
                + "div/div[2]/table[1]/tbody/tr[1]/td[1]",
            )
            .text.replace(",", "")
            .strip()[1:]
        )

        self.driver.find_element(
            "xpath", "//*[@id='myaccount_menu']/li[2]/a/span"
        ).click()
        time.sleep(3)
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        elem = soup.find("table", {"id": "positiontable"})
        stock = self.parse_table(elem)
        return cash, stock

    def parse_table(self, elem):
        data = elem.find("tbody").find_all("tr")
        rows = []

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
                "pnl_%": float(cols[9].text.replace(",", "").strip()[1:])
                * (1 if (cols[9].text)[0] == "+" else -1),
            }
            rows.append(dt)
        df = pd.DataFrame(rows)
        return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser("FIRSTRADE INFO")
    parser.add_argument("--uid", type=str, help="uid of the firstrade account")
    parser.add_argument("--pwd", type=str, help="pwd of the firstrade account")
    parser.add_argument("--pin", type=str, help="pin of the firstrade account")
    args = parser.parse_args()
    client = Firstrade(args.uid, args.pwd, args.pin)
    client.login()
    cash, stock = client.info()
    print(f"cash: {round(cash, 3)}")
    print(f"cap: {round(stock.cap.sum(), 3)}")
    print(f"asset: {round(cash + stock.cap.sum(), 3)}")
    print(f"pnl: {round(stock.pnl.sum(), 3)}")
    print(f"cost: {round(stock.total_cost.sum(), 3)}")
    print(f"pnl_%: {round(stock.pnl.sum()/stock.total_cost.sum() * 100, 3)}")
