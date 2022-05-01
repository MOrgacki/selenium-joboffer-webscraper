from helpers.util_helper import UtilHelper
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import requests
from helpers.selenium_helper import SeleniumHelper
from locator import Locator


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

    def scrape_offer_view(self, driver, offer_html, s, name):
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
                # driver.execute_script(
                #     "window.scrollTo(0, document.body.scrollHeight);")
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

    def parse_tiles(self, starting_page: int, website_html: BeautifulSoup, s: requests.Session, company_data_array: list, selenium_helper: SeleniumHelper) -> list:
        # list view
        job_tiles = website_html('div', {'class': "offer__info"})
        for count, job_tile in enumerate(job_tiles, start=1):
            # Clear before next iteration
            name = ''
            address = ''
            email = ''
            tax = ''
            www_link = ''

            tile_header = job_tile.select(Locator.offer_title)
            if tile_header[0].name == "a":
                job_offer_url = tile_header[0].get('href')
                # job offer view
                selenium_helper.pass_apply_button(job_offer_url)
                page = selenium_helper.driver.page_source
                offer_html = self.parse_html(page)
                apply_button = offer_html.select_one(
                    Locator.apply_button).get('href')
                if apply_button == '':
                    print("empty button", job_offer_url)
                    continue
                else:
                    page = s.get(apply_button)
                    print(count, " ", apply_button)
                if "system.erecruiter.pl" in page.url:
                    # job offer view
                    selenium_helper.pass_company_link(job_offer_url)
                    # WebDriverWait(driver, 1).until(EC.any_of(
                    #     EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='button-employer-link']")),
                    #     EC.presence_of_element_located((By.CSS_SELECTOR, "a.ep-profile-link")),
                    #     EC.presence_of_element_located((By.CSS_SELECTOR, "a.employers-MuiButtonBase-root"))
                    # ))
                    offer_html = self.parse_html(
                        selenium_helper.driver.page_source)
                    which_case, name, company_data_html = self.scrape_offer_view(
                        selenium_helper.driver, offer_html, s, name)
                    (name, address, email, tax, www_link) = self.scrape_company_view(
                        company_data_html, which_case, name, address, email, tax, www_link)
                    # ADD to array
                    company_data_array.append((name, address, email, www_link))
            elif tile_header[0].name == "button":
                tile_button = selenium_helper.driver.find_element(
                    by=By.CSS_SELECTOR, value='a')
                tile_button.click()
                tile_link_multiple_cities = job_tile(
                    'a', {'class': "offer-regions__label"})[0]
                selenium_helper.driver.get(
                    tile_link_multiple_cities.get('href'))
                print("Przebiłem się przez button :)",
                      tile_link_multiple_cities.get('href'))

        return starting_page, company_data_array
