from time import time
from helpers.selenium_helper import SeleniumHelper
from selenium.webdriver.remote.webdriver import WebDriver
import requests
import pandas as pd
import configparser
from selenium.webdriver.support.ui import WebDriverWait
from crawler import Crawler
from locator import Locator
from selenium.webdriver.support import expected_conditions as EC


# Config load
config = configparser.ConfigParser()
config.read('config.ini')
username = config['AUTH']['USERNAME']
password = config['AUTH']['PASSWORD']
main_url = config['APP']['URL']
login_url = config['APP']['LOGIN_URL']
temp_csv = config['FILES']['TEMP']
result_csv = config['FILES']['RESULT']

# Objects load
selenium_helper = SeleniumHelper()
driver = selenium_helper.driver
crawler = Crawler()

# Local vars
company_data_array = []
starting_page = 0
which_case = None


def assign_cookies(selenium: WebDriver):
    cookies = selenium.get_cookies()
    request = requests.Session()
    for cookie in cookies:
        request.cookies.set(cookie['name'], cookie['value'])
    return request


def main():
    selenium_helper.login(
        username, password, login_url)
    selenium_helper.cookies_handler()
    s = assign_cookies(driver)
    try:
        WebDriverWait(driver=driver, timeout=10).until(
            EC.title_contains(("Oferty pracy")))
    except:
        driver.get(main_url)
    offers_list_html = crawler.parse_html(driver.page_source)
    # count pages
    temp_nr = offers_list_html.select(Locator.pagination_number)
    page_nr = int(temp_nr[0].next_element.replace('\n', ''))
    ### DLA TESTU JEST HARDCODED 2!!!##########
    page_nr = 2
    #####!!!!!!!!!!!!!!##########
    for starting_page in range(1, page_nr, 1):
        print("Strona nr: ", starting_page)
        start = time()
        crawler.parse_tiles(starting_page, offers_list_html,
                            s, company_data_array, selenium_helper)
        end = time()
        print(f"Stronie nr {starting_page} zajęło wykonanie:",
              (end - start)/60, 'min')
        page = s.get(main_url + "?pn=" + str(starting_page))
        offers_list_html = crawler.parse_html(page.content)
    df = pd.DataFrame(company_data_array, columns=[
                      "Nazwa", "Adres", "Email", "Strona WWW"])
    df.to_csv(temp_csv, index=False, encoding='utf-8')
    data = pd.read_csv(
        r"/Applications/work/Private/Pracuj-WebScraping/temp.csv")
    data.drop_duplicates(keep='first', inplace=True)
    data.to_csv(result_csv)
    driver.quit()


if __name__ == "__main__":
    main()
