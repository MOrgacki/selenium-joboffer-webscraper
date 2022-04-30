import email
from time import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from locator import Locator
import requests


#nie biore pod uwage ofert z urzedow pracy
driver = webdriver.Chrome('./chromedriver')
company_data_array = []
url =  "https://www.pracuj.pl/pracuj"

def cfDecodeEmail(encodedString):
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email

def log_to_file(file_name, text, variable ):
        with open(file_name, 'a') as f:
            f.write(f"{text}+{variable}")
            f.write('\n')

def login(username: str, password: str) -> None:
    driver.get("https://login.pracuj.pl/")
    email_input = driver.find_element(by=By.CSS_SELECTOR, value="[data-test='input-email']")
    password_input = driver.find_element(by=By.CSS_SELECTOR, value="[data-test='input-password'")
    login_button = driver.find_element(by=By.CSS_SELECTOR, value="[data-test='button-login']")

    email_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()
    driver.implicitly_wait(20)

def cookies_handler():
    cookies_button = driver.find_element(by=By.CSS_SELECTOR, value="[data-test='button-accept-all-in-general']")
    cookies_button.click()

def assign_cookies(driver: webdriver):
    cookies = driver.get_cookies()
    request = requests.Session()
    for cookie in cookies:
       request.cookies.set(cookie['name'], cookie['value'])
    return request
    
def parse_html(content) -> BeautifulSoup:
    website_html = BeautifulSoup(content, "lxml")
    return website_html

def parse_tiles(website_html: BeautifulSoup) -> int:
    # list view
    job_tiles = website_html('div', {'class': "offer__info"})
    for count, job_tile in enumerate(job_tiles,start=1):
        tile_header = job_tile.select(".offer-details__title-link")
        if tile_header[0].name == "a":
            job_offer_url = tile_header[0].get('href')
            #job offer view
            driver.get(job_offer_url)
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-test='anchor-apply'][href^=http]")))
            except:
                try:
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='section-archived']")))
                    log_to_file('offers_archived.txt', 'Offer archived: ',job_offer_url)
                    break
                except:
                    print("Brak button aplikuj: ", job_offer_url)
                    break
            # try:
            #     driver.get(job_offer_url)
            #     WebDriverWait(driver, 20).until(EC.element_attribute_to_include((By.CSS_SELECTOR, "a[data-test='anchor-apply'][href^=http]")))
            # except:
            #     print("No button with anchor apply href")
            #     break
            page = driver.page_source
            offer_html = parse_html(page)
            apply_button = offer_html.select_one("[data-test='anchor-apply']").get('href')
            if apply_button == '':
                print("empty button", job_offer_url)
                break
            else:
                page = s.get(apply_button)
                print(count, " ",apply_button)
            if "system.erecruiter.pl" in page.url:
                #job offer view
                driver.get(job_offer_url+"#company-details")
                WebDriverWait(driver, 10).until(EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='button-employer-link']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.ep-profile-link")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.employers-MuiButtonBase-root"))
                ))
                offer_html = parse_html(driver.page_source)
                try:
                    company_link = offer_html.select_one("[data-test='button-employer-link']").get('href')
                    page = s.get(company_link)
                    print(company_link)
                    company_data_html = parse_html(page.content)
                except:
                    try:
                        company_link2 = offer_html.select_one("a.ep-profile-link").get('href')
                        page = s.get(company_link2)
                        print("erekturer link2", company_link2)
                        company_data_html = parse_html(page.content)
                    except:
                        try:
                            company_link3 = offer_html.select_one("a.employers-MuiButtonBase-root").get('href')
                            # driver.get(company_link3)
                            page = s.get(company_link3)
                            print("erekturer link3", company_link3)
                            company_data_html = parse_html(page.text)
                            for title in company_data_html.find_all('title'):
                                print(title.get_text())
                            break
                        except:
                            log_to_file('logs.txt', 'New case!',company_link3)
                #company details view
                company_data = company_data_html.select(".sidebar > .contact-details > div > div.text")
                # print(company_data[0].find("p") is not None)
                try:
                    company_data = company_data_html.select(".sidebar > .contact-details > div > div.text")
                    # print(company_data[0].find("h3") is not None)
                    if company_data[0].find("h3") is not None:
                        company_named = company_data[0].select("h3")
                        text = company_named[0].get_text()
                        print(text)
                    if company_data[0].find("p", itemprop="address") is not None:
                        company_address = company_data[0].find("p", itemprop="address")
                        text = company_address.get_text()
                        print(text)
                        if "protected" in text:
                           protected_email = company_data[0].find("p", itemprop="address").find("a", {"class":"__cf_email__"} )
                           encoded_email = protected_email.get("data-cfemail")
                           print(cfDecodeEmail(encoded_email)) 
                    if company_data[0].find("p", itemprop="taxID") is not None:
                        company_tax = company_data[0].find("p", itemprop="taxID")
                        text = company_tax.get_text()
                        print(text)
                    if company_data[0].find("a", itemprop="sameAs") is not None:
                        company_www_link = company_data[0].find("a", itemprop="sameAs")
                        text = company_www_link.get_text()
                        print(text)
                except:
                    try:
                        company_data = company_data_html.select("div.main-info > div.title-container > h1")
                        text = company_data[0].get_text()
                        print(text)
                        try:
                            company_data = company_data_html.select("ep-profile-link")
                        except:
                            log_to_file("companies.txt","Here is data for company without address: ",company_data_html)
                    except:
                        log_to_file("companies.txt","Here is data for company without address: ",company_data_html)
                
                #nazwa-#div.default-box.contact-details > div > div.text > h3
                #addres-#div.default-box.contact-details > div > div.text > [itemprop='address']
                #nip-div.default-box.contact-details > div > div.text > [itemprop='taxID']
                #itp-itd   


 
                # company_data_array.insert(len(company_data_array), company_data)
                # print(company_data_array)
        
        #jak istnieje ('button', {'class': "offer-details__title-link"}) to trzeba wybrac pierwszy offer-regions__label i wbic w jego link ahref
        elif tile_header[0].name == "button":
            tile_button = driver.find_element(by=By.CSS_SELECTOR, value='a')
            tile_button.click()
            tile_link_multiple_cities = job_tile('a', {'class': "offer-regions__label"})[0]
            driver.get(tile_link_multiple_cities.get('href'))
            print("Przebiłem się przez button :)", tile_link_multiple_cities.get('href'))
    return starting_page

login("organ108@o2.pl", "Swierku123!")
cookies_handler()

s = assign_cookies(driver)
try:
    WebDriverWait(driver=driver, timeout=10).until(EC.title_contains(("Oferty pracy")))
except:
    driver.get(url)


website_html = parse_html(driver.page_source)
#czytamy liczbe stron
temp_nr = website_html.select(Locator.pagination_number)
page_nr = int(temp_nr[0].next_element.replace('\n', ''))
for starting_page in range(1,page_nr,1):
    print("strona nr: ", starting_page)
    start = time.time()
    parse_tiles(website_html)
    end = time.time()
    print(f"dla strony nr {starting_page} wyszło:", (end - start)/60)
    page = s.get(url + "?pn=" + str(starting_page))
    website_html = parse_html(page.content)
