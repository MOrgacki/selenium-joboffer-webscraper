from configparser import ConfigParser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from helpers.util_helper import UtilHelper
from selenium.webdriver.remote.webdriver import BaseWebDriver
from selenium.webdriver.chrome.options import Options
from locator import Locator


class SeleniumHelper(BaseWebDriver):

    def __init__(self) -> None:
        # self.driver = webdriver.Chrome('./chromedriver')
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(
            './chromedriver', chrome_options=options)

    def login(self, username: str, password: str, login_url: ConfigParser) -> None:
        self.driver.get(login_url)
        email_input = self.driver.find_element(
            by=By.CSS_SELECTOR, value=Locator.email)
        password_input = self.driver.find_element(
            by=By.CSS_SELECTOR, value=Locator.password)
        login_button = self.driver.find_element(
            by=By.CSS_SELECTOR, value=Locator.login_btn)

        email_input.send_keys(username)
        password_input.send_keys(password)
        login_button.click()

    def cookies_handler(self):
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, Locator.accept_cookies_btn)))
        cookies_button = self.driver.find_element(
            by=By.CSS_SELECTOR, value=Locator.accept_cookies_btn)
        cookies_button.click()

    def pass_apply_button(self, job_offer_url):
        self.driver.get(job_offer_url)
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, Locator.apply_button_link)))
        except:
            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, Locator.archived_offer_button)))
                UtilHelper.log_to_file('./logs/offers_archived.txt',
                                       'Offer archived: ', job_offer_url)
            except:
                print("Brak button aplikuj: ", job_offer_url)

    def pass_company_link(self, job_offer_url):
        self.driver.get(job_offer_url+"#company-details")
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, Locator.company_profile1_link)))
        except:
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, Locator.company_profile2_link)))
            except:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, Locator.company_profile3_link)))
