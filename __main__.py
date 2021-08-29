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
    def __init__(self, proxy, headless=False):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--proxy-server=%s' % proxy)
        self.driver = webdriver.Chrome(options=options)
        self.driver.minimize_window()
        logger.info(options.arguments)

    def auth(self, login, password):
        self.driver.get('https://place.ua/user/login')
        logger.info([login, password])
        WebDriverWait(self.driver, 10).until(
            lambda d: self.driver.execute_script('return document.readyState;') == 'complete')

        email_xpath = '//*[@id="j-u-login-email"]'
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, email_xpath))).send_keys(login)
        password_xpath = '//*[@id="j-u-login-pass"]'
        self.driver.find_element_by_xpath(password_xpath).send_keys(password)

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
        logger.info('Auth: True')
        return True

    def dobavit_obyavlenie(self, title, description, phone):
        logger.info(title)
        self.driver.get('https://place.ua/item/add')
        WebDriverWait(self.driver, 10).until(
            lambda d: self.driver.execute_script('return document.readyState;') == 'complete')
        title_xpath = '//*[@id="j-i-title"]'
        self.driver.find_element_by_xpath(title_xpath).send_keys(title)
        j_i_form_xpath = '//*[@id="j-i-form"]/div[2]/div/div/div[2]/a'
        self.driver.find_element_by_xpath(j_i_form_xpath).click()
        rabota_xpath = '//*[@id="j-i-form"]/div[2]/div/div/div[3]/div/div[1]/div/a[9]/img'
        self.driver.find_element_by_xpath(rabota_xpath).click()
        category_xpath = '//span[text()="Начало карьеры, студенты"]'
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, category_xpath))).click()
        price_xpath = '//*[@name="price"]'
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, price_xpath))).send_keys(f'1{str(choice(range(6, 9)))}000')
        val_xpath = '//select[@name="d[6][572]"]/option[2]'
        self.driver.find_element_by_xpath(val_xpath).click()
        val_xpath = '//select[@name="d[6][571]"]/option[2]'
        self.driver.find_element_by_xpath(val_xpath).click()
        description_xpath = '//*[@id="j-i-descr"]'
        self.driver.find_element_by_xpath(description_xpath).send_keys(description)
        hr_xpath = '//*[@id="j-i-name"]'
        element = self.driver.find_element_by_xpath(hr_xpath)
        element.clear()
        element.send_keys(choice(['Юлия', 'Алёна']))
        phone_xpath = '//*[@name="phones[1]"]'
        self.driver.find_element_by_xpath(phone_xpath).send_keys(phone)
        submit_xpath = '//*[@value="Опубликовать объявление"]'
        element = self.driver.find_element_by_xpath(submit_xpath)
        element.click()
        return True

    def end(self):
        logger.info('ending session')
        self.driver.quit()

    def ubrat_obyavlenie(self):
        logger.info('ubrat_obyavlenie')
        self.driver.get('https://place.ua/cabinet/items?status=1&page=1&pp=-1')
        type_checkbox_xpath = '//*[@type="checkbox"]'
        try:
            self.driver.find_element_by_xpath(type_checkbox_xpath).click()
        except NoSuchElementException as error:
            logger.warning(error)
            return False
        title_xpath = '//*[@class="j-sel-title"]'
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, title_xpath))).click()
        select_ = '//*[@class="j-mass-select"]'
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, select_))).click()
        self.driver.find_element_by_class_name('j-sel-action').click()
        self.driver.get('https://place.ua/cabinet/items?status=3&page=1&pp=-1')
        self.driver.find_element_by_xpath(type_checkbox_xpath).click()
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, title_xpath))).click()
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, select_))).click()
        mass_delete = '//li[2]/a[@data-act="mass-delete"]'
        self.driver.find_element_by_xpath(mass_delete).click()
        self.driver.switch_to.alert.accept()
        self.driver.refresh()
        logger.info('Vacancies deleted')


def main():
    df = pd.read_csv('https://docs.google.com/spreadsheets/d/1zaxjdu9ESYy2MCNuDow0_5PnZpwEsyrdTQ_kk0PMZbw/'
                     'export?format=csv&id=1zaxjdu9ESYy2MCNuDow0_5PnZpwEsyrdTQ_kk0PMZbw&gid=892686484',
                     dtype={'phone': str, 'proxy': str})
    titles = df['title'].dropna().tolist()
    descriptions = df['description'].dropna().tolist()
    phones = df['phone'].dropna().tolist()
    logins = df['login'].dropna().tolist()
    passwords = df['password'].dropna().tolist()
    proxy = df['proxy'].dropna().tolist()[0]
    headless = False
    for i, _ in enumerate(titles):
        place = Placeua(proxy, headless=headless)
        place.auth(logins[i], passwords[i])
        place.dobavit_obyavlenie(titles[i], descriptions[i], phones[i])
        place.end()
        logger.info('sleeping')
        # sleep(35)


if __name__ == '__main__':
    while True:
        try:
            logger.info(__name__)
            main()
        except Exception as error:
            logger.exception(error)
