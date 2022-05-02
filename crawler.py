from asyncio import futures
from itertools import cycle
from threading import Thread
from helpers.util_helper import UtilHelper
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import requests
from helpers.selenium_helper import SeleniumHelper
from locator import Locator
from time import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait
import functools


class Crawler:

    def parse_html(self, content) -> BeautifulSoup:
        website_html = BeautifulSoup(content, "lxml")
        return website_html

    def scrape_company_view(self, company_data_html, which_case, name, address, email, tax, www_link):
        try:
            if which_case == 1 or 2:
                company_data = company_data_html.select(
                    Locator.company_data1)
            if company_data[0].find("h3") is not None:
                company_name = company_data[0].select("h3")
                name = company_name[0].get_text()
                print(name)
            if company_data[0].find("p", itemprop="address") is not None:
                company_address = company_data[0].find("p", itemprop="address")
                address = company_address.get_text()
                print(address)
                if "protected" in address:
                    protected_email = company_data[0].find(
                        "p", itemprop="address").find("a", {"class": "__cf_email__"})
                    encoded_email = protected_email.get("data-cfemail")
                    email = UtilHelper.cfDecodeEmail(encoded_email)
                    print(email)
            if company_data[0].find("p", itemprop="taxID") is not None:
                company_tax = company_data[0].find("p", itemprop="taxID")
                tax = company_tax.get_text()
                print(tax)
            if company_data[0].find("a", itemprop="sameAs") is not None:
                company_www_link = company_data[0].find("a", itemprop="sameAs")
                www_link = company_www_link.get_text()
                print(www_link)
            elif which_case == 3:
                company_data = company_data_html.select(
                    Locator.company_data3)
                name = company_data[0].get_text()
                print(name)
        except:
            UtilHelper.log_to_file(
                "./logs/companies.txt", "Here is data for company without address: ", company_data_html)

        return (name, address, email, tax, www_link)

    def scrape_offer_view(self, offer_html, s, name):
        try:
            if offer_html.select_one(Locator.company_profile1_link) is not None:
                company_link = offer_html.select_one(
                    Locator.company_profile1_link).get('href')
                page = s.get(company_link)
                company_data_html = self.parse_html(page.content)
                which_case = 1
            elif offer_html.select_one(Locator.company_profile2_link) is not None:
                company_link2 = offer_html.select_one(
                    Locator.company_profile2_link).get('href')
                page = s.get(company_link2)
                company_data_html = self.parse_html(page.content)
                which_case = 2
            elif offer_html.select_one(Locator.company_profile3_link) is not None:
                company_link3 = offer_html.select_one(
                    Locator.company_profile3_link).get('href')
                page = s.get(company_link3)
                company_data_html = self.parse_html(page.text)
                which_case = 3
                for title in company_data_html.find_all('title'):
                    name = title.get_text()
                    print(title.get_text())
        except:
            UtilHelper.log_to_file('./logs/logs.txt',
                                   'New case for: ', company_link3)

        return which_case, name, company_data_html

    def scrape_job_offer_view(self, selenium_helper, job_offer_url, s, count, company_data_array, name, address, email, tax, www_link):
        selenium_helper.pass_apply_button(
            selenium_helper, job_offer_url)
        page = selenium_helper.driver.page_source
        offer_html = self.parse_html(page)
        apply_button = offer_html.select_one(
            Locator.apply_button).get('href')
        if apply_button == '' or None:
            print("empty button", job_offer_url)
        else:
            page = s.get(apply_button)
            print(count, " ", apply_button)
            if "system.erecruiter.pl" in page.url:
                # job offer view
                selenium_helper.pass_company_link(job_offer_url)
                offer_html = self.parse_html(
                    selenium_helper.driver.page_source)
                which_case, name, company_data_html = self.scrape_offer_view(
                    offer_html, s, name)
                (name, address, email, tax, www_link) = self.scrape_company_view(
                    company_data_html, which_case, name, address, email, tax, www_link)
                # ADD to array
                company_data_array.append((name, address, email, www_link))

    def execute_logic(self, count, s, company_data_array, job_tile, selenium_helper):
        name = ''
        address = ''
        email = ''
        tax = ''
        www_link = ''
        tile_header = job_tile.select(Locator.offer_title)
        if tile_header[0].name == "a":
            job_offer_url = tile_header[0].get('href')
            # job offer view
            self.scrape_job_offer_view(
                selenium_helper, job_offer_url, s, count, company_data_array, name, address, email, tax, www_link)
        elif tile_header[0].name == "button":
            tile_link_multiple_cities = job_tile(
                'a', {'class': "offer-regions__label"})[0]
            job_offer_url = tile_link_multiple_cities.get('href')
            selenium_helper.driver.get(job_offer_url)
            print("Przebiłem się przez button :)",
                  job_offer_url)
            self.scrape_job_offer_view(
                selenium_helper, job_offer_url, s, count, company_data_array, name, address, email, tax, www_link)

    def parse_tiles(self, s: requests.Session, company_data_array: list, selenium_helper: SeleniumHelper, starting_page: int, drivers_instance) -> list:
        try:
            # list view
            count = 1
            futures = []
            # Clear before next iteration
            # futures.append(executor.submit(
            #     self.execute_logic, count, job_tile, selenium_helper, s, company_data_array))
            # self.execute_logic(
            #     count, job_tile, selenium_helper, s, company_data_array)
            selenium_helper.driver.get("https://www.pracuj.pl/praca" +
                                       "?pn=" + str(starting_page))
            offers_list_html = self.parse_html(
                selenium_helper.driver.page_source)
            job_tiles = offers_list_html('div', {'class': "offer"})
            with ThreadPoolExecutor(max_workers=2) as executor:
                zip_list = zip(job_tiles, cycle(drivers_instance)) if (len(job_tiles)) > len(
                    drivers_instance) else zip(cycle(job_tiles), drivers_instance)
                for par in zip_list:
                    # Clear before next iteration
                    futures.append(executor.submit(
                        self.execute_logic, count, s, company_data_array, par[0], selenium_helper))
                    # self.execute_logic(
                    #     count, job_tile, selenium_helper, s, company_data_array)
                    count = count+1
                    print(futures)
        except:
            pass

        wait(futures)
        return starting_page, company_data_array
