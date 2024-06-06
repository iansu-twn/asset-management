import argparse
import time

from asset import Asset


class Cathy(Asset):
    def __init__(self, arg):
        super().__init__(arg)

    def login(self):
        self.driver.get("https://www.cathaybk.com.tw/mybank/")

        # fill in the login info
        id = self.driver.find_element("xpath", "//*[@id='CustID']")
        id.send_keys(self.id)

        uid = self.driver.find_element("xpath", "//*[@id='UserIdKeyin']")
        uid.send_keys(self.uid)

        pwd = self.driver.find_element("xpath", "//*[@id='PasswordKeyin']")
        pwd.send_keys(self.pwd)

        btn_login = self.driver.find_element(
            "xpath", "//*[@id='divCUBNormalLogin']/div[2]/button"
        )
        btn_login.click()
        time.sleep(3)

    def info(self):
        # ntd info
        time.sleep(2)
        elem_ntd = self.driver.find_element("xpath", "//*[@id='TD-balance']")
        ntd = self.extract_cash(elem_ntd)

        # foreign info
        self.driver.find_element("xpath", "//*[@id='tabFTD']").click()
        time.sleep(2)
        elem_foreign = self.driver.find_element(
            "xpath", "//*[@id='FTD-balance']"
        )  # noqa: E501
        foreign = self.extract_cash(elem_foreign)

        # stock info
        self.driver.find_element("xpath", "//*[@id='tabFUND']").click()
        time.sleep(2)
        elem_stock = self.driver.find_element(
            "xpath", "//*[@id='FUND-balance']"
        )  # noqa: E501
        stock = self.extract_cash(elem_stock)

        return ntd, foreign, stock

    def logout(self):
        self.driver.find_element(
            "xpath", "//*[@id='sub-menu']/div/div[3]/a[1]"
        ).click()  # noqa: E501


if __name__ == "__main__":
    parser = argparse.ArgumentParser("CATHY INFO")
    args = parser.parse_args()
    client = Cathy("CATHY")
    client.login()
    ntd, foreign, stock = client.info()
    print(f"NTD: {ntd}")
    print(f"foreign: {foreign}")
    print(f"stock: {stock}")
    print(f"total: {ntd+foreign+stock}")
    client.logout()
    client.close_driver()
