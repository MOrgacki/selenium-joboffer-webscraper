
import selenium
from helpers.selenium_helper import SeleniumHelper
from selenium.webdriver.remote.webdriver import WebDriver
import requests
import pandas as pd
import configparser
from selenium.webdriver.support.ui import WebDriverWait
from crawler import Crawler
from locator import Locator
from selenium.webdriver.support import expected_conditions as EC
import time
import copy

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
selenium_helper2 = SeleniumHelper()
selenium_helper3 = SeleniumHelper()
selenium_helper4 = SeleniumHelper()
selenium_helper5 = SeleniumHelper()
selenium_helper6 = SeleniumHelper()
selenium_helper7 = SeleniumHelper()
selenium_helper8 = SeleniumHelper()
selenium_helper9 = SeleniumHelper()
selenium_helper10 = SeleniumHelper()
driver = selenium_helper.driver
driver2 = selenium_helper2.driver
driver3 = selenium_helper3.driver
driver4 = selenium_helper4.driver
driver5 = selenium_helper5.driver
driver6 = selenium_helper6.driver
driver7 = selenium_helper7.driver
driver8 = selenium_helper8.driver
driver9 = selenium_helper9.driver
driver10 = selenium_helper10.driver
crawler = Crawler()

# Local vars
company_data_array = []
starting_page = 0
which_case = None
futures = []


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
    session = assign_cookies(driver)
    try:
        time.sleep(5)
        driver.get(main_url)
        WebDriverWait(driver=driver, timeout=10).until(
            EC.title_contains(("Oferty pracy")))
    except:
        pass
    offers_list_html = crawler.parse_html(driver.page_source)
    # count pages
    temp_nr = offers_list_html.select(Locator.pagination_number)
    page_nr = int(temp_nr[0].next_element.replace('\n', ''))
    ### DLA TESTU JEST HARDCODED 2!!!##########
    page_nr = 20
    #####!!!!!!!!!!!!!!##########

    # with ThreadPoolExecutor(max_workers=2) as executor:
    #     for starting_page in executor.map(functools.partial(crawler.parse_tiles,
    #                                       s, company_data_array, selenium_helper), range(1, page_nr, 1)):
    #         print(starting_page)

    # crawler.parse_tiles(starting_page, offers_list_html,
    #                     s, company_data_array, selenium_helper)
    # wait(futures)

    # for starting_page in range(1, page_nr, 1):
    #     print("Strona nr: ", starting_page)
    #     start = time()
    #     crawler.parse_tiles(starting_page, offers_list_html,
    #                         s, company_data_array, selenium_helper)
    #     end = time()
    #     print(f"Stronie nr {starting_page} zajęło wykonanie:",
    #           (end - start)/60, 'min')
    #     page = s.get(main_url + "?pn=" + str(starting_page))
    #     offers_list_html = crawler.parse_html(page.content)

    # driver2.get("https://www.onet.pl")
    for starting_page in range(1, page_nr+1, 1):
        print("Strona nr: ", starting_page)
        start = time.time()
        crawler.parse_tiles(
            session, company_data_array, selenium_helper, starting_page)
        end = time.time()
        print(f"Stronie nr {starting_page} zajęło wykonanie:",
              (end - start)/60, 'min')
        page = session.get(main_url + "?pn=" + str(starting_page))
        offers_list_html = crawler.parse_html(page.content)
    df = pd.DataFrame(company_data_array, columns=[
        "Nazwa", "Adres", "Email", "Strona WWW"])
    df.to_csv(temp_csv, index=False, encoding='utf-8')
    data = pd.read_csv(
        r"./temp.csv")
    data.drop_duplicates(keep='first', inplace=True)
    data.to_csv(result_csv)
    driver.quit()


if __name__ == "__main__":
    main()
