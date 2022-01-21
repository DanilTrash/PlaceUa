from random import choice
from time import sleep

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from logger import log

logger = log(__name__)


class Placeua:
    def __init__(self, proxy, login, password, headless=False):
        options = webdriver.ChromeOptions()
        self.login = login
        self.password = password
        if headless:
            options.add_argument('--headless')
        options.add_argument('--proxy-server=%s' % proxy)
        self.driver = webdriver.Chrome(options=options)
        # self.driver.minimize_window()
        logger.info(options.arguments)

    def auth(self):
        self.driver.get('https://place.ua/user/login')
        logger.info([self.login, self.password])
        WebDriverWait(self.driver, 10).until(
            lambda d: self.driver.execute_script('return document.readyState;') == 'complete')

        email_xpath = '//*[@id="j-u-login-email"]'
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, email_xpath))).send_keys(self.login)
        password_xpath = '//*[@id="j-u-login-pass"]'
        self.driver.find_element_by_xpath(password_xpath).send_keys(self.password)

        submit_xpath = '//*[@type="submit"]'
        self.driver.find_element_by_xpath(submit_xpath).click()
        alert_xpath = '//*[@id="j-alert-global"]/div/div/p'
        sleep(0.5)
        dobavit_obyavlenie_xpath = '//*[@href="https://place.ua/item/add"]'
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, dobavit_obyavlenie_xpath)))
        except TimeoutException as error:
            logger.warning(error)
            return False
        return True

    def dobavit_obyavlenie(self, title, description, phone):
        logger.info(title)
        self.driver.get('https://place.ua/item/add')
        category_xpath = '//span[text()="Начало карьеры, студенты"]'
        price_xpath = '//*[@name="price"]'
        phone_xpath = '//*[@name="phones[1]"]'
        title_xpath = '//*[@id="j-i-title"]'
        self.driver.find_element_by_xpath(title_xpath).send_keys(title)
        j_i_form_xpath = '//*[@id="j-i-form"]/div[2]/div/div/div[2]/a'
        self.driver.find_element_by_xpath(j_i_form_xpath).click()
        rabota_xpath = '//*[@id="j-i-form"]/div[2]/div/div/div[3]/div/div[1]/div/a[9]/img'
        self.driver.find_element_by_xpath(rabota_xpath).click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, category_xpath))).click()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, price_xpath))).send_keys(f'2{str(choice(range(0, 5)))}000')
        val_xpath = '//select[@name="d[6][572]"]/option[2]'
        self.driver.find_element_by_xpath(val_xpath).click()
        val_xpath = '//select[@name="d[6][571]"]/option[2]'
        self.driver.find_element_by_xpath(val_xpath).click()
        description_xpath = '//*[@id="j-i-descr"]'
        for letter in description:
            self.driver.find_element_by_xpath(description_xpath).send_keys(letter)
        hr_xpath = '//*[@id="j-i-name"]'
        element = self.driver.find_element_by_xpath(hr_xpath)
        element.clear()
        element.send_keys(choice(['Юлия', 'Алёна']))
        self.driver.find_element_by_xpath(phone_xpath).send_keys(phone)
        submit_xpath = '//*[@value="Опубликовать объявление"]'
        element = self.driver.find_element_by_xpath(submit_xpath)
        element.click()
        return True


def main():
    from itertools import cycle
    df = pd.read_csv('https://docs.google.com/spreadsheets/d/1zaxjdu9ESYy2MCNuDow0_5PnZpwEsyr'
                     'dTQ_kk0PMZbw/export?format=csv&id=1zaxjdu9ESYy2MCNuDow0_5PnZ'
                     'pwEsyrdTQ_kk0PMZbw&gid=892686484', dtype={'phone': str, 'proxy': str})
    titles = cycle(df['title'].dropna().tolist())
    descriptions = cycle(df['description'].dropna().tolist())
    phones = cycle(df['phone'].dropna().tolist())
    logins = df['login'].dropna().tolist()
    passwords = df['password'].dropna().tolist()
    proxy = df['proxy'].dropna().tolist()
    headless = False
    place = Placeua(proxy[0], logins[0], passwords[0], headless=headless)
    place.auth()
    while True:
        place.dobavit_obyavlenie(next(titles), next(descriptions), next(phones))


if __name__ == '__main__':
    try:
        logger.info(__name__)
        main()
    except Exception as error:
        logger.exception(error)
