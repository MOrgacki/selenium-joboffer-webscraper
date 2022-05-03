
from posixpath import split
import selenium
from helpers.selenium_helper import SeleniumHelper
from selenium.webdriver.remote.webdriver import WebDriver
import requests
import pandas as pd
import configparser
from selenium.webdriver.support.ui import WebDriverWait
from crawler import Crawler
from helpers.util_helper import UtilHelper
from locator import Locator
from selenium.webdriver.support import expected_conditions as EC
import time
import numpy as np
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait

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


def initate_pairs(final_page, session, selenium_helper, starting_page):
    for starting_page in range(starting_page, final_page+1, 1):
        print("Strona nr: ", starting_page)
        start = time.time()
        crawler.parse_tiles(
            session, company_data_array, selenium_helper, starting_page)
        end = time.time()
        print(f"Stronie nr {starting_page} zajęło wykonanie:",
              (end - start)/60, 'min')
        page = session.get(main_url + "?pn=" +
                           str(starting_page))
        offers_list_html = crawler.parse_html(page.content)


def main():
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
    driver_instances = [selenium_helper, selenium_helper2, selenium_helper3, selenium_helper4, selenium_helper5,
                        selenium_helper6, selenium_helper7, selenium_helper8, selenium_helper9, selenium_helper10]

    selenium_helper.login(
        username, password, login_url)
    selenium_helper.cookies_handler()
    session = assign_cookies(selenium_helper.driver)
    try:
        time.sleep(5)
        selenium_helper.driver.get(main_url)
        WebDriverWait(driver=selenium_helper.driver, timeout=10).until(
            EC.title_contains(("Oferty pracy")))
    except:
        pass
    offers_list_html = crawler.parse_html(selenium_helper.driver.page_source)
    # count pages
    temp_nr = offers_list_html.select(Locator.pagination_number)
    page_nr = int(temp_nr[0].next_element.replace('\n', ''))
    ### DLA TESTU JEST HARDCODED 2!!!##########
    page_nr = 75
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

    page_nr = range(1, page_nr+1, 1)
    driver_pairs = len(driver_instances)
    splitted_pages = np.array_split(np.array(page_nr), driver_pairs)
    execution_pairs = list(zip(splitted_pages, driver_instances))
    futures = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        # page_nr = range(1, page_nr+1, 1)
        # driver_pairs = len(driver_instances)
        # splitted_pages = np.array_split(np.array(page_nr), driver_pairs)
        # execution_pairs = list(zip(splitted_pages, driver_instances))
        for pair in range(driver_pairs):
            starting_page = [*execution_pairs[pair][0]][:1][0]
            final_page = [*execution_pairs[pair][0]][-1]
            selenium_helper = execution_pairs[pair][1]
            futures.append(executor.submit(
                initate_pairs, final_page, session, selenium_helper, starting_page))
            # futures.append(executor.submit(
            #     self.scrape_job_tiles, count, s, company_data_array, par[0], selenium_helper))
            # count = count+1
        wait(futures)
    # for pair in range(driver_pairs):
    #     starting_page = [*execution_pairs[pair][0]][:1][0]
    #     final_page = [*execution_pairs[pair][0]][-1]
    #     selenium_helper = execution_pairs[pair][1]
    #     for starting_page in range(starting_page, final_page+1, 1):
    #         print("Strona nr: ", starting_page)
    #         start = time.time()
    #         crawler.parse_tiles(
    #             session, company_data_array, selenium_helper, starting_page)
    #         end = time.time()
    #         print(f"Stronie nr {starting_page} zajęło wykonanie:",
    #               (end - start)/60, 'min')
    #         page = session.get(main_url + "?pn=" +
    #                            str(starting_page))
    #         offers_list_html = crawler.parse_html(page.content)
    df = pd.DataFrame(company_data_array, columns=[
        "Nazwa", "Adres", "Email", "Strona WWW"])
    df.to_csv(temp_csv, index=False, encoding='utf-8')
    data = pd.read_csv(
        r"./temp.csv")
    data.drop_duplicates(keep='first', inplace=True)
    data.to_csv(result_csv)
    selenium_helper.driver.quit()


if __name__ == "__main__":
    main()
